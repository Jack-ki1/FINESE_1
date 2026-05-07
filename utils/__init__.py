# Backward compatibility imports for existing code
# This allows old imports like "from utils import ..." to continue working

try:
    from .data_utils import *
except ImportError:
    # If the submodule fails to import, define functions here or provide fallbacks
    pass

try:
    from .ml_utils import *
except ImportError:
    pass

try:
    from .ui_utils import *
except ImportError:
    pass

try:
    from .health_utils import *
except ImportError:
    pass

# Import availability constants from the original utils.py or define them here
try:
    from .. import utils as old_utils
    # Import the constants from the old utils module
    XGB_AVAILABLE = getattr(old_utils, 'XGB_AVAILABLE', False)
    LGBM_AVAILABLE = getattr(old_utils, 'LGBM_AVAILABLE', False)
    CATBOOST_AVAILABLE = getattr(old_utils, 'CATBOOST_AVAILABLE', False)
    IMBLEARN_AVAILABLE = getattr(old_utils, 'IMBLEARN_AVAILABLE', False)
    OPTUNA_AVAILABLE = getattr(old_utils, 'OPTUNA_AVAILABLE', False)
    SHAP_AVAILABLE = getattr(old_utils, 'SHAP_AVAILABLE', False)
except (ImportError, AttributeError):
    # Define defaults if old utils module is not available
    XGB_AVAILABLE = False
    LGBM_AVAILABLE = False
    CATBOOST_AVAILABLE = False
    IMBLEARN_AVAILABLE = False
    OPTUNA_AVAILABLE = False
    SHAP_AVAILABLE = False

# For functions that were in the original utils.py but not moved yet
import pandas as pd
import numpy as np
import streamlit as st
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def detect_high_cardinality(df: pd.DataFrame, threshold: int = 50) -> List[tuple]:
    """
    Detect columns with high cardinality (many unique values)
    """
    out = []
    for c in df.select_dtypes(include=['object','category']).columns:
        if df[c].nunique(dropna=True) > threshold:
            out.append((c, df[c].nunique()))
    return out

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