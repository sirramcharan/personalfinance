"""Personal Finance Tracker - Main Entry Point."""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.data_manager import DataManager
from utils.formatters import format_inr, format_currency_plain
from utils.charts import THEME

# Page config
st.set_page_config(
    page_title="Personal Finance",
    page_icon=":money_with_wings:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for glassmorphism
GLASS_CSS = """
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f3a 50%, #0f1424 100%);
        background-attachment: fixed;
    }
    
    /* Glass cards */
    .glass-card {
        background: rgba(25, 30, 45, 0.65);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 16px;
    }
    
    /* KPI card */
    .kpi-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(123, 97, 255, 0.08) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 14px;
        padding: 18px 22px;
        text-align: center;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #e0e6ed !important;
        font-weight: 600;
    }
    
    .accent-text {
        color: #00d4ff;
        font-weight: 700;
        font-size: 1.2em;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 26, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        padding: 8px 20px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #00d4ff !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8892a6 !important;
    }
    
    /* Table styling */
    table {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.03);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(0,212,255,0.3);
        border-radius: 3px;
    }
</style>
"""

st.markdown(GLASS_CSS, unsafe_allow_html=True)


def render_kpi(value, label, prefix="Rs "):
    """Render a styled KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div style="font-size: 2em; color: #00d4ff; font-weight: 700;">
                {prefix}{value:,.0f}
            </div>
            <div style="color: #8892a6; font-size: 0.9em; margin-top: 4px;">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_session():
    """Initialize session state with data manager."""
    if "dm" not in st.session_state:
        st.session_state.dm = DataManager()
    if "page" not in st.session_state:
        st.session_state.page = "dashboard"


def render_sidebar():
    """Render sidebar navigation."""
    st.sidebar.markdown(
        """
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 2.5em;">:moneybag:</div>
            <h2 style="color: #00d4ff; margin: 8px 0;">Finance Tracker</h2>
            <p style="color: #8892a6; font-size: 0.85em;">Your money, your control</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.sidebar.markdown("---")
    
    nav_options = {
        "dashboard": ":chart_with_upwards_trend: Dashboard",
        "income": ":moneybag: Income",
        "expenses": ":shopping_cart: Expenses",
        "savings": ":piggy_bank: Savings & Goals",
        "loan": ":bank: Loan Manager",
    }
    
    for key, label in nav_options.items():
        if st.sidebar.button(
            label,
            key=key,
            use_container_width=True,
            type="primary" if st.session_state.page == key else "secondary",
        ):
            st.session_state.page = key
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style="text-align: center; color: #8892a6; font-size: 0.8em; padding: 10px;">
            Built with Streamlit | Glassmorphism UI
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard():
    """Render the main dashboard page inline for single-file portability."""
    from utils.calculators import (
        calculate_emi,
        calculate_total_interest,
        calculate_sip_maturity,
        compute_health_score,
    )
    
    dm = st.session_state.dm
    data = dm.data
    
    st.title(":chart_with_upwards_trend: Dashboard")
    st.markdown(
        f"<p style='color: #8892a6;'>Welcome back, {data['profile']['name']}!</p>",
        unsafe_allow_html=True,
    )
    
    # Calculate key metrics
    income = data["income"]["salary_monthly"]
    fixed_exp = sum(data["expenses"]["fixed"].values())
    var_exp = sum(data["expenses"]["variable"].values())
    total_exp = fixed_exp + var_exp
    savings_rate = (income - total_exp) / income * 100 if income > 0 else 0
    potential_savings = income - total_exp
    
    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi(income, "Monthly Income")
    with c2:
        render_kpi(total_exp, "Monthly Expenses", "")
    with c3:
        render_kpi(potential_savings, "Potential Savings", "")
    with c4:
        render_kpi(savings_rate, "Savings Rate", "%")
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # Charts Row
    c1, c2 = st.columns(2)
    
    with c1:
        expense_labels = list(data["expenses"]["fixed"].keys()) + list(data["expenses"]["variable"].keys())
        expense_values = list(data["expenses"]["fixed"].values()) + list(data["expenses"]["variable"].values())
        from utils.charts import make_donut_chart
        fig = make_donut_chart(expense_labels, expense_values, "Expense Breakdown")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    with c2:
        from utils.charts import make_bar_chart
        fig = make_bar_chart(
            ["Income", "Expenses", "Savings"],
            [income, total_exp, potential_savings],
            "Monthly Overview",
            color="#00d4ff",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    
    # Financial Health
    health = compute_health_score(income, total_exp, data["savings"]["current_emergency"], data["loan"]["current_balance"])
    st.markdown("<br/>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 3em;">{"green" if health["score"] >= 70 else "orange" if health["score"] >= 40 else "red"}</div>
                <h3 style="color: #e0e6ed;">Financial Health</h3>
                <div style="font-size: 2em; color: {THEME['accent1']};">{health["score"]}/100</div>
                <p style="color: {THEME["subtext"]};">{health["label"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        loan = data["loan"]
        if loan["emi_start_date"]:
            emi = calculate_emi(loan["current_balance"], loan["interest_rate_annual"], loan["tenure_months"])
            st.markdown(
                f"""
                <div class="glass-card" style="text-align: center;">
                    <h3 style="color: #e0e6ed;">Monthly EMI</h3>
                    <div style="font-size: 2em; color: {THEME["accent4"]};">Rs {emi:,.0f}</div>
                    <p style="color: {THEME["subtext"]};">Starting {loan["emi_start_date"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="glass-card" style="text-align: center;">
                    <h3 style="color: #e0e6ed;">Loan Status</h3>
                    <div style="font-size: 2em; color: {THEME["accent3"]};">Moratorium</div>
                    <p style="color: {THEME["subtext"]};">No EMI yet</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with c3:
        sip = data["savings"]
        maturity = calculate_sip_maturity(sip["sip_monthly"], sip["sip_rate_annual"], 120)
        st.markdown(
            f"""
            <div class="glass-card" style="text-align: center;">
                <h3 style="color: #e0e6ed;">SIP Projection</h3>
                <div style="font-size: 2em; color: {THEME["accent3"]};">Rs {maturity["maturity_value"]:,.0f}</div>
                <p style="color: {THEME["subtext"]};">in 10 years</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <div class="glass-card">
            <h3 style="color: #e0e6ed;">:bulb: Smart Insights</h3>
            <ul style="color: #8892a6; line-height: 2;">
                <li>Your savings rate is <strong>{savings_rate:.1f}%</strong> - aim for 20-30% for strong financial health.</li>
                <li>Fixed expenses ({format_inr(fixed_exp, False)}) are {fixed_exp/total_exp*100:.1f}% of total spending.</li>
                <li>Emergency fund is at {data["savings"]["current_emergency"]:,} / {data["savings"]["emergency_fund_target"]:,} target.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder(title, emoji):
    """Render placeholder for pages under construction."""
    st.title(f"{emoji} {title}")
    st.markdown(
        """
        <div class="glass-card" style="text-align: center; padding: 40px;">
            <div style="font-size: 3em; margin-bottom: 16px;">:construction:</div>
            <h3 style="color: #e0e6ed;">Coming Soon</h3>
            <p style="color: #8892a6;">This page is under construction. Check back soon!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    init_session()
    render_sidebar()
    
    page = st.session_state.page
    
    if page == "dashboard":
        render_dashboard()
    elif page == "income":
        render_placeholder("Income", ":moneybag:")
    elif page == "expenses":
        render_placeholder("Expenses", ":shopping_cart:")
    elif page == "savings":
        render_placeholder("Savings & Goals", ":piggy_bank:")
    elif page == "loan":
        render_placeholder("Loan Manager", ":bank:")


if __name__ == "__main__":
    main()
