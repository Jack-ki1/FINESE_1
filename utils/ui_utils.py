import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

def create_kpis(df: pd.DataFrame) -> None:
    """Create KPI cards showing dataset health metrics."""
    if df.empty:
        st.warning("No data to display KPIs for")
        return
    
    # Calculate metrics
    total_rows = len(df)
    total_cols = len(df.columns)
    missing_cells = df.isnull().sum().sum()
    missing_pct = (missing_cells / (total_rows * total_cols)) * 100 if total_rows > 0 and total_cols > 0 else 0
    duplicate_rows = df.duplicated().sum()
    memory_usage = df.memory_usage(deep=True).sum() / (1024 * 1024)  # MB
    
    # Create KPI cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    with kpi1:
        st.metric(
            label="📊 Rows",
            value=f"{total_rows:,}",
            delta=None
        )
    
    with kpi2:
        st.metric(
            label="📈 Cols", 
            value=f"{total_cols}",
            delta=None
        )
    
    with kpi3:
        st.metric(
            label="❌ Missing (%)",
            value=f"{missing_pct:.1f}%",
            delta=None
        )
    
    with kpi4:
        st.metric(
            label="🔄 Duplicates", 
            value=f"{duplicate_rows:,}",
            delta=None
        )
    
    with kpi5:
        st.metric(
            label="💾 Memory (MB)",
            value=f"{memory_usage:.1f} MB",
            delta=None
        )

def log_change(operation: str, details: str = "") -> None:
    """Log a change to the change log in session state."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {operation}"
    if details:
        entry += f" ({details})"
    
    # Maintain only the last 20 log entries to prevent excessive memory usage
    if "change_log" not in st.session_state:
        st.session_state.change_log = []
    
    st.session_state.change_log.append(entry)
    
    # Keep only last 20 entries
    if len(st.session_state.change_log) > 20:
        st.session_state.change_log = st.session_state.change_log[-20:]
    
    # Also log to Python logger
    logger.info(f"Change logged: {entry}")

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
        st.session_state.change_log = []
        
        # Reset ML-related states
        ml_states = [
            'pipeline', 'target_col', 'problem_type', 'selected_features', 
            'learning_type', 'leaderboard', 'encoding_method', 'scaling_method',
            'missing_value_strategy', 'n_clusters', 'clustering_algo', 'unsupervised_task'
        ]
        
        for state in ml_states:
            if state in st.session_state:
                del st.session_state[state]
        
        # Reset chatbot states
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        
        # Reset filter states
        filter_keys = [k for k in st.session_state.keys() if k.startswith('filter_') or k.startswith('slider_')]
        for key in filter_keys:
            del st.session_state[key]
        
        # Reset cached states
        cache_keys = ['filtered_data_key', 'cached_data_health']
        for key in cache_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        st.rerun()
    except Exception as e:
        logger.error(f"Error during app reset: {e}")
        # Fallback: refresh the page
        st.rerun()

def display_change_log() -> None:
    """Display the change log in the UI."""
    if "change_log" in st.session_state and st.session_state.change_log:
        with st.expander("📝 Recent Actions", expanded=False):
            for entry in reversed(st.session_state.change_log):
                st.caption(f"`{entry}`")
    else:
        st.info("No actions logged yet")

def show_data_overview(df: pd.DataFrame) -> None:
    """Show an overview of the dataframe."""
    if df.empty:
        st.warning("No data to display overview for")
        return
    
    st.markdown("### 📋 Data Overview")
    
    # Shape info
    shape_info = pd.DataFrame({
        'Rows': [len(df)],
        'Columns': [len(df.columns)],
        'Cells': [df.size],
        'Memory Usage (MB)': [df.memory_usage(deep=True).sum() / (1024 * 1024)]
    })
    st.dataframe(shape_info, use_container_width=True)
    
    # Data types
    st.markdown("#### Column Types")
    dtype_counts = df.dtypes.value_counts()
    dtype_df = pd.DataFrame({
        'Type': dtype_counts.index.astype(str),
        'Count': dtype_counts.values
    })
    st.dataframe(dtype_df, use_container_width=True)
    
    # Sample of data
    st.markdown("#### Sample Data (First 5 rows)")
    st.dataframe(df.head(), use_container_width=True)