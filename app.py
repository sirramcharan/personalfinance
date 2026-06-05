"""Personal Finance Tracker - Single file App (all pages rendered internally)."""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_manager import DataManager

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg,#050510 0%,#0a0e24 50%,#050510 100%); background-attachment:fixed; }
[data-testid="stSidebar"] { background: rgba(8,10,20,0.97); border-right:1px solid rgba(0,212,255,0.08); }
.kpi { background:rgba(20,25,45,0.55); border:1px solid rgba(0,212,255,0.12); border-radius:14px; padding:18px 20px; }
.glass { background:rgba(20,25,45,0.55); border:1px solid rgba(0,212,255,0.12); border-radius:14px; padding:18px 22px; margin-bottom:8px; }
.accent1 { color:#00d4ff !important; }
.accent2 { color:#00ff9d !important; }
.accent3 { color:#ffd93d !important; }
.del-btn > button { background: linear-gradient(135deg,#ff4757,#ff6b6b) !important; border:none !important; border-radius:6px !important; color:white !important; font-weight:600 !important; padding: 2px 10px !important; font-size:0.85em !important; }
.stButton>button { background:linear-gradient(135deg,#00d4ff 0%,#7b61ff 100%) !important; border:none !important; border-radius:8px !important; color:white !important; font-weight:600 !important; }
.stButton>button:hover { opacity:0.85 !important; }
[data-testid="stMetricValue"] { color:#00d4ff !important; }
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
background:rgba(15,20,35,0.8) !important; border:1px solid rgba(255,255,255,0.1) !important;
color:#e0e6ed !important; border-radius:6px !important; }
.save-banner {
    background: linear-gradient(135deg, rgba(0,255,157,0.18), rgba(0,212,255,0.12));
    border: 2px solid #00ff9d;
    border-radius: 12px;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    animation: fadeInDown 0.4s ease;
}
.save-banner .save-icon { font-size: 1.5em; }
.save-banner .save-text { color: #00ff9d; font-weight: 700; font-size: 1em; }
.save-banner .save-sub  { color: #9aa7b7; font-size: 0.82em; margin-top: 2px; }
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.profile-badge { background: linear-gradient(135deg, rgba(0,212,255,0.2), rgba(123,97,255,0.2)); border:1px solid rgba(0,212,255,0.3); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "save_toast" not in st.session_state:
    st.session_state.save_toast = None  # stores a message string when a save just happened

# Initialize DataManager
if "dm" not in st.session_state:
    st.session_state.dm = DataManager()

dm = st.session_state.dm
data = dm.data
profile_name = dm.active_profile_name

# ── Helpers ───────────────────────────────────────────────────────────
def fmt(v): return f"{v:,.0f}"

def show_save_banner(message="Changes saved successfully!", sub="Your data has been updated."):
    """Render a green animated save confirmation banner."""
    st.markdown(f"""
    <div class='save-banner'>
        <span class='save-icon'>✅</span>
        <div>
            <div class='save-text'>🟢 {message}</div>
            <div class='save-sub'>{sub}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def plotly_dark():
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e6ed", margin=dict(l=10,r=10,t=30,b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"))

# ── Show persistent save banner at top of page if triggered ────────────────
if st.session_state.save_toast:
    show_save_banner(st.session_state.save_toast[0], st.session_state.save_toast[1])
    st.session_state.save_toast = None  # clear after one render

# ── HOME ──────────────────────────────────────────────────────────────
def page_home():
    st.markdown("""
<div style='text-align:center;padding:30px 0 10px;'>
<div style='font-size:3em;'>💰</div>
<h1 style='background:linear-gradient(90deg,#00d4ff,#00ff9d);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>Personal Finance Tracker</h1>
<p style='color:#9aa7b7;font-size:1.1em;'>AI-Powered Finance Assistant for Smart Money Management</p>
</div>""", unsafe_allow_html=True)
    with st.expander("📌 Quick Start Guide", expanded=False):
        st.write("1. **Dashboard** - See your financial snapshot at a glance\n2. **Income** - Track all sources of income\n3. **Expenses** - Monitor fixed and variable expenses\n4. **Savings** - Build emergency fund & track SIPs\n5. **Loan** - Manage your education loan\n6. **Profile & Defaults** - Configure your profile & categories")

# ── DASHBOARD ─────────────────────────────────────────────────────────
def page_dashboard():
    p = dm.get_profile()
    inc = dm.get_income()
    exp = dm.get_expenses()
    ln = dm.get_loan()
    sav = dm.get_savings()
    nw = dm.get_net_worth()

    total_fixed = sum(exp["fixed"].values())
    total_variable = sum(exp["variable"].values())
    total_expenses = total_fixed + total_variable
    monthly_savings = inc["salary_monthly"] - total_expenses
    savings_rate = (monthly_savings / inc["salary_monthly"] * 100) if inc["salary_monthly"] else 0

    st.markdown(f"""<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
<span class='profile-badge'>👤 Viewing: <span class='accent1'>{profile_name}</span>'s data</span></div>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='color:#e0e6ed;'>📊 Financial Dashboard</h3><hr style='border-color:rgba(0,212,255,0.2);'>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='kpi'><div style='color:#9aa7b7;font-size:0.85em;'>MONTHLY INCOME</div><div style='font-size:1.8em;color:#00ff9d;'>Rs {fmt(inc['salary_monthly'])}</div><div style='color:#9aa7b7;font-size:0.75em;'>Salary</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='kpi'><div style='color:#9aa7b7;font-size:0.85em;'>MONTHLY EXPENSES</div><div style='font-size:1.8em;color:#ff6b6b;'>Rs {fmt(total_expenses)}</div><div style='color:#9aa7b7;font-size:0.75em;'>Fixed + Variable</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='kpi'><div style='color:#9aa7b7;font-size:0.85em;'>MONTHLY SAVINGS</div><div style='font-size:1.8em;color:#ffd93d;'>Rs {fmt(max(0, monthly_savings))}</div><div style='color:#9aa7b7;font-size:0.75em;'>Savings Rate: {savings_rate:.0f}%</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='kpi'><div style='color:#9aa7b7;font-size:0.85em;'>LOAN BALANCE</div><div style='font-size:1.8em;color:#ff6b6b;'>Rs {fmt(nw['liabilities'])}</div><div style='color:#9aa7b7;font-size:0.75em;'>{ln['status'].title()}</div></div>", unsafe_allow_html=True)

    st.markdown("""<br>""", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("""<h4 class='accent1'>Expense Breakdown</h4>""", unsafe_allow_html=True)
        fixed_df = pd.DataFrame(list(exp["fixed"].items()), columns=["Category","Amount"])
        fig_fixed = px.pie(fixed_df, values="Amount", names="Category", hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
        fig_fixed.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
        st.plotly_chart(fig_fixed, use_container_width=True, config={"displayModeBar":False})
    with c2:
        st.markdown("""<h4 class='accent1'>Variable Expenses</h4>""", unsafe_allow_html=True)
        var_df = pd.DataFrame(list(exp["variable"].items()), columns=["Category","Amount"])
        fig_var = px.bar(var_df, x="Category", y="Amount", color="Amount", color_continuous_scale=["#00d4ff","#7b61ff"])
        fig_var.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed", showlegend=False)
        st.plotly_chart(fig_var, use_container_width=True, config={"displayModeBar":False})

# ── INCOME ────────────────────────────────────────────────────────────
def page_income():
    inc = dm.get_income()
    p = dm.get_profile()

    st.markdown(f"""<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
<span class='profile-badge'>👤 Viewing: <span class='accent1'>{profile_name}</span>'s data</span></div>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='color:#e0e6ed;'>💵 Income Tracker</h3><hr style='border-color:rgba(0,212,255,0.2);'>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='glass'><div style='color:#9aa7b7;font-size:0.85em;'>MONTHLY SALARY</div><div style='font-size:2em;color:#00ff9d;'>Rs {fmt(inc['salary_monthly'])}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h4 class='accent1'>➕ Add Income Record</h4>", unsafe_allow_html=True)
    with st.form("add_income"):
        col1,col2,col3 = st.columns(3)
        with col1:
            source = st.text_input("Source", placeholder="e.g. Freelance, Bonus, Interest")
        with col2:
            amount = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
        with col3:
            date = st.date_input("Date", datetime.now())
        col4,_ = st.columns([1,3])
        with col4:
            submitted = st.form_submit_button("➕ Add Income", use_container_width=True)
        if submitted:
            if source.strip() and amount > 0:
                record = {"source": source.strip(), "amount": float(amount), "date": date.strftime("%Y-%m-%d")}
                dm.add_income_record(record)
                st.session_state.save_toast = ("Income record added!", f"Rs {fmt(amount)} from {source.strip()} saved.")
                st.rerun()
            else:
                st.error("Please fill in all fields.")

    records = dm.get_income_records()
    if records:
        st.markdown("---")
        st.markdown("<h4 class='accent1'>📋 Income History</h4>", unsafe_allow_html=True)
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ── EXPENSES ──────────────────────────────────────────────────────────
def page_expenses():
    exp = dm.get_expenses()
    p = dm.get_profile()

    st.markdown(f"""<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
<span class='profile-badge'>👤 Viewing: <span class='accent1'>{profile_name}</span>'s data</span></div>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='color:#e0e6ed;'>💸 Expense Tracker</h3><hr style='border-color:rgba(0,212,255,0.2);'>""", unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        st.markdown("<h4 class='accent2'>Fixed Expenses</h4>", unsafe_allow_html=True)
        for cat, amt in exp["fixed"].items():
            st.markdown(f"<div class='glass'><span style='color:#e0e6ed;'>{cat.replace('_',' ').title()}</span><span style='float:right;color:#00ff9d;font-weight:600;'>Rs {fmt(amt)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='glass' style='border-color:rgba(0,255,157,0.3);'><span style='color:#00ff9d;font-weight:600;'>TOTAL FIXED</span><span style='float:right;color:#00ff9d;font-weight:600;'>Rs {fmt(sum(exp['fixed'].values()))}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h4 class='accent3'>Variable Expenses</h4>", unsafe_allow_html=True)
        for cat, amt in exp["variable"].items():
            st.markdown(f"<div class='glass'><span style='color:#e0e6ed;'>{cat.replace('_',' ').title()}</span><span style='float:right;color:#ffd93d;font-weight:600;'>Rs {fmt(amt)}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='glass' style='border-color:rgba(255,217,61,0.3);'><span style='color:#ffd93d;font-weight:600;'>TOTAL VARIABLE</span><span style='float:right;color:#ffd93d;font-weight:600;'>Rs {fmt(sum(exp['variable'].values()))}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h4 class='accent1'>➕ Add Expense Record</h4>", unsafe_allow_html=True)
    with st.form("add_expense"):
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            category = st.selectbox("Category", exp["fixed"].keys())
        with col2:
            exp_type = st.selectbox("Type", ["fixed", "variable"])
        with col3:
            amount = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
        with col4:
            date = st.date_input("Date", datetime.now())
        col5,_ = st.columns([1,3])
        with col5:
            submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)
        if submitted:
            if amount > 0:
                record = {"category": category, "amount": float(amount), "type": exp_type, "date": date.strftime("%Y-%m-%d")}
                dm.add_expense_record(record)
                st.session_state.save_toast = ("Expense record added!", f"Rs {fmt(amount)} — {category.replace('_',' ').title()} ({exp_type}) saved.")
                st.rerun()
            else:
                st.error("Please enter a valid amount.")

    records = dm.get_expense_records()
    if records:
        st.markdown("---")
        st.markdown("<h4 class='accent1'>📋 Expense History</h4>", unsafe_allow_html=True)
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ── SAVINGS ───────────────────────────────────────────────────────────
def page_savings():
    sav = dm.get_savings()
    p = dm.get_profile()

    st.markdown(f"""<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
<span class='profile-badge'>👤 Viewing: <span class='accent1'>{profile_name}</span>'s data</span></div>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='color:#e0e6ed;'>🏦 Savings & Investments</h3><hr style='border-color:rgba(0,212,255,0.2);'>""", unsafe_allow_html=True)

    progress = min(100, sav["current_emergency"] / sav["emergency_fund_target"] * 100)
    st.markdown(f"""<div class='glass'><div style='display:flex;justify-content:space-between;align-items:center;'>
<div><span style='color:#9aa7b7;font-size:0.85em;'>Emergency Fund</span><br><span style='font-size:1.5em;color:#00ff9d;'>Rs {fmt(sav['current_emergency'])} / Rs {fmt(sav['emergency_fund_target'])}</span></div>
<div style='text-align:right;'><span style='color:#00d4ff;font-weight:600;'>{progress:.0f}%</span></div></div>
<div style='background:rgba(0,0,0,0.3);border-radius:8px;margin-top:10px;'><div style='background:linear-gradient(90deg,#00ff9d,#00d4ff);height:8px;border-radius:8px;width:{progress}%;'></div></div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h4 class='accent1'>⚙️ Update Savings</h4>", unsafe_allow_html=True)
    with st.form("update_savings"):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            new_emergency = st.number_input("Current Emergency (Rs)", value=float(sav["current_emergency"]), step=5000.0)
        with c2:
            new_target = st.number_input("Target (Rs)", value=float(sav["emergency_fund_target"]), step=10000.0)
        with c3:
            new_sip = st.number_input("SIP Monthly (Rs)", value=float(sav["sip_monthly"]), step=1000.0)
        with c4:
            new_sip_rate = st.number_input("SIP Rate (% p.a.)", value=float(sav["sip_rate_annual"]), step=0.5)
        col5,_ = st.columns([1,3])
        with col5:
            saved = st.form_submit_button("💾 Save Savings", use_container_width=True)
        if saved:
            sav["current_emergency"] = float(new_emergency)
            sav["emergency_fund_target"] = float(new_target)
            sav["sip_monthly"] = float(new_sip)
            sav["sip_rate_annual"] = float(new_sip_rate)
            dm.save()
            st.session_state.save_toast = ("Savings updated!", "Emergency fund & SIP details saved successfully.")
            st.rerun()

    st.markdown("---")
    st.markdown("<h4 class='accent1'>📈 SIP Projection (10 years)</h4>", unsafe_allow_html=True)
    P = sav["sip_monthly"]
    r = sav["sip_rate_annual"] / 12 / 100
    n = 120
    if r > 0:
        fv = P * ((1+r)**n - 1) / r * (1+r)
    else:
        fv = P * n
    total_invested = P * n
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='glass' style='text-align:center;'><div style='color:#9aa7b7;font-size:0.85em;'>Total Invested</div><div style='font-size:1.8em;color:#00d4ff;'>Rs {fmt(total_invested)}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass' style='text-align:center;'><div style='color:#9aa7b7;font-size:0.85em;'>Wealth Gained</div><div style='font-size:1.8em;color:#00ff9d;'>Rs {fmt(fv - total_invested)}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='glass' style='text-align:center;'><div style='color:#9aa7b7;font-size:0.85em;'>Maturity Value</div><div style='font-size:1.8em;color:#ffd93d;'>Rs {fmt(fv)}</div></div>", unsafe_allow_html=True)

# ── LOAN ──────────────────────────────────────────────────────────────
def compute_emi(principal, rate, months):
    r = rate / 12 / 100
    if r == 0: return principal / months
    return principal * r * (1+r)**months / ((1+r)**months - 1)

def page_loan():
    ln = dm.get_loan()
    p = dm.get_profile()

    st.markdown(f"""<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
<span class='profile-badge'>👤 Viewing: <span class='accent1'>{profile_name}</span>'s data</span></div>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='color:#e0e6ed;'>📋 Loan Manager</h3><hr style='border-color:rgba(0,212,255,0.2);'>""", unsafe_allow_html=True)

    emi = compute_emi(ln["principal"], ln["interest_rate_annual"], ln["tenure_months"])
    total_payable = emi * ln["tenure_months"]
    total_interest = total_payable - ln["principal"]

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='glass'><div style='color:#9aa7b7;font-size:0.85em;'>PRINCIPAL</div><div style='font-size:1.5em;color:#00d4ff;'>Rs {fmt(ln['principal'])}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass'><div style='color:#9aa7b7;font-size:0.85em;'>INTEREST RATE</div><div style='font-size:1.5em;color:#ffd93d;'>{ln['interest_rate_annual']}% p.a.</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='glass'><div style='color:#9aa7b7;font-size:0.85em;'>TENURE</div><div style='font-size:1.5em;color:#00ff9d;'>{ln['tenure_months']} months</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='glass'><div style='color:#9aa7b7;font-size:0.85em;'>EMI</div><div style='font-size:1.5em;color:#ff6b6b;'>Rs {fmt(emi)}</div></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='glass'><div style='color:#9aa7b7;font-size:0.85em;'>Total Payable: Rs {fmt(total_payable)} | Total Interest: Rs {fmt(total_interest)} | Status: {ln['status'].title()}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<h4 class='accent1'>⚙️ Update Loan Details</h4>", unsafe_allow_html=True)
    with st.form("update_loan"):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            new_balance = st.number_input("Current Balance (Rs)", value=float(ln["current_balance"]), step=10000.0)
        with c2:
            new_rate = st.number_input("Interest Rate (%)", value=float(ln["interest_rate_annual"]), step=0.1)
        with c3:
            new_tenure = st.number_input("Tenure (months)", value=int(ln["tenure_months"]), step=1)
        with c4:
            new_status = st.selectbox("Status", ["moratorium", "active", "closed"], index=["moratorium", "active", "closed"].index(ln["status"]))
        col5,_ = st.columns([1,3])
        with col5:
            saved = st.form_submit_button("💾 Save Loan", use_container_width=True)
        if saved:
            ln["current_balance"] = float(new_balance)
            ln["interest_rate_annual"] = float(new_rate)
            ln["tenure_months"] = int(new_tenure)
            ln["status"] = new_status
            dm.save()
            st.session_state.save_toast = ("Loan details updated!", f"Balance, rate & tenure saved. Status: {new_status.title()}.")
            st.rerun()

# ── SETTINGS ──────────────────────────────────────────────────────────
def page_settings():
    global data, profile_name
    p = dm.get_profile()
    inc = dm.get_income()
    exp = dm.get_expenses()

    st.markdown(f"""<div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
<span class='profile-badge'>👤 Viewing: <span class='accent1'>{profile_name}</span>'s data</span></div>""", unsafe_allow_html=True)
    st.markdown("""<h3 style='color:#e0e6ed;'>⚙️ Profile & Defaults</h3><hr style='border-color:rgba(0,212,255,0.2);'>""", unsafe_allow_html=True)

    tabs = st.tabs(["👤 Profile & Income", "📦 Fixed Expenses", "🎲 Variable Expenses"])

    with tabs[0]:
        st.markdown("<h4 class='accent1'>Edit Profile</h4>", unsafe_allow_html=True)
        with st.form("profile_form"):
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                new_name = st.text_input("Name", value=p.get("name", profile_name))
            with c2:
                new_location = st.text_input("Location", value=p.get("location", ""))
            with c3:
                new_salary = st.number_input("Monthly Salary (Rs)", value=float(inc.get("salary_monthly", 0)), step=1000.0)
            with c4:
                new_rent = st.number_input("Rent (Rs)", value=float(p.get("rent", 0)), step=500.0)
            c5,c6,c7 = st.columns(3)
            with c5:
                new_food = st.number_input("Food (Rs)", value=float(p.get("food", 0)), step=500.0)
            with c6:
                new_transfer = st.number_input("Transfer to Parents (Rs)", value=float(p.get("transfer_to_parents", 0)), step=1000.0)
            with c7:
                _ = st.empty()
            _,col_btn,_ = st.columns([2,1,2])
            with col_btn:
                saved = st.form_submit_button("💾 Save Profile", use_container_width=True)
            if saved:
                p["name"] = new_name.strip()
                p["location"] = new_location.strip()
                p["rent"] = float(new_rent)
                p["food"] = float(new_food)
                p["transfer_to_parents"] = float(new_transfer)
                inc["salary_monthly"] = float(new_salary)
                dm.save()
                if new_name.strip() != profile_name:
                    profile_name = new_name.strip()
                st.session_state.save_toast = ("Profile saved!", f"Name, location & income defaults updated for {new_name.strip()}.")
                st.rerun()

    with tabs[1]:
        st.markdown("<h4 class='accent2'>Fixed Expenses</h4>", unsafe_allow_html=True)
        updated_fixed = {}
        for cat, amt in exp["fixed"].items():
            c1,c2 = st.columns([2,1])
            with c1:
                new_val = st.number_input(f"{cat.replace('_',' ').title()}", value=float(amt), step=100.0, key=f"fix_{cat}")
            updated_fixed[cat] = new_val
        with st.form("save_fixed_form"):
            st.markdown("<p style='color:#9aa7b7;font-size:0.85em;'>Click to save all fixed expense changes above.</p>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Save All Fixed Expenses", use_container_width=True):
                exp["fixed"].update(updated_fixed)
                dm.save()
                st.session_state.save_toast = ("Fixed expenses saved!", "All fixed expense amounts have been updated.")
                st.rerun()
        st.markdown("---")
        st.markdown("<h4 class='accent2'>🗑️ Remove Fixed Expense</h4>", unsafe_allow_html=True)
        with st.form("delete_fixed_form"):
            cat_to_delete = st.selectbox("Select category to remove", list(exp["fixed"].keys()), key="del_fixed_select")
            if st.form_submit_button("❌ Remove Selected", use_container_width=True):
                if cat_to_delete in exp["fixed"]:
                    del exp["fixed"][cat_to_delete]
                    dm.save()
                    st.session_state.save_toast = ("Category removed!", f"'{cat_to_delete}' has been deleted from fixed expenses.")
                    st.rerun()
        st.markdown("---")
        st.markdown("<h4 class='accent2'>➕ Add New Fixed Expense</h4>", unsafe_allow_html=True)
        with st.form("add_fixed"):
            c1,c2 = st.columns(2)
            with c1:
                new_cat_name = st.text_input("Category Name", placeholder="e.g. OTT, Gym, Coffee")
            with c2:
                new_cat_amt = st.number_input("Monthly Amount (Rs)", min_value=0.0, step=100.0)
            if st.form_submit_button("➕ Add Fixed Expense", use_container_width=True):
                if new_cat_name.strip():
                    key = new_cat_name.strip().lower().replace(" ","_")
                    exp["fixed"][key] = float(new_cat_amt)
                    dm.save()
                    st.session_state.save_toast = ("Fixed expense added!", f"'{new_cat_name}' — Rs {fmt(new_cat_amt)}/month added.")
                    st.rerun()
                else:
                    st.error("Please enter a category name.")

    with tabs[2]:
        st.markdown("<h4 class='accent3'>Variable Expenses</h4>", unsafe_allow_html=True)
        updated_var = {}
        for cat, amt in exp["variable"].items():
            c1,c2 = st.columns([2,1])
            with c1:
                new_val = st.number_input(f"{cat.replace('_',' ').title()}", value=float(amt), step=100.0, key=f"var_{cat}")
            updated_var[cat] = new_val
        with st.form("save_var_form"):
            st.markdown("<p style='color:#9aa7b7;font-size:0.85em;'>Click to save all variable expense changes above.</p>", unsafe_allow_html=True)
            if st.form_submit_button("💾 Save All Variable Expenses", use_container_width=True):
                exp["variable"].update(updated_var)
                dm.save()
                st.session_state.save_toast = ("Variable expenses saved!", "All variable expense amounts have been updated.")
                st.rerun()
        st.markdown("---")
        st.markdown("<h4 class='accent3'>🗑️ Remove Variable Expense</h4>", unsafe_allow_html=True)
        with st.form("delete_var_form"):
            var_to_delete = st.selectbox("Select category to remove", list(exp["variable"].keys()), key="del_var_select")
            if st.form_submit_button("❌ Remove Selected", use_container_width=True):
                if var_to_delete in exp["variable"]:
                    del exp["variable"][var_to_delete]
                    dm.save()
                    st.session_state.save_toast = ("Category removed!", f"'{var_to_delete}' has been deleted from variable expenses.")
                    st.rerun()
        st.markdown("---")
        st.markdown("<h4 class='accent3'>➕ Add New Variable Expense</h4>", unsafe_allow_html=True)
        with st.form("add_variable"):
            c1,c2 = st.columns(2)
            with c1:
                new_var_name = st.text_input("Category Name", placeholder="e.g. OTT, Cab, Coffee")
            with c2:
                new_var_amt = st.number_input("Monthly Amount (Rs)", min_value=0.0, step=100.0)
            if st.form_submit_button("➕ Add Variable Expense", use_container_width=True):
                if new_var_name.strip():
                    key = new_var_name.strip().lower().replace(" ","_")
                    exp["variable"][key] = float(new_var_amt)
                    dm.save()
                    st.session_state.save_toast = ("Variable expense added!", f"'{new_var_name}' — Rs {fmt(new_var_amt)}/month added.")
                    st.rerun()
                else:
                    st.error("Please enter a category name.")

# ── SIDEBAR ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style='text-align:center;padding:12px 0 6px 0;'>
<div style='font-size:2em;'>🤖</div>
<p style='color:#00d4ff;font-weight:600;margin:4px 0;font-size:1em;'>AI Finance Assistant</p>
</div>""", unsafe_allow_html=True)
    st.markdown("---")

    # Profile Switcher
    st.markdown("<p style='color:#00ff9d;font-weight:600;font-size:0.9em;'>👤 SELECT PROFILE</p>", unsafe_allow_html=True)
    profile_names = dm.profile_names
    selected_profile = st.selectbox("", profile_names, index=profile_names.index(dm.active_profile_name), key="profile_select", label_visibility="collapsed")
    if selected_profile != dm.active_profile_name:
        dm.switch_profile(selected_profile)
        st.session_state.dm = dm
        st.cache_data.clear()
        st.rerun()

    # Profile badge showing current profile
    st.markdown(f"""<div class='profile-badge' style='text-align:center;'>👤 Viewing: <span class='accent1'><b>{dm.active_profile_name}</b></span></div>""", unsafe_allow_html=True)

    pages = [
        ("📊 Dashboard", "Dashboard"),
        ("💵 Income", "Income"),
        ("💸 Expenses", "Expenses"),
        ("🏦 Savings", "Savings"),
        ("📋 Loan Manager", "Loan"),
        ("⚙️ Profile & Defaults", "Settings"),
    ]
    for label, key in pages:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("<div style='text-align:center;color:#7c8fa6;font-size:0.75em;'>Built with <b>Streamlit</b> · AI-Powered</div>", unsafe_allow_html=True)

# ── ROUTER ────────────────────────────────────────────────────────────
page = st.session_state.page
if   page == "Dashboard":  page_dashboard()
elif page == "Income":     page_income()
elif page == "Expenses":    page_expenses()
elif page == "Savings":     page_savings()
elif page == "Loan":        page_loan()
elif page == "Settings":    page_settings()
else:                       page_home()
