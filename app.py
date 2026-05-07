import streamlit as st
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from io import StringIO
import requests
import base64

# Import custom modules — ONLY the final, harmonized ones
from config import *
from theme import LIGHT, DARK


# Always import from the utils PACKAGE (utils/) to avoid conflicts with the top-level utils.py
from utils.ui_utils import reset_app, create_kpis
from utils.data_utils import get_filtered_data
from utils.health_utils import calculate_data_health_score

from state import SESSION_DEFAULTS

# Define supported LLM providers and their models
SUPPORTED_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
    },
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    },
    "google": {
        "name": "Google Gemini",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]
    }
}

# =============== PAGE CONFIG =================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# Add this for Hugging Face compatibility
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# =============== LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import new state management
from state import init_session

# Initialize session state
init_session()

# Apply theme function
def apply_theme():
    from theme import LIGHT, DARK
    css = LIGHT if st.session_state.theme == "light" else DARK
    st.markdown(css, unsafe_allow_html=True)

# Apply the appropriate theme based on user preference
apply_theme()

for key, default_value in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =============== HELPER FUNCTIONS FOR LAZY LOADING =================
def lazy_load_tab(tab_name):
    """Dynamically import and render tab content only when needed"""
    try:
        if tab_name == "review":
            from tabs.review import render_review_tab
            return render_review_tab
        elif tab_name == "cleaning":
            from tabs.cleaning import render_cleaning_tab
            return render_cleaning_tab
        elif tab_name == "charts":
            from tabs.charts import render_charts_tab
            return render_charts_tab
        elif tab_name == "chatbot":
            from tabs.chatbot import render_chatbot_tab
            return render_chatbot_tab
        elif tab_name == "make_a_model":
            from tabs.make_a_model import render_make_a_model_tab
            return render_make_a_model_tab
        elif tab_name == "export":
            from tabs.export import render_export_tab
            return render_export_tab
    except Exception as e:
        logger.error(f"Error loading tab {tab_name}: {e}")
        def error_tab(*args, **kwargs):
            st.error(f"Failed to load {tab_name} tab. Please refresh the app.")
        return error_tab


