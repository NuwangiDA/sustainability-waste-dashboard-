import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="🌍 Global Waste Management Dashboard", page_icon="🗑️", layout="wide")

# ── THEME CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f0f4f8; }

/* Sidebar */
[data-testid="stSidebar"] { background: #1b4332; }
[data-testid="stSidebar"] * { color: #d8f3dc !important; }
[data-testid="stSidebar"] h2 { color: #74c69d !important; font-size:0.7rem !important; letter-spacing:2px; text-transform:uppercase; }
#KPI Cards 
/* Metric cards */
[data-testid="stMetric"] {
    background: white; border-radius: 14px;
    padding: 1.2rem 1.4rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-top: 4px solid #2d6a4f;
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size:0.72rem !important; font-weight:600 !important; text-transform:uppercase; letter-spacing:1px; }
[data-testid="stMetricValue"] { color: #1b4332 !important; font-size:1.9rem !important; font-weight:700 !important; }

/* All chart/section boxes */
.box {
    background: white; border-radius: 14px;
    padding: 1.4rem 1.6rem; margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border: 1px solid #e8f5e9;
}
.box-title {
    font-size: 1rem; font-weight: 700; color: #1b4332;
    margin-bottom: 0.2rem;
}
.box-sub {
    font-size: 0.78rem; color: #6b7280; margin-bottom: 1rem;
}

/* Warning */
.stWarning { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("WB_WAW_what a wate 3.0 dataset.csv")
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    return df

df = load_data()

# ── COLOUR THEMES ─────────────────────────────────────────────────────────────
THEMES = {
    "🌿 Forest Green": ["#1b4332","#2d6a4f","#40916c","#52b788","#74c69d","#95d5b2","#b7e4c7"],
    "🌊 Ocean Blue":  ["#03045e","#0077b6","#0096c7","#00b4d8","#48cae4","#90e0ef","#caf0f8"],
    "🌅 Sunset":      ["#7f0000","#c62828","#e53935","#f57c00","#fb8c00","#ffa726","#ffcc02"],
    "🪨 Earth Tones": ["#3e2723","#5d4037","#795548","#8d6e63","#a1887f","#bcaaa4","#d7ccc8"],
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎨 Theme")
    theme_choice = st.selectbox("Colour Theme", list(THEMES.keys()))
    COLORS = THEMES[theme_choice]
    PRIMARY = COLORS[0]
    SCALE = [[i/6, c] for i, c in enumerate(COLORS)]

    st.markdown("## 🔽 Filters")
    regions = sorted(df["REGION_WB"].dropna().unique())
    selected_region = st.multiselect("Region", regions, default=regions)

    income_groups = sorted(df["INCOME_GR"].dropna().unique())
    selected_income = st.multiselect("Income Group", income_groups, default=income_groups)

    indicators = sorted(df["INDICATOR_LABEL"].dropna().unique())
    selected_indicator = st.selectbox("Indicator", indicators)

    good_years = [y for y in sorted(df["TIME_PERIOD"].dropna().unique()) if y <= 2022]
    selected_year = st.selectbox("Year", good_years, index=len(good_years)-1)

    st.markdown("## 🏆 Top N")
    top_n = st.slider("Show Top Countries", 5, 20, 10)

# ── FILTER DATA ───────────────────────────────────────────────────────────────
filtered_df = df[
    (df["REGION_WB"].isin(selected_region)) &
    (df["INCOME_GR"].isin(selected_income)) &
    (df["INDICATOR_LABEL"] == selected_indicator) &
    (df["TIME_PERIOD"] == selected_year)
].dropna(subset=["OBS_VALUE"])

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,{PRIMARY},{COLORS[2]});
            border-radius:16px; padding:2rem 2.5rem; margin-bottom:1.5rem;">
    <div style="font-size:2rem; font-weight:800; color:white; letter-spacing:-0.5px;">
        🗑️ Global Waste Management Dashboard
    </div>
    <div style="background:rgba(255,255,255,0.15); border-radius:10px;
                padding:0.8rem 1.2rem; margin-top:1rem; border-left:4px solid rgba(255,255,255,0.5);">
        <div style="color:rgba(255,255,255,0.95); font-size:0.9rem; line-height:1.6;">
             This dashboard explores how countries across the world manage, treat, and reduce solid waste.<br>
             Use the filters on the left to explore data by region, income group, indicator and year.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
avg = filtered_df["OBS_VALUE"].mean()
k1.metric("📦 Total Records", f"{len(filtered_df):,}")
k2.metric("🌍 Countries Covered", f"{filtered_df['REF_AREA_LABEL'].nunique()}")
k3.metric("📅 Selected Year", f"{selected_year}")
k4.metric("📊 Average Value", f"{avg:,.1f}" if not pd.isna(avg) else "—")

st.markdown("<br>", unsafe_allow_html=True)
#Bar Chart
# ── CHART 1: Bar by Region ────────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">📊 Average Value by Region</div>', unsafe_allow_html=True)
st.markdown('<div class="box-sub">Comparing waste management values across world regions</div>', unsafe_allow_html=True)
if not filtered_df.empty:
    bar_data = filtered_df.groupby("REGION_WB")["OBS_VALUE"].mean().reset_index()
    bar_data.columns = ["Region", "Average Value"]
    fig1 = px.bar(bar_data, x="Region", y="Average Value", color="Region",
                  color_discrete_sequence=COLORS,
                  title=f"<b>{selected_indicator}</b> by Region ({selected_year})")
    fig1.update_traces(marker_line_width=0)
    fig1.update_layout(paper_bgcolor="white", plot_bgcolor="white", showlegend=False,
                       margin=dict(l=10,r=10,t=40,b=10), height=350,
                       title_font=dict(size=13, color="#374151"),
                       xaxis=dict(showgrid=False, tickfont=dict(size=11)),
                       yaxis=dict(showgrid=True, gridcolor="#f3f4f6"))
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("No data available — try a different indicator or year.")
st.markdown('</div>', unsafe_allow_html=True)
#World Map
# ── CHART 2: World Map ────────────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">🗺️ World Map View</div>', unsafe_allow_html=True)
st.markdown('<div class="box-sub">Country-level distribution across the globe</div>', unsafe_allow_html=True)
map_df = df[(df["INDICATOR_LABEL"]==selected_indicator) &
            (df["TIME_PERIOD"]==selected_year)].dropna(subset=["OBS_VALUE","REF_AREA"])
if not map_df.empty:
    fig2 = px.choropleth(map_df, locations="REF_AREA", color="OBS_VALUE",
                         hover_name="REF_AREA_LABEL", color_continuous_scale=SCALE,
                         title=f"<b>World Map:</b> {selected_indicator} ({selected_year})")
    fig2.update_layout(paper_bgcolor="white", margin=dict(l=0,r=0,t=40,b=0), height=380,
                       title_font=dict(size=13, color="#374151"),
                       geo=dict(showframe=False, showcoastlines=True,
                                coastlinecolor="#e5e7eb", landcolor="#f9fafb",
                                showocean=True, oceancolor="#eff6ff"),
                       coloraxis_colorbar=dict(thickness=10, len=0.5))
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No map data for this selection.")
st.markdown('</div>', unsafe_allow_html=True)

# ── CHART 3: Top N Countries ──────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown(f'<div class="box-title">🏆 Top {top_n} Countries</div>', unsafe_allow_html=True)
st.markdown(f'<div class="box-sub">Highest values for {selected_indicator} in {selected_year}</div>', unsafe_allow_html=True)
if not filtered_df.empty:
    top_df = filtered_df.groupby("REF_AREA_LABEL")["OBS_VALUE"].mean().reset_index()
    top_df.columns = ["Country", "Value"]
    top_df = top_df.nlargest(top_n, "Value")
    fig_top = px.bar(top_df, x="Value", y="Country", orientation="h",
                     color="Value", color_continuous_scale=SCALE)
    fig_top.update_traces(marker_line_width=0)
    fig_top.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                          coloraxis_showscale=False,
                          margin=dict(l=10,r=10,t=10,b=10), height=max(300, top_n*32),
                          yaxis=dict(showgrid=False, autorange="reversed",
                                     tickfont=dict(size=11, color="#374151")),
                          xaxis=dict(showgrid=True, gridcolor="#f3f4f6"))
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.warning("No data for top countries.")
st.markdown('</div>', unsafe_allow_html=True)

# ── CHART 4: Trend Over Time ──────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">📈 Trend Over Time</div>', unsafe_allow_html=True)
st.markdown('<div class="box-sub">Track how waste indicators change year by year for a selected country</div>', unsafe_allow_html=True)
country_list = sorted(df["REF_AREA_LABEL"].dropna().unique())
default = "India" if "India" in country_list else country_list[0]
selected_country = st.selectbox("Select a Country", country_list, index=country_list.index(default))
trend_df = df[(df["INDICATOR_LABEL"]==selected_indicator) &
              (df["REF_AREA_LABEL"]==selected_country)].dropna(subset=["OBS_VALUE"]).sort_values("TIME_PERIOD")
if not trend_df.empty:
    fig3 = px.area(trend_df, x="TIME_PERIOD", y="OBS_VALUE",
                   color_discrete_sequence=[PRIMARY],
                   title=f"<b>{selected_indicator}</b> — {selected_country}")
    fig3.update_traces(line=dict(width=2.5, color=PRIMARY),
                       fillcolor=f"rgba({int(PRIMARY[1:3],16)},{int(PRIMARY[3:5],16)},{int(PRIMARY[5:],16)},0.1)")
    fig3.update_layout(paper_bgcolor="white", plot_bgcolor="white",
                       margin=dict(l=10,r=10,t=40,b=10), height=300,
                       title_font=dict(size=13, color="#374151"),
                       xaxis=dict(showgrid=False, title="Year"),
                       yaxis=dict(showgrid=True, gridcolor="#f3f4f6", title="Value"))
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("No trend data for this country and indicator.")
st.markdown('</div>', unsafe_allow_html=True)

# ── CHART 5: Waste Composition ────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">🍩 Waste Composition Breakdown</div>', unsafe_allow_html=True)
st.markdown('<div class="box-sub">Breakdown of global waste by material type for the selected year</div>', unsafe_allow_html=True)
composition_df = df[
    df["WASTE_PRODUCT_LABEL"].notna() &
    (~df["WASTE_PRODUCT_LABEL"].isin(["Not applicable"])) &
    (df["TIME_PERIOD"]==selected_year)
].dropna(subset=["OBS_VALUE"]).copy()
composition_df["OBS_VALUE"] = pd.to_numeric(composition_df["OBS_VALUE"], errors="coerce")
composition_df = composition_df.dropna(subset=["OBS_VALUE"])
if not composition_df.empty:
    pie_data = composition_df.groupby("WASTE_PRODUCT_LABEL")["OBS_VALUE"].mean().reset_index().nlargest(8,"OBS_VALUE")
    fig4 = px.pie(pie_data, names="WASTE_PRODUCT_LABEL", values="OBS_VALUE",
                  hole=0.5, color_discrete_sequence=COLORS,
                  title=f"<b>Global Waste Composition</b> ({selected_year})")
    fig4.update_traces(textfont_size=11, marker=dict(line=dict(color="white", width=2)))
    fig4.update_layout(paper_bgcolor="white", margin=dict(l=10,r=10,t=40,b=10), height=380,
                       title_font=dict(size=13, color="#374151"),
                       legend=dict(font=dict(size=10, color="#6b7280"), bgcolor="white"))
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("No waste composition data for this year.")
st.markdown('</div>', unsafe_allow_html=True)

# ── CHART 6: Rich vs Poor ─────────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">💰 Rich vs Poor Countries</div>', unsafe_allow_html=True)
st.markdown('<div class="box-sub">How waste management differs across income groups globally</div>', unsafe_allow_html=True)
income_df = df[df["INDICATOR_LABEL"]==selected_indicator].dropna(subset=["OBS_VALUE","INCOME_GR"])
if not income_df.empty:
    fig5 = px.box(income_df, x="INCOME_GR", y="OBS_VALUE", color="INCOME_GR",
                  color_discrete_sequence=COLORS,
                  title=f"<b>{selected_indicator}</b> by Income Group",
                  labels={"INCOME_GR":"Income Group","OBS_VALUE":"Value"})
    fig5.update_traces(marker_line_width=0)
    fig5.update_layout(paper_bgcolor="white", plot_bgcolor="white", showlegend=False,
                       margin=dict(l=10,r=10,t=40,b=10), height=320,
                       title_font=dict(size=13, color="#374151"),
                       xaxis=dict(showgrid=False),
                       yaxis=dict(showgrid=True, gridcolor="#f3f4f6"))
    st.plotly_chart(fig5, use_container_width=True)
else:
    st.warning("No income group data available.")
st.markdown('</div>', unsafe_allow_html=True)

# ── STRATEGY SECTION ──────────────────────────────────────────────────────────
st.markdown('<div class="box">', unsafe_allow_html=True)
st.markdown('<div class="box-title">💡 Waste Management Strategies</div>', unsafe_allow_html=True)
st.markdown('<div class="box-sub">Key global strategies for improving waste management outcomes</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(f"""
    <div style="background:#f0fdf4; border-radius:12px; padding:1.2rem; border-left:4px solid {COLORS[1]};">
        <div style="font-size:1.5rem;">♻️</div>
        <div style="font-weight:700; color:#1b4332; font-size:0.95rem; margin:0.4rem 0;">Reduce & Recycle</div>
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
            Encouraging households and industries to reduce waste at source and recycle materials like plastic, glass, and paper.
        </div>
    </div>
    """, unsafe_allow_html=True)
with s2:
    st.markdown(f"""
    <div style="background:#f0fdf4; border-radius:12px; padding:1.2rem; border-left:4px solid {COLORS[2]};">
        <div style="font-size:1.5rem;">🏭</div>
        <div style="font-weight:700; color:#1b4332; font-size:0.95rem; margin:0.4rem 0;">Waste-to-Energy</div>
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
            Converting non-recyclable waste into usable energy through incineration and biogas — reducing landfill dependency.
        </div>
    </div>
    """, unsafe_allow_html=True)
with s3:
    st.markdown(f"""
    <div style="background:#f0fdf4; border-radius:12px; padding:1.2rem; border-left:4px solid {COLORS[3]};">
        <div style="font-size:1.5rem;">🌱</div>
        <div style="font-weight:700; color:#1b4332; font-size:0.95rem; margin:0.4rem 0;">Composting</div>
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
            Turning organic food and garden waste into compost — reducing methane emissions and enriching soil naturally.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
s4, s5, s6 = st.columns(3)
with s4:
    st.markdown(f"""
    <div style="background:#f0fdf4; border-radius:12px; padding:1.2rem; border-left:4px solid {COLORS[4]};">
        <div style="font-size:1.5rem;">📋</div>
        <div style="font-weight:700; color:#1b4332; font-size:0.95rem; margin:0.4rem 0;">Extended Producer Responsibility</div>
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
            Making manufacturers responsible for the end-of-life disposal of their products — reducing packaging waste.
        </div>
    </div>
    """, unsafe_allow_html=True)
with s5:
    st.markdown(f"""
    <div style="background:#f0fdf4; border-radius:12px; padding:1.2rem; border-left:4px solid {COLORS[5]};">
        <div style="font-size:1.5rem;">🚛</div>
        <div style="font-weight:700; color:#1b4332; font-size:0.95rem; margin:0.4rem 0;">Improved Collection Systems</div>
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
            Expanding waste collection coverage especially in low-income countries to prevent open dumping and burning.
        </div>
    </div>
    """, unsafe_allow_html=True)
with s6:
    st.markdown(f"""
    <div style="background:#f0fdf4; border-radius:12px; padding:1.2rem; border-left:4px solid {COLORS[6] if len(COLORS)>6 else COLORS[0]};">
        <div style="font-size:1.5rem;">🎓</div>
        <div style="font-weight:700; color:#1b4332; font-size:0.95rem; margin:0.4rem 0;">Public Awareness</div>
        <div style="font-size:0.8rem; color:#6b7280; line-height:1.5;">
            Educating communities about proper waste segregation, recycling habits, and the environmental impact of waste.
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; background:white; border-radius:14px; padding:1rem;
            box-shadow:0 2px 8px rgba(0,0,0,0.06); color:#9ca3af; font-size:0.8rem;">
    Data Source: World Bank · What a Waste 3.0 &nbsp;·&nbsp;
    Dashboard by Nuwangi &nbsp;·&nbsp; 5DATA004C Coursework
</div>
""", unsafe_allow_html=True)