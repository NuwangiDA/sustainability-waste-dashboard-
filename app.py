import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global Waste Dashboard", page_icon="🗑️", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("WB_WAW_what a wate 3.0 dataset.csv")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df

df = load_data()

st.title("🌍 Global Waste Management Dashboard")
st.markdown("Exploring how countries around the world manage their waste.")
st.divider()

st.sidebar.header("🔽 Filters")
regions = sorted(df["REGION_WB"].dropna().unique())
selected_region = st.sidebar.multiselect("Select Region", regions, default=regions)
income_groups = sorted(df["INCOME_GR"].dropna().unique())
selected_income = st.sidebar.multiselect("Select Income Group", income_groups, default=income_groups)
indicators = sorted(df["INDICATOR_LABEL"].dropna().unique())
selected_indicator = st.sidebar.selectbox("Select Indicator", indicators)
years = sorted(df["TIME_PERIOD"].dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)

filtered_df = df[
    (df["REGION_WB"].isin(selected_region)) &
    (df["INCOME_GR"].isin(selected_income)) &
    (df["INDICATOR_LABEL"] == selected_indicator) &
    (df["TIME_PERIOD"] == selected_year)
]

col1, col2, col3 = st.columns(3)
col1.metric("📦 Total Records", f"{len(filtered_df):,}")
col2.metric("🌍 Countries Covered", filtered_df["REF_AREA_LABEL"].nunique())
col3.metric("📅 Selected Year", selected_year)
st.divider()

st.subheader("📊 Average Value by Region")
if not filtered_df.empty:
    bar_data = filtered_df.groupby("REGION_WB")["OBS_VALUE"].mean().reset_index()
    bar_data.columns = ["Region", "Average Value"]
    fig1 = px.bar(bar_data, x="Region", y="Average Value", color="Region",
                  title=f"{selected_indicator} by Region ({selected_year})")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No data available for this selection.")
st.divider()

st.subheader("🗺️ World Map View")
map_df = df[
    (df["INDICATOR_LABEL"] == selected_indicator) &
    (df["TIME_PERIOD"] == selected_year)
].dropna(subset=["OBS_VALUE", "REF_AREA"])
if not map_df.empty:
    fig2 = px.choropleth(map_df, locations="REF_AREA", color="OBS_VALUE",
                         hover_name="REF_AREA_LABEL", color_continuous_scale="Viridis",
                         title=f"World Map: {selected_indicator} ({selected_year})")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No map data for this selection.")
st.divider()

st.subheader("📈 Trend Over Time")
country_list = sorted(df["REF_AREA_LABEL"].dropna().unique())
selected_country = st.selectbox("Pick a Country to Track", country_list)
trend_df = df[
    (df["INDICATOR_LABEL"] == selected_indicator) &
    (df["REF_AREA_LABEL"] == selected_country)
].dropna(subset=["OBS_VALUE"])
if not trend_df.empty:
    fig3 = px.line(trend_df, x="TIME_PERIOD", y="OBS_VALUE",
                   title=f"{selected_indicator} Trend — {selected_country}",
                   markers=True)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No trend data for this country and indicator.")
st.divider()

st.subheader("🍕 Waste Composition Breakdown")
composition_df = df[
    df["WASTE_PRODUCT_LABEL"].notna() &
    (df["WASTE_PRODUCT_LABEL"] != "Not applicable") &
    (df["TIME_PERIOD"] == selected_year)
].dropna(subset=["OBS_VALUE"])
composition_df = composition_df.copy()
composition_df["OBS_VALUE"] = pd.to_numeric(composition_df["OBS_VALUE"], errors="coerce")
composition_df = composition_df.dropna(subset=["OBS_VALUE"])
if not composition_df.empty:
    pie_data = composition_df.groupby("WASTE_PRODUCT_LABEL")["OBS_VALUE"].mean().reset_index()
    fig4 = px.pie(pie_data, names="WASTE_PRODUCT_LABEL", values="OBS_VALUE",
                  title=f"Global Waste Composition ({selected_year})")
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("No waste composition data for this year.")
st.divider()

st.subheader("💰 Rich vs Poor Countries")
income_df = df[
    df["INDICATOR_LABEL"] == selected_indicator
].dropna(subset=["OBS_VALUE", "INCOME_GR"])
if not income_df.empty:
    fig5 = px.box(income_df, x="INCOME_GR", y="OBS_VALUE", color="INCOME_GR",
                  title=f"{selected_indicator} by Income Group",
                  labels={"INCOME_GR": "Income Group", "OBS_VALUE": "Value"})
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("No income group data available.")
st.divider()

st.caption("Data Source: World Bank — What a Waste 3.0 | Dashboard by Nuwangi")