# =============== SIDEBAR ===============
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    
    # Theme selector
    theme = st.selectbox(
        "🎨 Theme",
        ["light", "dark"],
        index=0 if st.session_state.theme == "light" else 1,
        key="theme_selector"
    )
    
    # Update theme in session state and apply it
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

    # Reset Button — resets homepage flag too!
    if st.session_state.data_loaded:
        if st.button("🔄 Reset App", type="primary", use_container_width=True):
            reset_app()
            st.session_state.homepage_shown = False  # 👈 RESET HOMEPAGE FLAG ON RESET
            st.rerun()

    st.markdown("### 📂 Load Data")
    source = st.selectbox(
        "Source",
        ["Upload Files", "Paste JSON", "API Request", "Web Page (tables)"],
        key="data_source"
    )

    uploaded_map = {}

    if source == "Upload Files":
        files = st.file_uploader(
            "Upload CSV, Excel, or JSON (multi-file ok)",
            type=["csv", "xlsx", "xls", "json"],
            accept_multiple_files=True,
            key="file_uploader"
        )
        if files:
            for f in files:
                nm = f.name
                try:
                    if nm.lower().endswith(".csv"):
                        uploaded_map[nm] = pd.read_csv(f)
                    elif nm.lower().endswith((".xlsx", ".xls")):
                        xls = pd.ExcelFile(f)
                        for sh in xls.sheet_names:
                            uploaded_map[f"{nm} :: {sh}"] = pd.read_excel(f, sheet_name=sh)
                    elif nm.lower().endswith(".json"):
                        try:
                            uploaded_map[nm] = pd.read_json(f)
                        except ValueError:
                            f.seek(0)
                            uploaded_map[nm] = pd.read_json(f, lines=True)
                except Exception as e:
                    st.error(f"{nm}: {e}")

    elif source == "Paste JSON":
        raw = st.text_area("Paste JSON array or JSON Lines", key="json_paste")
        if raw.strip():
            try:
                uploaded_map["pasted.json"] = pd.read_json(StringIO(raw))
            except ValueError:
                uploaded_map["pasted.jsonl"] = pd.read_json(StringIO(raw), lines=True)

    elif source == "API Request":
        url = st.text_input("GET URL", key="api_url")
        if url:
            try:
                r = requests.get(url, timeout=20)
                if r.ok:
                    try:
                        uploaded_map[url] = pd.read_json(StringIO(r.text))
                    except ValueError:
                        uploaded_map[url] = pd.read_csv(StringIO(r.text))
                else:
                    st.error(f"HTTP {r.status_code}")
            except Exception as e:
                st.error(f"Request failed: {e}")

    elif source == "Web Page (tables)":
        page = st.text_input("URL with HTML tables", key="web_url")
        if page:
            try:
                html = requests.get(page, timeout=20).text
                tables = pd.read_html(html)
                idx = st.number_input("Table index", 0, max(0, len(tables) - 1), 0, key="table_idx")
                uploaded_map[page] = tables[int(idx)]
            except Exception as e:
                st.error(f"Scrape failed: {e}")

    # Handle dataset selection
        
    if uploaded_map:
        if len(uploaded_map) == 1:
            st.session_state.base_df = next(iter(uploaded_map.values()))
            st.session_state.data_loaded = True
            st.session_state.work_df = st.session_state.base_df.copy()  # ✅ Initialize work_df
            # Invalidate cached filtered view and health score when data changes
            st.session_state['filtered_data'] = None
            st.session_state['cached_data_health'] = None
            st.success("✅ Dataset loaded.")
        else:
            choice = st.radio("Multiple datasets found", ["Combine (union columns)", "Pick one"], key="combine_choice")
            if choice.startswith("Combine"):
                all_cols = sorted(set().union(*[set(v.columns) for v in uploaded_map.values()]))
                aligned = [v.reindex(columns=all_cols) for v in uploaded_map.values()]
                st.session_state.base_df = pd.concat(aligned, ignore_index=True, sort=False)
                st.session_state.data_loaded = True
                st.session_state.work_df = st.session_state.base_df.copy()  # ✅ FIXED
                # Invalidate cached filtered view and health score when data changes
                st.session_state['filtered_data'] = None
                st.session_state['cached_data_health'] = None
                st.success(f"✅ Combined {len(uploaded_map)} datasets.")
            else:
                pick = st.selectbox("Select dataset", list(uploaded_map.keys()), key="dataset_select")
                st.session_state.base_df = uploaded_map[pick]
                st.session_state.data_loaded = True
                st.session_state.work_df = st.session_state.base_df.copy()  # ✅ FIXED
                # Invalidate cached filtered view and health score when data changes
                st.session_state['filtered_data'] = None
                st.session_state['cached_data_health'] = None
                
    # Reduce / Shape Data
    # Guard against None: base_df may be None if no dataset was loaded yet.
    if st.session_state.base_df is not None and not getattr(st.session_state.base_df, "empty", True):
        st.markdown("---")
        st.markdown("### ✂️ Reduce / Shape")
        subset_rows = st.number_input("Limit rows (0 = no limit)", 0, len(st.session_state.base_df), 0, key="subset_rows")
        drop_cols = st.multiselect("Drop columns", list(st.session_state.base_df.columns), key="drop_cols")

        reduced = st.session_state.base_df.copy()
        if subset_rows > 0:
            reduced = reduced.head(subset_rows)
        if drop_cols:
            reduced = reduced.drop(columns=drop_cols)

        if st.button("Reset Working to Reduced", key="reset_working"):
            st.session_state.work_df = reduced.copy()
            # Invalidate caches after changing working dataset
            st.session_state['filtered_data'] = None
            st.session_state['cached_data_health'] = None
            st.success("✅ Working dataset updated.")

    # === CHATBOT LLM SETTINGS ===
    st.markdown("---")
    st.markdown("### 🤖 Chatbot Options")

    use_llm = st.toggle(
        "💡 Use External AI",
        value=False,
        key="use_llm",
        help="Enables advanced AI responses (requires API key)."
    )

    if use_llm:
        # Provider selection
        provider = st.selectbox(
            "🧠 AI Provider",
            options=list(SUPPORTED_PROVIDERS.keys()),
            format_func=lambda x: SUPPORTED_PROVIDERS[x]["name"],
            key="llm_provider"
        )
        
        # Get the selected provider info
        provider_info = SUPPORTED_PROVIDERS[provider]
        
        # API key input
        api_key = st.text_input(
            f"🔑 {provider_info['name']} API Key",
            type="password",
            key=f"{provider}_api_key",
            help=f"Enter your {provider_info['name']} API key"
        )
        
        # Model selection
        available_models = provider_info["models"]
        model_name = st.selectbox(
            "🤖 Model",
            options=available_models,
            index=0 if DEFAULT_LLM_MODEL in available_models else None,
            key="llm_model",
            help="Select the model to use"
        )
    else:
        st.info("🔒 Small Brain is active. No internet needed. Fast and safe.")


