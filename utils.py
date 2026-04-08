import io
import os
import time
import json
import tempfile
import base64
import numpy as np
import pandas as pd
import logging
import streamlit as st
from datetime import datetime
# Heavy ML and preprocessing imports are loaded lazily inside functions to
# reduce cold-start time (especially important for deployments like HF Spaces).
from typing import List, Dict, Optional, Tuple, Any, Union
import warnings

warnings.filterwarnings("ignore")

# Import configuration
from config import (
    BRAND_NAME,
    DEFAULT_CV_FOLDS,
    DEFAULT_N_ESTIMATORS,
    DEFAULT_RANDOM_STATE,
    DATE_PARSE_THRESHOLD
)

# Optional library availability flags
try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

try:
    from xgboost import XGBClassifier, XGBRegressor
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier, LGBMRegressor
    LGBM_AVAILABLE = True
except Exception:
    LGBM_AVAILABLE = False

try:
    from catboost import CatBoostClassifier, CatBoostRegressor
    CATBOOST_AVAILABLE = True
except Exception:
    CATBOOST_AVAILABLE = False

try:
    from imblearn.over_sampling import SMOTE
    IMBLEARN_AVAILABLE = True
except Exception:
    IMBLEARN_AVAILABLE = False

try:
    import optuna
    OPTUNA_AVAILABLE = True
except Exception:
    OPTUNA_AVAILABLE = False

try:
    import chardet
    CHARDET_AVAILABLE = True
except Exception:
    CHARDET_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_app() -> None:
    """
    Reset all application state to initial empty state.
    Clears base_df, work_df, resets flags, and triggers rerun.
    """
    try:
        # Explicitly delete DataFrames to free memory
        if 'base_df' in st.session_state and st.session_state.base_df is not None:
            del st.session_state.base_df
        if 'work_df' in st.session_state and st.session_state.work_df is not None:
            del st.session_state.work_df
        if 'filtered_data' in st.session_state and st.session_state.filtered_data is not None:
            del st.session_state.filtered_data
            
        st.session_state.base_df = None
        st.session_state.work_df = None
        st.session_state.filtered_data = None
        st.session_state.data_loaded = False
        st.session_state.reset_requested = True
        st.session_state.selected_date_col = None
        st.session_state.date_range = None
        # Clear all dynamic filters
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith(("filter_", "slider_"))]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        logger.info("App reset: All session state cleared.")
        st.rerun()
    except Exception as e:
        logger.error(f"Error during reset_app(): {e}")
        st.error("❌ Failed to reset app. Please refresh the page.")


