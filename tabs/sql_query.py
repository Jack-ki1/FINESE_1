import streamlit as st
import pandas as pd
import numpy as np
import duckdb
import time
from datetime import datetime
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import shared utilities and config
from utils import log_change
from config import BRAND_NAME, SECTION_HEADER_CLASS, SECTION_SUBHEADER_CLASS

def render_sql_tab(df: pd.DataFrame) -> None:
    """
    SQL Query Interface - allows users to query their data using SQL
    """
    if df is None or df.empty:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return

    st.markdown(f'<div class="{SECTION_HEADER_CLASS}">🔍 SQL Query Interface</div>', unsafe_allow_html=True)
    st.caption("Query your data using DuckDB SQL — no database setup required.")

    # Register the DataFrame as a table
    conn = duckdb.connect()
    conn.register("data", df)

    # Show schema
    with st.expander("📋 Table schema"):
        try:
            schema = conn.execute("DESCRIBE data").fetchdf()
            st.dataframe(schema, use_container_width=True)
        except Exception as e:
            st.error(f"Error getting schema: {e}")

    # Query editor
    default_query = "SELECT *\nFROM data\nLIMIT 100"
    query = st.text_area("SQL Query", value=default_query, height=120, key="sql_query")

    col1, col2 = st.columns([1, 4])
    with col1:
        run = st.button("▶ Run Query", type="primary")
    with col2:
        st.caption("Ctrl+Enter to run · DuckDB dialect")

    if run and query.strip():
        try:
            start = time.time()
            result = conn.execute(query).fetchdf()
            elapsed = time.time() - start

            st.success(f"✅ {len(result):,} rows returned in {elapsed*1000:.0f}ms")
            st.dataframe(result, use_container_width=True)

            # Export result
            st.download_button(
                "📥 Download Result (CSV)",
                data=result.to_csv(index=False),
                file_name="query_result.csv",
                mime="text/csv"
            )
            
            log_change("Executed SQL query", f"Rows returned: {len(result)}, Time: {elapsed*1000:.0f}ms")
        except Exception as e:
            st.error(f"❌ Query error: {e}")
            logger.error(f"SQL query error: {e}")

    conn.close()