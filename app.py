"""Personal Finance Tracker - Single File App (all pages rendered internally)."""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_manager import load_data, save_data

# ── Page config (MUST be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg,#050510 0%,#0a0e24 50%,#050510 100%); background-attachment:fixed; }
[data-testid="stSidebar"] { background: rgba(8,10,20,0.97) !important; border-right:1px solid rgba(0,212,255,0.08); }
.kpi { background:rgba(20,25,45,0.55); border:1px solid rgba(0,212,255,0.12); border-radius:14px; padding:18px 20px; }
.glass { background:rgba(20,25,45,0.55); border:1px solid rgba(0,212,255,0.12); border-radius:14px; padding:18px 22px; margin-bottom:8px; }
.accent1 { color:#00d4ff !important; }
.accent2 { color:#00ff9d !important; }
.accent3 { color:#ffd93d !important; }
.stButton>button {
    background:linear-gradient(135deg,#00d4ff 0%,#7b61ff 100%) !important;
    border:none !important; border-radius:8px !important; color:white !important; font-weight:600 !important;
}
.stButton>button:hover { opacity:0.85 !important; }
[data-testid="stMetricValue"] { color:#00d4ff !important; }
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {
    background:rgba(15,20,35,0.8) !important; border:1px solid rgba(255,255,255,0.1) !important;
    color:#e0e6ed !important; border-radius:6px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Home"

data = load_data()
for key in ["income_records", "expense_records"]:
    if key not in data:
        data[key] = []
        save_data(data)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center;padding:12px 0 6px 0;'>
            <div style='font-size:2em;'>🤖</div>
            <p style='color:#00d4ff;font-weight:600;margin:4px 0;font-size:1em;'>AI Finance Assistant</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    pages = [
        ("📊 Dashboard", "Dashboard"),
        ("💰 Income",    "Income"),
        ("💸 Expenses",  "Expenses"),
        ("🐖 Savings",   "Savings"),
        ("🏦 Loan Manager", "Loan"),
    ]
    for label, key in pages:
        active = st.session_state.page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.rerun()

    st.markdown("---")
    st.markdown("<div style='text-align:center;color:#7c8fa6;font-size:0.75em;'>Built with <b>Streamlit</b> · AI-Powered</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════════════════════════
def fmt(v): return f"{v:,.0f}"

def plotly_dark():
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e0e6ed", margin=dict(l=10,r=10,t=30,b=10),
                legend=dict(bgcolor="rgba(0,0,0,0)"))

# ═══════════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
        <div style='text-align:center;padding:30px 0 10px;'>
            <div style='font-size:3em;'>💰</div>
            <h1 style='background:linear-gradient(90deg,#00d4ff,#00ff9d);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin:6px 0;'>Personal Finance Tracker</h1>
            <p style='color:#7c8fa6;'>Your money, your control</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    nav_map = {"📊 Dashboard":"Dashboard","💰 Income":"Income","💸 Expenses":"Expenses","🐖 Savings":"Savings","🏦 Loan":"Loan"}
    for col,(lbl,pg) in zip([c1,c2,c3,c4,c5], nav_map.items()):
        with col:
            if st.button(lbl, use_container_width=True, key=f"home_{pg}"):
                st.session_state.page = pg
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    income_val  = data["income"]["salary_monthly"]
    fixed_exp   = sum(data["expenses"]["fixed"].values())
    var_exp     = sum(data["expenses"]["variable"].values())
    total_exp   = fixed_exp + var_exp
    savings_pot = income_val - total_exp
    sav_rate    = (savings_pot / income_val * 100) if income_val > 0 else 0
    profile     = data["profile"]

    st.title("📊 Dashboard")
    st.markdown(f"<p style='color:#7c8fa6;'>Welcome back, <b style='color:#00d4ff;'>{profile['name']}</b>! Here's your financial snapshot.</p>", unsafe_allow_html=True)
    st.markdown("---")

    c1,c2,c3,c4 = st.columns(4)
    kpis = [
        (f"Rs {fmt(income_val)}",  "#00d4ff", "💵 Monthly Income"),
        (f"Rs {fmt(total_exp)}",   "#ff6b6b", "🛒 Monthly Expenses"),
        (f"Rs {fmt(savings_pot)}", "#00ff9d" if savings_pot>=0 else "#ff6b6b", "💎 Savings Potential"),
        (f"{sav_rate:.1f}%",      "#00ff9d" if sav_rate>=20 else "#ffd93d" if sav_rate>=10 else "#ff6b6b", "📈 Savings Rate"),
    ]
    for col,(val,color,label) in zip([c1,c2,c3,c4], kpis):
        with col:
            st.markdown(f"<div class='kpi'><div style='font-size:1.8em;font-weight:700;color:{color};'>{val}</div><div style='color:#7c8fa6;font-size:0.8em;margin-top:4px;'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        labels = list(data["expenses"]["fixed"].keys()) + list(data["expenses"]["variable"].keys())
        values = list(data["expenses"]["fixed"].values()) + list(data["expenses"]["variable"].values())
        if any(v>0 for v in values):
            fig = px.pie(names=labels, values=values, hole=0.4, title="Expense Breakdown",
                         color_discrete_sequence=px.colors.sequential.Plasma_r)
            fig.update_layout(**plotly_dark())
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(x=["Income","Expenses","Savings"], y=[income_val,total_exp,max(savings_pot,0)],
                      color=["Income","Expenses","Savings"], title="Monthly Overview",
                      color_discrete_map={"Income":"#00d4ff","Expenses":"#ff6b6b","Savings":"#00ff9d"})
        fig2.update_layout(**plotly_dark())
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("<h4 class='accent1'>💡 Smart Insights</h4>", unsafe_allow_html=True)
    insights = [
        f"Savings rate is <b style='color:#00d4ff;'>{sav_rate:.1f}%</b> — target <b>20-30%</b> for strong financial health.",
        f"Fixed expenses (Rs {fmt(fixed_exp)}) are <b>{(fixed_exp/total_exp*100 if total_exp else 0):.1f}%</b> of total spending.",
        f"Emergency fund: <b style='color:#ffd93d;'>Rs {data['savings']['current_emergency']:,}</b> / Rs {data['savings']['emergency_fund_target']:,} target.",
    ]
    for i, insight in enumerate(insights, 1):
        st.markdown(f"<div class='glass' style='border-left:3px solid #00d4ff;'><span style='color:#7c8fa6;'>{i}.</span> {insight}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# INCOME
# ═══════════════════════════════════════════════════════════════════════════════
def page_income():
    st.title("💰 Income Tracker")
    records = data.get("income_records", [])
    tab1, tab2, tab3 = st.tabs(["Overview", "Add Income", "Transaction History"])

    now_month = datetime.now().month
    total_income, monthly_income, by_source = 0, 0, {}
    if records:
        df = pd.DataFrame(records)
        total_income = df["amount"].sum()
        monthly_income = df[df["date"].apply(lambda x: datetime.strptime(x,"%Y-%m-%d").month == now_month)]["amount"].sum()
        by_source = df.groupby("source")["amount"].sum().to_dict()

    with tab1:
        c1,c2,c3 = st.columns(3)
        metrics = [("💵 Total Income",f"Rs {fmt(total_income)}","#00ff9d"),
                   ("📅 This Month",f"Rs {fmt(monthly_income)}","#00d4ff"),
                   ("📊 Sources",str(len(by_source)),"#ffd93d")]
        for col,(label,val,color) in zip([c1,c2,c3],metrics):
            with col:
                st.markdown(f"<div class='kpi'><h4 class='accent1'>{label}</h4><div style='font-size:1.8em;font-weight:700;color:{color};'>{val}</div></div>", unsafe_allow_html=True)
        st.markdown("---")
        if by_source:
            c1,c2 = st.columns(2)
            with c1:
                df_src = pd.DataFrame(list(by_source.items()),columns=["Source","Amount"])
                fig = px.pie(df_src, values="Amount", names="Source", hole=0.4, title="Income by Source",
                             color_discrete_sequence=["#00ff9d","#00d4ff","#ffd93d","#7b61ff","#ff6b6b"])
                fig.update_layout(**plotly_dark())
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                df_t = pd.DataFrame(records)
                df_t["month"] = df_t["date"].apply(lambda x: x[:7])
                trend = df_t.groupby("month")["amount"].sum().reset_index()
                fig2 = px.bar(trend, x="month", y="amount", title="Monthly Trend", color_discrete_sequence=["#00ff9d"])
                fig2.update_layout(**plotly_dark())
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No income records yet. Add your first entry in the 'Add Income' tab.")

    with tab2:
        with st.form("add_income"):
            st.subheader("Add New Income Entry")
            c1,c2 = st.columns(2)
            with c1:
                source = st.selectbox("Source",["Salary","Freelance","Investments","Side Business","Bonus","Other"])
                amount = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
            with c2:
                date   = st.date_input("Date", value=datetime.now().date())
                desc   = st.text_input("Description (optional)")
            if st.form_submit_button("➕ Add Income", use_container_width=True):
                if amount > 0:
                    data["income_records"].append({"source":source,"amount":float(amount),"date":str(date),"description":desc})
                    save_data(data)
                    st.success(f"✅ Added Rs {fmt(amount)} from {source}!")
                    st.rerun()
                else:
                    st.error("Please enter a valid amount.")

    with tab3:
        if records:
            df_all = pd.DataFrame(records)
            st.dataframe(df_all[["date","source","amount","description"]], use_container_width=True)
            st.download_button("📥 Download CSV", df_all.to_csv(index=False), "income_records.csv", "text/csv")
        else:
            st.info("No income records found.")

# ═══════════════════════════════════════════════════════════════════════════════
# EXPENSES
# ═══════════════════════════════════════════════════════════════════════════════
def page_expenses():
    st.title("💸 Expenses Tracker")
    records = data.get("expense_records", [])
    tab1, tab2, tab3 = st.tabs(["Overview", "Add Expense", "Transaction History"])

    now_month = datetime.now().month
    total_exp, monthly_exp, by_cat, by_type = 0, 0, {}, {}
    if records:
        df = pd.DataFrame(records)
        total_exp   = df["amount"].sum()
        monthly_exp = df[df["date"].apply(lambda x: datetime.strptime(x,"%Y-%m-%d").month==now_month)]["amount"].sum()
        by_cat  = df.groupby("category")["amount"].sum().to_dict()
        by_type = df.groupby("type")["amount"].sum().to_dict()

    with tab1:
        c1,c2,c3 = st.columns(3)
        fixed_v = by_type.get("Fixed",0); var_v = by_type.get("Variable",0)
        for col,(label,val,color) in zip([c1,c2,c3],[
            ("💵 Total Expenses",f"Rs {fmt(total_exp)}","#ff6b6b"),
            ("📅 This Month",f"Rs {fmt(monthly_exp)}","#ffd93d"),
            ("🔒 Fixed / 📦 Variable",f"Rs {fmt(fixed_v)} / Rs {fmt(var_v)}","#7b61ff")
        ]):
            with col:
                st.markdown(f"<div class='kpi'><h4 class='accent1'>{label}</h4><div style='font-size:1.6em;font-weight:700;color:{color};'>{val}</div></div>", unsafe_allow_html=True)
        st.markdown("---")
        if by_cat:
            c1,c2 = st.columns(2)
            with c1:
                df_cat = pd.DataFrame(list(by_cat.items()),columns=["Category","Amount"])
                fig = px.pie(df_cat, values="Amount", names="Category", hole=0.4, title="Expense Breakdown",
                             color_discrete_sequence=["#ff6b6b","#ffd93d","#7b61ff","#4ECDC4","#00ff9d","#ff8fab"])
                fig.update_layout(**plotly_dark())
                fig.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                df_t = pd.DataFrame(records)
                df_t["month"] = df_t["date"].apply(lambda x: x[:7])
                trend = df_t.groupby("month")["amount"].sum().reset_index()
                fig2 = px.bar(trend, x="month", y="amount", title="Monthly Trend", color_discrete_sequence=["#ff6b6b"])
                fig2.update_layout(**plotly_dark())
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No expense records yet. Add your first entry in the 'Add Expense' tab.")

    with tab2:
        with st.form("add_expense"):
            st.subheader("Add New Expense")
            c1,c2 = st.columns(2)
            with c1:
                category = st.selectbox("Category",["Rent","Food","Transport","Utilities","Entertainment","Shopping","Healthcare","Education","EMI","Other"])
                exp_type = st.selectbox("Type",["Fixed","Variable"])
            with c2:
                amount = st.number_input("Amount (Rs)", min_value=0.0, step=50.0)
                date   = st.date_input("Date", value=datetime.now().date())
            desc = st.text_input("Description (optional)")
            if st.form_submit_button("➕ Add Expense", use_container_width=True):
                if amount > 0:
                    data["expense_records"].append({"category":category,"type":exp_type,"amount":float(amount),"date":str(date),"description":desc})
                    save_data(data)
                    st.success(f"✅ Added Rs {fmt(amount)} - {category} ({exp_type})!")
                    st.rerun()
                else:
                    st.error("Please enter a valid amount.")

    with tab3:
        if records:
            df_all = pd.DataFrame(records)
            st.dataframe(df_all[["date","category","type","amount","description"]], use_container_width=True)
            st.download_button("📥 Download CSV", df_all.to_csv(index=False), "expense_records.csv", "text/csv")
        else:
            st.info("No expense records found.")

# ═══════════════════════════════════════════════════════════════════════════════
# SAVINGS
# ═══════════════════════════════════════════════════════════════════════════════
def page_savings():
    st.title("🐖 Savings Manager")
    savings = data["savings"]
    income_val = data["income"]["salary_monthly"]
    total_exp  = sum(data["expenses"]["fixed"].values()) + sum(data["expenses"]["variable"].values())
    savings_pot = income_val - total_exp
    sav_rate = (savings_pot/income_val*100) if income_val > 0 else 0

    tab1, tab2 = st.tabs(["Overview & Analysis", "Update Savings"])

    with tab1:
        c1,c2,c3 = st.columns(3)
        ef_pct = min(savings["current_emergency"]/savings["emergency_fund_target"]*100, 100) if savings["emergency_fund_target"] else 0
        for col,(label,val,color) in zip([c1,c2,c3],[
            ("💎 Monthly Savings Potential",f"Rs {fmt(savings_pot)}","#00ff9d" if savings_pot>=0 else "#ff6b6b"),
            ("📈 Savings Rate",f"{sav_rate:.1f}%","#00ff9d" if sav_rate>=20 else "#ffd93d" if sav_rate>=10 else "#ff6b6b"),
            ("🆘 Emergency Fund",f"{ef_pct:.0f}% funded","#00d4ff")
        ]):
            with col:
                st.markdown(f"<div class='kpi'><h4 class='accent1'>{label}</h4><div style='font-size:1.8em;font-weight:700;color:{color};'>{val}</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<h4 class='accent1'>📊 50/30/20 Rule Analysis</h4>", unsafe_allow_html=True)
        needs_budget = income_val * 0.50
        wants_budget = income_val * 0.30
        savings_budget = income_val * 0.20
        fixed_exp = sum(data["expenses"]["fixed"].values())
        var_exp   = sum(data["expenses"]["variable"].values())
        rows = [
            {"Category":"Needs (50%)","Budget":needs_budget,"Actual":fixed_exp,"Status":"✅ Good" if fixed_exp<=needs_budget else "⚠️ Over"},
            {"Category":"Wants (30%)","Budget":wants_budget,"Actual":var_exp,  "Status":"✅ Good" if var_exp<=wants_budget else "⚠️ Over"},
            {"Category":"Savings (20%)","Budget":savings_budget,"Actual":savings_pot,"Status":"✅ Good" if savings_pot>=savings_budget else "⚠️ Below Target"},
        ]
        df_rule = pd.DataFrame(rows)
        st.dataframe(df_rule.style.format({"Budget":"Rs {:,.0f}","Actual":"Rs {:,.0f}"}), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 class='accent1'>📈 SIP Projection</h4>", unsafe_allow_html=True)
        sip_m = savings["sip_monthly"]; rate = savings["sip_rate_annual"]/12/100
        projections = []
        for yr in [1,3,5,10]:
            n = yr*12
            mat = sip_m * (((1+rate)**n - 1)/rate) * (1+rate) if rate > 0 else sip_m*n
            projections.append({"Years":yr,"Invested":sip_m*n,"Maturity Value":mat,"Returns":mat-sip_m*n})
        df_sip = pd.DataFrame(projections)
        fig = px.bar(df_sip, x="Years", y=["Invested","Returns"], barmode="stack", title=f"SIP Growth (Rs {fmt(sip_m)}/month @ {savings['sip_rate_annual']}%)",
                     color_discrete_map={"Invested":"#00d4ff","Returns":"#00ff9d"})
        fig.update_layout(**plotly_dark())
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.form("update_savings"):
            st.subheader("Update Savings Details")
            c1,c2 = st.columns(2)
            with c1:
                new_emergency = st.number_input("Current Emergency Fund (Rs)", min_value=0.0, value=float(savings["current_emergency"]), step=1000.0)
                new_ef_target = st.number_input("Emergency Fund Target (Rs)", min_value=0.0, value=float(savings["emergency_fund_target"]), step=5000.0)
            with c2:
                new_sip       = st.number_input("Monthly SIP Amount (Rs)", min_value=0.0, value=float(savings["sip_monthly"]), step=500.0)
                new_sip_rate  = st.number_input("Expected SIP Return (% p.a.)", min_value=0.0, max_value=30.0, value=float(savings["sip_rate_annual"]), step=0.5)
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                data["savings"]["current_emergency"]  = new_emergency
                data["savings"]["emergency_fund_target"] = new_ef_target
                data["savings"]["sip_monthly"]        = new_sip
                data["savings"]["sip_rate_annual"]    = new_sip_rate
                save_data(data)
                st.success("✅ Savings details updated!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# LOAN
# ═══════════════════════════════════════════════════════════════════════════════
def page_loan():
    st.title("🏦 Loan Manager")
    loan = data["loan"]

    def compute_emi(principal, annual_rate, months):
        if annual_rate == 0: return principal / months
        r = annual_rate / 12 / 100
        return principal * r * (1+r)**months / ((1+r)**months - 1)

    tab1, tab2 = st.tabs(["Loan Overview", "Update Loan Details"])

    with tab1:
        emi = compute_emi(loan["current_balance"], loan["interest_rate_annual"], loan["tenure_months"])
        total_payable = emi * loan["tenure_months"]
        total_interest = total_payable - loan["current_balance"]

        c1,c2,c3,c4 = st.columns(4)
        for col,(label,val,color) in zip([c1,c2,c3,c4],[
            ("🏷️ Loan Balance",f"Rs {fmt(loan['current_balance'])}","#ff6b6b"),
            ("📅 Monthly EMI",f"Rs {fmt(emi)}","#ffd93d"),
            ("💸 Total Payable",f"Rs {fmt(total_payable)}","#7b61ff"),
            ("📊 Total Interest",f"Rs {fmt(total_interest)}","#ff6b6b"),
        ]):
            with col:
                st.markdown(f"<div class='kpi'><h4 class='accent1'>{label}</h4><div style='font-size:1.5em;font-weight:700;color:{color};'>{val}</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("<h4 class='accent1'>📊 Amortization Preview (First 12 months)</h4>", unsafe_allow_html=True)
        rows, bal = [], loan["current_balance"]
        r = loan["interest_rate_annual"]/12/100
        for m in range(1, min(13, loan["tenure_months"]+1)):
            int_part  = bal * r
            prin_part = emi - int_part
            bal -= prin_part
            rows.append({"Month":m,"EMI":emi,"Principal":prin_part,"Interest":int_part,"Balance":max(bal,0)})
        df_amort = pd.DataFrame(rows)
        fig = px.bar(df_amort, x="Month", y=["Principal","Interest"], barmode="stack", title="EMI Split — Principal vs Interest",
                     color_discrete_map={"Principal":"#00d4ff","Interest":"#ff6b6b"})
        fig.update_layout(**plotly_dark())
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Amortization Table")
        st.dataframe(df_amort.style.format({"EMI":"Rs {:,.0f}","Principal":"Rs {:,.0f}","Interest":"Rs {:,.0f}","Balance":"Rs {:,.0f}"}), use_container_width=True)

    with tab2:
        with st.form("update_loan"):
            st.subheader("Update Loan Details")
            c1,c2 = st.columns(2)
            with c1:
                new_balance  = st.number_input("Current Balance (Rs)", min_value=0.0, value=float(loan["current_balance"]), step=10000.0)
                new_rate     = st.number_input("Interest Rate (% p.a.)", min_value=0.0, max_value=30.0, value=float(loan["interest_rate_annual"]), step=0.1)
            with c2:
                new_tenure   = st.number_input("Remaining Tenure (months)", min_value=1, max_value=360, value=int(loan["tenure_months"]), step=1)
                new_status   = st.selectbox("Loan Status",["moratorium","active","prepaid"], index=["moratorium","active","prepaid"].index(loan["status"]))
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                data["loan"]["current_balance"]    = new_balance
                data["loan"]["interest_rate_annual"] = new_rate
                data["loan"]["tenure_months"]      = new_tenure
                data["loan"]["status"]             = new_status
                save_data(data)
                st.success("✅ Loan details updated!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
page = st.session_state.page
if   page == "Dashboard": page_dashboard()
elif page == "Income":    page_income()
elif page == "Expenses":  page_expenses()
elif page == "Savings":   page_savings()
elif page == "Loan":      page_loan()
else:                     page_home()
