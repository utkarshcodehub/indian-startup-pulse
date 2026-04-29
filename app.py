import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import Counter

st.set_page_config(
    page_title="India Startup Funding Pulse",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Force white background everywhere */
html, body { background-color: #FFFFFF !important; }
[data-testid="stAppViewContainer"] { background-color: #FFFFFF !important; }
[data-testid="stHeader"] { background-color: #FFFFFF !important; }
[data-testid="stToolbar"] { background-color: #FFFFFF !important; }
[data-testid="stSidebar"] { background-color: #FAFAFA !important; }
.main { background-color: #FFFFFF !important; }
.block-container { background-color: #FFFFFF !important; padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
section[data-testid="stMain"] { background-color: #FFFFFF !important; }

/* Typography */
html, body, [class*="css"], p, div, span, h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif !important;
    color: #1A1A2E;
}

/* KPI Cards */
.kpi-card {
    background: #F8F8FF;
    border-radius: 12px;
    padding: 1.4rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(108,99,255,0.08);
    border: 1px solid #EEEEFF;
}
.kpi-value { font-size: 1.8rem; font-weight: 700; color: #6C63FF; margin: 0; line-height: 1.2; }
.kpi-label { font-size: 0.7rem; color: #999; margin: 0; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.4rem; }

/* Section headers */
.section-header {
    font-size: 0.95rem;
    font-weight: 600;
    color: #1A1A2E;
    margin-bottom: 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #6C63FF;
    display: inline-block;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 8px 18px;
    font-weight: 500; font-size: 0.88rem;
    background: #F5F5FF; color: #6C63FF;
}
.stTabs [aria-selected="true"] {
    background-color: #6C63FF !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-panel"] { background: #FFFFFF; padding-top: 1.5rem; }

/* Selectbox */
div[data-testid="stSelectbox"] > div { border-radius: 8px; }

/* Remove default streamlit red elements */
footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
ACCENT = "#6C63FF"
COLORS = ["#6C63FF", "#FF6B6B", "#FFB347", "#4ECDC4", "#45B7D1", "#96CEB4", "#A89CFF", "#FF8B94", "#88D8B0", "#FCBF49"]

PLOT_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter", color="#333", size=12),
)

SECTOR_KEYWORDS = [
    (["fintech","finance","financial","payment","banking","insurance","lending","wallet","nbfc","invest","wealth","stock","mutual fund","credit","loan"], "FinTech"),
    (["edtech","education","e-learning","elearning","learning","ed-tech","e-tech","exam","school","college","course","tutor","skill","upskill"], "EdTech"),
    (["ecommerce","e-commerce","retail","marketplace","shopping","fashion","d2c","apparel","jewel","ethnic","luxury","lingerie"], "E-Commerce"),
    (["health","healthcare","medical","diagnostic","pharma","wellness","hospital","clinic","dental","doctor","telemedicine"], "HealthTech"),
    (["food","restaurant","foodtech","food-tech","dining","beverage","grocery","nutrition","meal","kitchen","cloud kitchen"], "FoodTech"),
    (["logistics","transport","freight","supply chain","trucking","delivery","last mile","courier","warehouse"], "Logistics"),
    (["saas","enterprise","b2b","software","cloud","erp","crm","automation","analytics platform","data platform"], "SaaS & Enterprise"),
    (["real estate","property","housing","home","interior","furniture","construction"], "Real Estate & Home"),
    (["travel","hotel","hospitality","tourism","holiday","trip","flight","cab","taxi","ride"], "Travel & Mobility"),
    (["media","social","content","gaming","entertainment","consumer internet","video","music","streaming","news"], "Media & Gaming"),
    (["agri","agritech","clean","solar","renewable","ev","electric","environment","sustainable"], "AgriTech & CleanTech"),
]

CITY_MAP = {
    "bangalore": "Bangalore", "bengaluru": "Bangalore",
    "gurgaon": "Gurugram", "gurugram": "Gurugram",
    "new delhi": "Delhi", "delhi": "Delhi",
    "mumbai": "Mumbai", "pune": "Pune",
    "hyderabad": "Hyderabad", "chennai": "Chennai",
    "noida": "Noida", "kolkata": "Kolkata",
    "ahmedabad": "Ahmedabad", "jaipur": "Jaipur",
}

CITY_COORDS = {
    "Bangalore":  (12.9716, 77.5946),
    "Mumbai":     (19.0760, 72.8777),
    "Delhi":      (28.6139, 77.2090),
    "Gurugram":   (28.4595, 77.0266),
    "Hyderabad":  (17.3850, 78.4867),
    "Chennai":    (13.0827, 80.2707),
    "Pune":       (18.5204, 73.8567),
    "Noida":      (28.5355, 77.3910),
    "Kolkata":    (22.5726, 88.3639),
    "Ahmedabad":  (23.0225, 72.5714),
    "Jaipur":     (26.9124, 75.7873),
}

# ── DATA ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    srk = pd.read_csv("data/startup_funding.csv")
    srk = srk.rename(columns={
        "Startup Name": "company",
        "Industry Vertical": "sector_raw",
        "City  Location": "city_raw",
        "Investors Name": "investors",
        "InvestmentnType": "stage_raw",
        "Amount in USD": "amount_raw",
        "Date dd/mm/yyyy": "date_raw",
    })
    srk["date"] = pd.to_datetime(srk["date_raw"], dayfirst=True, errors="coerce")
    srk["year"] = srk["date"].dt.year
    srk["amount"] = pd.to_numeric(
        srk["amount_raw"].astype(str).str.replace(",", "").str.strip(), errors="coerce"
    )

    df21 = pd.read_csv("data/India-startup-funding-2021-full.csv")
    df21 = df21.rename(columns={
        "Company/Brand": "company",
        "Sector": "sector_raw",
        "Headquarters": "city_raw",
        "Investor/s": "investors",
        "Stage": "stage_raw",
        "Amount ($)": "amount_raw",
        "Month": "month_raw",
    })
    month_map = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,
                 "July":7,"August":8,"September":9,"October":10,"November":11,"December":12}
    df21["month_num"] = df21["month_raw"].map(month_map)
    df21["date"] = pd.to_datetime(df21["month_num"].apply(lambda x: f"2021-{int(x):02d}-01" if pd.notna(x) else None), errors="coerce")
    df21["year"] = 2021
    df21["amount"] = pd.to_numeric(
        df21["amount_raw"].astype(str).str.replace(",", "").str.strip(), errors="coerce"
    )

    keep = ["company", "sector_raw", "city_raw", "investors", "stage_raw", "amount", "date", "year"]
    df = pd.concat([srk[keep], df21[keep]], ignore_index=True)

    def map_sector(s):
        if pd.isna(s): return "Others"
        sl = str(s).lower()
        for keywords, label in SECTOR_KEYWORDS:
            if any(k in sl for k in keywords):
                return label
        return "Others"

    def map_city(c):
        if pd.isna(c): return "Other"
        cl = str(c).lower().strip()
        for key, val in CITY_MAP.items():
            if key in cl:
                return val
        return "Other"

    def map_stage(s):
        if pd.isna(s): return "Unknown"
        sl = str(s).lower()
        if any(x in sl for x in ["seed","angel","pre-seed","preseed"]): return "Seed / Angel"
        if "series a" in sl or "seriesa" in sl: return "Series A"
        if "series b" in sl: return "Series B"
        if "series c" in sl: return "Series C"
        if any(x in sl for x in ["series d","series e","series f","series g"]): return "Series D+"
        if "private equity" in sl: return "Private Equity"
        if "debt" in sl: return "Debt"
        return "Other"

    df["sector"] = df["sector_raw"].apply(map_sector)
    df["city"]   = df["city_raw"].apply(map_city)
    df["stage"]  = df["stage_raw"].apply(map_stage)

    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    # Exclude 2020 — SRK dataset only has 7 entries (Jan 2020 only), creates a misleading gap
    df = df[df["year"].isin([2015, 2016, 2017, 2018, 2019, 2021])]
    # Cap amounts at $5B — anything above is a data entry error (e.g. Alteria Capital $150B)
    df.loc[df["amount"] > 5_000_000_000, "amount"] = None
    return df

@st.cache_data
def get_coinvestment_pairs(_df):
    pairs = Counter()
    for _, row in _df.iterrows():
        if pd.isna(row["investors"]): continue
        invs = [i.strip() for i in str(row["investors"]).split(",") if len(i.strip()) > 2]
        if len(invs) < 2: continue
        for i in range(len(invs)):
            for j in range(i+1, len(invs)):
                pairs[tuple(sorted([invs[i], invs[j]]))] += 1
    return pairs

def fmt(val):
    if val >= 1e9: return f"${val/1e9:.1f}B"
    if val >= 1e6: return f"${val/1e6:.0f}M"
    if val >= 1e3: return f"${val/1e3:.0f}K"
    return f"${val:.0f}"

def kpi(label, value):
    return f'<div class="kpi-card"><p class="kpi-value">{value}</p><p class="kpi-label">{label}</p></div>'

def section(text):
    return f'<p class="section-header">{text}</p>'

def base_fig(**kwargs):
    d = {**PLOT_BASE, **kwargs}
    return d

# ── APP ───────────────────────────────────────────────────────────────────────
df = load_data()
df_amt = df.dropna(subset=["amount"])

st.markdown("# 🚀 India Startup Funding Pulse")
st.markdown("<p style='color:#999;margin-top:-12px;font-size:0.9rem;'>2015–2019 & 2021 &nbsp;·&nbsp; 4,200+ deals &nbsp;·&nbsp; Real Indian ecosystem data</p>", unsafe_allow_html=True)
st.markdown("""
<div style="background:#F8F8FF;border-radius:14px;padding:1.5rem 2rem;margin:1.2rem 0 1.6rem 0;border-left:4px solid #6C63FF;">
    <p style="font-size:1rem;color:#1A1A2E;margin:0 0 0.5rem 0;font-weight:600;">What is this?</p>
    <p style="font-size:0.88rem;color:#555;margin:0;line-height:1.75;">
        India saw one of the most dramatic startup funding cycles in the world between 2015 and 2021 —
        edtech exploded, fintech matured, and unicorns multiplied. But most of that data lives in scattered CSVs and news articles.
        <br><br>
        <strong>Funding Pulse</strong> merges 4,200+ real deals across 7 years into a navigable intelligence layer.
        Track which sectors got hot when, which cities are rising, which investors always co-invest,
        and how the market matured from seed-heavy chaos to structured late-stage rounds.
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊  Big Picture", "🏭  Sectors", "🏙️  Cities", "💼  Investors"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — BIG PICTURE
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Total Deals", f"{len(df):,}"), unsafe_allow_html=True)
    c2.markdown(kpi("Total Funding", fmt(df_amt["amount"].sum())), unsafe_allow_html=True)
    c3.markdown(kpi("Unique Startups", f"{df['company'].nunique():,}"), unsafe_allow_html=True)
    c4.markdown(kpi("Peak Year", str(df.groupby("year").size().idxmax())), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(section("Deals per Year"), unsafe_allow_html=True)
        yd = df.groupby("year").size().reset_index(name="deals")
        fig = px.bar(yd, x="year", y="deals", color_discrete_sequence=[ACCENT],
                     text="deals")
        fig.update_traces(textposition="outside", marker_line_width=0,
                          hovertemplate="%{x}: %{y} deals<extra></extra>")
        fig.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                          xaxis=dict(showgrid=False, tickmode="linear", title=""),
                          yaxis=dict(showgrid=False, title=""))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(section("Funding Volume per Year"), unsafe_allow_html=True)
        ya = df_amt.groupby("year")["amount"].sum().reset_index()
        ya["label"] = ya["amount"].apply(fmt)
        fig2 = go.Figure(go.Scatter(
            x=ya["year"], y=ya["amount"], mode="lines+markers+text",
            text=ya["label"], textposition="top center",
            fill="tozeroy", line=dict(color=ACCENT, width=3),
            fillcolor="rgba(108,99,255,0.08)",
            marker=dict(size=8, color=ACCENT),
            hovertemplate="%{x}: %{text}<extra></extra>"
        ))
        fig2.update_layout(**base_fig(margin=dict(l=10,r=10,t=20,b=10)),
                           xaxis=dict(showgrid=False, tickmode="linear", title=""),
                           yaxis=dict(showgrid=False, title="", showticklabels=False))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(section("Sector Heat Timeline — Where Money Moved"), unsafe_allow_html=True)
    heat = df_amt[df_amt["sector"] != "Others"].groupby(["year","sector"])["amount"].sum().reset_index()
    heat_pivot = heat.pivot(index="sector", columns="year", values="amount").fillna(0)
    fig3 = px.imshow(
        heat_pivot,
        color_continuous_scale=[[0,"#F5F5FF"],[0.4,"#A89CFF"],[1,"#3D35CC"]],
        aspect="auto", text_auto=False,
        labels=dict(color="Funding ($)")
    )
    fig3.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                       coloraxis_colorbar=dict(title="$", tickformat="$,.0f"))
    fig3.update_xaxes(side="bottom", title="")
    fig3.update_yaxes(title="")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(section("Funding Stage Mix by Year"), unsafe_allow_html=True)
    sy = df[~df["stage"].isin(["Unknown","Other"])].groupby(["year","stage"]).size().reset_index(name="count")
    fig4 = px.bar(sy, x="year", y="count", color="stage", barmode="stack",
                  color_discrete_sequence=COLORS)
    fig4.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                       xaxis=dict(showgrid=False, tickmode="linear", title=""),
                       yaxis=dict(showgrid=False, title=""),
                       legend=dict(orientation="h", y=-0.15, title=""))
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SECTORS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    sectors = sorted([s for s in df["sector"].unique() if s != "Others"])
    sel = st.selectbox("Choose a sector", sectors, key="sector_sel")
    sdf = df[df["sector"] == sel]
    sdf_amt = sdf.dropna(subset=["amount"])

    s1, s2, s3 = st.columns(3)
    s1.markdown(kpi("Total Deals", f"{len(sdf):,}"), unsafe_allow_html=True)
    s2.markdown(kpi("Total Funding", fmt(sdf_amt["amount"].sum()) if len(sdf_amt) else "N/A"), unsafe_allow_html=True)
    s3.markdown(kpi("Unique Startups", f"{sdf['company'].nunique():,}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(section("Deal Volume — Year on Year"), unsafe_allow_html=True)
        trend = sdf.groupby("year").size().reset_index(name="deals")
        fig = px.area(trend, x="year", y="deals", color_discrete_sequence=[ACCENT],
                      markers=True)
        fig.update_traces(line=dict(width=3), marker=dict(size=8),
                          fillcolor="rgba(108,99,255,0.1)")
        fig.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                          xaxis=dict(showgrid=False, tickmode="linear", title=""),
                          yaxis=dict(showgrid=False, title=""))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(section("Stage Distribution"), unsafe_allow_html=True)
        stg = sdf[~sdf["stage"].isin(["Unknown","Other"])]["stage"].value_counts().reset_index()
        stg.columns = ["stage","count"]
        fig2 = px.pie(stg, values="count", names="stage",
                      color_discrete_sequence=COLORS, hole=0.5)
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        fig2.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(section("Top Funded Startups in this Sector"), unsafe_allow_html=True)
    top = sdf_amt.groupby("company")["amount"].sum().sort_values(ascending=False).head(12).reset_index()
    top["label"] = top["amount"].apply(fmt)
    fig3 = px.bar(top, x="amount", y="company", orientation="h",
                  color_discrete_sequence=[ACCENT], text="label")
    fig3.update_traces(textposition="outside", marker_line_width=0)
    fig3.update_layout(**base_fig(margin=dict(l=10,r=80,t=10,b=10)),
                       yaxis=dict(autorange="reversed", showgrid=False, title=""),
                       xaxis=dict(showgrid=False, showticklabels=False, title=""))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(section("Average Deal Size by Year"), unsafe_allow_html=True)
    avg = sdf_amt.groupby("year")["amount"].mean().reset_index()
    avg["label"] = avg["amount"].apply(fmt)
    fig4 = px.bar(avg, x="year", y="amount", color_discrete_sequence=["#A89CFF"],
                  text="label")
    fig4.update_traces(textposition="outside", marker_line_width=0)
    fig4.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                       xaxis=dict(showgrid=False, tickmode="linear", title=""),
                       yaxis=dict(showgrid=False, showticklabels=False, title=""))
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CITIES
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    cdf = df[df["city"] != "Other"]
    cdf_amt = cdf.dropna(subset=["amount"])

    # Bubble map
    st.markdown(section("Startup Funding Map — India"), unsafe_allow_html=True)
    city_stats = cdf_amt.groupby("city").agg(
        total_funding=("amount","sum"), deals=("amount","count")
    ).reset_index()
    city_stats["lat"] = city_stats["city"].map(lambda c: CITY_COORDS.get(c,(None,None))[0])
    city_stats["lon"] = city_stats["city"].map(lambda c: CITY_COORDS.get(c,(None,None))[1])
    city_stats["funding_label"] = city_stats["total_funding"].apply(fmt)
    city_stats = city_stats.dropna(subset=["lat"])

    fig_map = px.scatter_geo(
        city_stats, lat="lat", lon="lon",
        size="total_funding", color="deals",
        hover_name="city",
        hover_data={"deals":True,"funding_label":True,"lat":False,"lon":False,"total_funding":False},
        color_continuous_scale=[[0,"#C8C6FF"],[1,"#3D35CC"]],
        size_max=55, scope="asia",
        center=dict(lat=20, lon=78),
    )
    fig_map.update_geos(
        visible=True, resolution=50,
        showcountries=True, countrycolor="#DDD",
        showsubunits=True, subunitcolor="#EEE",
        showland=True, landcolor="#FAFAFA",
        showocean=True, oceancolor="#EEF2FF",
        lataxis_range=[8,37], lonaxis_range=[67,92]
    )
    fig_map.update_layout(paper_bgcolor="white", margin=dict(l=0,r=0,t=0,b=0), height=460,
                          coloraxis_colorbar=dict(title="Deals"))
    st.plotly_chart(fig_map, use_container_width=True)

    # City vs City
    st.markdown(section("City vs City Comparison"), unsafe_allow_html=True)
    top_cities = cdf["city"].value_counts().head(8).index.tolist()
    c1, c2 = st.columns(2)
    city_a = c1.selectbox("City A", top_cities, index=0, key="city_a")
    city_b = c2.selectbox("City B", top_cities, index=1, key="city_b")

    col1, col2 = st.columns(2)
    for city, col in [(city_a, col1), (city_b, col2)]:
        cd = cdf[cdf["city"] == city]
        cd_amt = cd.dropna(subset=["amount"])
        sb = cd["sector"].value_counts().head(7).reset_index()
        sb.columns = ["sector","deals"]
        with col:
            st.markdown(f"**{city}** &nbsp;·&nbsp; {len(cd):,} deals &nbsp;·&nbsp; {fmt(cd_amt['amount'].sum())}", unsafe_allow_html=True)
            fig = px.bar(sb, x="deals", y="sector", orientation="h",
                         color_discrete_sequence=[ACCENT])
            fig.update_layout(**base_fig(height=300, margin=dict(l=10,r=10,t=5,b=5)),
                              yaxis=dict(autorange="reversed", showgrid=False, title=""),
                              xaxis=dict(showgrid=False, title="deals"))
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

    # City deal trend
    st.markdown(section("Top Cities — Deal Volume Over Time"), unsafe_allow_html=True)
    cy = cdf[cdf["city"].isin(top_cities[:6])].groupby(["year","city"]).size().reset_index(name="deals")
    fig_ct = px.line(cy, x="year", y="deals", color="city", markers=True,
                     color_discrete_sequence=COLORS)
    fig_ct.update_traces(line=dict(width=2.5), marker=dict(size=7))
    fig_ct.update_layout(**base_fig(margin=dict(l=10,r=10,t=10,b=10)),
                         xaxis=dict(showgrid=False, tickmode="linear", title=""),
                         yaxis=dict(showgrid=False, title="Deals"),
                         legend=dict(orientation="h", y=-0.2, title=""))
    st.plotly_chart(fig_ct, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — INVESTORS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    inv_df = df.dropna(subset=["investors"]).copy()
    inv_df["investor_list"] = inv_df["investors"].str.split(",")
    inv_exp = inv_df.explode("investor_list")
    inv_exp["investor"] = inv_exp["investor_list"].str.strip()
    inv_exp = inv_exp[inv_exp["investor"].str.len() > 2]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(section("Top Investors by Deal Count"), unsafe_allow_html=True)
        top_inv = inv_exp["investor"].value_counts().head(15).reset_index()
        top_inv.columns = ["investor","deals"]
        fig = px.bar(top_inv, x="deals", y="investor", orientation="h",
                     color_discrete_sequence=[ACCENT], text="deals")
        fig.update_traces(textposition="outside", marker_line_width=0)
        fig.update_layout(**base_fig(height=480, margin=dict(l=10,r=40,t=10,b=10)),
                          yaxis=dict(autorange="reversed", showgrid=False, title=""),
                          xaxis=dict(showgrid=False, showticklabels=False, title=""))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(section("Top Investors by Funding Amount"), unsafe_allow_html=True)
        inv_amt = inv_exp.dropna(subset=["amount"])
        top_amt = inv_amt.groupby("investor")["amount"].sum().sort_values(ascending=False).head(15).reset_index()
        top_amt["label"] = top_amt["amount"].apply(fmt)
        fig2 = px.bar(top_amt, x="amount", y="investor", orientation="h",
                      color_discrete_sequence=["#A89CFF"], text="label")
        fig2.update_traces(textposition="outside", marker_line_width=0)
        fig2.update_layout(**base_fig(height=480, margin=dict(l=10,r=80,t=10,b=10)),
                           yaxis=dict(autorange="reversed", showgrid=False, title=""),
                           xaxis=dict(showgrid=False, showticklabels=False, title=""))
        st.plotly_chart(fig2, use_container_width=True)

    # Investor deep-dive
    st.markdown(section("Investor Deep-Dive"), unsafe_allow_html=True)
    top_inv_list = inv_exp["investor"].value_counts().head(40).index.tolist()
    sel_inv = st.selectbox("Select investor", top_inv_list, key="inv_sel")

    inv_data = inv_exp[inv_exp["investor"] == sel_inv]
    i1, i2, i3 = st.columns(3)
    i1.markdown(kpi("Total Deals", f"{len(inv_data):,}"), unsafe_allow_html=True)
    inv_data_amt = inv_data.dropna(subset=["amount"])
    i2.markdown(kpi("Total Deployed", fmt(inv_data_amt["amount"].sum()) if len(inv_data_amt) else "N/A"), unsafe_allow_html=True)
    i3.markdown(kpi("Avg Ticket Size", fmt(inv_data_amt["amount"].mean()) if len(inv_data_amt) else "N/A"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        sec_pref = inv_data["sector"].value_counts().reset_index()
        sec_pref.columns = ["sector","deals"]
        fig3 = px.pie(sec_pref, values="deals", names="sector",
                      color_discrete_sequence=COLORS, hole=0.45,
                      title="Sector Preference")
        fig3.update_traces(textposition="inside", textinfo="percent+label")
        fig3.update_layout(**base_fig(margin=dict(l=10,r=10,t=40,b=10)), showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        stg_pref = inv_data[~inv_data["stage"].isin(["Unknown","Other"])]["stage"].value_counts().reset_index()
        stg_pref.columns = ["stage","deals"]
        fig4 = px.bar(stg_pref, x="stage", y="deals", color_discrete_sequence=[ACCENT],
                      title="Stage Preference", text="deals")
        fig4.update_traces(textposition="outside", marker_line_width=0)
        fig4.update_layout(**base_fig(margin=dict(l=10,r=10,t=40,b=10)),
                           xaxis=dict(showgrid=False, title=""),
                           yaxis=dict(showgrid=False, showticklabels=False, title=""))
        st.plotly_chart(fig4, use_container_width=True)

    # Co-investment pairs
    st.markdown(section("Top Co-Investment Pairs"), unsafe_allow_html=True)
    pairs = get_coinvestment_pairs(df)
    top_pairs = pd.DataFrame(
        [(f"{a}  +  {b}", c) for (a,b),c in pairs.most_common(12)],
        columns=["pair","count"]
    )
    fig5 = px.bar(top_pairs, x="count", y="pair", orientation="h",
                  color_discrete_sequence=["#4ECDC4"], text="count")
    fig5.update_traces(textposition="outside", marker_line_width=0)
    fig5.update_layout(**base_fig(height=420, margin=dict(l=10,r=40,t=10,b=10)),
                       yaxis=dict(autorange="reversed", showgrid=False, title=""),
                       xaxis=dict(showgrid=False, showticklabels=False, title=""))
    st.plotly_chart(fig5, use_container_width=True)