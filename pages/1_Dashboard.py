"""Dashboard - Overview of your personal finances."""

import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_manager import DataManager
from utils.formatters import format_inr, format_currency_plain
from utils.charts import THEME, make_donut_chart, make_bar_chart
from utils.calculators import compute_emi, compute_sip_maturity, compute_health_score

# ============= Page Config =============
st.set_page_config(page_title="Dashboard", page_icon=":chart_with_upwards_trend:", layout="wide")

# ============= Load Data =============
dm = DataManager()
data = dm.data
profile = data["profile"]
income = data["income"]["salary_monthly"]
fixed = data["expenses"]["fixed"]
variable = data["expenses"]["variable"]
loan = data["loan"]
savings = data["savings"]
net_worth = data["net_worth"]
goals = data["goals"]
history = data["history"]

# Calculated metrics
fixed_exp = sum(fixed.values())
var_exp = sum(variable.values())
total_exp = fixed_exp + var_exp
savings_pot = income - total_exp
savings_rate = (savings_pot / income * 100) if income > 0 else 0

# ============= Header =============
st.title(":chart_with_upwards_trend: Dashboard")
st.markdown(
    f"<p style='color:#7c8fa6; font-size:1.05em;'>Welcome back, <b class='accent1'>{profile['name']}</b>! Here's your financial snapshot.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# ============= Row 1: KPI Cards =============
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""<div class='kpi'>
            <div style='font-size:1.8em; font-weight:700; color:#00d4ff;'>Rs {income:,.0f}</div>
            <div style='color:#7c8fa6; font-size:0.8em; margin-top:4px;'>&#128176; Monthly Income</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""<div class='kpi'>
            <div style='font-size:1.8em; font-weight:700; color:#ff6b6b;'>Rs {total_exp:,.0f}</div>
            <div style='color:#7c8fa6; font-size:0.8em; margin-top:4px;'>&#128722; Monthly Expenses</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c3:
    sav_color = "#00ff9d" if savings_pot >= 0 else "#ff6b6b"
    st.markdown(
        f"""<div class='kpi'>
            <div style='font-size:1.8em; font-weight:700; color:{sav_color};'>Rs {savings_pot:,.0f}</div>
            <div style='color:#7c8fa6; font-size:0.8em; margin-top:4px;'>{'&#128178;' if savings_pot >= 0 else '&#9888;'} Savings Potential</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c4:
    sr_color = "#00ff9d" if savings_rate >= 20 else "#ffd93d" if savings_rate >= 10 else "#ff6b6b"
    st.markdown(
        f"""<div class='kpi'>
            <div style='font-size:1.8em; font-weight:700; color:{sr_color};'>{savings_rate:.1f}%</div>
            <div style='color:#7c8fa6; font-size:0.8em; margin-top:4px;'>&#128200; Savings Rate</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br/>", unsafe_allow_html=True)

# ============= Row 2: Charts =============
c1, c2 = st.columns(2)

with c1:
    st.markdown("<div class='glass'><h4 class='accent1'>&#128202; Expense Breakdown</h4></div>", unsafe_allow_html=True)
    all_labels = list(fixed.keys()) + list(variable.keys())
    all_values = list(fixed.values()) + list(variable.values())
    fig_donut = make_donut_chart(all_labels, all_values, "")
    fig_donut.update_layout(height=300, margin=dict(l=30, r=30, t=30, b=30))
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

with c2:
    st.markdown("<div class='glass'><h4 class='accent1'>&#128200; Monthly Overview</h4></div>", unsafe_allow_html=True)
    fig_bar = make_bar_chart(["Income", "Expenses", "Savings"], [income, total_exp, savings_pot], "", color="#00d4ff")
    fig_bar.update_layout(height=300, margin=dict(l=30, r=30, t=30, b=30))
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

st.markdown("---")

# ============= Row 3: Health, EMI, SIP =============
c1, c2, c3 = st.columns(3)

with c1:
    health = compute_health_score(data)
    h_color = "#00ff9d" if health["score"] >= 71 else "#ffd93d" if health["score"] >= 51 else "#ff6b6b" if health["score"] >= 31 else "#ff4757"
    st.markdown(
        f"""<div class='glass' style='text-align:center;'>
            <h4 class='accent1'>&#128170; Financial Health</h4>
            <div style='font-size:3.5em; font-weight:700; color:{h_color}; margin:12px 0;'>{health['score']}/100</div>
            <div style='color:{h_color}; font-weight:600; font-size:1.1em;'>{health['label']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

with c2:
    if loan["emi_start_date"]:
        emi_amt = compute_emi(loan["current_balance"], loan["interest_rate_annual"], loan["tenure_months"])
        st.markdown(
            f"""<div class='glass' style='text-align:center;'>
                <h4 class='accent1'>&#127970; Monthly EMI</h4>
                <div style='font-size:2.2em; font-weight:700; color:#ff6b6b; margin:12px 0;'>Rs {emi_amt:,.0f}</div>
                <div style='color:#7c8fa6; font-size:0.9em;'>Starting: {loan["emi_start_date"]}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""<div class='glass' style='text-align:center;'>
                <h4 class='accent1'>&#127970; Loan Status</h4>
                <div style='font-size:2em; font-weight:700; color:#ffd93d; margin:12px 0;'>Moratorium</div>
                <div style='color:#7c8fa6; font-size:0.9em;'>No EMI active yet</div>
            </div>""",
            unsafe_allow_html=True,
        )

with c3:
    sip_proj = compute_sip_maturity(savings["sip_monthly"], savings["sip_rate_annual"], 10)
    st.markdown(
        f"""<div class='glass' style='text-align:center;'>
            <h4 class='accent1'>&#128179; SIP (10-Yr)</h4>
            <div style='font-size:1.6em; font-weight:700; color:#00ff9d; margin:8px 0;'>Rs {sip_proj['maturity_value']:,.0f}</div>
            <div style='color:#7c8fa6; font-size:0.8em;'>Invested: Rs {sip_proj['total_invested']:,.0f} &bull; Returns: <span style='color:#00ff9d;'>Rs {sip_proj['estimated_returns']:,.0f}</span></div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============= Smart Insights =============
st.markdown("<h4 class='accent1'>&#128161; Smart Insights</h4>", unsafe_allow_html=True)
insights = [
    f"Savings rate is <b class='accent1'>{savings_rate:.1f}%</b> - target <b>20-30%</b> for strong financial health.",
    f"Fixed expenses (Rs {format_inr(fixed_exp, False)}) are <b>{(fixed_exp/total_exp*100):.1f}%</b> of total spending.",
    f"Emergency fund: <b class='accent3'>Rs {savings['current_emergency']:,}</b> / Rs {savings['emergency_fund_target']:,} target.",
    f"Net worth: <b class='accent1'>Rs {format_inr(net_worth['cash'] + net_worth['bank_balance'] + net_worth['investments'] - net_worth['liabilities'], False)}</b>",
]

for i, insight in enumerate(insights, 1):
    st.markdown(f"<div class='glass' style='padding:12px 20px; margin-bottom:8px; border-left:3px solid #00d4ff;'>"
                f"<span style='color:#7c8fa6;'>{i}.</span> {insight}</div>", unsafe_allow_html=True)
