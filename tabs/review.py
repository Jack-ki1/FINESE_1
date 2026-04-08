import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import StringIO
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import shared utilities
from utils import (
    get_numeric_columns, 
    get_categorical_columns, 
    get_datetime_columns,
    calculate_data_health_score,
    generate_recommendation_list
)
from config import BRAND_NAME, SECTION_HEADER_CLASS, SECTION_SUBHEADER_CLASS

# --- GLOBAL BADGE MAP (Single Source of Truth) ---
BADGE_MAP = {
    95: "🏆 Perfect Dataset",
    90: "🥇 Data Master",
    80: "🥈 Clean Data Apprentice",
    70: "🥉 Data Novice",
    60: "⚠️ Needs Attention",
    0: "📉 Critical Issues"
}


def render_review_tab(filtered: pd.DataFrame) -> None:
    """
    Unified Data Review Tab: Combines Overview + Quality into a single intelligent workflow.
    """
    if filtered is None or filtered.empty:
        st.warning("⚠️ No data available. Please load or filter data first.")
        return

    # --- Section 1: Data Preview (from overview.py) ---
    st.markdown(f'<div class="{SECTION_HEADER_CLASS}">📊 Data Snapshot</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="{SECTION_SUBHEADER_CLASS}">First & last 10 rows</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Rows")
        st.dataframe(filtered.head(10), use_container_width=True)
    with col2:
        st.subheader("Bottom 10 Rows")
        st.dataframe(filtered.tail(10), use_container_width=True)

    # --- Section 2: Column Summary (from overview.py) ---
    st.markdown('<hr class="div" />', unsafe_allow_html=True)
    st.markdown(f'<div class="{SECTION_HEADER_CLASS}">📋 Column Summary</div>', unsafe_allow_html=True)

    try:
        miss = filtered.isnull().sum()
        pct_missing = (miss / len(filtered) * 100).round(2)
        n_unique = filtered.nunique(dropna=False)

        meta_df = pd.DataFrame({
            "Column": filtered.columns,
            "Dtype": filtered.dtypes.astype(str),
            "Missing": miss.values,
            "% Missing": pct_missing.values,
            "Unique Values": n_unique.values
        })
        st.dataframe(meta_df, use_container_width=True, hide_index=True)

        with st.expander("🔍 Raw DataFrame.info()"):
            buf = StringIO()
            filtered.info(buf=buf)
            st.text(buf.getvalue())
    except Exception as e:
        logger.error(f"Error generating column summary: {e}")
        st.error("❌ Failed to generate column summary.")

    # --- Section 3: Auto-Summary Engine (from overview.py) ---
    st.markdown('<hr class="div" />', unsafe_allow_html=True)
    st.markdown(f'<div class="{SECTION_HEADER_CLASS}">🧠 Auto-Summary Engine</div>', unsafe_allow_html=True)
    st.caption("AI-driven insights to detect hidden data issues")

    if st.button("📄 Generate Data DNA Report", type="primary"):
        with st.spinner("Analyzing your data..."):
            insights = _generate_data_insights(filtered)

        st.markdown("### 🧬 Data DNA Report")
        if not insights:
            st.success("✅ No critical issues detected. Your data looks clean!")
        else:
            for insight in insights:
                st.markdown(f"- {insight}")

        with st.expander("📊 Suggested Next Steps"):
            st.markdown("""
            - 🔧 Use **Clean → Fill Mode** on columns with >30% missing values  
            - 🔄 Use **Types → Convert** to fix inconsistent strings (e.g., currency, commas)  
            - 📉 Use **Review → Outlier Analysis** to investigate skewed distributions  
            - 📈 Use **Chart Builder** to auto-generate visualizations  
            - 📤 Export this report via **Review → Export Report**
            """)

    # --- Section 4: Data Health Scorecard (from quality.py) ---
    st.markdown('<hr class="div" />', unsafe_allow_html=True)
    st.markdown(f'<div class="{SECTION_HEADER_CLASS}">🎯 Data Quality Dashboard</div>', unsafe_allow_html=True)
    st.caption("Comprehensive assessment of completeness, consistency, accuracy, and reliability")

    scorecard = calculate_data_health_score(filtered)
    _render_scorecard(scorecard)

    # --- Section 5: Visual Diagnostics (from quality.py) ---
    tabs = st.tabs([
        "🔍 Completeness",
        "🟨 Missing Heatmap",
        "📉 Outliers",
        "🌡️ Correlation",
        "📈 Distributions"
    ])

    with tabs[0]:
        _render_completeness_chart(filtered)
    with tabs[1]:
        _render_missing_heatmap(filtered)
    with tabs[2]:
        _render_outlier_analysis(filtered)
    with tabs[3]:
        _render_correlation_heatmap(filtered)
    with tabs[4]:
        _render_distributions(filtered)

    # --- Section 6: AI Recommendations & Export ---
    st.markdown('<hr class="div" />', unsafe_allow_html=True)
    st.markdown(f'<div class="{SECTION_HEADER_CLASS}">💡 Smart Recommendations & Export</div>', unsafe_allow_html=True)

    _render_recommendations(filtered, scorecard)
    _render_export_section(filtered, scorecard)


# =============== HELPER FUNCTIONS ===============

# --- From overview.py ---
def _generate_data_insights(df: pd.DataFrame) -> list[str]:
    insights = []
    missing = df.isnull().sum()
    high_miss_cols = missing[missing > len(df) * 0.3].index.tolist()
    if high_miss_cols:
        insights.append(f"⚠️ **Critical Missing Values**: `{', '.join(high_miss_cols)}` (>30% missing)")

    obj_cols = get_categorical_columns(df)
    for col in obj_cols:
        sample = df[col].dropna().astype(str)
        if sample.str.contains(r'[$€£¥]', na=False).any():
            insights.append(f"⚠️ **Inconsistent formatting in `{col}`**: Contains currency symbols")
        if sample.str.contains(r'[,\s]{2,}', na=False).any():
            insights.append(f"⚠️ **Inconsistent formatting in `{col}`**: Extra commas or whitespace detected")

    dup_count = df.duplicated().sum()
    if dup_count > 0:
        insights.append(f"⚠️ **Duplicates**: {dup_count:,} duplicate row(s) found")

    date_cols = get_datetime_columns(df)
    for col in date_cols:
        try:
            dates = pd.to_datetime(df[col], errors='coerce').dropna()
            if len(dates) < 2:
                continue
            gaps = dates.diff().dt.days.dropna()
            if len(gaps) > 0:
                median_gap = gaps.median()
                if median_gap > 7:
                    insights.append(f"⚠️ **Irregular sampling in `{col}`**: Median gap = {median_gap:.0f} days")
        except Exception as e:
            logger.debug(f"Could not analyze date column {col}: {e}")

    for col in df.columns:
        n_unique = df[col].nunique()
        n_total = len(df)
        if n_unique > 10 and (n_unique / n_total) > 0.95:
            insights.append(f"💡 **High cardinality in `{col}`**: {n_unique}/{n_total} unique values — consider label encoding or binning")

    num_cols = get_numeric_columns(df)
    for col in num_cols:
        skew = df[col].skew()
        if abs(skew) > 2:
            insights.append(f"⚠️ **Skewed distribution in `{col}`**: Skewness = {skew:.2f} (non-normal)")

    zero_var = df.nunique() == 1
    if zero_var.any():
        cols = zero_var[zero_var].index.tolist()
        insights.append(f"⚠️ **Zero variance columns**: `{', '.join(cols)}` — these contain only one value")

    return insights


def _render_scorecard(scorecard: Dict) -> None:
    score = scorecard["final_score"]
    badge = next((v for k, v in BADGE_MAP.items() if score >= k), BADGE_MAP[0])
    st.markdown(f"""
    <div style="text-align:center; padding:20px; background:#f0f7ff; border-radius:12px; margin:20px 0;">
        <h2>📊 DATA HEALTH SCORE: <span style="font-size:2em; color:#0ea5a4;">{score}/100</span></h2>
        <p style="font-size:1.2em; color:#1f2937;">🎯 {badge}</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    metrics = [
        ("Completeness", scorecard["details"]["completeness"], "🟢 Good" if scorecard["details"]["completeness"] >= 90 else "🟡 Warning"),
        ("Consistency", scorecard["details"]["consistency"], "🟢 Good" if scorecard["details"]["consistency"] >= 90 else "🟡 Warning"),
        ("Accuracy", scorecard["details"]["accuracy"], "🟢 Good" if scorecard["details"]["accuracy"] >= 80 else "🟡 Warning"),
        ("Uniqueness", scorecard["details"]["uniqueness"], "🟢 Good" if scorecard["details"]["uniqueness"] >= 90 else "🟡 Warning"),
        ("Timeliness", scorecard["details"]["timeliness"], "🟢 Good" if scorecard["details"]["timeliness"] >= 80 else "🟡 Warning"),
    ]
    for i, (label, value, status) in enumerate(metrics):
        with cols[i]:
            st.metric(label=label, value=f"{value}%", delta=status)


def _render_completeness_chart(df: pd.DataFrame) -> None:
    completeness = (1 - df.isnull().sum() / len(df)) * 100
    fig = px.bar(x=completeness.index, y=completeness.values,
                 labels={'x': 'Columns', 'y': 'Completeness (%)'},
                 title="Column Completeness (%)",
                 color=completeness.values, color_continuous_scale='RdYlGn', range_color=[0, 100])
    fig.update_layout(yaxis_range=[0, 100], height=400)
    st.plotly_chart(fig, use_container_width=True)


def _render_missing_heatmap(df: pd.DataFrame) -> None:
    missing_matrix = df.isnull().astype(int)
    fig = px.imshow(missing_matrix.T, labels=dict(x="Rows", y="Columns", color="Missing"),
                    title="Missing Values Heatmap (Yellow = Missing)", color_continuous_scale='Viridis')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def _render_outlier_analysis(df: pd.DataFrame) -> None:
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        st.info("No numeric columns available for outlier analysis.")
        return
    selected_col = st.selectbox("Select column for outlier analysis", numeric_cols, key="outlier_col_select")
    try:
        Q1 = df[selected_col].quantile(0.25)
        Q3 = df[selected_col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[selected_col] < lower_bound) | (df[selected_col] > upper_bound)]
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"#### Outlier Stats: `{selected_col}`")
            st.write(f"Lower Bound: `{lower_bound:.2f}`")
            st.write(f"Upper Bound: `{upper_bound:.2f}`")
            st.write(f"Outliers: `{len(outliers):,}` ({(len(outliers)/len(df)*100):.1f}%)")
            if len(outliers) > 0:
                st.warning("⚠️ Consider investigating or cleaning these outliers.")
        with col2:
            fig = px.box(df, y=selected_col, title=f"Box Plot: {selected_col}")
            fig.add_hline(y=lower_bound, line_dash="dash", line_color="red")
            fig.add_hline(y=upper_bound, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        logger.error(f"Outlier analysis failed on {selected_col}: {e}")
        st.error(f"❌ Could not compute outliers for `{selected_col}`")


def _render_correlation_heatmap(df: pd.DataFrame) -> None:
    num_cols = get_numeric_columns(df)
    if len(num_cols) < 2:
        st.info("Need at least 2 numeric columns for correlation analysis.")
        return
    corr = df[num_cols].corr(numeric_only=True)
    fig = px.imshow(corr, title="Correlation Heatmap", color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
    st.plotly_chart(fig, use_container_width=True)


def _render_distributions(df: pd.DataFrame) -> None:
    num_cols = get_numeric_columns(df)[:3]
    cat_cols = get_categorical_columns(df)[:3]
    if len(num_cols) > 0:
        st.markdown("##### Numeric Columns")
        cols = st.columns(len(num_cols))
        for i, col in enumerate(num_cols):
            with cols[i]:
                fig = px.histogram(df, x=col, nbins=30, title=col, marginal="box")
                st.plotly_chart(fig, use_container_width=True)
    if len(cat_cols) > 0:
        st.markdown("##### Categorical Columns")
        cols = st.columns(len(cat_cols))
        for i, col in enumerate(cat_cols):
            with cols[i]:
                vc = df[col].astype(str).value_counts(dropna=False).head(10)
                fig = px.bar(vc, x=vc.index, y=vc.values, title=col)
                st.plotly_chart(fig, use_container_width=True)


def _render_recommendations(df: pd.DataFrame, scorecard: Dict) -> None:
    recs = generate_recommendation_list(df, scorecard)
    if recs:
        for r in recs:
            st.markdown(f"- {r}")
    else:
        st.success("✅ Your data looks excellent! No major quality issues detected.")


def _render_export_section(df: pd.DataFrame, scorecard: Dict) -> None:
    st.markdown("##### 📥 Export Full Report")
    final_score_float = float(scorecard['final_score'])
    badge = next((v for k, v in BADGE_MAP.items() if final_score_float >= k), BADGE_MAP[0])

    report = StringIO()
    report.write("# 📊 Data Review Report\n\n")
    report.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    report.write(f"## 🏆 Data Health Score: **{final_score_float}/100** ({badge})\n\n")
    report.write("## 🔍 Key Metrics\n")
    for key, val in scorecard["details"].items():
        report.write(f"- **{key.title()}**: {val}%\n")
    report.write("\n## 💡 Recommendations\n")
    for r in generate_recommendation_list(df, scorecard):
        report.write(f"- {r}\n")
    report_content = report.getvalue()

    st.download_button(
        label="📥 Download as Markdown (.md)",
        data=report_content,
        file_name="data_review_report.md",
        mime="text/markdown",
        key="download_review_report"
    )

    if st.button("🖨️ Export as HTML (for PDF)", type="secondary"):
        badge_html = next((v for k, v in BADGE_MAP.items() if final_score_float >= k), BADGE_MAP[0])
        html = f"""
        <html><head><title>Data Review Report</title><style>
        body {{ font-family: sans-serif; margin: 40px; }}
        h1, h2 {{ color: #2c3e50; }}
        .badge {{ background: #0ea5a4; color: white; padding: 5px 10px; border-radius: 10px; }}
        </style></head><body>
        <h1>📊 Data Review Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <h2>🏆 Score: {final_score_float}/100 <span class="badge">{badge_html}</span></h2>
        <h3>Key Metrics</h3>
        <ul>{''.join(f'<li><strong>{k.title()}</strong>: {v}%</li>' for k,v in scorecard['details'].items())}</ul>
        <h3>Recommendations</h3>
        <ul>{''.join(f'<li>{r}</li>' for r in generate_recommendation_list(df, scorecard))}</ul>
        </body></html>
        """
        st.download_button(
            label="⬇️ Download as HTML",
            data=html.encode('utf-8'),
            file_name="data_review_report.html",
            mime="text/html",
            key="download_review_html"
        )