import streamlit as st
from typing import Literal

# =============================
# AETHER THEME — THE SOUL OF DATA
# =============================
# Designed for emotional resonance, cognitive ease, and timeless elegance.
# Light = Celestial Dawn | Dark = Nebula Night
# No clutter. No noise. Just clarity, crafted.

# Base CSS variables for both themes
BASE_CSS = """
/* === BASE LAYER — CEREMONIAL SPACE === */
:root {
  /* Typography */
  --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Border Radius */
  --border-radius: 16px;
  --border-width: 1px;

  /* Shadows — Depth Without Weight */
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

  /* Chart Palette — 8 Harmonized Hues */
  --chart-1: #0ea5e9;   /* Teal */
  --chart-2: #3b82f6;   /* Blue */
  --chart-3: #8b5cf6;   /* Purple */
  --chart-4: #10b981;   /* Emerald */
  --chart-5: #f59e0b;   /* Amber */
  --chart-6: #ef4444;   /* Red */
  --chart-7: #ec4899;   /* Pink */
  --chart-8: #84cc16;   /* Lime */

  /* Hover & Interaction */
  --hover-glow: 0 0 12px rgba(147, 197, 253, 0.3);
  --focus-ring: 0 0 0 2px rgba(147, 197, 253, 0.4);
}

/* === GLOBAL RESET === */
* {
  font-family: var(--font-primary);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-sizing: border-box;
}

body {
  line-height: 1.6;
  overflow-x: hidden;
  padding: 0 !important;
  margin: 0 !important;
}

/* === HEADER / BRAND BAR === */
.header {
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: var(--shadow-lg);
  margin-bottom: 0.5rem;
  animation: fadeInDown 0.7s ease-out;
}

.brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.logo::after {
  content: '';
  position: absolute;
  width: 120%;
  height: 120%;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: rotate 12s linear infinite;
  opacity: 0.2;
}

.title {
  font-weight: 800;
  font-size: 1.4rem;
  letter-spacing: -0.3px;
  margin: 0;
  line-height: 1.1;
}

.subtitle {
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 2px;
  opacity: 0.9;
  display: block;
  letter-spacing: -0.1px;
}

.time-badge {
  text-align: right;
  font-size: 0.8rem;
}

.time-badge strong {
  font-weight: 700;
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
  box-shadow: var(--shadow-md);
  padding-top: 1rem;
  position: relative;
  overflow: visible;
}

section[data-testid="stSidebar"] .block-container {
  padding: 0 1rem 1rem;
}

section[data-testid="stSidebar"] h3 {
  font-weight: 700;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  font-size: 1.1rem;
  letter-spacing: -0.05px;
}

/* === MAIN CONTENT === */
.main .block-container {
  max-width: 1500px;
  padding: 1rem;
  margin: 0 auto;
  position: relative;
}

/* === BUTTONS === */
.stButton > button,
button.stButton {
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-family: var(--font-primary);
}

.stButton > button:hover,
button.stButton:hover {
  transform: translateY(-2px);
  box-shadow: var(--hover-glow);
}

.btn-reset {
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.btn-reset:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

/* === KPI CARDS === */
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin: 1.25rem 0 1.5rem;
  padding: 0 1rem;
}

.kpi {
  border-radius: var(--border-radius);
  padding: 1.25rem;
  box-shadow: var(--kpi-shadow);
  text-align: center;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(147, 197, 253, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.5s ease;
  z-index: -1;
}

.kpi:hover::before {
  opacity: 1;
}

.kpi:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 32px rgba(147, 197, 253, 0.2);
}

.kpi .lbl {
  font-size: 0.8rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  margin-bottom: 0.5rem;
  display: block;
  text-transform: uppercase;
  font-family: var(--font-primary);
}

.kpi .val {
  font-size: 1.75rem;
  font-weight: 800;
  line-height: 1.1;
  font-feature-settings: "tnum";
  font-variant-numeric: tabular-nums;
  font-family: var(--font-primary);
}

/* === SECTIONS === */
.section-h {
  font-weight: 800;
  font-size: 1.4rem;
  margin: 1.5rem 0 1rem;
  padding-bottom: 0.5rem;
  position: relative;
  letter-spacing: -0.2px;
}

.section-h::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 3px;
  border-radius: 2px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.section-sub {
  font-size: 0.95rem;
  margin-bottom: 1.25rem;
  font-weight: 500;
  opacity: 0.9;
  letter-spacing: -0.05px;
}

hr.div {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(156, 163, 175, 0.2), transparent);
  margin: 1.5rem 0;
}

/* === DATAFRAMES === */
[data-testid="stDataFrame"] {
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  margin: 1rem 0;
}

[data-testid="stDataFrame"] th {
  font-weight: 600;
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
}

[data-testid="stDataFrame"] td {
  padding: 0.6rem 0.8rem;
  font-size: 0.9rem;
}

[data-testid="stDataFrame"] tr:hover {
  transform: scale(1.005);
  transition: all 0.2s ease;
}

/* === EXPANDERS === */
.streamlit-expanderHeader {
  border-radius: var(--border-radius);
  padding: 0.8rem 1.2rem;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.3rem;
  box-shadow: var(--shadow-sm);
}

.streamlit-expanderHeader:hover {
  box-shadow: var(--shadow-md);
}

.streamlit-expanderContent {
  border-radius: 0 0 var(--border-radius) var(--border-radius);
  padding: 1.2rem;
  margin-top: -1px;
  box-shadow: var(--shadow-sm);
}

/* === CHART CONTAINERS === */
div[data-testid="stPlotlyChart"] {
  border-radius: var(--border-radius);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  margin: 1.25rem 0;
}

div[data-testid="stPlotlyChart"] .main svg {
  background: var(--bg-card) !important;
}

/* === SLIDERS & INPUTS === */
.stSlider > div > div {
  border-radius: 9999px;
  height: 6px;
}

.stSlider > div > div > div {
  box-shadow: var(--shadow-sm);
  border-radius: 50%;
  width: 18px;
  height: 18px;
  transition: all 0.2s ease;
}

.stSlider > div > div > div:hover {
  transform: scale(1.15);
}

.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  outline: none;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
  box-shadow: var(--focus-ring);
}

/* === TOOLTIPS & INFO BOXES === */
.stAlert {
  border-left: 4px solid var(--accent-primary);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  margin: 1rem 0;
  padding: 0.8rem 1rem;
}

.stInfo {
  border-left-color: var(--accent-primary);
}

.stWarning {
  border-left-color: var(--accent-amber);
}

.stError {
  border-left-color: var(--danger);
}

/* === FONTS & TYPOGRAPHY === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* === ANIMATIONS === */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* === MOBILE RESPONSIVE === */
@media (max-width: 768px) {
  .header {
    padding: 0.5rem 0.75rem;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  .brand {
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }
  .title {
    font-size: 1.2rem;
  }
  .kpis {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  .main .block-container {
    padding: 0.75rem;
  }
  .section-h {
    font-size: 1.2rem;
    margin: 1rem 0 0.75rem;
  }
  .section-sub {
    font-size: 0.9rem;
  }
  .kpi .val {
    font-size: 1.5rem;
  }
  [data-testid="stDataFrame"] th,
  [data-testid="stDataFrame"] td {
    padding: 0.4rem;
    font-size: 0.8rem;
  }
}

/* === FINAL TOUCHES === */
*::-webkit-scrollbar {
  width: 8px;
}

*::-webkit-scrollbar-track {
  background: transparent;
}

*::-webkit-scrollbar-thumb {
  border-radius: 10px;
  border: 2px solid var(--bg-primary);
}

*::-webkit-scrollbar-thumb:hover {
  background: var(--accent-secondary);
}

/* === DISABLE STREAMLIT DEFAULT ANIMATIONS === */
.stSpinner {
  display: none !important;
}

/* === CUSTOM RADIO BUTTONS === */
.stRadio > div > label {
  border-radius: var(--border-radius);
  padding: 0.4rem 0.8rem;
  margin: 0.2rem 0;
  transition: all 0.2s ease;
}

.stRadio > div > label:hover {
  box-shadow: var(--shadow-sm);
}

.stRadio > div > label:nth-child(1) {
  border-top-left-radius: var(--border-radius);
  border-bottom-left-radius: var(--border-radius);
}

.stRadio > div > label:nth-last-child(1) {
  border-top-right-radius: var(--border-radius);
  border-bottom-right-radius: var(--border-radius);
}
"""

