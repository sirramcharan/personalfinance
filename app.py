"""Personal Finance Tracker - Main Entry Point (AI-powered)."""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.formatters import format_inr, format_currency_plain, get_period_label
from utils.charts import THEME, make_kpi_card
from utils.calculators import (
    compute_emi, compute_total_interest, compute_sip_maturity,
    compute_health_score, compute_inhand_from_ctc,
)

# ============= Page Config =============
st.set_page_config(
    page_title="Personal Finance",
    page_icon=":money_bag:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============= Custom CSS - Glassmorphism + Neon Bracelet Theme =============
CSS = f"""<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap");

    /* Global styles */
    * {{ font-family: "Inter", sans-serif; }}

    /* Main background */
    .stApp {{
        background: linear-gradient(135deg, #050510 0%, #0a0e24 50%, #050510 100%);
        background-attachment: fixed;
    }}

    /* Glass cards */
    .glass {{
        background: rgba(20, 25, 45, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 212, 255, 0.12);
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 4px 24px rgba(0, 212, 255, 0.08);
    }}

    /* KPI card */
    .kpi {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08) 0%, rgba(123, 97, 255, 0.06) 100%);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        text-align: center;
    }}

    /* Accent text */
    .accent1 {{ color: #00d4ff !important; }}
    .accent2 {{ color: #7b61ff !important; }}
    .accent3 {{ color: #00ff9d !important; }}
    .accent4 {{ color: #ff6b6b !important; }}
    .accent5 {{ color: #ffd93d !important; }}

    /* Headers */
    h1, h2, h3 {{ color: #e0e6ed !important; font-weight: 600; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: rgba(8, 10, 20, 0.96);
        border-right: 1px solid rgba(0, 212, 255, 0.08);
    }}

    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
        border: none;
        border-radius: 8px;
        color: white; font-weight: 600;
        padding: 10px 20px;
    }}

    /* Metrics */
    [data-testid="stMetricValue"] {{ color: #00d4ff !important; }}
    [data-testid="stMetricLabel"] {{ color: #7c8fa6 !important; }}

    /* Inputs */
    div.stNumberInput input, div.stTextInput input {{
        background: rgba(15, 20, 35, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px;
        color: #e0e6ed !important;
    }}

    /* Tables */
    table {{ border-radius: 10px; overflow: hidden; }}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

# ============= App Layout =============
# App title at top
st.markdown(f"""
    <div style="text-align:center; padding: 16px 0;">
        <div style="font-size:2.5em;">&#128176;</div>
        <h1 style="margin: 4px 0; background: linear-gradient(90deg, #00d4ff, #00ff9d); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Personal Finance Tracker</h1>
        <p style="color:#7c8fa6; margin-top:4px;">Your money, your control</p>
    </div>
""", unsafe_allow_html=True)

# ============= Initialize session state =============
if "dm" not in st.session_state:
    st.session_state.dm = DataManager()

if "current_page" not in st.session_state:
    st.session_state.current_page = "1_Dashboard"

# ============= Sidebar Navigation =============
with st.sidebar:
    st.markdown(f"""
        <div style="text-align:center; padding: 12px 0;">
            <div style="font-size:2em;">&#129302;</div>
            <p style="color:#00d4ff; font-weight:600; margin:4px 0;">AI Finance Assistant</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    nav = {
        "1_Dashboard": "&#128200; Dashboard",
        "2_Income": "&#128176; Income",
        "3_Expenses": "&#128722; Expenses",
        "4_Savings": "&#128022; Savings",
        "5_Loan": "&#127970; Loan Manager",
    }

    for page, label in nav.items():
        is_active = st.session_state.current_page == page
        btn_type = "primary" if is_active else "secondary"
        if st.sidebar.button(label, key=page, use_container_width=True, type=btn_type):
            st.session_state.current_page = page

    st.markdown("---")
    st.markdown(f"""
        <div style="text-align:center; color:#7c8fa6; font-size:0.78em; padding:8px;">
            Built with <b>Streamlit</b> &bull; AI-Powered
        </div>
    """, unsafe_allow_html=True)

# ============= Main Content Area =============
# Each page lives in the pages/ folder
# Streamlit auto-routes based on file names in pages/