# =============== HEADER ===============
now_str = datetime.now().strftime("%b %d, %Y · %H:%M")

# Function to convert image to base64 - simplified for Hugging Face
def get_image_as_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None


# Path to your logo image - use relative path for Hugging Face
logo_path = "logo.png"
logo_base64 = get_image_as_base64(logo_path)

if logo_base64:
    logo_url = f"data:image/png;base64,{logo_base64}"
else:
    # Fallback to default logo or placeholder
    logo_url = "https://placehold.co/40x40/png"  # Placeholder image

st.markdown(f"""
<div class="header">
  <div class="brand">
    <div class="logo"><img src="{logo_url}" alt="logo" width="32" height="32"></div>
    <div>
      <div class="title">FINESE · Smart Data Explorer Pro</div>
      <div class="subtitle">Fast insights • Clean visuals • Board-ready reports</div>
    </div>
  </div>
  <div style="text-align:right;">
    <div style="font-weight:700;">{now_str}</div>
    <div style="opacity:.8;">Today</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Early stop if no data — but now we assume user came from homepage or loaded data
if not st.session_state.data_loaded or st.session_state.work_df is None:
    st.info("📥 Load a dataset from the sidebar to begin. CSV/Excel/JSON/API/HTML tables all supported.")
    st.stop()

# =============== GLOBAL FILTERS ===============
filtered = get_filtered_data()

# =============== KPIs ===============
with st.container():
    create_kpis(filtered)

# =============== TABS ===============
tabs = st.tabs([
    "🔎 Review",
    "🧹 Cleaning",
    "📊 Charts & Pivot",
    "🤖 Chatbot",
    "⚙️ Make a Model",
     "📥 Export"     
])

# ---------- LAZY LOADING OF TABS ----------
# Only load and render content for the active tab to reduce memory usage

# NEW — Single Review Tab
with tabs[0]:
    render_func = lazy_load_tab("review")
    render_func(filtered)

# NEW — Unified Cleaning Tab
with tabs[1]:
    render_func = lazy_load_tab("cleaning")
    render_func()

# NEW — Unified Charts & Pivot Tab
with tabs[2]:
    render_func = lazy_load_tab("charts")
    render_func(filtered)

# ---------- CHATBOT ----------
with tabs[3]:
    render_func = lazy_load_tab("chatbot")
    render_func(filtered)

# ---------- MAKE A MODEL ----------
with tabs[4]:
    render_func = lazy_load_tab("make_a_model")
    render_func(filtered)
    
# ---------- EXPORT ----------
with tabs[5]:
    render_func = lazy_load_tab("export")
    render_func(filtered)