# Light Theme CSS
LIGHT_CSS = """
body {
  background-color: #fafafa !important;
  color: #1f2937;
}

.header {
  background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,250,0.9));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(156, 163, 175, 0.2);
}

/* Color System — Calibrated for the Human Eye */
:root {
  --bg-primary: #fafafa;
  --bg-secondary: #f3f4f6;
  --bg-card: #ffffff;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-mute: #9ca3af;
  
  /* Primary Accent — Trust & Intelligence (Teal) */
  --accent-primary: #0ea5e9;
  --accent-secondary: #3b82f6;
  --accent-gradient: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));

  /* Secondary Accent — Insight (Amber) */
  --accent-amber: #f59e0b;
  --accent-amber-light: #fbbf24;

  /* Semantic Colors */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;

  /* KPI Card — Soft Glow, Not Noise */
  --kpi-bg: rgba(239, 246, 255, 0.8);
  --kpi-border: rgba(147, 197, 253, 0.3);
  --kpi-shadow: 0 8px 24px rgba(147, 197, 253, 0.1);
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
  background: linear-gradient(to bottom, var(--bg-primary), var(--bg-secondary));
  border-right: 1px solid rgba(156, 163, 175, 0.15);
}

section[data-testid="stSidebar"] h3 {
  color: var(--text-primary);
  border-bottom: 1px solid rgba(156, 163, 175, 0.15);
}

.logo {
  background: var(--accent-gradient);
  border: 1px solid rgba(255,255,255,0.5);
}

.title {
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--text-primary), #1e40af);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--text-secondary);
}

.time-badge {
  color: var(--text-secondary);
}

.time-badge strong {
  color: var(--text-primary);
}

/* === BUTTONS === */
.stButton > button,
button.stButton {
  background: var(--accent-gradient);
  border: 1px solid rgba(147, 197, 253, 0.3);
}

.stButton > button:hover,
button.stButton:hover {
  border-color: rgba(147, 197, 253, 0.6);
  background: linear-gradient(135deg, #3b82f6, #0ea5e9);
}

.btn-reset {
  background: linear-gradient(135deg, var(--danger), #dc2626);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-reset:hover {
  background: linear-gradient(135deg, #dc2626, #ef4444);
}

/* === KPI CARDS === */
.kpi {
  background: var(--kpi-bg);
  border: 1px solid var(--kpi-border);
  border: 1px solid rgba(239, 246, 255, 0.5);
}

.kpi:hover {
  border-color: rgba(147, 197, 253, 0.6);
}

.kpi .lbl {
  color: var(--text-secondary);
}

.kpi .val {
  color: var(--text-primary);
}

/* === SECTIONS === */
.section-h {
  color: var(--text-primary);
  border-bottom: 2px solid rgba(156, 163, 175, 0.2);
}

.section-h::after {
  background: var(--accent-gradient);
}

.section-sub {
  color: var(--text-secondary);
}

/* === DATAFRAMES === */
[data-testid="stDataFrame"] {
  border: 1px solid rgba(156, 163, 175, 0.2);
  background: var(--bg-card);
}

[data-testid="stDataFrame"] th {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom: 1px solid rgba(156, 163, 175, 0.2);
}

[data-testid="stDataFrame"] td {
  border-bottom: 1px solid rgba(156, 163, 175, 0.1);
}

[data-testid="stDataFrame"] tr:hover {
  background-color: rgba(239, 246, 255, 0.5);
}

/* === EXPANDERS === */
.streamlit-expanderHeader {
  background: var(--bg-secondary);
  border: 1px solid rgba(156, 163, 175, 0.2);
  color: var(--text-primary);
}

.streamlit-expanderHeader:hover {
  background: var(--bg-secondary);
}

.streamlit-expanderContent {
  background: var(--bg-card);
  border: 1px solid rgba(156, 163, 175, 0.2);
  border-top: none;
}

/* === CHART CONTAINERS === */
div[data-testid="stPlotlyChart"] {
  background: var(--bg-card);
  border: 1px solid rgba(156, 163, 175, 0.1);
}

/* === SLIDERS & INPUTS === */
.stSlider > div > div {
  background: var(--accent-gradient);
}

.stSlider > div > div > div {
  background-color: var(--bg-card);
  border: 2px solid var(--accent-primary);
}

.stSlider > div > div > div:hover {
  box-shadow: 0 0 10px rgba(147, 197, 253, 0.4);
}

.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
  background: var(--bg-card);
  border: 1px solid rgba(156, 163, 175, 0.3);
  color: var(--text-primary);
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
  border-color: var(--accent-primary);
}

/* === TOOLTIPS & INFO BOXES === */
.stAlert {
  background: var(--bg-card);
  border: 1px solid rgba(156, 163, 175, 0.1);
}

.stInfo {
  background: rgba(239, 246, 255, 0.4);
}

.stWarning {
  background: rgba(255, 247, 230, 0.4);
}

.stError {
  background: rgba(254, 235, 235, 0.4);
}

/* === CUSTOM RADIO BUTTONS === */
.stRadio > div > label {
  background: var(--bg-secondary);
  border: 1px solid rgba(156, 163, 175, 0.2);
  color: var(--text-primary);
}

.stRadio > div > label:hover {
  background: var(--bg-card);
}

*::-webkit-scrollbar-thumb {
  background: var(--accent-primary);
  border: 2px solid var(--bg-primary);
}
"""

