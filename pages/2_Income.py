import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_manager import load_data, save_data, load_config
from utils.formatters import format_currency, format_percentage
from datetime import datetime

st.set_page_config(page_title="Income Tracker", page_icon="💰")

# Load data and config
data = load_data()
config = load_config()

# Initialize income records if not present
if "income_records" not in data:
    data["income_records"] = []
    save_data(data)

# CSS styles - matching dashboard glassmorphism
st.markdown("""
<style>
    .big-metric { font-size: 1.8rem; font-weight: 700; color: #00FFA3; }
    .accent1 { color: #00FFA3; }
    .section-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# Title
st.title("💰 Income Tracker")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Overview", "Add Income", "Transaction History"])

# Calculate totals
def get_income_stats(records):
    if not records:
        return 0, 0, [], {}
    df = pd.DataFrame(records)
    total = df["amount"].sum()
    monthly = df[df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").month == datetime.now().month)]["amount"].sum()
    by_source = df.groupby("source")["amount"].sum().to_dict()
    monthly_trend = df.groupby(df["date"].apply(lambda x: x[:7]))["amount"].sum().to_dict()
    return total, monthly, by_source, monthly_trend

total_income, monthly_income, by_source, monthly_trend = get_income_stats(data["income_records"])

with tab1:
    # KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">💵 Total Income</h4>
            <div class="big-metric">Rs {format_currency(total_income)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">📅 This Month</h4>
            <div class="big-metric">Rs {format_currency(monthly_income)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="glass" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
            <h4 class="accent1">📊 Sources</h4>
            <div class="big-metric">{len(by_source)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    if by_source:
        col1, col2 = st.columns(2)
        with col1:
            # Income by Source - Donut
            df_sources = pd.DataFrame(list(by_source.items()), columns=["Source", "Amount"])
            fig = px.pie(df_sources, values="Amount", names="Source", hole=0.4,
                         color_discrete_sequence=["#00FFA3", "#FF6B6B", "#4ECDC4", "#FFD93D", "#6C63FF"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font_color="white", legend=dict(bgcolor="rgba(0,0,0,0)"),
                             margin=dict(l=0, r=0, t=30, b=0))
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True, key="income_pie")
        with col2:
            # Monthly Trend - Bar
            if monthly_trend:
                df_trend = pd.DataFrame(list(monthly_trend.items()), columns=["Month", "Amount"])
                fig2 = px.bar(df_trend, x="Month", y="Amount",
                             color_discrete_sequence=["#00FFA3"])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font_color="white",
                                  xaxis=dict(showgrid=False, color="white"),
                                  yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)", color="white"),
                                  margin=dict(l=0, r=0, t=30, b=40))
                st.plotly_chart(fig2, use_container_width=True, key="income_bar")
    else:
        st.info("No income records yet. Add your first income entry in the 'Add Income' tab.")

with tab2:
    # Add Income Form
    with st.form("add_income"):
        st.subheader("Add New Income Entry")
        c1, c2 = st.columns(2)
        with c1:
            source = st.selectbox("Source", ["Salary", "Freelance", "Investments", "Side Business", "Bonus", "Other"], index=0)
            amount = st.number_input("Amount (Rs)", min_value=0.0, step=100.0)
        with c2:
            date = st.date_input("Date", value=datetime.now().date())
            description = st.text_input("Description (optional)")

        submitted = st.form_submit_button("➕ Add Income", use_container_width=True)

        if submitted:
            if amount > 0:
                record = {
                    "source": source,
                    "amount": float(amount),
                    "date": str(date),
                    "description": description
                }
                data["income_records"].append(record)
                save_data(data)
                st.success(f"Added Rs {format_currency(amount)} from {source}!")
                st.rerun()
            else:
                st.error("Please enter a valid amount.")

with tab3:
    # Transaction History
    st.subheader("All Income Transactions")
    if data["income_records"]:
        df_all = pd.DataFrame(data["income_records"])
        df_display = df_all[["date", "source", "amount", "description"]].copy()
        df_display.columns = ["Date", "Source", "Amount (Rs)", "Description"]
        st.dataframe(df_display, use_container_width=True)

        # Export option
        csv = df_all.to_csv(index=False)
        st.download_button("📥 Download as CSV", csv, "income_records.csv", "text/csv")
    else:
        st.info("No income records found.")