def get_filtered_data() -> pd.DataFrame:
    """
    Apply global user-defined filters to the working dataset (`work_df`).
    Filters include:
      - Date range (auto-detected date columns)
      - Categorical selection (dropdowns for low-cardinality columns)
      - Numeric range sliders (for top 10 numeric columns)

    Returns:
        pd.DataFrame: Filtered view of `st.session_state.work_df`
    """
    if "work_df" not in st.session_state or st.session_state.work_df is None or st.session_state.work_df.empty:
        return pd.DataFrame()

    # Lightweight caching: avoid recomputing filtered view on every render
    try:
        work = st.session_state.work_df
        fkey = (
            len(work),
            work.shape[1],
            int(work.isnull().sum().sum()),
            int(work.duplicated().sum()),
            int(work.memory_usage(deep=True).sum())
        )
        cached = st.session_state.get('filtered_data')
        cached_key = st.session_state.get('filtered_data_key')
        if cached is not None and cached_key == fkey:
            return cached.copy()
    except Exception:
        # if anything goes wrong, fall through and recompute
        pass

    # Work with a copy to avoid modifying the original
    filtered = st.session_state.work_df.copy()

    # Limit the size of data we work with to prevent memory issues
    max_rows = 10000  # Limit to 10k rows for performance
    if len(filtered) > max_rows:
        filtered = filtered.sample(n=max_rows, random_state=42)
        st.warning(f"⚠️ Working with a sample of {max_rows:,} rows for performance. Load fewer rows for full data.")

    # --- DATE RANGE FILTER ---
    date_candidates = [
        c for c in filtered.columns
        if "date" in c.lower() or "time" in c.lower() or pd.api.types.is_datetime64_any_dtype(filtered[c])
    ]

    if date_candidates:
        # Initialize selected date column if not set
        if "selected_date_col" not in st.session_state:
            st.session_state.selected_date_col = date_candidates[0]

        dcol = st.session_state.selected_date_col

        try:
            filtered[dcol] = pd.to_datetime(filtered[dcol], errors="coerce")
            valid_dates = filtered[dcol].dropna()
            if len(valid_dates) > 0:
                mind, maxd = valid_dates.min(), valid_dates.max()
                if pd.notna(mind) and pd.notna(maxd):
                    # Initialize date range if not set
                    if "date_range" not in st.session_state:
                        st.session_state.date_range = (mind.date(), maxd.date())

                    sel = st.session_state.date_range
                    if isinstance(sel, tuple) and len(sel) == 2:
                        try:
                            s = pd.to_datetime(sel[0])
                            e = pd.to_datetime(sel[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                            filtered = filtered[(filtered[dcol] >= s) & (filtered[dcol] <= e)]
                        except Exception as e:
                            logger.warning(f"Invalid date range: {e}")
        except Exception as e:
            logger.warning(f"Failed to parse date column '{dcol}': {e}")

    # --- CATEGORICAL FILTERS ---
    cat_cols = filtered.select_dtypes(include=["object", "category"]).columns.tolist()

    for c in cat_cols:
        n_unique = filtered[c].nunique(dropna=False)
        if 1 < n_unique <= 30:  # Reasonable cardinality for dropdown
            key = f"filter_{c}"
            unique_vals = filtered[c].astype(str).unique().tolist()
            default_selection = unique_vals  # Default: all selected

            # Initialize session state if needed
            if key not in st.session_state:
                st.session_state[key] = default_selection

            picked = st.session_state[key]
            if isinstance(picked, list) and len(picked) > 0:
                filtered = filtered[filtered[c].astype(str).isin(picked)]

    # --- NUMERIC SLIDERS ---
    num_cols = filtered.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = num_cols[:10]  # Cap at 10 to avoid clutter

    for c in num_cols:
        min_val = float(filtered[c].min())
        max_val = float(filtered[c].max())

        if min_val == max_val:
            continue

        key = f"slider_{c}"

        if key not in st.session_state:
            st.session_state[key] = (min_val, max_val)

        lo, hi = st.session_state[key]
        lo = max(lo, min_val)
        hi = min(hi, max_val)
        filtered = filtered[(filtered[c] >= lo) & (filtered[c] <= hi)]

    # Store filtered copy in session state for quick reuse
    try:
        st.session_state['filtered_data'] = filtered.copy()
        st.session_state['filtered_data_key'] = fkey
    except Exception:
        pass

    return filtered

def create_kpis(k1, k2, k3, k4, k5, df: pd.DataFrame) -> None:
    """
    Render five KPI cards in provided Streamlit columns.
    Dynamically adapts to light/dark theme via CSS classes.

    Args:
        k1-k5: Streamlit columns where KPIs will be rendered
        df: DataFrame to compute metrics from
    """
    if df.empty:
        for col in [k1, k2, k3, k4, k5]:
            col.markdown("<div class='kpi'><div class='lbl'>N/A</div><div class='val'>-</div></div>", unsafe_allow_html=True)
        return

    rows = len(df)
    cols = df.shape[1]
    nulls = int(df.isnull().sum().sum())
    duplicates = int(df.duplicated().sum())
    memory_kb = df.memory_usage(deep=True).sum() / 1024

    theme = st.session_state.get("theme", "light")
    theme_class = "dark" if theme == "dark" else "light"

    kpi_template = """
    <div class="kpi kpi-{theme}">
        <div class="lbl">{label}</div>
        <div class="val">{value}</div>
    </div>
    """

    with k1:
        st.markdown(
            kpi_template.format(theme=theme_class, label="Rows", value=f"{rows:,}"),
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            kpi_template.format(theme=theme_class, label="Columns", value=f"{cols:,}"),
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            kpi_template.format(theme=theme_class, label="Nulls", value=f"{nulls:,}"),
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            kpi_template.format(theme=theme_class, label="Duplicates", value=f"{duplicates:,}"),
            unsafe_allow_html=True
        )
    with k5:
        st.markdown(
            kpi_template.format(theme=theme_class, label="Memory (KB)", value=f"{memory_kb:,.1f}"),
            unsafe_allow_html=True
        )


def detect_encoding_bytes(raw_bytes: bytes) -> str:
    """
    Detect encoding of raw bytes using chardet if available, otherwise default to utf-8
    """
    if CHARDET_AVAILABLE:
        try:
            return chardet.detect(raw_bytes).get('encoding', 'utf-8')
        except Exception:
            return 'utf-8'
    return 'utf-8'


def read_csv_robust(uploaded_file) -> pd.DataFrame:
    """
    Robust CSV reader that tries multiple encodings
    """
    try:
        raw = uploaded_file.read()
        enc = detect_encoding_bytes(raw)
        uploaded_file.seek(0)

        for e in [enc, 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding=e)
            except Exception:
                continue

        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file)
    except Exception as e:
        raise Exception(f"Failed to read file: {e}")


def df_memory_kb(df: pd.DataFrame) -> float:
    """
    Calculate memory usage of dataframe in KB
    """
    return df.memory_usage(deep=True).sum() / 1024.0


def detect_duplicates(df: pd.DataFrame) -> int:
    """
    Count duplicate rows in dataframe
    """
    return int(df.duplicated().sum())


def detect_high_cardinality(df: pd.DataFrame, threshold: int = 50) -> List[Tuple[str, int]]:
    """
    Detect columns with high cardinality (many unique values)
    """
    out = []
    for c in df.select_dtypes(include=['object','category']).columns:
        if df[c].nunique(dropna=True) > threshold:
            out.append((c, df[c].nunique()))
    return out


def try_parse_dates(df: pd.DataFrame, sample_rows: int = 1000) -> Tuple[pd.DataFrame, List[str]]:
    """
    Try to parse date columns automatically
    Returns tuple of (df, list of converted columns)
    """
    converted = []
    for col in df.columns:
        if np.issubdtype(df[col].dtype, np.datetime64):
            continue
        if df[col].dtype == object or np.issubdtype(df[col].dtype, np.number):
            sample = df[col].dropna().astype(str).head(sample_rows)
            if sample.empty:
                continue
            try:
                parsed = pd.to_datetime(sample, errors='coerce', infer_datetime_format=True)
                if parsed.notnull().mean() > DATE_PARSE_THRESHOLD:
                    df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    converted.append(col)
            except Exception:
                continue
    return df, converted


def date_feature_engineer(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """
    Expand datetime column into components (year, month, day, etc.)
    """
    s = pd.to_datetime(df[col], errors='coerce')
    df[f"{col}__year"] = s.dt.year
    df[f"{col}__month"] = s.dt.month
    df[f"{col}__day"] = s.dt.day
    df[f"{col}__weekday"] = s.dt.weekday
    df[f"{col}__is_weekend"] = s.dt.weekday.isin([5,6]).astype(int)
    df[f"{col}__dayofyear"] = s.dt.dayofyear
    return df


def target_encode_column(train_series: pd.Series, target_series: pd.Series, smoothing: float = 0.2) -> pd.Series:
    """
    Simple target encoding with smoothing to avoid overfitting
    """
    temp = pd.concat([train_series, target_series], axis=1)
    stats = temp.groupby(train_series.name)[target_series.name].agg(['mean','count'])
    global_mean = target_series.mean()
    stats['smoothed'] = (stats['mean'] * stats['count'] + global_mean * smoothing) / (stats['count'] + smoothing)
    return train_series.map(stats['smoothed']).fillna(global_mean)


def build_preprocessor(
    df: pd.DataFrame,
    target: str,
    encoding_strategy: str = 'onehot',
    scale_numeric: bool = True,
    poly_degree: int = 1,
    include_interactions: bool = False,
    target_encode_cols: Optional[List[str]] = None
) -> Tuple[Any, List[str], List[str], callable]:
    """
    Build ColumnTransformer preprocessor with options
    Returns: (preprocessor, numeric_cols, cat_cols, get_feature_names_func)
    """
    # Lazy-import sklearn preprocessing tools to reduce cold-start time
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler, PolynomialFeatures
    X = df.drop(columns=[target])
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(include=['object','category','bool']).columns.tolist()
    numeric_cols = [c for c in numeric_cols if not np.issubdtype(df[c].dtype, np.datetime64)]

    num_steps = [('imputer', SimpleImputer(strategy='mean'))]
    if scale_numeric:
        num_steps.append(('scaler', StandardScaler()))
    if poly_degree > 1:
        pf = PolynomialFeatures(degree=poly_degree, include_bias=False, interaction_only=not include_interactions)
        num_steps.append(('poly', pf))

    cat_steps = [('imputer', SimpleImputer(strategy='most_frequent'))]
    if encoding_strategy == 'onehot':
        cat_steps.append(('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
    else:
        cat_steps.append(('encoder', OrdinalEncoder()))

    transformers = []
    if numeric_cols:
        transformers.append(('num', Pipeline(num_steps), numeric_cols))
    if cat_cols:
        transformers.append(('cat', Pipeline(cat_steps), cat_cols))

    preproc = ColumnTransformer(transformers=transformers, remainder='drop', sparse_threshold=0)

    def get_feature_names(preproc_obj):
        fn = []
        if not hasattr(preproc_obj, 'transformers_'):
            return fn
        for name, trans, cols in preproc_obj.transformers_:
            if name == 'num':
                fn.extend(cols)
            elif name == 'cat':
                enc = trans.named_steps.get('encoder')
                if enc is not None and hasattr(enc, 'get_feature_names_out'):
                    try:
                        fn.extend(list(enc.get_feature_names_out(cols)))
                    except Exception:
                        fn.extend(cols)
                else:
                    fn.extend(cols)
        return fn

    return preproc, numeric_cols, cat_cols, get_feature_names


def model_key_to_estimator(key: str, problem_type: str):
    """
    Convert model key string to sklearn estimator instance
    """
    # Lazy-import estimators to avoid heavy sklearn imports during app startup
    try:
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
        from sklearn.naive_bayes import GaussianNB
        from sklearn.svm import SVC
        from sklearn.linear_model import LogisticRegression, LinearRegression
    except Exception:
        # If sklearn isn't available, raise an informative error when used
        RandomForestClassifier = RandomForestRegressor = None
        KNeighborsClassifier = KNeighborsRegressor = None
        GaussianNB = SVC = None
        LogisticRegression = LinearRegression = None

    k = key.lower()
    if problem_type == 'Classification':
        if 'randomforest' in k:
            return RandomForestClassifier(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'xgb' in k or 'xgboost' in k:
            return XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=DEFAULT_RANDOM_STATE, n_estimators=DEFAULT_N_ESTIMATORS) if XGB_AVAILABLE else RandomForestClassifier(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'lgbm' in k or 'lightgbm' in k:
            return LGBMClassifier(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE) if LGBM_AVAILABLE else RandomForestClassifier(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'catboost' in k or 'cat' in k:
            return CatBoostClassifier(verbose=0, random_seed=DEFAULT_RANDOM_STATE) if CATBOOST_AVAILABLE else RandomForestClassifier(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'knn' in k:
            return KNeighborsClassifier()
        if 'naive' in k or 'bayes' in k:
            return GaussianNB()
        if 'logistic' in k or 'linear' in k:
            return LogisticRegression(max_iter=4000)
        if 'svc' in k or 'svm' in k:
            return SVC(probability=True)
        return RandomForestClassifier(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
    else:  # Regression
        if 'randomforest' in k:
            return RandomForestRegressor(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'xgb' in k or 'xgboost' in k:
            return XGBRegressor(random_state=DEFAULT_RANDOM_STATE, n_estimators=DEFAULT_N_ESTIMATORS) if XGB_AVAILABLE else RandomForestRegressor(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'lgbm' in k or 'lightgbm' in k:
            return LGBMRegressor(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE) if LGBM_AVAILABLE else RandomForestRegressor(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'catboost' in k or 'cat' in k:
            return CatBoostRegressor(verbose=0, random_seed=DEFAULT_RANDOM_STATE) if CATBOOST_AVAILABLE else RandomForestRegressor(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)
        if 'knn' in k:
            return KNeighborsRegressor()
        if 'linear' in k:
            return LinearRegression()
        return RandomForestRegressor(n_estimators=DEFAULT_N_ESTIMATORS, random_state=DEFAULT_RANDOM_STATE, n_jobs=-1)


def generate_code_snippet(preproc, model, problem_type: str, target: str) -> str:
    """
    Generate a reproducible Python snippet for training & inference
    """
    snippet = f"""# Auto-generated training snippet
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split

# Load your dataset
df = pd.read_csv("your_dataset.csv")
X = df.drop(columns=["{target}"])
y = df["{target}"]

# Replace this with the preprocessor and model used in the app
# pipeline = joblib.load("pipeline_model.joblib")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the pipeline
# pipeline.fit(X_train, y_train)

# Make predictions
# preds = pipeline.predict(X_test)

# Save the trained pipeline
# joblib.dump(pipeline, "pipeline_model.joblib")
"""
    return snippet


# new  add
def log_change(action: str, details: str = "") -> None:
    """
    Append a change to the change log with timestamp
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "change_log" not in st.session_state:
        st.session_state["change_log"] = []
    st.session_state["change_log"].append(f"[{ts}] {action} {details}".strip())


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of numeric columns from a DataFrame
    """
    return df.select_dtypes(include=[np.number]).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of categorical columns from a DataFrame
    """
    return df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()


def get_datetime_columns(df: pd.DataFrame) -> List[str]:
    """
    Get list of datetime columns from a DataFrame
    """
    return [c for c in df.columns if "date" in c.lower() or "time" in c.lower() or pd.api.types.is_datetime64_any_dtype(df[c])]


def safe_convert_type(series: pd.Series, target_type: str) -> pd.Series:
    """
    Safely convert a pandas series to a target type
    """
    try:
        if target_type == "datetime64[ns]":
            return pd.to_datetime(series, errors="coerce")
        elif target_type in ["bool", "boolean"]:
            mapping = {"true": True, "false": False, "yes": True, "no": False, "1": True, "0": False}
            return series.astype(str).str.lower().map(mapping).astype(target_type)
        elif target_type in ["Int64", "Float64"]:
            return pd.to_numeric(series, errors="coerce").astype(target_type)
        elif target_type == "category":
            return series.astype("category")
        elif target_type == "string":
            return series.astype("string")
        else:
            return series.astype(target_type, errors="raise")
    except Exception as e:
        logger.warning(f"Failed to convert series to {target_type}: {e}")
        return series


def calculate_data_health_score(df: pd.DataFrame) -> Dict:
    """
    Calculate a comprehensive data health score for a DataFrame
    """
    # Lightweight caching: avoid recomputing across tab switches when data unchanged
    try:
        key = (
            len(df),
            df.shape[1],
            int(df.isnull().sum().sum()),
            int(df.duplicated().sum()),
            int(df.memory_usage(deep=True).sum())
        )
        cached = st.session_state.get('cached_data_health')
        if cached and isinstance(cached, dict) and cached.get('key') == key:
            return cached.get('value')
    except Exception:
        # Fallback to normal computation if any quick metric fails
        pass
    total_cols = len(df.columns)
    total_cells = len(df) * total_cols
    missing_cells = df.isnull().sum().sum()
    completeness = max(0, 100 - (missing_cells / total_cells * 100))

    consistency = 100
    obj_cols = get_categorical_columns(df)
    for col in obj_cols:
        series = df[col].astype(str)
        if series.str.contains(r'^\s+|\s+$', regex=True).any():
            consistency -= 3
        if series.str.contains(r'[A-Z]{2,}').any() and series.str.contains(r'[a-z]').any():
            consistency -= 2
        if series.str.contains(r'[$€£¥,]', regex=True).any():
            consistency -= 4

    accuracy = 100
    num_cols = get_numeric_columns(df)
    for col in num_cols:
        col_lower = col.lower()
        if any(k in col_lower for k in ['price', 'cost', 'amount', 'fee', 'age', 'year']):
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                accuracy -= min(15, (neg_count / len(df)) * 100)
        if 'age' in col_lower:
            impossible = (df[col] > 150).sum()
            if impossible > 0:
                accuracy -= min(10, (impossible / len(df)) * 100)

    uniqueness = 100
    for col in df.columns:
        ratio = df[col].nunique() / len(df)
        if ratio > 0.95 and df[col].dtype == 'object':
            uniqueness -= 5

    timeliness = 100
    date_cols = get_datetime_columns(df)
    latest_date = None
    if date_cols:
        try:
            d = pd.to_datetime(df[date_cols[0]], errors='coerce').dropna()
            if len(d) > 0:
                latest_date = d.max()
                days_old = (pd.Timestamp.now() - latest_date).days
                if days_old > 365:
                    timeliness -= 20
                elif days_old > 180:
                    timeliness -= 10
        except Exception as e:
            logger.debug(f"Could not parse date column {date_cols[0]}: {e}")

    weights = {"completeness": 0.3, "consistency": 0.25, "accuracy": 0.25, "uniqueness": 0.1, "timeliness": 0.1}
    final_score = (
        completeness * weights["completeness"] +
        consistency * weights["consistency"] +
        accuracy * weights["accuracy"] +
        uniqueness * weights["uniqueness"] +
        timeliness * weights["timeliness"]
    )

    result = {
        "final_score": round(final_score, 1),
        "details": {
            "completeness": round(completeness, 1),
            "consistency": round(consistency, 1),
            "accuracy": round(accuracy, 1),
            "uniqueness": round(uniqueness, 1),
            "timeliness": round(timeliness, 1),
        },
        "weights": weights,
        "metrics": {
            "total_rows": len(df),
            "total_cols": total_cols,
            "missing_cells": missing_cells,
            "missing_pct": round(missing_cells / total_cells * 100, 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "date_col": date_cols[0] if date_cols else None,
            "latest_date": latest_date.isoformat() if latest_date else None,
        }
    }

    # Store in session cache (key computed earlier) when possible
    try:
        st.session_state['cached_data_health'] = {'key': key, 'value': result}
    except Exception:
        pass

    return result


def generate_recommendation_list(df: pd.DataFrame, scorecard: Dict) -> List[str]:
    """
    Generate a list of recommendations based on data health score
    """
    recs = []
    if scorecard["details"]["completeness"] < 85:
        recs.append("🔴 High missing values detected — Use **Clean → Fill Mode** to impute or drop columns.")
    if scorecard["details"]["consistency"] < 90:
        recs.append("🟡 Inconsistent text formats — Use **Clean → Convert** to standardize currency, casing, or spacing.")
    if scorecard["details"]["accuracy"] < 80:
        recs.append("🔴 Invalid values found — Check for negative prices, impossible ages, or illogical entries.")
    if scorecard["details"]["uniqueness"] < 90:
        recs.append("💡 High-cardinality categories — Consider binning or encoding for ML pipelines.")
    if scorecard["details"]["timeliness"] < 80:
        date_col = scorecard["metrics"].get("date_col")
        if date_col:
            recs.append(f"⏳ Dataset appears outdated — Last update: {scorecard['metrics']['latest_date']}. Refresh source?")
    num_cols = get_numeric_columns(df)
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if len(outliers) > len(df) * 0.05:
            recs.append(f"⚠️ High outliers in `{col}` — Use **Review → Outlier Analysis** to investigate.")
    return recs