# Dark Theme CSS
DARK_CSS = """
body {
  background-color: #0f172a !important;
  color: #f1f5f9;
}

.header {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}

/* Color System — Deep Space, Zero Eye Strain */
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-card: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-mute: #64748b;
  
  /* Primary Accent — Electric Teal */
  --accent-primary: #0ea5e9;
  --accent-secondary: #3b82f6;
  --accent-gradient: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));

  /* Secondary Accent — Neon Amber */
  --accent-amber: #f59e0b;
  --accent-amber-light: #fbbf24;

  /* Semantic Colors */
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;

  /* KPI Card — Glowing Translucency */
  --kpi-bg: rgba(30, 41, 59, 0.7);
  --kpi-border: rgba(147, 197, 253, 0.15);
  --kpi-shadow: 0 8px 24px rgba(147, 197, 253, 0.1);
}

/* === SIDEBAR === */
section[data-testid="stSidebar"] {
  background: linear-gradient(to bottom, var(--bg-primary), var(--bg-secondary));
  border-right: 1px solid rgba(147, 197, 253, 0.1);
}

section[data-testid="stSidebar"] h3 {
  color: var(--text-primary);
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}

.logo {
  background: var(--accent-gradient);
  border: 1px solid rgba(147, 197, 253, 0.1);
}

.logo::after {
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  opacity: 0.15;
}

.title {
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--text-primary), #dbeafe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--text-secondary);
}

.time-badge {
  color: var(--text-secondary);
}

.time-badge strong {
  color: var(--text-primary);
}

/* === BUTTONS === */
.stButton > button,
button.stButton {
  background: var(--accent-gradient);
  border: 1px solid rgba(147, 197, 253, 0.3);
}

.stButton > button:hover,
button.stButton:hover {
  border-color: rgba(147, 197, 253, 0.6);
  background: linear-gradient(135deg, #3b82f6, #0ea5e9);
}

.btn-reset {
  background: linear-gradient(135deg, var(--danger), #dc2626);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-reset:hover {
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
  background: linear-gradient(135deg, #dc2626, #ef4444);
}

/* === KPI CARDS === */
.kpi {
  background: var(--kpi-bg);
  border: 1px solid var(--kpi-border);
  border: 1px solid rgba(147, 197, 253, 0.15);
}

.kpi:hover {
  box-shadow: 0 16px 32px rgba(147, 197, 253, 0.25);
  border-color: rgba(147, 197, 253, 0.3);
}

.kpi .lbl {
  color: var(--text-secondary);
}

.kpi .val {
  color: var(--text-primary);
}

/* === SECTIONS === */
.section-h {
  color: var(--text-primary);
  border-bottom: 2px solid rgba(147, 197, 253, 0.2);
}

.section-h::after {
  background: var(--accent-gradient);
}

.section-sub {
  color: var(--text-secondary);
}

/* === DATAFRAMES === */
[data-testid="stDataFrame"] {
  border: 1px solid rgba(147, 197, 253, 0.1);
  background: var(--bg-card);
}

[data-testid="stDataFrame"] th {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom: 1px solid rgba(147, 197, 253, 0.1);
}

[data-testid="stDataFrame"] td {
  border-bottom: 1px solid rgba(147, 197, 253, 0.08);
}

[data-testid="stDataFrame"] tr:hover {
  background-color: rgba(30, 41, 59, 0.4);
}

/* === EXPANDERS === */
.streamlit-expanderHeader {
  background: var(--bg-secondary);
  border: 1px solid rgba(147, 197, 253, 0.1);
  color: var(--text-primary);
}

.streamlit-expanderHeader:hover {
  background: var(--bg-secondary);
}

.streamlit-expanderContent {
  background: var(--bg-primary);
  border: 1px solid rgba(147, 197, 253, 0.1);
  border-top: none;
}

/* === CHART CONTAINERS === */
div[data-testid="stPlotlyChart"] {
  background: var(--bg-primary);
  border: 1px solid rgba(147, 197, 253, 0.1);
}

div[data-testid="stPlotlyChart"] .main svg {
  background: var(--bg-primary) !important;
}

/* === SLIDERS & INPUTS === */
.stSlider > div > div {
  background: var(--accent-gradient);
}

.stSlider > div > div > div {
  background-color: var(--bg-card);
  border: 2px solid var(--accent-primary);
}

.stSlider > div > div > div:hover {
  box-shadow: 0 0 10px rgba(147, 197, 253, 0.6);
}

.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
  background: var(--bg-card);
  border: 1px solid rgba(147, 197, 253, 0.2);
  color: var(--text-primary);
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
  border-color: var(--accent-primary);
}

/* === TOOLTIPS & INFO BOXES === */
.stAlert {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(147, 197, 253, 0.1);
}

.stInfo {
  background: rgba(30, 41, 59, 0.7);
}

.stWarning {
  background: rgba(46, 38, 16, 0.7);
}

.stError {
  background: rgba(48, 20, 20, 0.7);
}

/* === CUSTOM RADIO BUTTONS === */
.stRadio > div > label {
  background: var(--bg-secondary);
  border: 1px solid rgba(147, 197, 253, 0.1);
  color: var(--text-primary);
}

.stRadio > div > label:hover {
  background: var(--bg-card);
}

*::-webkit-scrollbar-thumb {
  background: var(--accent-primary);
  border: 2px solid var(--bg-primary);
}
"""

# Combine base CSS with theme-specific CSS
LIGHT = f"<style>{BASE_CSS}{LIGHT_CSS}</style>"
DARK = f"<style>{BASE_CSS}{DARK_CSS}</style>"

def apply_theme() -> None:
    """
    Apply the current theme (light/dark) with zero FOUC (Flash of Unstyled Content).
    Uses a single, optimized CSS injection with no redundant re-renders.
    """
    try:
        css = LIGHT if st.session_state.get("theme", "light") == "light" else DARK
        st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        st.error("❌ Theme failed to load. Please refresh.")
        print(f"[THEME ERROR] {e}")