"""Personal Finance Tracker - Main Entry Point."""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager

# ============= Page Config =============
st.set_page_config(
    page_title="Personal Finance",
    page_icon=":money_bag:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============= Custom CSS =============
CSS = """<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap");
    * { font-family: "Inter", sans-serif; }
    .stApp {
        background: linear-gradient(135deg, #050510 0%, #0a0e24 50%, #050510 100%);
        background-attachment: fixed;
    }
    .glass {
        background: rgba(20, 25, 45, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 212, 255, 0.12);
        border-radius: 14px;
        padding: 20px 24px;
        box-shadow: 0 4px 24px rgba(0, 212, 255, 0.08);
    }
    h1, h2, h3 { color: #e0e6ed !important; font-weight: 600; }
    [data-testid="stSidebar"] {
        background: rgba(8, 10, 20, 0.96);
        border-right: 1px solid rgba(0, 212, 255, 0.08);
    }
    .stButton>button {
        background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
        border: none;
        border-radius: 8px;
        color: white; font-weight: 600;
        padding: 10px 20px;
    }
    [data-testid="stMetricValue"] { color: #00d4ff !important; }
    [data-testid="stMetricLabel"] { color: #7c8fa6 !important; }
    div.stNumberInput input, div.stTextInput input {
        background: rgba(15, 20, 35, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px;
        color: #e0e6ed !important;
    }
    table { border-radius: 10px; overflow: hidden; }
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

# ============= Initialize session state =============
if "dm" not in st.session_state:
    st.session_state.dm = DataManager()

# ============= Sidebar Navigation =============
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; padding: 12px 0;">
            <div style="font-size:2em;">&#129302;</div>
            <p style="color:#00d4ff; font-weight:600; margin:4px 0;">AI Finance Assistant</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.sidebar.button("&#128200; Dashboard", key="nav_dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

    if st.sidebar.button("&#128176; Income", key="nav_income", use_container_width=True):
        st.switch_page("pages/2_Income.py")

    if st.sidebar.button("&#128722; Expenses", key="nav_expenses", use_container_width=True):
        st.switch_page("pages/3_Expenses.py")

    if st.sidebar.button("&#128022; Savings", key="nav_savings", use_container_width=True):
        st.switch_page("pages/4_Savings.py")

    if st.sidebar.button("&#127970; Loan Manager", key="nav_loan", use_container_width=True):
        st.switch_page("pages/5_Loan.py")

    st.markdown("---")
    st.markdown("""
        <div style="text-align:center; color:#7c8fa6; font-size:0.78em; padding:8px;">
            Built with <b>Streamlit</b> &bull; AI-Powered
        </div>
    """, unsafe_allow_html=True)

# ============= Home Page Content =============
st.markdown("""
    <div style="text-align:center; padding: 16px 0;">
        <div style="font-size:2.5em;">&#128176;</div>
        <h1 style="margin: 4px 0; background: linear-gradient(90deg, #00d4ff, #00ff9d);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Personal Finance Tracker
        </h1>
        <p style="color:#7c8fa6; margin-top:4px;">Your money, your control</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick nav cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("&#128200;\n\nDashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")
with col2:
    if st.button("&#128176;\n\nIncome", use_container_width=True):
        st.switch_page("pages/2_Income.py")
with col3:
    if st.button("&#128722;\n\nExpenses", use_container_width=True):
        st.switch_page("pages/3_Expenses.py")
with col4:
    if st.button("&#128022;\n\nSavings", use_container_width=True):
        st.switch_page("pages/4_Savings.py")
with col5:
    if st.button("&#127970;\n\nLoan Manager", use_container_width=True):
        st.switch_page("pages/5_Loan.py")
