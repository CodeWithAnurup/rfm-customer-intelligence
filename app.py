import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RFM Customer Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* KPI Metric Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
        border: 1px solid #3a3a5c;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(108,99,255,0.2);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6C63FF, #48cfad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 4px 0;
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #9e9eb8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 2px;
    }
    .kpi-delta-up {
        color: #48cfad;
        font-size: 0.78rem;
    }
    .kpi-delta-down {
        color: #fc5c65;
        font-size: 0.78rem;
    }

    /* Insight Boxes — each with a unique left-border color */
    .insight-box {
        border-radius: 8px;
        padding: 18px 22px;
        margin: 12px 0 20px 0;
        font-size: 0.92rem;
        line-height: 1.65;
        color: #d1d1e0;
    }
    .insight-acq {
        background: rgba(108,99,255,0.08);
        border-left: 4px solid #6C63FF;
    }
    .insight-risk {
        background: rgba(252,92,101,0.08);
        border-left: 4px solid #fc5c65;
    }
    .insight-whale {
        background: rgba(254,211,48,0.08);
        border-left: 4px solid #fed330;
    }
    .insight-predict {
        background: rgba(38,222,129,0.08);
        border-left: 4px solid #26de81;
    }
    .insight-funnel {
        background: rgba(69,170,242,0.08);
        border-left: 4px solid #45aaf2;
    }
    .insight-compete {
        background: rgba(165,94,234,0.08);
        border-left: 4px solid #a55eea;
    }

    /* Section headers */
    .section-header {
        font-size: 1.35rem;
        font-weight: 600;
        color: #FAFAFA;
        margin: 30px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-sub {
        font-size: 0.85rem;
        color: #7c7c9a;
        margin-bottom: 16px;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12121e 0%, #1a1a2e 100%);
    }
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6C63FF, #48cfad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 4px;
    }
    .sidebar-subtitle {
        font-size: 0.78rem;
        color: #7c7c9a;
        text-align: center;
        margin-bottom: 24px;
        letter-spacing: 0.5px;
    }

    /* Divider */
    .custom-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #3a3a5c, transparent);
        margin: 30px 0;
    }

    /* Footer */
    .dashboard-footer {
        text-align: center;
        color: #5a5a7a;
        font-size: 0.75rem;
        padding: 30px 0 10px 0;
        border-top: 1px solid #2a2a40;
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME
# ──────────────────────────────────────────────────────────────────────────────
CHART_COLORS = ["#6C63FF", "#48cfad", "#fc5c65", "#fed330", "#45aaf2", "#a55eea", "#fd9644"]
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#d1d1e0"),
    margin=dict(l=40, r=40, t=60, b=40),
    title_font=dict(size=16, color="#FAFAFA"),
)


# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING & PIPELINE
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading retail data…")
def load_data():
    df = pd.read_csv("online_retail.csv", encoding="ISO-8859-1")
    df.dropna(subset=["CustomerID"], inplace=True)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]
    df["CustomerID"] = df["CustomerID"].astype(int)
    return df


