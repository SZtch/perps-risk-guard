# ============================================================
#  PERPS RISK GUARD
#  Phase 4 — Plotly Charts + Enhanced Analytics
#  Pacifica Hackathon | Analytics & Data Track
# ============================================================

import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page Configuration ───────────────────────────────────────
st.set_page_config(
    page_title="Perps Risk Guard",
    page_icon="⚡",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root Variables ─────────────────────────────── */
:root {
    --bg-base:      #080b12;
    --bg-surface:   #0f1420;
    --bg-card:      #141926;
    --bg-input:     #1a2035;
    --border:       #232a3d;
    --border-glow:  #00e5b050;
    --accent:       #00e5b0;
    --accent-dim:   #00e5b020;
    --accent-amber: #f59e0b;
    --accent-red:   #ef4444;
    --accent-blue:  #3b82f6;
    --text-primary: #e8edf5;
    --text-muted:   #6b7a99;
    --text-dim:     #3d4a66;
    --green:        #00e5b0;
    --amber:        #f59e0b;
    --red:          #ef4444;
    --radius:       10px;
    --radius-lg:    16px;
}

/* ── Global Reset ───────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}

.stApp {
    background-color: var(--bg-base) !important;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% -10%, #00e5b015 0%, transparent 60%),
        linear-gradient(180deg, #080b12 0%, #080b12 100%);
}

/* ── Main container ─────────────────────────────── */
.block-container {
    max-width: 1280px !important;
    padding: 2rem 2rem 4rem !important;
}

/* ── Header / Title ─────────────────────────────── */
h1 {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1.6rem, 4vw, 2.4rem) !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
}

h1 span.accent { color: var(--accent); }

h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em !important;
}

/* ── Subheader ──────────────────────────────────── */
.stMarkdown h3 {
    font-size: 1rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--text-muted) !important;
    margin-bottom: 0.5rem !important;
}

/* ── Tabs ───────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 2px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 7px !important;
    padding: 8px 18px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.2s ease !important;
    border: none !important;
}

.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 0 12px var(--accent-dim) !important;
}

.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem !important;
}

/* ── Metrics ────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem 1.2rem !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 16px var(--accent-dim) !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Mono', monospace !important;
    font-size: clamp(1rem, 2.5vw, 1.35rem) !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
}

/* ── Inputs ─────────────────────────────────────── */
.stTextInput input,
.stNumberInput input,
.stSelectbox select,
[data-baseweb="input"] input,
[data-baseweb="select"] {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
    outline: none !important;
}

/* ── Labels ─────────────────────────────────────── */
label, .stSelectbox label, .stNumberInput label, .stTextInput label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--text-muted) !important;
    margin-bottom: 4px !important;
}

/* ── Buttons ────────────────────────────────────── */
.stButton > button {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    box-shadow: 0 0 16px var(--accent-dim) !important;
    transform: translateY(-1px) !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #080b12 !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
}

.stButton > button[kind="primary"]:hover {
    background: #00ffcc !important;
    color: #080b12 !important;
    box-shadow: 0 0 24px #00e5b055 !important;
    transform: translateY(-1px) !important;
}

/* ── Radio ──────────────────────────────────────── */
.stRadio [data-baseweb="radio"] {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 6px 14px !important;
    margin-right: 6px !important;
    transition: all 0.2s ease !important;
}

/* ── Alerts ─────────────────────────────────────── */
.stSuccess, [data-baseweb="notification"][kind="positive"] {
    background: #00e5b012 !important;
    border: 1px solid #00e5b040 !important;
    border-radius: var(--radius) !important;
    color: var(--green) !important;
}

.stWarning, [data-baseweb="notification"][kind="warning"] {
    background: #f59e0b12 !important;
    border: 1px solid #f59e0b40 !important;
    border-radius: var(--radius) !important;
    color: var(--amber) !important;
}

.stError, [data-baseweb="notification"][kind="negative"] {
    background: #ef444412 !important;
    border: 1px solid #ef444440 !important;
    border-radius: var(--radius) !important;
    color: var(--red) !important;
}

.stInfo, [data-baseweb="notification"][kind="info"] {
    background: #3b82f612 !important;
    border: 1px solid #3b82f640 !important;
    border-radius: var(--radius) !important;
    color: var(--accent-blue) !important;
}

/* ── Dataframe / Table ──────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] table {
    background: var(--bg-card) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--bg-surface) !important;
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    font-weight: 600 !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 10px 14px !important;
}

[data-testid="stDataFrame"] td {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 8px 14px !important;
}

[data-testid="stDataFrame"] tr:hover td {
    background: var(--bg-input) !important;
}

/* ── Divider ────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Caption / small text ───────────────────────── */
.stCaption, small, caption {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
}

/* ── Selectbox dropdown ─────────────────────────── */
[data-baseweb="popover"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

[data-baseweb="menu"] {
    background: var(--bg-card) !important;
}

[data-baseweb="menu"] li:hover {
    background: var(--bg-input) !important;
}

/* ── Spinner ────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--accent) !important;
}

/* ── Scrollbar ──────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ── Responsive: mobile ─────────────────────────── */
@media (max-width: 768px) {
    .block-container { padding: 1rem 1rem 3rem !important; }
    h1 { font-size: 1.5rem !important; }
    [data-testid="stMetricValue"] { font-size: 1rem !important; }
    .stTabs [data-baseweb="tab"] { padding: 6px 10px !important; font-size: 0.78rem !important; }
}

/* ── Header badge pill ──────────────────────────── */
.header-badge {
    display: inline-block;
    background: var(--accent-dim);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 3px 10px;
    border-radius: 20px;
    margin-left: 10px;
    vertical-align: middle;
}

/* ── Stat card for custom HTML blocks ───────────── */
.stat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    transition: border-color 0.2s ease;
}

.stat-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 16px var(--accent-dim);
}

.stat-label {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    font-weight: 600;
    margin-bottom: 4px;
}

.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
}

