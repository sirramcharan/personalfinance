import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import load_data, save_data, load_config
from utils.calculators import calculate_emi, calculate_remaining_balance
from utils.formatters import format_currency, format_percentage
from datetime import datetime

st.set_page_config(page_title="Loan Manager", page_icon="🏠")

data = load_data()
config = load_config()

if "loans" not in data:
    data["loans"] = []

st.markdown("""
<style>
    .big-metric { font-size: 1.8rem; font-weight: 700; color: #6C63FF; }
    .accent1 { color: #00FFA3; }
</style>
""", unsafe_allow_html=True)

st.title("🏠 Loan Manager")

tab1, tab2, tab3 = st.tabs(["Overview", "Add Loan", "EMIs & Schedule"])

# Calculate loan stats
def get_loan_stats(loans):
    if not loans:
        return 0, 0, 0, 0
    total_principal = sum(l.get("principal", 0) for l in loans)
    total_outstanding = sum(l.get("outstanding", l.get("principal", 0)) for l in loans)
    total_paid = total_principal - total_outstanding
    total_emi = sum(l.get("emi", 0) for l in loans)
    return total_principal, total_outstanding, total_paid, total_emi

loan_principal, outstanding, paid, monthly_emi = get_loan_stats(data["loans"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">💵 Total Loan Principal</h4>
            <div class="big-metric">Rs {format_currency(loan_principal)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">📉 Outstanding</h4>
            <div class="big-metric">Rs {format_currency(outstanding)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">💳 Monthly EMI</h4>
            <div class="big-metric">Rs {format_currency(monthly_emi)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Loan breakdown chart
    if data["loans"]:
        df_loans = pd.DataFrame(data["loans"])
        if "principal" in df_loans.columns and "outstanding" in df_loans.columns:
            df_plot = df_loans[["name", "principal", "outstanding"]].copy()
            fig = px.bar(df_plot, x="name", y=["principal", "outstanding"], barmode="group",
                         color_discrete_sequence=["#6C63FF", "#FF6B6B"],
                         labels={"name": "Loan", "value": "Amount (Rs)"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font_color="white",
                             xaxis=dict(showgrid=False, color="white"),
                             yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="white"),
                             legend=dict(bgcolor="rgba(0,0,0,0)"),
                             margin=dict(l=0, r=0, t=30, b=60), showlegend=True)
            st.plotly_chart(fig, use_container_width=True, key="loans_bar")
        else:
            st.info("Loans don't have principal/outstanding data. Add loans to see breakdown.")
    else:
        st.info("No loans added yet. Add your first loan in the 'Add Loan' tab.")

    # Repayment progress
    if data["loans"]:
        st.markdown("---")
        st.subheader("🏆 Repayment Progress")
        for i, loan in enumerate(data["loans"]):
            principal = loan.get("principal", 0)
            outstanding_val = loan.get("outstanding", principal)
            progress = ((principal - outstanding_val) / (principal if principal else 1)) * 100
            st.markdown(f"**{loan['name']}** ({loan.get('type', 'Loan')})")
            st.progress(progress / 100)
            st.markdown(f"*Paid: Rs {format_currency(principal - outstanding_val)} / Rs {format_currency(principal)} ({progress:.1f}%)*")

with tab2:
    # Add Loan Form
    with st.form("add_loan"):
        st.subheader("Add New Loan")
        c1, c2 = st.columns(2)
        with c1:
            loan_name = st.text_input("Loan Name")
            loan_type = st.selectbox("Loan Type", ["Home Loan", "Car Loan", "Personal Loan", "Education Loan", "Business Loan", "Other"])
            principal = st.number_input("Principal Amount (Rs)", min_value=1000.0, step=10000.0)
        with c2:
            rate = st.number_input("Annual Interest Rate (%)", min_value=0.5, value=8.5, step=0.25)
            tenure = st.number_input("Tenure (Years)", min_value=1, value=15, step=1)
            start_date = st.date_input("Start Date", value=datetime.now().date())
        submitted = st.form_submit_button("➕ Add Loan", use_container_width=True)
        if submitted:
            if loan_name and principal > 0:
                emi, _, _ = calculate_emi(principal, rate, tenure)
                data["loans"].append({
                    "name": loan_name,
                    "type": loan_type,
                    "principal": float(principal),
                    "outstanding": float(principal),
                    "rate": float(rate),
                    "tenure_years": int(tenure),
                    "emi": float(emi),
                    "start_date": str(start_date),
                    "payments_made": 0
                })
                save_data(data)
                st.success(f"Loan '{loan_name}' added! Monthly EMI: Rs {format_currency(emi)}")
                st.rerun()
            else:
                st.error("Please enter a loan name and valid principal amount.")

    st.markdown("---")

    # EMI Calculator
    with st.form("calc_emi_loan"):
        st.subheader("🔢 EMI Calculator (Quick)")
        c1, c2 = st.columns(2)
        with c1:
            calc_loan_amt = st.number_input("Loan Amount (Rs)", min_value=0.0, step=10000.0, key="calc_loan")
            calc_rate = st.number_input("Interest Rate (%)", min_value=0.5, value=8.5, step=0.25, key="calc_rate")
        with c2:
            calc_tenure = st.number_input("Tenure (Years)", min_value=1, value=15, step=1, key="calc_tenure")
        submitted = st.form_submit_button("Calculate EMI", use_container_width=True, key="btn_calc_emi")
        if submitted:
            if calc_loan_amt > 0:
                emi, total, interest = calculate_emi(calc_loan_amt, calc_rate, calc_tenure)
                st.markdown(f"""
                <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                    <h4 class="accent1">Monthly EMI</h4>
                    <div class="big-metric">Rs {format_currency(emi)}</div>
                    <p>Total: Rs {format_currency(total)} | Interest: Rs {format_currency(interest)}</p>
                </div>
                """, unsafe_allow_html=True)

with tab3:
    # Payment History & Schedule
    st.subheader("📋 Loan Payment History")
    if data["loans"]:
        # Select loan to view
        loan_names = [l["name"] for l in data["loans"]]
        selected_loan = st.selectbox("Select Loan", loan_names)
        loan_idx = next(i for i, l in enumerate(data["loans"]) if l["name"] == selected_loan)
        loan = data["loans"][loan_idx]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
                <h4 class="accent1">EMIs Paid</h4>
                <div class="big-metric">{loan.get("payments_made", 0)} / {loan.get("tenure_years", 0) * 12}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
                <h4 class="accent1">Remaining Balance</h4>
                <div class="big-metric">Rs {format_currency(loan.get("outstanding", loan.get("principal", 0)))}</div>
            </div>
            """, unsafe_allow_html=True)

        # Record payment
        with st.form("record_payment"):
            st.subheader("Record EMI Payment")
            payment_amount = st.number_input("Payment Amount (Rs)", min_value=0.0, value=loan["emi"], step=1000.0)
            payment_date = st.date_input("Payment Date", value=datetime.now().date(), key="pay_date")
            submitted = st.form_submit_button("💰 Record Payment", use_container_width=True)
            if submitted:
                if payment_amount > 0:
                    remaining = loan["outstanding"] - payment_amount
                    data["loans"][loan_idx]["outstanding"] = max(0, remaining)
                    data["loans"][loan_idx]["payments_made"] = loan.get("payments_made", 0) + 1
                    save_data(data)
                    st.success(f"Payment of Rs {format_currency(payment_amount)} recorded! Outstanding: Rs {format_currency(remaining)}")
                    st.rerun()
                else:
                    st.error("Please enter a valid payment amount.")

        st.markdown("---")

        # EMI Schedule
        if st.checkbox("Show EMI Amortization Schedule", key="show_emi"):
            total_months = loan["tenure_years"] * 12
            monthly_rate = loan["rate"] / 12 / 100
            emi = loan["emi"]

            rows = []
            balance = loan["principal"]
            for month in range(1, min(total_months + 1, 121)):
                interest_component = balance * monthly_rate
                principal_component = emi - interest_component
                balance -= principal_component
                rows.append({
                    "Month": month,
                    "EMI": f"Rs {format_currency(emi)}",
                    "Interest": f"Rs {format_currency(interest_component)}",
                    "Principal": f"Rs {format_currency(principal_component)}",
                    "Balance": f"Rs {format_currency(max(0, balance))}"
                })

            df_schedule = pd.DataFrame(rows)
            st.dataframe(df_schedule, use_container_width=True, height=400)
    else:
        st.info("No loans found. Add a loan first.")