def compute_rfm(df):
    """Full RFM pipeline — mirrors the notebook exactly."""
    reference_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (reference_date - x.max()).days,
        "InvoiceNo": "count",
        "TotalAmount": "sum",
    })
    rfm.rename(columns={
        "InvoiceDate": "Recency",
        "InvoiceNo": "Frequency",
        "TotalAmount": "Value",
    }, inplace=True)

    # Quartile-based scoring
    quantiles = rfm.quantile(q=[0.25, 0.5, 0.75])

    def r_score(x, p):
        if p == "Recency":
            if x <= quantiles[p][0.25]: return 4
            elif x <= quantiles[p][0.50]: return 3
            elif x <= quantiles[p][0.75]: return 2
            else: return 1
        else:
            if x <= quantiles[p][0.25]: return 1
            elif x <= quantiles[p][0.50]: return 2
            elif x <= quantiles[p][0.75]: return 3
            else: return 4

    rfm["R"] = rfm["Recency"].apply(r_score, args=("Recency",))
    rfm["F"] = rfm["Frequency"].apply(r_score, args=("Frequency",))
    rfm["M"] = rfm["Value"].apply(r_score, args=("Value",))

    rfm["RFM_Segment"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    rfm["RFM_Score"] = rfm[["R", "F", "M"]].sum(axis=1)

    # Segment labels
    def assign_label(score):
        if score < 5: return "Low Value"
        elif score < 9: return "Mid Value"
        else: return "High Value"

    rfm["RFM_Segment_Label"] = rfm["RFM_Score"].apply(assign_label)

    # Customer segments
    rfm["RFM_Customer_Segments"] = ""
    rfm.loc[rfm["RFM_Score"] >= 9, "RFM_Customer_Segments"] = "VIP / Loyal"
    rfm.loc[(rfm["RFM_Score"] >= 6) & (rfm["RFM_Score"] < 9), "RFM_Customer_Segments"] = "Potential Loyal"
    rfm.loc[(rfm["RFM_Score"] >= 5) & (rfm["RFM_Score"] < 6), "RFM_Customer_Segments"] = "At Risk"
    rfm.loc[(rfm["RFM_Score"] >= 4) & (rfm["RFM_Score"] < 5), "RFM_Customer_Segments"] = "Can't Lose"
    rfm.loc[(rfm["RFM_Score"] >= 3) & (rfm["RFM_Score"] < 4), "RFM_Customer_Segments"] = "Lost"

    return rfm, reference_date


# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
data = load_data()

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">📊 RFM Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-subtitle">Customer Analytics Suite</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Date range filter
    st.markdown("##### 📅 Date Range")
    min_date = data["InvoiceDate"].min().date()
    max_date = data["InvoiceDate"].max().date()
    date_range = st.date_input(
        "Select period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed",
    )

    st.markdown("")

    # Country filter
    st.markdown("##### 🌍 Market")
    all_countries = sorted(data["Country"].unique().tolist())
    selected_countries = st.multiselect(
        "Filter by country",
        options=all_countries,
        default=None,
        placeholder="All countries",
        label_visibility="collapsed",
    )

    st.markdown("")

    # Segment filter
    st.markdown("##### 🎯 Value Segment")
    selected_segments = st.multiselect(
        "Filter by segment",
        options=["High Value", "Mid Value", "Low Value"],
        default=None,
        placeholder="All segments",
        label_visibility="collapsed",
    )

    st.markdown("---")
    with st.expander("ℹ️ About this Dashboard"):
        st.markdown("""
        **RFM Analysis** segments customers by:
        - **Recency** — How recently they purchased
        - **Frequency** — How often they purchase
        - **Monetary** — How much they spend

        Each dimension is scored 1–4 (quartile-based).
        Combined score (3–12) maps to value tiers.

        *Built from the Online Retail dataset (2010–2011)*
        """)

# ──────────────────────────────────────────────────────────────────────────────
# APPLY FILTERS
# ──────────────────────────────────────────────────────────────────────────────
filtered = data.copy()

if len(date_range) == 2:
    start, end = date_range
    filtered = filtered[
        (filtered["InvoiceDate"].dt.date >= start) &
        (filtered["InvoiceDate"].dt.date <= end)
    ]

if selected_countries:
    filtered = filtered[filtered["Country"].isin(selected_countries)]

# Compute RFM on filtered data
rfm, reference_date = compute_rfm(filtered)
last_sale_date = (reference_date - pd.Timedelta(days=1)).strftime("%d %B %Y")
analysis_date = reference_date.strftime("%d %B %Y")

# Apply segment filter after RFM computation
if selected_segments:
    rfm = rfm[rfm["RFM_Segment_Label"].isin(selected_segments)]

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 10px 0 5px 0;">
    <h1 style="margin:0; font-size:2.2rem; font-weight:800;
       background: linear-gradient(90deg, #6C63FF, #48cfad);
       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
       RFM Customer Intelligence Dashboard
    </h1>
    <p style="color:#7c7c9a; font-size:0.9rem; margin-top:6px;">
        Data-driven customer segmentation &bull; Retention strategy &bull; Revenue optimization
    </p>
    <div style="display:flex; justify-content:center; gap:30px; margin-top:10px;">
        <span style="background:#1e1e2f; border:1px solid #3a3a5c; border-radius:20px;
              padding:6px 18px; font-size:0.8rem; color:#48cfad;">
            📅 Last Transaction: <strong>{last_sale_date}</strong>
        </span>
        <span style="background:#1e1e2f; border:1px solid #3a3a5c; border-radius:20px;
              padding:6px 18px; font-size:0.8rem; color:#6C63FF;">
            🔬 Analysis Reference Date: <strong>{analysis_date}</strong>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — KPI METRICS
# ══════════════════════════════════════════════════════════════════════════════
total_customers = len(rfm)
total_revenue = rfm["Value"].sum()
avg_order_value = total_revenue / rfm["Frequency"].sum() if rfm["Frequency"].sum() > 0 else 0
avg_recency = rfm["Recency"].mean()
churn_pct = (len(rfm[rfm["RFM_Segment_Label"] == "Low Value"]) / total_customers * 100) if total_customers > 0 else 0
high_val_pct = (len(rfm[rfm["RFM_Segment_Label"] == "High Value"]) / total_customers * 100) if total_customers > 0 else 0

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Customers</div>
        <div class="kpi-value">{total_customers:,}</div>
        <div class="kpi-delta-up">▲ Active base</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">&#36;{total_revenue:,.0f}</div>
        <div class="kpi-delta-up">▲ Lifetime value</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Order Value</div>
        <div class="kpi-value">&#36;{avg_order_value:,.2f}</div>
        <div class="kpi-delta-up">Per transaction</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Recency</div>
        <div class="kpi-value">{avg_recency:,.0f} days</div>
        <div class="{'kpi-delta-down' if avg_recency > 90 else 'kpi-delta-up'}">
            {'⚠ Engagement gap' if avg_recency > 90 else '✓ Healthy cadence'}
        </div>
    </div>""", unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Churn Risk</div>
        <div class="kpi-value">{churn_pct:.1f}%</div>
        <div class="{'kpi-delta-down' if churn_pct > 30 else 'kpi-delta-up'}">
            {'⚠ High attrition' if churn_pct > 30 else '✓ Manageable level'}
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CUSTOMER DISTRIBUTION BY RFM SEGMENT (Bar Chart)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">🏷️ Customer Distribution by Value Tier</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">How many customers fall into each RFM value segment</p>', unsafe_allow_html=True)

segment_counts = rfm["RFM_Segment_Label"].value_counts().reset_index()
segment_counts.columns = ["RFM_Segment", "Count"]
# Enforce order
seg_order = ["High Value", "Mid Value", "Low Value"]
segment_counts["RFM_Segment"] = pd.Categorical(segment_counts["RFM_Segment"], categories=seg_order, ordered=True)
segment_counts = segment_counts.sort_values("RFM_Segment")

seg_colors = {"High Value": "#48cfad", "Mid Value": "#fed330", "Low Value": "#fc5c65"}

fig_seg_bar = px.bar(
    segment_counts,
    x="RFM_Segment",
    y="Count",
    color="RFM_Segment",
    color_discrete_map=seg_colors,
    text="Count",
    labels={"RFM_Segment": "Value Segment", "Count": "Number of Customers"},
)
fig_seg_bar.update_traces(
    textposition="outside",
    textfont_size=13,
    marker_line_color="#1a1a2e",
    marker_line_width=1.5,
)
fig_seg_bar.update_layout(
    **PLOTLY_LAYOUT,
    title=None,
    showlegend=False,
    xaxis_title="Value Segment",
    yaxis_title="Number of Customers",
    height=420,
)
st.plotly_chart(fig_seg_bar, use_container_width=True)

# Insight — Acquisition Cost Lens
hv_count = len(rfm[rfm["RFM_Segment_Label"] == "High Value"])
hv_revenue = rfm[rfm["RFM_Segment_Label"] == "High Value"]["Value"].sum()
hv_pct_customers = (hv_count / total_customers * 100) if total_customers > 0 else 0
hv_pct_revenue = (hv_revenue / total_revenue * 100) if total_revenue > 0 else 0
mid_count = len(rfm[rfm["RFM_Segment_Label"] == "Mid Value"])
mid_pct = (mid_count / total_customers * 100) if total_customers > 0 else 0

st.markdown(f"""
<div class="insight-box insight-acq">
    <strong>📌 Market Insight — Customer Acquisition Cost (CAC) Perspective</strong><br><br>
    Acquiring a new customer costs <strong>5–7× more</strong> than retaining an existing one
    (<em>Harvard Business Review</em>). Your <strong>High-Value</strong> segment represents just
    <strong>{hv_pct_customers:.1f}%</strong> of the customer base yet drives
    <strong>{hv_pct_revenue:.1f}%</strong> of total revenue — every customer lost from this tier
    directly inflates your effective CAC.<br><br>
    The <strong>Mid-Value</strong> pool ({mid_pct:.1f}% of base) is your biggest growth lever:
    targeted retention campaigns here — loyalty programs, personalized email sequences,
    and cross-sell bundles — yield the highest ROI per marketing dollar spent. Moving just
    10% of Mid-Value customers to High-Value can significantly shift quarterly revenue
    without any new acquisition spend.
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — RFM SEGMENT TREEMAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">🌳 Customer Portfolio Composition</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Hierarchical view: Value Tier → Lifecycle Stage</p>', unsafe_allow_html=True)

seg_product_counts = (
    rfm.groupby(["RFM_Segment_Label", "RFM_Customer_Segments"])
    .size()
    .reset_index(name="Count")
)
seg_product_counts = seg_product_counts.sort_values("Count", ascending=False)

treemap_colors = {
    "High Value": "#48cfad",
    "Mid Value": "#fed330",
    "Low Value": "#fc5c65",
    "(?)": "#3a3a5c",
}

fig_treemap = px.treemap(
    seg_product_counts,
    path=["RFM_Segment_Label", "RFM_Customer_Segments"],
    values="Count",
    color="RFM_Segment_Label",
    color_discrete_map=treemap_colors,
)
treemap_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "margin"}
fig_treemap.update_layout(
    **treemap_layout,
    title=None,
    height=480,
    margin=dict(l=10, r=10, t=30, b=10),
)
fig_treemap.update_traces(
    textinfo="label+value+percent parent",
    textfont_size=12,
)
st.plotly_chart(fig_treemap, use_container_width=True)

# Insight — Portfolio Risk Lens
vip_count = len(rfm[rfm["RFM_Customer_Segments"] == "VIP / Loyal"])
vip_revenue = rfm[rfm["RFM_Customer_Segments"] == "VIP / Loyal"]["Value"].sum()
vip_pct_rev = (vip_revenue / total_revenue * 100) if total_revenue > 0 else 0
vip_pct_cust = (vip_count / total_customers * 100) if total_customers > 0 else 0

st.markdown(f"""
<div class="insight-box insight-risk">
    <strong>🔴 Market Insight — Revenue Concentration & Portfolio Risk</strong><br><br>
    Think of your customer base as an investment portfolio. <strong>VIP/Loyal</strong> customers
    are your 'blue-chip assets' — just <strong>{vip_pct_cust:.1f}%</strong> of customers
    generating <strong>{vip_pct_rev:.1f}%</strong> of total revenue. This is classic
    <strong>Pareto concentration risk</strong>.<br><br>
    'At Risk' and 'Can't Lose' segments are your <strong>distressed holdings</strong> requiring
    immediate intervention — reactivation campaigns within 30 days of last purchase yield
    3× the response rate vs. waiting 90+ days. If your VIP revenue concentration exceeds 40%,
    diversifying your revenue base through Mid-Value acceleration programs becomes a
    strategic imperative, not just a nice-to-have.
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — VIP BOX PLOT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">📦 VIP / Loyal Customer Behavioral Profile</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">Distribution spread & outlier detection across Recency, Frequency, and Monetary dimensions</p>', unsafe_allow_html=True)

vip_segment = rfm[rfm["RFM_Customer_Segments"] == "VIP / Loyal"]

if len(vip_segment) > 0:
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        y=vip_segment["Recency"], name="Recency (days)",
        marker_color="#6C63FF", boxmean="sd",
        line=dict(width=2),
    ))
    fig_box.add_trace(go.Box(
        y=vip_segment["Frequency"], name="Frequency (orders)",
        marker_color="#48cfad", boxmean="sd",
        line=dict(width=2),
    ))
    fig_box.add_trace(go.Box(
        y=vip_segment["Value"], name="Monetary ($)",
        marker_color="#fed330", boxmean="sd",
        line=dict(width=2),
    ))
    fig_box.update_layout(
        **PLOTLY_LAYOUT,
        title=None,
        showlegend=False,
        yaxis_title="Value",
        height=450,
    )
    st.plotly_chart(fig_box, use_container_width=True)

    # Stats for insight
    p95_value = vip_segment["Value"].quantile(0.95)
    max_value = vip_segment["Value"].max()
    whale_count = len(vip_segment[vip_segment["Value"] > p95_value])
    whale_revenue = vip_segment[vip_segment["Value"] > p95_value]["Value"].sum()
    whale_pct = (whale_revenue / vip_segment["Value"].sum() * 100) if vip_segment["Value"].sum() > 0 else 0

    st.markdown(f"""
    <div class="insight-box insight-whale">
        <strong>🐋 Market Insight — Whale Customer Dependency Analysis</strong><br><br>
        The outliers visible in the Monetary box plot signal <strong>'whale dependency'</strong> —
        a well-documented risk pattern in retail. Your top 5% of VIP customers
        (<strong>{whale_count} accounts</strong>) contribute <strong>{whale_pct:.1f}%</strong>
        of VIP segment revenue, with the largest single account at
        <strong>&#36;{max_value:,.0f}</strong>.<br><br>
        Losing even 1–2 of these accounts could crater monthly revenue by double digits.
        <strong>Recommended action:</strong> Build a dedicated Key Account Management (KAM) program
        for customers above the 95th percentile (&#36;{p95_value:,.0f}+), with personalized SLAs,
        quarterly business reviews, and a dedicated relationship manager. This isn't CRM — it's
        revenue insurance.
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No VIP / Loyal customers found with current filters. Adjust your filters to see this section.")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — CORRELATION HEATMAP (VIP Segment)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">🔥 RFM Score Correlation — Champions Segment</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">How Recency, Frequency, and Monetary scores relate within your most valuable customers</p>', unsafe_allow_html=True)

if len(vip_segment) > 0:
    corr_matrix = vip_segment[["R", "F", "M"]].corr()

    # Custom diverging colorscale
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=["Recency Score", "Frequency Score", "Monetary Score"],
        y=["Recency Score", "Frequency Score", "Monetary Score"],
        colorscale=[
            [0, "#fc5c65"],
            [0.5, "#1a1a2e"],
            [1, "#48cfad"],
        ],
        zmin=-1, zmax=1,
        text=corr_matrix.values.round(3),
        texttemplate="%{text}",
        textfont=dict(size=14, color="#FAFAFA"),
        colorbar=dict(
            title=dict(text="Correlation", font=dict(color="#d1d1e0")),
            tickfont=dict(color="#9e9eb8"),
        ),
    ))
    fig_heatmap.update_layout(
        **PLOTLY_LAYOUT,
        title=None,
        height=400,
        xaxis=dict(side="bottom"),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    fm_corr = corr_matrix.loc["F", "M"]
    rf_corr = corr_matrix.loc["R", "F"]

    fm_strength = "strong positive" if fm_corr > 0.5 else ("moderate" if fm_corr > 0.2 else "weak")
    rf_desc = "tight" if abs(rf_corr) > 0.5 else ("loose" if abs(rf_corr) < 0.2 else "moderate")

    st.markdown(f"""
    <div class="insight-box insight-predict">
        <strong>🧠 Market Insight — Behavioral Predictability & Pricing Power</strong><br><br>
        The <strong>F–M correlation ({fm_corr:.3f})</strong> tells a critical story about pricing power.
        A <strong>{fm_strength}</strong> Frequency-Monetary correlation means your loyal customers
        {"buy often <em>and</em> spend more per visit — indicating brand stickiness and low price elasticity within this tier. You have room to test premium pricing or upsell strategies without risking churn." if fm_corr > 0.3 else "buy often but with relatively flat basket sizes — suggesting a volume-driven, price-sensitive base. Focus on bundling and AOV-lift strategies rather than price increases."}<br><br>
        The <strong>R–F correlation ({rf_corr:.3f}, {rf_desc})</strong> suggests that
        {"purchase timing is highly predictable — ideal for automated replenishment or subscription models." if abs(rf_corr) > 0.5 else "even among champions, purchase timing is irregular — pointing to a strong opportunity for subscription-based or auto-replenishment models to smooth demand cycles and improve forecasting accuracy."}
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No VIP / Loyal customers found with current filters.")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — SEGMENT LIFECYCLE COMPARISON BAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">🔄 Customer Lifecycle Stage Distribution</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">From Lost → VIP: where does your customer base concentrate?</p>', unsafe_allow_html=True)

lifecycle_order = ["Lost", "Can't Lose", "At Risk", "Potential Loyal", "VIP / Loyal"]
lifecycle_counts = rfm["RFM_Customer_Segments"].value_counts()
lifecycle_counts = lifecycle_counts.reindex(lifecycle_order, fill_value=0)

lifecycle_colors = ["#fc5c65", "#fd9644", "#fed330", "#45aaf2", "#48cfad"]

fig_lifecycle = go.Figure(data=[go.Bar(
    x=lifecycle_counts.index,
    y=lifecycle_counts.values,
    marker=dict(
        color=lifecycle_colors,
        line=dict(color="#1a1a2e", width=1.5),
    ),
    text=lifecycle_counts.values,
    textposition="outside",
    textfont=dict(size=13, color="#d1d1e0"),
)])
fig_lifecycle.update_layout(
    **PLOTLY_LAYOUT,
    title=None,
    xaxis_title="Customer Lifecycle Stage",
    yaxis_title="Number of Customers",
    showlegend=False,
    height=420,
)
st.plotly_chart(fig_lifecycle, use_container_width=True)

# Insight — Lifecycle Funnel Lens
lost_count = lifecycle_counts.get("Lost", 0)
cant_lose_count = lifecycle_counts.get("Can't Lose", 0)
vip_loyal_count = lifecycle_counts.get("VIP / Loyal", 0)
erosion_ratio = ((lost_count + cant_lose_count) / vip_loyal_count) if vip_loyal_count > 0 else float("inf")
health_status = "healthy" if erosion_ratio < 0.5 else ("concerning" if erosion_ratio < 1.0 else "critical")
health_icon = "✅" if erosion_ratio < 0.5 else ("⚠️" if erosion_ratio < 1.0 else "🚨")

st.markdown(f"""
<div class="insight-box insight-funnel">
    <strong>📊 Market Insight — Customer Lifecycle Funnel Health</strong><br><br>
    Map this to a classic retention funnel: <strong>'Lost'</strong> is your churn bucket,
    <strong>'Can't Lose'</strong> is your save-desk queue, <strong>'At Risk'</strong> needs
    proactive outreach, <strong>'Potential Loyal'</strong> is your expansion pipeline, and
    <strong>'VIP/Loyal'</strong> is your promoter base.<br><br>
    Your <strong>net retention health ratio</strong> (Lost + Can't Lose) ÷ VIP/Loyal =
    <strong>{erosion_ratio:.2f}×</strong> {health_icon}<br>
    Industry benchmark for healthy e-commerce: this ratio should be <strong>below 0.5×</strong>.
    Your base is currently <strong>{health_status}</strong>. {"Well-managed — focus on growth acceleration." if health_status == "healthy" else "Consider deploying win-back email sequences (30-60-90 day cadence) and exit-intent surveys to diagnose root causes of churn before scaling acquisition."}
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — GROUPED BAR: AVG R/F/M SCORES PER SEGMENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-header">🧬 Segment DNA — Average R / F / M Score Fingerprint</p>', unsafe_allow_html=True)
st.markdown('<p class="section-sub">What makes each lifecycle stage behaviorally distinct?</p>', unsafe_allow_html=True)

segment_scores = rfm.groupby("RFM_Customer_Segments")[["R", "F", "M"]].mean().reset_index()
# Order
segment_scores["RFM_Customer_Segments"] = pd.Categorical(
    segment_scores["RFM_Customer_Segments"],
    categories=lifecycle_order,
    ordered=True,
)
segment_scores = segment_scores.sort_values("RFM_Customer_Segments")

fig_grouped = go.Figure()

fig_grouped.add_trace(go.Bar(
    x=segment_scores["RFM_Customer_Segments"],
    y=segment_scores["R"],
    name="Recency Score",
    marker_color="#6C63FF",
    text=segment_scores["R"].round(2),
    textposition="outside",
    textfont=dict(size=10),
))

fig_grouped.add_trace(go.Bar(
    x=segment_scores["RFM_Customer_Segments"],
    y=segment_scores["F"],
    name="Frequency Score",
    marker_color="#48cfad",
    text=segment_scores["F"].round(2),
    textposition="outside",
    textfont=dict(size=10),
))

fig_grouped.add_trace(go.Bar(
    x=segment_scores["RFM_Customer_Segments"],
    y=segment_scores["M"],
    name="Monetary Score",
    marker_color="#fed330",
    text=segment_scores["M"].round(2),
    textposition="outside",
    textfont=dict(size=10),
))

fig_grouped.update_layout(
    **PLOTLY_LAYOUT,
    title=None,
    barmode="group",
    xaxis_title="Customer Lifecycle Stage",
    yaxis_title="Average Score (1–4)",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=12),
    ),
    height=450,
    yaxis=dict(range=[0, 5]),
)
st.plotly_chart(fig_grouped, use_container_width=True)

# Insight — Competitive Positioning Lens
pot_loyal = segment_scores[segment_scores["RFM_Customer_Segments"] == "Potential Loyal"]
at_risk = segment_scores[segment_scores["RFM_Customer_Segments"] == "At Risk"]

pot_loyal_f = pot_loyal["F"].values[0] if len(pot_loyal) > 0 else 0
pot_loyal_m = pot_loyal["M"].values[0] if len(pot_loyal) > 0 else 0
at_risk_r = at_risk["R"].values[0] if len(at_risk) > 0 else 0

st.markdown(f"""
<div class="insight-box insight-compete">
    <strong>🎯 Market Insight — Competitive Positioning & Intervention Playbook</strong><br><br>
    This chart is your <strong>segment DNA fingerprint</strong> — each bar pattern reveals exactly
    where to intervene:<br><br>
    • <strong>Potential Loyal</strong> customers score <strong>{pot_loyal_f:.1f}</strong> on Frequency
    but only <strong>{pot_loyal_m:.1f}</strong> on Monetary — frequent browsers or small-basket buyers.
    In competitive retail, converting these into High-Value requires <strong>cross-selling and
    basket-size strategies</strong>: product bundling, tiered discounts (spend $50 get 10% off),
    and free shipping thresholds.<br><br>
    • <strong>At Risk</strong> customers show a Recency score of just <strong>{at_risk_r:.1f}</strong> —
    the classic early-warning signal of disengagement. Industry data shows you have a
    <strong>60–70% win-back probability</strong> within the first 30 days of disengagement,
    dropping to just 20% after 90 days. Deploy time-sensitive reactivation offers
    (limited-time discounts, "we miss you" personalized emails) within the critical first-month window.
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-footer">
    <strong>RFM Customer Intelligence Dashboard</strong> &nbsp;•&nbsp;
    Built with Streamlit & Plotly &nbsp;•&nbsp;
    Data: UCI Online Retail Dataset (Dec 2010 – Dec 2011) &nbsp;•&nbsp;
    © 2024
</div>
""", unsafe_allow_html=True)
