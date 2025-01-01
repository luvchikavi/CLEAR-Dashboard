import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Automatically change the working directory to the script's directory
os.chdir(os.path.dirname(__file__))

# Set page configuration
st.set_page_config(page_title="CLEAR Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return pd.DataFrame()

data_file = "sano_lca_products.csv"
data = load_data(data_file)

if data.empty:
    st.error("Dataset could not be loaded. Please ensure the CSV file is available.")
    st.stop()

# Header Section
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("CLEAR_LOGO.png", width=100)  # Replace with the correct file name
    except FileNotFoundError:
        st.error("Logo image not found!")
with col_title:
    st.title("CLEAR: Compliance, Lifecycle, Emissions, Analysis, Reporting")

# Sidebar Navigation
st.sidebar.header("Navigation")
selected_tab = st.sidebar.radio("Select a tab:", ["Environmental Analysis", "Financial Analysis", "Regulatory Compliance"])

# Environmental Analysis Tab
if selected_tab == "Environmental Analysis":
    st.header("🌿 Environmental Analysis")

    # Scenario Modeling Sliders
    st.sidebar.header("Adjust Parameters")
    transport_type = st.sidebar.selectbox("Transportation Type", ["Air", "Road", "Sea"], key="transport")
    energy_source = st.sidebar.selectbox("Energy Source", ["Renewable", "Non-renewable"], key="energy")
    export_ratio = st.sidebar.slider("Percent of Products Exported to EU", 0, 100, 20, key="export")

    # Adjust emissions based on scenario inputs
    adjusted_data = data.copy()
    if transport_type == "Air":
        adjusted_data["Logistics (kg CO2)"] *= 1.5
    elif transport_type == "Sea":
        adjusted_data["Logistics (kg CO2)"] *= 0.8

    if energy_source == "Renewable":
        adjusted_data["Production (kg CO2)"] *= 0.7
    else:
        adjusted_data["Production (kg CO2)"] *= 1.2

    # Update Total Carbon Footprint
    adjusted_data["Total Carbon Footprint (kg CO2)"] = (
        adjusted_data["Raw Material (kg CO2)"] +
        adjusted_data["Production (kg CO2)"] +
        adjusted_data["Logistics (kg CO2)"]
    )

    # Display Adjusted Metrics
    st.subheader("Adjusted Emissions Data")
    st.dataframe(adjusted_data[["Product Name", "Raw Material (kg CO2)", "Production (kg CO2)", "Logistics (kg CO2)", "Total Carbon Footprint (kg CO2)"]])

    # Emissions Breakdown Pie Chart
    st.subheader("Emissions Breakdown by Category")
    pie_chart = px.pie(
        adjusted_data.melt(id_vars="Product Name", value_vars=["Raw Material (kg CO2)", "Production (kg CO2)", "Logistics (kg CO2)"], var_name="Category", value_name="Emissions (kg CO2)"),
        values="Emissions (kg CO2)",
        names="Category",
        title="Emissions Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(pie_chart, use_container_width=True)

    # Bar Chart for Per-Product Emissions
    st.subheader("Per-Product Emissions Comparison")
    bar_chart = px.bar(
        adjusted_data,
        x="Product Name",
        y="Total Carbon Footprint (kg CO2)",
        title="Total Emissions by Product",
        labels={"Product Name": "Product", "Total Carbon Footprint (kg CO2)": "Total Emissions (kg CO2)"},
        color="Total Carbon Footprint (kg CO2)",
        color_continuous_scale=px.colors.sequential.Blues
    )
    st.plotly_chart(bar_chart, use_container_width=True)

# Financial Analysis Tab
elif selected_tab == "Financial Analysis":
    st.header("💰 Financial Analysis")

    # Carbon Tax Slider
    carbon_tax_rate = st.slider("Set Carbon Tax Rate (€/ton)", min_value=10, max_value=100, value=25, step=5)

    # Calculate Total Carbon Emissions (tons)
    data["Total Carbon Footprint (tons)"] = data["Total Carbon Footprint (kg CO2)"] / 1000
    data["Carbon Tax (€)"] = data["Total Carbon Footprint (tons)"] * carbon_tax_rate

    # Display Metrics
    total_emissions = data["Total Carbon Footprint (tons)"].sum()
    total_tax_cost = data["Carbon Tax (€)"].sum()

    st.metric(label="Total Carbon Emissions (tons)", value=f"{total_emissions:.2f}")
    st.metric(label="Total Carbon Tax Cost (€)", value=f"€{total_tax_cost:.2f}")

    # Cost Breakdown Table
    st.subheader("Cost Breakdown by Product")
    st.dataframe(data[["Product Name", "Total Carbon Footprint (tons)", "Carbon Tax (€)"]])

    # Bar Chart for Cost Distribution
    st.subheader("Cost Distribution by Product")
    bar_chart = px.bar(
        data,
        x="Product Name",
        y="Carbon Tax (€)",
        title="Carbon Tax Costs by Product",
        labels={"Product Name": "Product", "Carbon Tax (€)": "Tax Cost (€)"},
        color="Carbon Tax (€)",
        color_continuous_scale=px.colors.sequential.Blues
    )
    st.plotly_chart(bar_chart, use_container_width=True)

# Regulatory Compliance Tab
elif selected_tab == "Regulatory Compliance":
    st.header("📜 Regulatory Compliance Tools")
    st.write("This section will include compliance evaluation and rule enforcement tools.")

# Footer Attribution
st.write("---")
st.write("**CLEAR v1.0**")
st.write("Tool created by Dr. Avi Luvchik. All rights reserved.")
