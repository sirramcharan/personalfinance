import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import load_data, save_data, load_config
from utils.calculators import calculate_sip_maturity, calculate_fd_maturity, calculate_em
i
from utils.formatters import format_currency, format_percentage
from datetime import datetime

st.set_page_config(page_title="Savings & Investments", page_icon="💎")

data = load_data()
config = load_config()

if "savings_records" not in data:
    data["savings_records"] = []
if "savings_goals" not in data:
    data["savings_goals"] = []
if "config" not in data:
    data["config"] = {}

st.markdown("""
<style>
    .big-metric { font-size: 1.8rem; font-weight: 700; color: #4ECDC4; }
    .accent1 { color: #00FFA3; }
</style>
""", unsafe_allow_html=True)

st.title("💎 Savings & Investments")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Goals", "Calculators", "Records"])

# Calculate savings stats
def get_savings_stats(records, goals):
    total_saved = sum(r.get("amount", 0) for r in records)
    total_target = sum(g.get("target", 0) for g in goals)
    achieved = sum(g.get("target", 0) for g in goals if g.get("achieved", False))
    return total_saved, total_target, achieved, len(goals)

total_saved, total_target, achieved, goal_count = get_savings_stats(data["savings_records"], data["savings_goals"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">💵 Total Saved</h4>
            <div class="big-metric">Rs {format_currency(total_saved)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">🎯 Total Target</h4>
            <div class="big-metric">Rs {format_currency(total_target)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        progress = (achieved / (total_target + 1)) * 100 if total_target else 0
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">🏆 Goals Achieved</h4>
            <div class="big-metric">{goal_count - len([g for g in data["savings_goals"] if not g.get("achieved")])} / {goal_count}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Goal Progress Chart
    if data["savings_goals"]:
        df_goals = pd.DataFrame(data["savings_goals"])
        if "current" in df_goals.columns:
            df_goals_display = df_goals[["name", "current", "target"]].copy()
            fig = px.bar(df_goals_display, x="name", y=["current", "target"], barmode="group",
                         color_discrete_sequence=["#4ECDC4", "#FFD93D"],
                         labels={"name": "Goal", "value": "Amount (Rs)"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font_color="white",
                             xaxis=dict(showgrid=False, color="white"),
                             yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="white"),
                             legend=dict(bgcolor="rgba(0,0,0,0)"),
                             margin=dict(l=0, r=0, t=30, b=60), showlegend=True)
            st.plotly_chart(fig, use_container_width=True, key="goals_bar")
        else:
            st.info("Goals don't have 'current' amounts yet. Update your goals to see progress.")
    else:
        st.info("No savings goals set. Create one in the 'Goals' tab.")

with tab2:
    # Add Goal
    with st.form("add_goal"):
        st.subheader("Create New Savings Goal")
        c1, c2 = st.columns(2)
        with c1:
            goal_name = st.text_input("Goal Name")
            target = st.number_input("Target Amount (Rs)", min_value=1000.0, step=5000.0)
        with c2:
            deadline = st.date_input("Target Date", value=datetime.now().date())
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        submitted = st.form_submit_button("➕ Create Goal", use_container_width=True)
        if submitted:
            if goal_name and target > 0:
                data["savings_goals"].append({
                    "name": goal_name,
                    "target": float(target),
                    "current": 0.0,
                    "deadline": str(deadline),
                    "priority": priority,
                    "achieved": False
                })
                save_data(data)
                st.success(f"Goal '{goal_name}' created with target Rs {format_currency(target)}!")
                st.rerun()
            else:
                st.error("Please enter a goal name and valid target amount.")

    st.markdown("---")

    # Existing Goals
    if data["savings_goals"]:
        st.subheader("Your Savings Goals")
        for i, goal in enumerate(data["savings_goals"]):
            with st.expander(f"{'✅' if goal.get('achieved') else '⏳'} {goal['name']} - Rs {format_currency(goal.get('current', 0))} / Rs {format_currency(goal['target'])}"):
                c1, c2 = st.columns(2)
                with c1:
                    new_amount = st.number_input(f"Update current amount (Rs)", key=f"upd_{i}", value=float(goal.get("current", 0)), step=500.0)
                    if st.button("Update Amount", key=f"btn_upd_{i}"):
                        data["savings_goals"][i]["current"] = new_amount
                        if new_amount >= goal["target"]:
                            data["savings_goals"][i]["achieved"] = True
                        save_data(data)
                        st.success("Updated!")
                        st.rerun()
                with c2:
                    if st.button("Delete Goal", key=f"btn_del_{i}"):
                        data["savings_goals"].pop(i)
                        save_data(data)
                        st.success("Goal deleted!")
                        st.rerun()
    else:
        st.info("No goals created yet.")

with tab3:
    st.subheader("Financial Calculators")
    calc_tab1, calc_tab2, calc_tab3 = st.tabs(["SIP Calculator", "FD Calculator", "EMI Calculator"])
    with calc_tab1:
        st.markdown("### 📈 SIP (Systematic Investment Plan) Calculator")
        c1, c2 = st.columns(2)
        with c1:
            sip_p = st.number_input("Monthly Investment (Rs)", min_value=500.0, value=5000.0, step=500.0)
            sip_r = st.number_input("Expected Annual Return (%)", min_value=1.0, value=12.0, step=0.5)
        with c2:
            sip_n = st.number_input("Investment Period (Years)", min_value=1, value=10, step=1)
        if st.button("Calculate SIP Returns", key="calc_sip"):
            maturity, invested, gains = calculate_sip_maturity(sip_p, sip_r, sip_n)
            st.markdown(f"""
            <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <h4 class="accent1">Maturity Value</h4>
                <div class="big-metric">Rs {format_currency(maturity)}</div>
                <p>Invested: Rs {format_currency(invested)} | Gains: Rs {format_currency(gains)}</p>
            </div>
            """, unsafe_allow_html=True)
    with calc_tab2:
        st.markdown("### 🏦 Fixed Deposit Calculator")
        c1, c2 = st.columns(2)
        with c1:
            fd_p = st.number_input("Principal Amount (Rs)", min_value=1000.0, value=100000.0, step=5000.0)
            fd_r = st.number_input("Annual Interest Rate (%)", min_value=1.0, value=7.0, step=0.25)
        with c2:
            fd_n = st.number_input("Tenure (Years)", min_value=1, value=5, step=1)
            quarterly = st.checkbox("Quarterly Compounding", value=True)
        if st.button("Calculate FD Returns", key="calc_fd"):
            maturity, interest = calculate_fd_maturity(fd_p, fd_r, fd_n, quarterly)
            st.markdown(f"""
            <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <h4 class="accent1">Maturity Value</h4>
                <div class="big-metric">Rs {format_currency(maturity)}</div>
                <p>Principal: Rs {format_currency(fd_p)} | Interest: Rs {format_currency(interest)}</p>
            </div>
            """, unsafe_allow_html=True)
    with calc_tab3:
        st.markdown("### 🏠 EMI Calculator")
        c1, c2 = st.columns(2)
        with c1:
            loan_amt = st.number_input("Loan Amount (Rs)", min_value=10000.0, value=500000.0, step=10000.0)
            loan_r = st.number_input("Annual Interest Rate (%)", min_value=0.5, value=8.5, step=0.25)
        with c2:
            loan_n = st.number_input("Tenure (Years)", min_value=1, value=15, step=1)
        if st.button("Calculate EMI", key="calc_emi"):
            emi, total, interest = calculate_emi(loan_amt, loan_r, loan_n)
            st.markdown(f"""
            <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <h4 class="accent1">Monthly EMI</h4>
                <div class="big-metric">Rs {format_currency(emi)}</div>
                <p>Total Payment: Rs {format_currency(total)} | Interest: Rs {format_currency(interest)}</p>
            </div>
            """, unsafe_allow_html=True)

with tab4:
    # Add Savings Record
    with st.form("add_savings"):
        st.subheader("Record a Savings Deposit")
        c1, c2 = st.columns(2)
        with c1:
            savings_type = st.selectbox("Savings Type", ["Bank Savings", "Fixed Deposit", "SIP", "Stocks", "Mutual Fund", "Gold", "Other"])
            amount = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
        with c2:
            date = st.date_input("Date", value=datetime.now().date())
            notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("➕ Add Savings Record", use_container_width=True)
        if submitted:
            if amount > 0:
                data["savings_records"].append({
                    "type": savings_type,
                    "amount": float(amount),
                    "date": str(date),
                    "notes": notes
                })
                save_data(data)
                st.success(f"Recorded Rs {format_currency(amount)} in {savings_type}!")
                st.rerun()
            else:
                st.error("Please enter a valid amount.")

    st.markdown("---")
    if data["savings_records"]:
        st.subheader("Savings History")
        df_sav = pd.DataFrame(data["savings_records"])
        df_disp = df_sav[["date", "type", "amount", "notes"]].copy()
        df_disp.columns = ["Date", "Type", "Amount (Rs)", "Notes"]
        st.dataframe(df_disp, use_container_width=True)
        csv = df_sav.to_csv(index=False)
        st.download_button("📥 Download as CSV", csv, "savings_records.csv", "text/csv")
    else:
        st.info("No savings records found.")
