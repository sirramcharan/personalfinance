import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import load_data, save_data, load_config
from utils.formatters import format_currency, format_percentage
from datetime import datetime

st.set_page_config(page_title="Expenses Tracker", page_icon="💸")

data = load_data()
config = load_config()

if "expense_records" not in data:
    data["expense_records"] = []
    save_data(data)

st.markdown("""
<style>
    .big-metric { font-size: 1.8rem; font-weight: 700; color: #FF6B6B; }
    .accent1 { color: #00FFA3; }
</style>
""", unsafe_allow_html=True)

st.title("💸 Expenses Tracker")

tab1, tab2, tab3 = st.tabs(["Overview", "Add Expense", "Transaction History"])

def get_expense_stats(records):
    if not records:
        return 0, 0, [], [], {}
    df = pd.DataFrame(records)
    total = df["amount"].sum()
    monthly = df[df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").month == datetime.now().month)]["amount"].sum()
    by_cat = df.groupby("category")["amount"].sum().to_dict()
    by_fix_var = df.groupby("type")["amount"].sum().to_dict()
    monthly_trend = df.groupby(df["date"].apply(lambda x: x[:7]))["amount"].sum().to_dict()
    return total, monthly, by_cat, by_fix_var, monthly_trend

total_exp, monthly_exp, by_cat, by_fix_var, monthly_trend = get_expense_stats(data["expense_records"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">💵 Total Expenses</h4>
            <div class="big-metric">Rs {format_currency(total_exp)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">📅 This Month</h4>
            <div class="big-metric">Rs {format_currency(monthly_exp)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        fixed_cost = by_fix_var.get("Fixed", 0)
        variable_cost = by_fix_var.get("Variable", 0)
        savings_rate = ((total_exp - variable_cost) / (total_exp + 1)) * 100 if total_exp else 0
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">📊 Fixed vs Variable</h4>
            <div class="big-metric">Rs {format_currency(fixed_cost)} / Rs {format_currency(variable_cost)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if by_cat:
        col1, col2 = st.columns(2)
        with col1:
            df_cat = pd.DataFrame(list(by_cat.items()), columns=["Category", "Amount"])
            fig = px.pie(df_cat, values="Amount", names="Category", hole=0.4,
                         color_discrete_sequence=["#FF6B6B", "#FFD93D", "#6C63FF", "#4ECDC4", "#00FFA3", "#FF8FAB"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font_color="white", legend=dict(bgcolor="rgba(0,0,0,0)"),
                             margin=dict(l=0, r=0, t=30, b=0))
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True, key="expense_pie")
        with col2:
            if monthly_trend:
                df_trend = pd.DataFrame(list(monthly_trend.items()), columns=["Month", "Amount"])
                fig2 = px.bar(df_trend, x="Month", y="Amount",
                             color_discrete_sequence=["#FF6B6B"])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="white",
                                  xaxis=dict(showgrid=False, color="white"),
                                  yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="white"),
                                  margin=dict(l=0, r=0, t=30, b=40))
                st.plotly_chart(fig2, use_container_width=True, key="expense_bar")
    else:
        st.info("No expense records yet. Add your first expense in the 'Add Expense' tab.")

with tab2:
    with st.form("add_expense"):
        st.subheader("Add New Expense Entry")
        c1, c2 = st.columns(2)
        with c1:
            category = st.selectbox("Category", ["Rent", "Food", "Transport", "Utilities", "Entertainment", "Shopping", "Healthcare", "Education", "EMI", "Other"], index=0)
            exp_type = st.selectbox("Type", ["Fixed", "Variable"], index=1)
        with c2:
            amount = st.number_input("Amount (Rs)", min_value=0.0, step=50.0)
            date = st.date_input("Date", value=datetime.now().date())
        description = st.text_input("Description (optional)")
        submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)
        if submitted:
            if amount > 0:
                record = {
                    "category": category,
                    "type": exp_type,
                    "amount": float(amount),
                    "date": str(date),
                    "description": description
                }
                data["expense_records"].append(record)
                save_data(data)
                st.success(f"Added Rs {format_currency(amount)} - {category} ({exp_type})!")
                st.rerun()
            else:
                st.error("Please enter a valid amount.")

with tab3:
    st.subheader("All Expense Transactions")
    if data["expense_records"]:
        df_all = pd.DataFrame(data["expense_records"])
        df_display = df_all[["date", "category", "type", "amount", "description"]].copy()
        df_display.columns = ["Date", "Category", "Type", "Amount (Rs)", "Description"]
        st.dataframe(df_display, use_container_width=True)
        csv = df_all.to_csv(index=False)
        st.download_button("📥 Download as CSV", csv, "expense_records.csv", "text/csv")
    else:
        st.info("No expense records found.")
