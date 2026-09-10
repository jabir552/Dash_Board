import streamlit as st
import pandas as pd
import re

# 1. Page Configuration
st.set_page_config(
    page_title="Porting Operations Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Helper: Count individual phone numbers in a cell
def count_phone_numbers(text):
    if pd.isna(text):
        return 0
    # Split by newlines or commas and filter out empty lines
    lines = [line.strip() for line in re.split(r'[\r\n,]+', str(text)) if line.strip()]
    return len(lines)

# 3. Load & Process Data
@st.cache_data
def load_data():
    df = pd.read_csv("DashBoard Sheet - Sheet1.csv")
    df = df.dropna(how="all").copy()
    
    # Clean text columns
    df["Practice"] = df["Practice"].astype(str).str.strip()
    df["Status"] = df["Status"].astype(str).str.strip()
    
    # Calculate number of ported phone numbers per row
    df["Number Count"] = df["Ported numbers"].apply(count_phone_numbers)
    return df

df = load_data()

# 4. Sidebar Controls
with st.sidebar:
    st.header("⚙️ Dashboard Settings")
    working_days = st.number_input(
        "Working Days in Period",
        min_value=1,
        max_value=365,
        value=22,
        help="Used to compute the average ported numbers per working day."
    )
    
    status_filter = st.multiselect(
        "Filter by Status",
        options=sorted(df["Status"].unique()),
        default=sorted(df["Status"].unique())
    )

# Filter dataset based on sidebar
filtered_df = df[df["Status"].isin(status_filter)]

# 5. Core KPI Calculations
total_requests = len(filtered_df)
total_numbers_all = filtered_df["Number Count"].sum()

# Specific to successfully completed ports
completed_df = filtered_df[filtered_df["Status"].str.lower() == "completed"]
total_completed_numbers = completed_df["Number Count"].sum()

# Average completed numbers per working day
avg_per_working_day = total_completed_numbers / working_days if working_days > 0 else 0

# 6. Top Metric Cards (Scorecards)
st.title("📞 Q3 Porting DashBoard")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Total Requests", value=f"{total_requests:,}")
kpi2.metric(label="Total Numbers Ported", value=f"{total_completed_numbers:,}")
kpi3.metric(label="Avg Ported / Working Day", value=f"{avg_per_working_day:.2f}")
kpi4.metric(label="Total In Scope (All Statuses)", value=f"{total_numbers_all:,}")

st.divider()

# 7. Visual Charts Section
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📌 Porting Volume by Status")
    # Group numbers by Status
    status_summary = (
        filtered_df.groupby("Status")["Number Count"]
        .sum()
        .reset_index()
        .rename(columns={"Number Count": "Total Phone Numbers"})
        .sort_values(by="Total Phone Numbers", ascending=False)
    )
    st.bar_chart(data=status_summary.set_index("Status"), color="#2b83ba")

with col_chart2:
    st.subheader("🏢 Top 10 Practices by Number Volume")
    top_practices = (
        filtered_df.groupby("Practice")["Number Count"]
        .sum()
        .reset_index()
        .sort_values(by="Number Count", ascending=False)
        .head(10)
    )
    st.bar_chart(data=top_practices.set_index("Practice"), color="#41b6c4")

st.divider()

# 8. Detailed Data Table
st.subheader("📋 Filtered Records")
st.dataframe(
    filtered_df[["Practice", "Status", "Number Count", "Ported numbers"]],
    use_container_width=True,
    hide_index=True
)