.stat-value.green { color: var(--green); }
.stat-value.red   { color: var(--red); }
.stat-value.amber { color: var(--amber); }
</style>
""", unsafe_allow_html=True)

# ── Constants ────────────────────────────────────────────────
PACIFICA_BASE_URL = "https://api.pacifica.fi/api/v1"
PRICES_ENDPOINT   = f"{PACIFICA_BASE_URL}/info/prices"
MARKETS_ENDPOINT  = f"{PACIFICA_BASE_URL}/info/markets"

# ── Session State ────────────────────────────────────────────
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []
if "trade_counter" not in st.session_state:
    st.session_state.trade_counter = 0
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "portfolio_counter" not in st.session_state:
    st.session_state.portfolio_counter = 0


# ── Helper: Fetch Live Prices ─────────────────────────────────
def fetch_prices():
    try:
        response = requests.get(PRICES_ENDPOINT, timeout=5)
        data     = response.json()
        if data.get("success") and data.get("data"):
            return {
                item["symbol"]: float(item["mark"])
                for item in data["data"]
                if "symbol" in item and "mark" in item
            }
    except Exception:
        pass
    return {}


# ── Helper: Fetch Market Info ─────────────────────────────────
def fetch_markets():
    try:
        response = requests.get(MARKETS_ENDPOINT, timeout=5)
        data     = response.json()
        if data.get("success") and data.get("data"):
            return {
                item["symbol"]: item
                for item in data["data"]
                if "symbol" in item
            }
    except Exception:
        pass
    return {}


# ── Global Plotly Theme ───────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="#141926",
    plot_bgcolor="#0f1420",
    font=dict(family="DM Sans, sans-serif", color="#6b7a99", size=12),
    margin=dict(t=48, b=24, l=16, r=16),
    xaxis=dict(gridcolor="#232a3d", linecolor="#232a3d", tickfont=dict(size=11, color="#6b7a99")),
    yaxis=dict(gridcolor="#232a3d", linecolor="#232a3d", tickfont=dict(size=11, color="#6b7a99")),
)

def apply_theme(fig, height=320, title="", extra=None):
    layout = {**PLOT_THEME, "height": height}
    if title:
        layout["title"] = dict(text=title, font=dict(size=13, color="#e8edf5", family="DM Sans, sans-serif"), x=0, xanchor="left")
    if extra:
        layout.update(extra)
    fig.update_layout(**layout)
    return fig


# ── Plotly: Risk Gauge ────────────────────────────────────────
def make_risk_gauge(risk_pct):
    color = "#00e5b0" if risk_pct < 5 else ("#f59e0b" if risk_pct <= 15 else "#ef4444")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_pct,
        number={"suffix": "%", "font": {"size": 38, "color": color, "family": "Space Mono"}},
        delta={"reference": 5, "increasing": {"color": "#ef4444"}, "decreasing": {"color": "#00e5b0"}},
        gauge={
            "axis": {"range": [0, 30], "tickwidth": 1, "tickcolor": "#3d4a66", "tickfont": {"color": "#6b7a99"}},
            "bar": {"color": color, "thickness": 0.6},
            "bgcolor": "#0f1420",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  5],  "color": "#00e5b010"},
                {"range": [5,  15], "color": "#f59e0b10"},
                {"range": [15, 30], "color": "#ef444410"},
            ],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.75, "value": risk_pct}
        },
        title={"text": "Risk % of Balance", "font": {"size": 13, "color": "#6b7a99", "family": "DM Sans"}}
    ))
    apply_theme(fig, height=260)
    fig.update_layout(margin=dict(t=50, b=10, l=30, r=30))
    return fig


# ── Plotly: Price Level Chart ─────────────────────────────────
def make_price_levels(entry, sl, tp, liq, symbol, is_long):
    levels = {"Take Profit": tp, "Entry": entry, "Stop Loss": sl, "Liquidation": liq}
    colors = {"Take Profit": "#00e5b0", "Entry": "#3b82f6", "Stop Loss": "#f59e0b", "Liquidation": "#ef4444"}
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
    labels = [l[0] for l in sorted_levels]
    prices = [l[1] for l in sorted_levels]
    clrs   = [colors[l[0]] for l in sorted_levels]

    fig = go.Figure()

    if is_long:
        fig.add_hrect(y0=entry, y1=tp,  fillcolor="#00e5b0", opacity=0.06, line_width=0)
        fig.add_hrect(y0=liq,   y1=entry, fillcolor="#ef4444", opacity=0.06, line_width=0)

    for label, price, clr in zip(labels, prices, clrs):
        fig.add_hline(
            y=price, line_dash="dash", line_color=clr, line_width=1.2,
            annotation_text=f"  {label}: ${price:,.2f}",
            annotation_position="right",
            annotation_font_color=clr,
            annotation_font_size=11,
        )

    fig.add_trace(go.Scatter(
        x=[""] * len(prices), y=prices, mode="markers",
        marker=dict(size=10, color=clrs, symbol="diamond"),
        text=labels,
        hovertemplate="<b>%{text}</b><br>$%{y:,.4f}<extra></extra>"
    ))

    apply_theme(fig, height=320, title=f"{symbol} — Key Price Levels",
                extra=dict(
                    xaxis=dict(showticklabels=False, showgrid=False),
                    yaxis=dict(gridcolor="#232a3d", title="Price ($)"),
                    showlegend=False,
                    margin=dict(t=48, b=20, l=16, r=120)
                ))
    return fig


# ── Plotly: Adverse Move Waterfall ────────────────────────────
def make_adverse_waterfall(balance, position_size, entry_price, is_long, leverage):
    moves    = list(range(1, 11))
    losses   = [(pct / 100) * position_size for pct in moves]
    balances = [balance - l for l in losses]
    liq_pct  = 100 / leverage

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=[f"-{p}%" for p in moves],
        y=losses,
        name="Estimated Loss ($)",
        marker_color=["#ef4444" if b > 0 else "#7f1d1d" for b in balances],
        hovertemplate="Move: %{x}<br>Loss: $%{y:,.2f}<extra></extra>"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=[f"-{p}%" for p in moves],
        y=balances,
        name="Remaining Balance ($)",
        mode="lines+markers",
        line=dict(color="#3b82f6", width=2),
        marker=dict(size=6, color="#3b82f6"),
        hovertemplate="Move: %{x}<br>Balance: $%{y:,.2f}<extra></extra>"
    ), secondary_y=True)

    if liq_pct <= 10:
        fig.add_vline(
            x=f"-{int(liq_pct)}%", line_dash="dot", line_color="#ef4444",
            annotation_text="⚡ Liq.", annotation_font_color="#ef4444", annotation_font_size=11
        )

    apply_theme(fig, height=320, title="Adverse Move Simulation (1%–10%)",
                extra=dict(
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                                font=dict(size=11, color="#6b7a99")),
                    yaxis=dict(gridcolor="#232a3d", title="Loss ($)"),
                    yaxis2=dict(title="Balance ($)", overlaying="y", side="right", gridcolor="#232a3d"),
                    hovermode="x unified"
                ))
    return fig


# ── Plotly: Analytics Charts ──────────────────────────────────
def make_rr_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Trade #"], y=df["Risk Amount"], name="Risk ($)",
        marker_color="#ef4444",
        hovertemplate="<b>%{x}</b><br>Risk: $%{y:,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=df["Trade #"], y=df["Reward Amount"], name="Reward ($)",
        marker_color="#00e5b0",
        hovertemplate="<b>%{x}</b><br>Reward: $%{y:,.2f}<extra></extra>"
    ))
    apply_theme(fig, height=300, title="Risk vs Reward per Trade",
                extra=dict(barmode="group",
                           legend=dict(orientation="h", y=1.02, x=1, xanchor="right", font=dict(size=11)),
                           yaxis=dict(gridcolor="#232a3d", title="Amount ($)")))
    return fig


def make_risk_pct_chart(df):
    colors = df["Classification"].map({"SAFE": "#00e5b0", "MEDIUM RISK": "#f59e0b", "HIGH RISK": "#ef4444"}).fillna("#6b7a99")
    max_y  = max(df["Risk %"].max() + 5, 20)
    fig = go.Figure()
    fig.add_hrect(y0=0,  y1=5,     fillcolor="#00e5b0", opacity=0.05, line_width=0)
    fig.add_hrect(y0=5,  y1=15,    fillcolor="#f59e0b", opacity=0.05, line_width=0)
    fig.add_hrect(y0=15, y1=max_y, fillcolor="#ef4444", opacity=0.05, line_width=0)
    fig.add_hline(y=5,  line_dash="dot", line_color="#00e5b0", line_width=1,
                  annotation_text="5% safe", annotation_font_color="#00e5b0", annotation_font_size=10)
    fig.add_hline(y=15, line_dash="dot", line_color="#ef4444", line_width=1,
                  annotation_text="15% high", annotation_font_color="#ef4444", annotation_font_size=10)
    fig.add_trace(go.Scatter(
        x=df["Trade #"], y=df["Risk %"], mode="lines+markers",
        line=dict(width=2, color="#3b82f6"),
        marker=dict(size=9, color=colors, line=dict(width=2, color="#141926")),
        hovertemplate="<b>%{x}</b><br>Risk: %{y:.2f}%<extra></extra>"
    ))
    apply_theme(fig, height=300, title="Risk % per Trade",
                extra=dict(yaxis=dict(gridcolor="#232a3d", title="Risk %", range=[0, max_y]),
                           margin=dict(t=48, b=24, l=16, r=80)))
    return fig


def make_rr_ratio_chart(df):
    bar_colors = ["#00e5b0" if r >= 2 else "#f59e0b" if r >= 1 else "#ef4444" for r in df["RR Ratio"]]
    fig = go.Figure()
    fig.add_hline(y=2, line_dash="dot", line_color="#00e5b0", line_width=1,
                  annotation_text="1:2 target", annotation_position="right",
                  annotation_font_color="#00e5b0", annotation_font_size=10)
    fig.add_trace(go.Bar(
        x=df["Trade #"], y=df["RR Ratio"],
        marker_color=bar_colors,
        hovertemplate="<b>%{x}</b><br>RR: 1:%{y:.2f}<extra></extra>"
    ))
    apply_theme(fig, height=300, title="Risk/Reward Ratio per Trade",
                extra=dict(showlegend=False,
                           yaxis=dict(gridcolor="#232a3d", title="RR Ratio"),
                           margin=dict(t=48, b=24, l=16, r=80)))
    return fig


def make_classification_pie(df):
    counts    = df["Classification"].value_counts()
    color_map = {"SAFE": "#00e5b0", "MEDIUM RISK": "#f59e0b", "HIGH RISK": "#ef4444"}
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values,
        marker_colors=[color_map.get(c, "#6b7a99") for c in counts.index],
        hole=0.55,
        textinfo="label+percent",
        textfont=dict(size=11, family="DM Sans"),
        hovertemplate="<b>%{label}</b><br>%{value} trades (%{percent})<extra></extra>"
    ))
    apply_theme(fig, height=300, title="Trade Risk Distribution",
                extra=dict(showlegend=False, margin=dict(t=48, b=10, l=10, r=10)))
    return fig


# ═══════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:0.25rem;">
    <span style="font-family:'Space Mono',monospace; font-size:clamp(1.5rem,4vw,2.2rem); font-weight:700; color:#e8edf5; letter-spacing:-0.02em;">
        ⚡ Perps Risk Guard
    </span>
    <span class="header-badge">PACIFICA HACKATHON</span>
</div>
<p style="color:#6b7a99; font-size:0.875rem; margin-top:0; margin-bottom:1.5rem; font-family:'DM Sans',sans-serif;">
    Real-time risk analytics for perpetual traders — powered by Pacifica API
</p>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔍  Calculator", "📊  Analytics", "💼  Portfolio Risk", "🌐  Live Market"])


# ═══════════════════════════════════════════════════════════
#  TAB 1 — CALCULATOR
# ═══════════════════════════════════════════════════════════
with tab1:

    st.subheader("① Trade Details")

    live_prices  = fetch_prices()
    live_markets = fetch_markets()

    available_symbols = sorted(live_prices.keys()) if live_prices else ["BTC", "ETH", "SOL"]

    col_sym, col_dir = st.columns([2, 2])
    with col_sym:
        selected_symbol = st.selectbox("Select Symbol", options=available_symbols,
                                       index=available_symbols.index("BTC") if "BTC" in available_symbols else 0)
    with col_dir:
        direction = st.radio("Position Direction", options=["Long 📈", "Short 📉"], horizontal=True)

    is_long    = direction.startswith("Long")
    live_price = live_prices.get(selected_symbol, 0.0)

    if live_price > 0:
        st.success(f"🟢  Live {selected_symbol} Mark Price: **${live_price:,.2f}**  *(from Pacifica API)*")
    else:
        st.warning("⚠️  Could not fetch live price. Please enter entry price manually.")

    market_info  = live_markets.get(selected_symbol, {})
    max_leverage = float(market_info.get("max_leverage", 1000))

    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        balance       = st.number_input("Account Balance ($)",   min_value=1.0,    value=1000.0,   step=100.0)
        stop_loss     = st.number_input("Stop Loss Price ($)",   min_value=0.01,
                                         value=round(live_price * 0.95, 2) if live_price > 0 else 95.0, step=1.0)
    with col2:
        position_size = st.number_input("Position Size ($)",     min_value=1.0,    value=5000.0,   step=100.0)
        take_profit   = st.number_input("Take Profit Price ($)", min_value=0.01,
                                         value=round(live_price * 1.10, 2) if live_price > 0 else 110.0, step=1.0)
    with col3:
        entry_price   = st.number_input("Entry Price ($)", min_value=0.01,
                                         value=round(live_price, 2) if live_price > 0 else 100.0, step=1.0)
        leverage      = st.number_input(f"Leverage (max {int(max_leverage)}x)",
                                         min_value=1.0, max_value=max_leverage, value=5.0, step=1.0)

    st.divider()

    if st.button("🔍 Calculate Risk", use_container_width=True, type="primary"):

        # ── Validation ──────────────────────────────────────
        if entry_price == stop_loss:
            st.error("❌  Entry price and stop loss cannot be the same."); st.stop()
        if entry_price == take_profit:
            st.error("❌  Entry price and take profit cannot be the same."); st.stop()
        if position_size > balance * leverage:
            st.error("❌  Position size exceeds your balance × leverage limit."); st.stop()
        if is_long and stop_loss >= entry_price:
            st.error("❌  Long position: stop loss must be below entry price."); st.stop()
        if is_long and take_profit <= entry_price:
            st.error("❌  Long position: take profit must be above entry price."); st.stop()
        if not is_long and stop_loss <= entry_price:
            st.error("❌  Short position: stop loss must be above entry price."); st.stop()
        if not is_long and take_profit >= entry_price:
            st.error("❌  Short position: take profit must be below entry price."); st.stop()
        if leverage >= 100:
            st.warning(f"⚠️  You are using {int(leverage)}x leverage. Liquidation price is very close to entry.")

        # ── Calculations ────────────────────────────────────
        sl_diff             = abs(entry_price - stop_loss)
        pct_to_sl           = (sl_diff / entry_price) * 100
        risk_amount         = (pct_to_sl / 100) * position_size
        risk_pct            = (risk_amount / balance) * 100

        tp_diff             = abs(take_profit - entry_price)
        pct_to_tp           = (tp_diff / entry_price) * 100
        reward_amount       = (pct_to_tp / 100) * position_size

        rr_ratio            = reward_amount / risk_amount
        capital_utilization = position_size / balance
        margin_used         = position_size / leverage
        effective_leverage  = position_size / margin_used

        liq_drop  = 100 / leverage
        liq_price = (
            entry_price * (1 - liq_drop / 100) if is_long
            else entry_price * (1 + liq_drop / 100)
        )

        if risk_pct < 5:
            risk_label = "SAFE"
        elif risk_pct <= 15:
            risk_label = "MEDIUM RISK"
        else:
            risk_label = "HIGH RISK"

        # ── Save to Trade History ────────────────────────────
        st.session_state.trade_counter += 1
        st.session_state.trade_history.append({
            "Trade #"            : f"#{st.session_state.trade_counter}",
            "Symbol"             : selected_symbol,
            "Direction"          : "Long" if is_long else "Short",
            "Entry"              : entry_price,
            "Stop Loss"          : stop_loss,
            "Take Profit"        : take_profit,
            "Leverage"           : int(leverage),
            "Position Size"      : position_size,
            "Risk Amount"        : round(risk_amount, 2),
            "Risk %"             : round(risk_pct, 2),
            "Reward Amount"      : round(reward_amount, 2),
            "RR Ratio"           : round(rr_ratio, 2),
            "Effective Leverage" : round(effective_leverage, 2),
            "Liq. Price"         : round(liq_price, 2),
            "Classification"     : risk_label,
        })

        # ── Section 2: Risk Gauge + Price Levels ────────────
        direction_label = "Long 📈" if is_long else "Short 📉"
        st.subheader(f"② Risk Analysis — {selected_symbol} {direction_label}")

        gauge_col, levels_col = st.columns([1, 1.6])
        with gauge_col:
            st.plotly_chart(make_risk_gauge(risk_pct), use_container_width=True)
        with levels_col:
            st.plotly_chart(make_price_levels(entry_price, stop_loss, take_profit, liq_price, selected_symbol, is_long),
                            use_container_width=True)

        # ── Metrics ─────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Amount",         f"${risk_amount:,.2f}")
        c2.metric("Risk % of Balance",   f"{risk_pct:.2f}%")
        c3.metric("Est. Liquidation",    f"${liq_price:,.2f}")

        r1, r2, r3 = st.columns(3)
        r1.metric("Potential Reward",    f"${reward_amount:,.2f}")
        r2.metric("Risk / Reward Ratio", f"1 : {rr_ratio:.2f}")
        r3.metric("Leverage Used",       f"{int(leverage)}x")

        e1, e2, e3 = st.columns(3)
        e1.metric("Capital Utilization", f"{capital_utilization:.2f}x")
        e2.metric("Effective Leverage",  f"{effective_leverage:.2f}x")
        e3.metric("Margin Used",         f"${margin_used:,.2f}")

        st.caption(
            f"📌  **Capital Utilization {capital_utilization:.2f}x** — "
            f"your position is {capital_utilization:.2f}x your total balance.   "
            f"**Effective Leverage {effective_leverage:.2f}x** — "
            f"actual leveraged exposure based on margin used (${margin_used:,.2f})."
        )

        p1, p2, p3 = st.columns(3)
        p1.metric("% Move to Stop Loss",   f"{pct_to_sl:.2f}%")
        p2.metric("% Move to Take Profit", f"{pct_to_tp:.2f}%")
        p3.metric("Max Position Allowed",  f"${balance * leverage:,.2f}")

        st.divider()

        # ── Risk Classification ──────────────────────────────
        st.subheader("③ Risk Classification")
        if risk_pct < 5:
            st.success("✅  SAFE — Risk is within a healthy range (< 5% of balance).")
        elif risk_pct <= 15:
            st.warning("⚠️  MEDIUM RISK — Consider reducing your position size (5–15%).")
        else:
            st.error("🔴  HIGH RISK — This trade risks too much of your balance (> 15%).")

        # ── Auto Insight ─────────────────────────────────────
        st.subheader("💡 Smart Insights")

        insights = []
        if rr_ratio < 1:
            insights.append("🔴 **Poor RR Ratio** — You're risking more than your potential reward. Consider moving your take profit further or tightening your stop loss.")
        elif rr_ratio < 2:
            insights.append("🟡 **Decent RR** — A 1:2 ratio is generally the minimum for sustainable trading. Try to get at least 1:2.")
        else:
            insights.append(f"🟢 **Good RR Ratio** — Your 1:{rr_ratio:.1f} ratio gives you a statistical edge even with a 50% win rate.")

        if leverage > 20:
            insights.append(f"⚠️ **High Leverage Warning** — At {int(leverage)}x, a {liq_drop:.1f}% move against you triggers liquidation. Make sure your stop loss is well above ${liq_price:,.2f}.")
        elif leverage > 10:
            insights.append(f"🟡 **Moderate Leverage** — {int(leverage)}x leverage is manageable, but stay disciplined with your stop loss.")
        else:
            insights.append(f"🟢 **Conservative Leverage** — {int(leverage)}x is relatively safe. Your liquidation price (${liq_price:,.2f}) has a good buffer.")

        if capital_utilization > 5:
            insights.append(f"⚠️ **Overexposed** — Your position is {capital_utilization:.1f}x your balance. Consider sizing down to protect your account.")
        elif capital_utilization > 2:
            insights.append(f"🟡 **Position Sizing** — Position is {capital_utilization:.1f}x your balance. Manageable, but monitor closely.")
        else:
            insights.append(f"🟢 **Well-Sized Position** — Position size relative to balance looks healthy.")

        for insight in insights:
            st.markdown(f"- {insight}")

        st.divider()

        # ── Adverse Move Simulation ──────────────────────────
        st.subheader("④ Adverse Move Simulation")
        move_label = "falls" if is_long else "rises"
        st.caption(f"What happens if {selected_symbol} price {move_label} against your {'Long' if is_long else 'Short'} position?")

        st.plotly_chart(
            make_adverse_waterfall(balance, position_size, entry_price, is_long, leverage),
            use_container_width=True
        )

        # Table version for quick reference
        rows = []
        for pct in [1, 2, 3, 5, 10]:
            new_price   = entry_price * (1 - pct/100) if is_long else entry_price * (1 + pct/100)
            pnl         = -1 * (pct / 100) * position_size
            new_balance = balance + pnl
            rows.append({
                "Adverse Move"      : f"-{pct}%",
                "New Price"         : f"${new_price:,.2f}",
                "Estimated Loss"    : f"(${abs(pnl):,.2f})",
                "Remaining Balance" : f"${new_balance:,.2f}",
                "Status"            : "💀 Liquidated" if new_price <= liq_price and is_long else
                                      "💀 Liquidated" if new_price >= liq_price and not is_long else "✅ Alive"
            })

        st.dataframe(pd.DataFrame(rows).set_index("Adverse Move"), use_container_width=True)

        st.divider()
        st.info("💡 Discipline in risk management is the key to surviving the market.")

        if len(st.session_state.trade_history) >= 2:
            st.success(f"📊  You now have {len(st.session_state.trade_history)} trades saved. Check the **Analytics** tab!")


# ═══════════════════════════════════════════════════════════
#  TAB 2 — ANALYTICS
# ═══════════════════════════════════════════════════════════
with tab2:

    if len(st.session_state.trade_history) == 0:
        st.info("📭  No trades yet. Go to the **Calculator** tab, enter a trade, and click Calculate Risk.")
    else:
        df = pd.DataFrame(st.session_state.trade_history)

        if "Symbol" not in df.columns:
            df["Symbol"] = "-"

        st.subheader("📋 Trade History")
        st.caption(f"{len(df)} trade(s) analyzed this session.")

        summary_cols = [
            "Trade #", "Symbol", "Direction", "Entry", "Stop Loss", "Take Profit",
            "Leverage", "Risk Amount", "Risk %", "Reward Amount", "RR Ratio", "Classification"
        ]
        st.dataframe(df[summary_cols].set_index("Trade #"), hide_index=False, use_container_width=True)

        st.divider()

        st.subheader("📈 Session Analytics")

        total_trades = len(df)
        avg_risk_pct = df["Risk %"].mean()
        avg_rr       = df["RR Ratio"].mean()
        best_rr      = df["RR Ratio"].max()
        safe_count   = len(df[df["Classification"] == "SAFE"])
        medium_count = len(df[df["Classification"] == "MEDIUM RISK"])
        high_count   = len(df[df["Classification"] == "HIGH RISK"])

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Total Trades",   total_trades)
        a2.metric("Avg Risk %",     f"{avg_risk_pct:.2f}%")
        a3.metric("Avg RR Ratio",   f"1 : {avg_rr:.2f}")
        a4.metric("Best RR Ratio",  f"1 : {best_rr:.2f}")

        b1, b2, b3 = st.columns(3)
        b1.metric("✅  Safe Trades",      safe_count)
        b2.metric("⚠️  Medium Trades",    medium_count)
        b3.metric("🔴  High Risk Trades", high_count)

        st.divider()

        # ── Plotly Charts ────────────────────────────────────
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(make_rr_chart(df), use_container_width=True)
        with ch2:
            st.plotly_chart(make_classification_pie(df), use_container_width=True)

        st.plotly_chart(make_risk_pct_chart(df), use_container_width=True)
        st.plotly_chart(make_rr_ratio_chart(df), use_container_width=True)

        st.divider()

        if st.button("🗑️  Clear Trade History", use_container_width=False):
            st.session_state.trade_history = []
            st.session_state.trade_counter = 0
            st.rerun()


# ═══════════════════════════════════════════════════════════
#  TAB 3 — PORTFOLIO RISK AGGREGATOR
# ═══════════════════════════════════════════════════════════
with tab3:

    st.subheader("💼 Portfolio Risk Aggregator")
    st.caption("Connect your Pacifica wallet to auto-load real positions, or add manually.")

    # ── Fetch prices for live defaults ──────────────────────
    port_prices  = fetch_prices()
    port_markets = fetch_markets()
    port_symbols = sorted(port_prices.keys()) if port_prices else ["BTC", "ETH", "SOL"]

    # ── Wallet Integration ───────────────────────────────────
    st.markdown("#### 🔗 Load Real Positions from Wallet")

    w_col1, w_col2 = st.columns([4, 1])
    with w_col1:
        wallet_address = st.text_input(
            "Pacifica Wallet Address",
            placeholder="Paste your wallet address (e.g. 42trU9A5...)",
            help="Read-only — your positions and balance are fetched publicly. No signature or login required."
        )
    with w_col2:
        st.write("")
        st.write("")
        load_wallet = st.button("🔍 Load Wallet", use_container_width=True, type="primary")

    if load_wallet and wallet_address.strip():
        wallet = wallet_address.strip()
        with st.spinner("Fetching your Pacifica positions..."):

            # ── Fetch account info ──────────────────────────
            try:
                acc_resp = requests.get(
                    f"{PACIFICA_BASE_URL}/account",
                    params={"account": wallet}, timeout=8
                )
                acc_data = acc_resp.json()
                acc_info = acc_data.get("data", [{}])[0] if acc_data.get("success") else {}
            except Exception:
                acc_info = {}

            # ── Fetch positions ─────────────────────────────
            try:
                pos_resp = requests.get(
                    f"{PACIFICA_BASE_URL}/positions",
                    params={"account": wallet}, timeout=8
                )
                pos_data = pos_resp.json()
                positions = pos_data.get("data", []) if pos_data.get("success") else []
            except Exception:
                positions = []

        if not acc_info and not positions:
            st.error("❌ Could not fetch wallet data. Check your address and try again.")
        else:
            # Show account summary
            if acc_info:
                st.success(f"✅ Wallet loaded: `{wallet[:6]}...{wallet[-4:]}`")
                wa1, wa2, wa3, wa4 = st.columns(4)
                wa1.metric("Balance",          f"${float(acc_info.get('balance', 0)):,.2f}")
                wa2.metric("Account Equity",   f"${float(acc_info.get('account_equity', 0)):,.2f}")
                wa3.metric("Margin Used",      f"${float(acc_info.get('total_margin_used', 0)):,.2f}")
                wa4.metric("Available",        f"${float(acc_info.get('available_to_spend', 0)):,.2f}")

            if not positions:
                st.info("📭 No open positions found for this wallet.")
            else:
                st.markdown(f"**{len(positions)} open position(s) found — importing into portfolio...**")

                # Convert API positions to portfolio format
                wallet_balance = float(acc_info.get("balance", 10000)) if acc_info else 10000
                imported = 0

                for pos in positions:
                    symbol    = pos.get("symbol", "")
                    side      = pos.get("side", "bid")   # "bid" = long, "ask" = short
                    is_long   = side in ("bid", "long")
                    entry     = float(pos.get("entry_price", 0))
                    amount    = float(pos.get("amount", 0))          # in token units
                    funding   = float(pos.get("funding", 0))
                    isolated  = pos.get("isolated", False)
                    margin    = float(pos.get("margin", 0)) if isolated else 0

                    live_px   = port_prices.get(symbol, entry)
                    size_usd  = amount * live_px                      # position size in $

                    # Estimate leverage from market max if not isolated
                    mkt       = port_markets.get(symbol, {})
                    est_lev   = float(mkt.get("max_leverage", 10)) / 2  # conservative estimate
                    if isolated and margin > 0:
                        est_lev = round(size_usd / margin, 1)

                    # Default SL/TP: ±5% / ±10% from entry (user can refine manually)
                    est_sl = entry * (0.95 if is_long else 1.05)
                    est_tp = entry * (1.10 if is_long else 0.90)

                    sl_diff   = abs(entry - est_sl)
                    pct_sl    = (sl_diff / entry) * 100 if entry > 0 else 5
                    risk_amt  = (pct_sl / 100) * size_usd
                    risk_pct  = (risk_amt / wallet_balance) * 100 if wallet_balance > 0 else 0
                    tp_diff   = abs(est_tp - entry)
                    pct_tp    = (tp_diff / entry) * 100 if entry > 0 else 10
                    rew_amt   = (pct_tp / 100) * size_usd
                    rr        = rew_amt / risk_amt if risk_amt > 0 else 0
                    liq_drop  = 100 / est_lev if est_lev > 0 else 100
                    liq_px    = entry * (1 - liq_drop / 100) if is_long else entry * (1 + liq_drop / 100)

                    # Avoid duplicate import
                    existing_syms = [(p["Symbol"], p["Direction"]) for p in st.session_state.portfolio]
                    direction_str = "Long" if is_long else "Short"
                    if (symbol, direction_str) not in existing_syms:
                        st.session_state.portfolio_counter += 1
                        st.session_state.portfolio.append({
                            "Pos #"       : f"#{st.session_state.portfolio_counter}",
                            "Symbol"      : symbol,
                            "Direction"   : direction_str,
                            "Entry"       : round(entry, 4),
                            "Stop Loss"   : round(est_sl, 4),
                            "Take Profit" : round(est_tp, 4),
                            "Leverage"    : int(est_lev),
                            "Size ($)"    : round(size_usd, 2),
                            "Margin ($)"  : round(size_usd / est_lev, 2) if est_lev > 0 else 0,
                            "Liq. Price"  : round(liq_px, 4),
                            "Risk ($)"    : round(risk_amt, 2),
                            "Risk %"      : round(risk_pct, 2),
                            "Reward ($)"  : round(rew_amt, 2),
                            "RR Ratio"    : round(rr, 2),
                        })
                        imported += 1

                if imported > 0:
                    st.success(f"✅ {imported} position(s) imported! Scroll down to see your portfolio.")
                    st.info("💡 **Note:** Stop Loss and Take Profit are estimated at ±5%/±10% from entry. Edit them manually if you have specific levels set.")
                    st.rerun()
                else:
                    st.warning("⚠️ All positions already in portfolio (no duplicates added).")

    elif load_wallet and not wallet_address.strip():
        st.warning("Please enter a wallet address first.")

    st.divider()
    st.markdown("#### ➕ Add Position Manually")

    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        p_symbol    = st.selectbox("Symbol", options=port_symbols, key="p_symbol")
        p_direction = st.radio("Direction", ["Long 📈", "Short 📉"], horizontal=True, key="p_dir")
    with pc2:
        p_live      = port_prices.get(p_symbol, 0.0)
        p_entry     = st.number_input("Entry Price ($)", min_value=0.01,
                                      value=round(p_live, 2) if p_live > 0 else 100.0,
                                      step=1.0, key="p_entry")
        p_size      = st.number_input("Position Size ($)", min_value=1.0, value=5000.0,
                                      step=100.0, key="p_size")
    with pc3:
        p_market    = port_markets.get(p_symbol, {})
        p_max_lev   = float(p_market.get("max_leverage", 1000))
        p_leverage  = st.number_input(f"Leverage (max {int(p_max_lev)}x)", min_value=1.0,
                                       max_value=p_max_lev, value=5.0, step=1.0, key="p_lev")
        p_sl        = st.number_input("Stop Loss ($)", min_value=0.01,
                                      value=round(p_live * 0.95, 2) if p_live > 0 else 95.0,
                                      step=1.0, key="p_sl")
    with pc4:
        p_balance   = st.number_input("Account Balance ($)", min_value=1.0, value=10000.0,
                                       step=100.0, key="p_balance")
        p_tp        = st.number_input("Take Profit ($)", min_value=0.01,
                                      value=round(p_live * 1.10, 2) if p_live > 0 else 110.0,
                                      step=1.0, key="p_tp")

    if st.button("➕ Add to Portfolio", use_container_width=True, type="primary"):
        p_is_long  = p_direction.startswith("Long")
        p_sl_diff  = abs(p_entry - p_sl)
        p_pct_sl   = (p_sl_diff / p_entry) * 100
        p_risk_amt = (p_pct_sl / 100) * p_size
        p_risk_pct = (p_risk_amt / p_balance) * 100

        p_tp_diff  = abs(p_tp - p_entry)
        p_pct_tp   = (p_tp_diff / p_entry) * 100
        p_rew_amt  = (p_pct_tp / 100) * p_size

        p_liq_drop = 100 / p_leverage
        p_liq      = (p_entry * (1 - p_liq_drop / 100) if p_is_long
                      else p_entry * (1 + p_liq_drop / 100))

        p_rr       = p_rew_amt / p_risk_amt if p_risk_amt > 0 else 0
        p_margin   = p_size / p_leverage

        # Validate basics
        err = None
        if p_entry == p_sl:
            err = "Entry and Stop Loss cannot be the same."
        elif p_is_long and p_sl >= p_entry:
            err = "Long: stop loss must be below entry."
        elif not p_is_long and p_sl <= p_entry:
            err = "Short: stop loss must be above entry."

        if err:
            st.error(f"❌ {err}")
        else:
            st.session_state.portfolio_counter += 1
            st.session_state.portfolio.append({
                "Pos #"       : f"#{st.session_state.portfolio_counter}",
                "Symbol"      : p_symbol,
                "Direction"   : "Long" if p_is_long else "Short",
                "Entry"       : p_entry,
                "Stop Loss"   : p_sl,
                "Take Profit" : p_tp,
                "Leverage"    : int(p_leverage),
                "Size ($)"    : p_size,
                "Margin ($)"  : round(p_margin, 2),
                "Liq. Price"  : round(p_liq, 2),
                "Risk ($)"    : round(p_risk_amt, 2),
                "Risk %"      : round(p_risk_pct, 2),
                "Reward ($)"  : round(p_rew_amt, 2),
                "RR Ratio"    : round(p_rr, 2),
            })
            st.success(f"✅ {p_symbol} {'Long' if p_is_long else 'Short'} added to portfolio!")
            st.rerun()

    # ── Portfolio Table ──────────────────────────────────────
    if len(st.session_state.portfolio) == 0:
        st.info("📭 No positions yet. Add your first position above.")
    else:
        st.divider()
        pdf = pd.DataFrame(st.session_state.portfolio)

        st.subheader(f"📋 Open Positions ({len(pdf)})")
        st.dataframe(pdf.set_index("Pos #"), use_container_width=True)

        # ── Delete individual position ───────────────────────
        del_options = [f"{r['Pos #']} — {r['Symbol']} {r['Direction']}" for _, r in pdf.iterrows()]
        del_choice  = st.selectbox("Remove a position:", ["— select —"] + del_options, key="del_pos")
        if st.button("🗑️ Remove Selected Position") and del_choice != "— select —":
            pos_num = del_choice.split(" — ")[0]
            st.session_state.portfolio = [p for p in st.session_state.portfolio if p["Pos #"] != pos_num]
            st.rerun()

        st.divider()

        # ── Aggregate Metrics ────────────────────────────────
        st.subheader("🧮 Portfolio-Level Risk Summary")

        total_size       = pdf["Size ($)"].sum()
        total_margin     = pdf["Margin ($)"].sum()
        total_risk_usd   = pdf["Risk ($)"].sum()
        total_reward_usd = pdf["Reward ($)"].sum()
        p_balance_ref    = p_balance  # last entered balance as reference
        total_risk_pct   = (total_risk_usd / p_balance_ref) * 100
        portfolio_rr     = total_reward_usd / total_risk_usd if total_risk_usd > 0 else 0
        avg_leverage     = (pdf["Leverage"] * pdf["Size ($)"]).sum() / total_size

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Exposure",    f"${total_size:,.2f}")
        m2.metric("Total Margin Used", f"${total_margin:,.2f}")
        m3.metric("Total Risk ($)",    f"${total_risk_usd:,.2f}")
        m4.metric("Total Risk %",      f"{total_risk_pct:.2f}%",
                  delta=f"{'🔴 HIGH' if total_risk_pct > 15 else '⚠️ MEDIUM' if total_risk_pct > 5 else '✅ SAFE'}")

        n1, n2, n3 = st.columns(3)
        n1.metric("Total Potential Reward", f"${total_reward_usd:,.2f}")
        n2.metric("Portfolio RR Ratio",     f"1 : {portfolio_rr:.2f}")
        n3.metric("Weighted Avg Leverage",  f"{avg_leverage:.1f}x")

        # Portfolio health warning
        if total_risk_pct > 15:
            st.error(f"🔴 **DANGER** — Your combined positions risk **{total_risk_pct:.1f}%** of your balance. This is extremely high. Consider closing some positions.")
        elif total_risk_pct > 5:
            st.warning(f"⚠️ **CAUTION** — Combined risk is **{total_risk_pct:.1f}%** of your balance. Monitor your positions carefully.")
        else:
            st.success(f"✅ **HEALTHY** — Combined risk is **{total_risk_pct:.1f}%** of your balance. Well diversified.")

        st.divider()

        # ── Portfolio Charts ─────────────────────────────────
        st.subheader("📊 Portfolio Visualizations")

        ch_a, ch_b = st.columns(2)

        with ch_a:
            # Exposure by symbol (pie)
            exp_by_sym = pdf.groupby("Symbol")["Size ($)"].sum().reset_index()
            fig_pie = go.Figure(go.Pie(
                labels=exp_by_sym["Symbol"],
                values=exp_by_sym["Size ($)"],
                hole=0.5,
                textinfo="label+percent",
                textfont=dict(size=11, family="DM Sans"),
                hovertemplate="<b>%{label}</b><br>$%{value:,.2f} (%{percent})<extra></extra>"
            ))
            apply_theme(fig_pie, height=280, title="Exposure by Symbol",
                        extra=dict(showlegend=False, margin=dict(t=48, b=10, l=10, r=10)))
            st.plotly_chart(fig_pie, use_container_width=True)

        with ch_b:
            # Long vs Short exposure
            dir_exp = pdf.groupby("Direction")["Size ($)"].sum().reset_index()
            dir_colors = ["#00e5b0" if d == "Long" else "#ef4444" for d in dir_exp["Direction"]]
            fig_dir = go.Figure(go.Bar(
                x=dir_exp["Direction"], y=dir_exp["Size ($)"],
                marker_color=dir_colors,
                hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>"
            ))
            apply_theme(fig_dir, height=280, title="Long vs Short Exposure",
                        extra=dict(showlegend=False,
                                   yaxis=dict(gridcolor="#232a3d", title="Size ($)")))
            st.plotly_chart(fig_dir, use_container_width=True)

        # Risk per position bar chart
        fig_risk = go.Figure()
        fig_risk.add_trace(go.Bar(
            x=pdf["Pos #"] + " " + pdf["Symbol"], y=pdf["Risk ($)"], name="Risk ($)",
            marker_color="#ef4444",
            hovertemplate="<b>%{x}</b><br>Risk: $%{y:,.2f}<extra></extra>"
        ))
        fig_risk.add_trace(go.Bar(
            x=pdf["Pos #"] + " " + pdf["Symbol"], y=pdf["Reward ($)"], name="Reward ($)",
            marker_color="#00e5b0",
            hovertemplate="<b>%{x}</b><br>Reward: $%{y:,.2f}<extra></extra>"
        ))
        apply_theme(fig_risk, height=300, title="Risk vs Reward per Position",
                    extra=dict(barmode="group",
                               legend=dict(orientation="h", y=1.02, x=1, xanchor="right", font=dict(size=11)),
                               yaxis=dict(gridcolor="#232a3d", title="Amount ($)")))
        st.plotly_chart(fig_risk, use_container_width=True)

        # Leverage per position
        lev_colors = ["#ef4444" if l >= 20 else "#f59e0b" if l >= 10 else "#00e5b0" for l in pdf["Leverage"]]
        fig_lev = go.Figure(go.Bar(
            x=pdf["Pos #"] + " " + pdf["Symbol"], y=pdf["Leverage"],
            marker_color=lev_colors,
            hovertemplate="<b>%{x}</b><br>Leverage: %{y}x<extra></extra>"
        ))
        fig_lev.add_hline(y=10, line_dash="dot", line_color="#f59e0b",
                          annotation_text="10x", annotation_font_color="#f59e0b", annotation_font_size=10)
        fig_lev.add_hline(y=20, line_dash="dot", line_color="#ef4444",
                          annotation_text="20x high risk", annotation_font_color="#ef4444", annotation_font_size=10)
        apply_theme(fig_lev, height=280, title="Leverage per Position",
                    extra=dict(showlegend=False,
                               yaxis=dict(gridcolor="#232a3d", title="Leverage (x)"),
                               margin=dict(t=48, b=24, l=16, r=90)))
        st.plotly_chart(fig_lev, use_container_width=True)

        st.divider()

        # ── Portfolio Correlation Warning ────────────────────
        long_syms  = set(pdf[pdf["Direction"] == "Long"]["Symbol"].tolist())
        short_syms = set(pdf[pdf["Direction"] == "Short"]["Symbol"].tolist())
        overlap    = long_syms & short_syms

        if overlap:
            st.warning(f"⚠️ **Hedged Positions Detected** — You have both Long and Short on: {', '.join(overlap)}. Make sure this is intentional.")

        num_symbols  = pdf["Symbol"].nunique()
        num_long     = len(pdf[pdf["Direction"] == "Long"])
        num_short    = len(pdf[pdf["Direction"] == "Short"])

        insights_p = []
        if num_symbols == 1 and len(pdf) > 1:
            insights_p.append("📌 **Concentrated Risk** — All positions are in one symbol. Consider diversifying across assets.")
        if num_long > 0 and num_short == 0:
            insights_p.append("📌 **All Long** — Your portfolio has no short positions. If the market drops, all positions lose simultaneously.")
        elif num_short > 0 and num_long == 0:
            insights_p.append("📌 **All Short** — Your portfolio has no long positions. A market rally would impact all positions.")
        if avg_leverage > 15:
            insights_p.append(f"🔴 **High Avg Leverage ({avg_leverage:.1f}x)** — Your portfolio weighted leverage is dangerously high.")
        if portfolio_rr >= 2:
            insights_p.append(f"🟢 **Good Portfolio RR ({portfolio_rr:.1f}x)** — Your combined risk/reward ratio is favorable.")

        if insights_p:
            st.subheader("💡 Portfolio Insights")
            for tip in insights_p:
                st.markdown(f"- {tip}")

        st.divider()
        if st.button("🗑️ Clear All Positions", use_container_width=False):
            st.session_state.portfolio = []
            st.session_state.portfolio_counter = 0
            st.rerun()


# ═══════════════════════════════════════════════════════════
#  TAB 4 — LIVE MARKET
# ═══════════════════════════════════════════════════════════
with tab4:

    st.subheader("🌐 Live Market Data")
    st.caption("Powered by Pacifica API — prices update on every page refresh.")

    if st.button("🔄  Refresh Prices", use_container_width=False):
        st.rerun()

    prices  = fetch_prices()
    markets = fetch_markets()

    if not prices:
        st.error("❌  Could not connect to Pacifica API. Please try refreshing.")
    else:
        market_rows = []
        for symbol, mark_price in sorted(prices.items()):
            market_data = markets.get(symbol, {})
            funding     = float(market_data.get("funding_rate", 0)) * 100
            market_rows.append({
                "Symbol"       : symbol,
                "Mark Price"   : f"${mark_price:,.4f}",
                "Max Leverage" : f"{market_data.get('max_leverage', '-')}x",
                "Funding Rate" : f"{funding:+.4f}%",
                "Min Order"    : f"${market_data.get('min_order_size', '-')}",
                "Max Order"    : f"${market_data.get('max_order_size', '-')}",
            })

        st.dataframe(
            pd.DataFrame(market_rows).set_index("Symbol"),
            hide_index=False,
            use_container_width=True
        )

        # ── Funding Rate Bar Chart ────────────────────────────
        funding_data = []
        for symbol, mark_price in sorted(prices.items()):
            market_data = markets.get(symbol, {})
            funding     = float(market_data.get("funding_rate", 0)) * 100
            if funding != 0:
                funding_data.append({"Symbol": symbol, "Funding Rate (%)": funding})

        if funding_data:
            fdf    = pd.DataFrame(funding_data).sort_values("Funding Rate (%)")
            colors = ["#ef4444" if f > 0 else "#00e5b0" for f in fdf["Funding Rate (%)"]]

            fig = go.Figure(go.Bar(
                x=fdf["Symbol"], y=fdf["Funding Rate (%)"],
                marker_color=colors,
                hovertemplate="<b>%{x}</b><br>Funding: %{y:+.4f}%<extra></extra>"
            ))
            fig.add_hline(y=0, line_color="#6b7a99", line_width=0.5)
            apply_theme(fig, height=340, title="Funding Rates — 🔴 Positive (longs pay)  |  🟢 Negative (shorts pay)",
                        extra=dict(yaxis=dict(gridcolor="#232a3d", title="Funding Rate (%)")))
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.caption(f"✅  Live data from `{PRICES_ENDPOINT}` — {len(prices)} markets loaded.")
