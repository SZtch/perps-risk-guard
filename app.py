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
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a1d27; border-radius: 8px; padding: 12px; }
    .risk-safe    { color: #00d4aa; font-weight: bold; font-size: 1.2rem; }
    .risk-medium  { color: #ffa500; font-weight: bold; font-size: 1.2rem; }
    .risk-high    { color: #ff4b4b; font-weight: bold; font-size: 1.2rem; }
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


# ── Plotly: Risk Gauge ────────────────────────────────────────
def make_risk_gauge(risk_pct):
    color = "#00d4aa" if risk_pct < 5 else ("#ffa500" if risk_pct <= 15 else "#ff4b4b")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_pct,
        number={"suffix": "%", "font": {"size": 36, "color": color}},
        delta={"reference": 5, "increasing": {"color": "#ff4b4b"}, "decreasing": {"color": "#00d4aa"}},
        gauge={
            "axis": {"range": [0, 30], "tickwidth": 1, "tickcolor": "#555"},
            "bar": {"color": color},
            "bgcolor": "#1a1d27",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  5],  "color": "#0d2b22"},
                {"range": [5,  15], "color": "#2b2200"},
                {"range": [15, 30], "color": "#2b0d0d"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.75,
                "value": risk_pct
            }
        },
        title={"text": "Risk % of Balance", "font": {"size": 16, "color": "#aaa"}}
    ))
    fig.update_layout(
        paper_bgcolor="#1a1d27",
        font_color="white",
        height=260,
        margin=dict(t=50, b=10, l=30, r=30)
    )
    return fig


# ── Plotly: Price Level Chart ─────────────────────────────────
def make_price_levels(entry, sl, tp, liq, symbol, is_long):
    levels = {
        "Take Profit": tp,
        "Entry":       entry,
        "Stop Loss":   sl,
        "Liquidation": liq,
    }
    colors = {
        "Take Profit": "#00d4aa",
        "Entry":       "#4da6ff",
        "Stop Loss":   "#ffa500",
        "Liquidation": "#ff4b4b",
    }
    sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
    labels  = [l[0] for l in sorted_levels]
    prices  = [l[1] for l in sorted_levels]
    clrs    = [colors[l[0]] for l in sorted_levels]

    fig = go.Figure()

    # Shaded zones
    if is_long:
        fig.add_hrect(y0=entry, y1=tp,  fillcolor="#00d4aa", opacity=0.08, line_width=0)
        fig.add_hrect(y0=liq,   y1=entry, fillcolor="#ff4b4b", opacity=0.08, line_width=0)

    for label, price, clr in zip(labels, prices, clrs):
        fig.add_hline(
            y=price, line_dash="dash", line_color=clr, line_width=1.5,
            annotation_text=f"  {label}: ${price:,.2f}",
            annotation_position="right",
            annotation_font_color=clr,
            annotation_font_size=12,
        )

    fig.add_trace(go.Scatter(
        x=["Level"] * len(prices),
        y=prices,
        mode="markers",
        marker=dict(size=12, color=clrs, symbol="diamond"),
        text=labels,
        hovertemplate="<b>%{text}</b><br>$%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        title=f"{symbol} — Key Price Levels",
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#0e1117",
        font_color="white",
        height=320,
        margin=dict(t=50, b=20, l=20, r=120),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(gridcolor="#2a2d3a", title="Price ($)"),
        showlegend=False,
    )
    return fig


# ── Plotly: Adverse Move Waterfall ────────────────────────────
def make_adverse_waterfall(balance, position_size, entry_price, is_long, leverage):
    moves   = list(range(1, 11))
    losses  = [(pct / 100) * position_size for pct in moves]
    balances = [balance - l for l in losses]
    liq_pct  = 100 / leverage

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=[f"-{p}%" for p in moves],
        y=losses,
        name="Estimated Loss ($)",
        marker_color=["#ff4b4b" if b > 0 else "#800000" for b in balances],
        hovertemplate="Move: %{x}<br>Loss: $%{y:,.2f}<extra></extra>"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=[f"-{p}%" for p in moves],
        y=balances,
        name="Remaining Balance ($)",
        mode="lines+markers",
        line=dict(color="#4da6ff", width=2),
        marker=dict(size=6),
        hovertemplate="Move: %{x}<br>Balance: $%{y:,.2f}<extra></extra>"
    ), secondary_y=True)

    # Liquidation line
    if liq_pct <= 10:
        fig.add_vline(
            x=f"-{int(liq_pct)}%",
            line_dash="dot",
            line_color="#ff4b4b",
            annotation_text="⚡ Liquidation",
            annotation_font_color="#ff4b4b"
        )

    fig.update_layout(
        title="Adverse Move Simulation (1%–10%)",
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#0e1117",
        font_color="white",
        height=340,
        margin=dict(t=50, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="#2a2d3a"),
        yaxis=dict(gridcolor="#2a2d3a", title="Loss ($)"),
        yaxis2=dict(title="Balance ($)", overlaying="y", side="right"),
        hovermode="x unified"
    )
    return fig


# ── Plotly: Analytics Charts ──────────────────────────────────
def make_rr_chart(df):
    colors = df["Classification"].map({
        "SAFE": "#00d4aa", "MEDIUM RISK": "#ffa500", "HIGH RISK": "#ff4b4b"
    }).fillna("#aaa")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Trade #"],
        y=df["Risk Amount"],
        name="Risk ($)",
        marker_color="#ff6b6b",
        hovertemplate="<b>%{x}</b><br>Risk: $%{y:,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=df["Trade #"],
        y=df["Reward Amount"],
        name="Reward ($)",
        marker_color="#00d4aa",
        hovertemplate="<b>%{x}</b><br>Reward: $%{y:,.2f}<extra></extra>"
    ))
    fig.update_layout(
        title="Risk vs Reward per Trade",
        barmode="group",
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#0e1117",
        font_color="white",
        height=320,
        margin=dict(t=50, b=20, l=20, r=20),
        xaxis=dict(gridcolor="#2a2d3a"),
        yaxis=dict(gridcolor="#2a2d3a", title="Amount ($)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    return fig


def make_risk_pct_chart(df):
    colors = df["Classification"].map({
        "SAFE": "#00d4aa", "MEDIUM RISK": "#ffa500", "HIGH RISK": "#ff4b4b"
    }).fillna("#aaa")

    fig = go.Figure()
    fig.add_hrect(y0=0, y1=5, fillcolor="#00d4aa", opacity=0.05, line_width=0, annotation_text="Safe zone", annotation_position="right")
    fig.add_hrect(y0=5, y1=15, fillcolor="#ffa500", opacity=0.05, line_width=0, annotation_text="Medium zone", annotation_position="right")
    fig.add_hrect(y0=15, y1=max(df["Risk %"].max() + 5, 20), fillcolor="#ff4b4b", opacity=0.05, line_width=0, annotation_text="High risk zone", annotation_position="right")
    fig.add_hline(y=5,  line_dash="dot", line_color="#00d4aa", line_width=1)
    fig.add_hline(y=15, line_dash="dot", line_color="#ff4b4b", line_width=1)

    fig.add_trace(go.Scatter(
        x=df["Trade #"],
        y=df["Risk %"],
        mode="lines+markers",
        line=dict(width=2, color="#4da6ff"),
        marker=dict(size=10, color=colors, line=dict(width=2, color="white")),
        hovertemplate="<b>%{x}</b><br>Risk: %{y:.2f}%<extra></extra>"
    ))
    fig.update_layout(
        title="Risk % per Trade (with Safe/Medium/High zones)",
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#0e1117",
        font_color="white",
        height=320,
        margin=dict(t=50, b=20, l=20, r=80),
        xaxis=dict(gridcolor="#2a2d3a"),
        yaxis=dict(gridcolor="#2a2d3a", title="Risk %")
    )
    return fig


def make_rr_ratio_chart(df):
    fig = go.Figure()
    fig.add_hline(y=2, line_dash="dot", line_color="#00d4aa", line_width=1,
                  annotation_text="Good RR (1:2)", annotation_position="right",
                  annotation_font_color="#00d4aa")

    fig.add_trace(go.Bar(
        x=df["Trade #"],
        y=df["RR Ratio"],
        marker_color=["#00d4aa" if r >= 2 else "#ffa500" if r >= 1 else "#ff4b4b" for r in df["RR Ratio"]],
        hovertemplate="<b>%{x}</b><br>RR Ratio: 1:%{y:.2f}<extra></extra>"
    ))
    fig.update_layout(
        title="Risk/Reward Ratio per Trade",
        paper_bgcolor="#1a1d27",
        plot_bgcolor="#0e1117",
        font_color="white",
        height=320,
        margin=dict(t=50, b=20, l=20, r=80),
        xaxis=dict(gridcolor="#2a2d3a"),
        yaxis=dict(gridcolor="#2a2d3a", title="RR Ratio"),
        showlegend=False
    )
    return fig


def make_classification_pie(df):
    counts = df["Classification"].value_counts()
    color_map = {"SAFE": "#00d4aa", "MEDIUM RISK": "#ffa500", "HIGH RISK": "#ff4b4b"}
    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        marker_colors=[color_map.get(c, "#aaa") for c in counts.index],
        hole=0.5,
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>%{value} trades (%{percent})<extra></extra>"
    ))
    fig.update_layout(
        title="Trade Risk Distribution",
        paper_bgcolor="#1a1d27",
        font_color="white",
        height=320,
        margin=dict(t=50, b=20, l=20, r=20),
        showlegend=False
    )
    return fig


# ═══════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════
st.title("⚡ Perps Risk Guard")
st.caption("Know your risk before you enter the trade. Powered by Pacifica API.")
st.divider()

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
    st.caption("Add multiple open positions and see your total exposure in one view.")

    # ── Fetch prices for live defaults ──────────────────────
    port_prices  = fetch_prices()
    port_markets = fetch_markets()
    port_symbols = sorted(port_prices.keys()) if port_prices else ["BTC", "ETH", "SOL"]

    st.markdown("#### ➕ Add Position")

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
                hole=0.45,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>$%{value:,.2f} (%{percent})<extra></extra>"
            ))
            fig_pie.update_layout(
                title="Exposure by Symbol",
                paper_bgcolor="#1a1d27", font_color="white",
                height=300, margin=dict(t=50, b=10, l=10, r=10), showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with ch_b:
            # Long vs Short exposure
            dir_exp = pdf.groupby("Direction")["Size ($)"].sum().reset_index()
            dir_colors = ["#00d4aa" if d == "Long" else "#ff4b4b" for d in dir_exp["Direction"]]
            fig_dir = go.Figure(go.Bar(
                x=dir_exp["Direction"],
                y=dir_exp["Size ($)"],
                marker_color=dir_colors,
                hovertemplate="<b>%{x}</b><br>$%{y:,.2f}<extra></extra>"
            ))
            fig_dir.update_layout(
                title="Long vs Short Exposure",
                paper_bgcolor="#1a1d27", plot_bgcolor="#0e1117", font_color="white",
                height=300, margin=dict(t=50, b=10, l=10, r=10),
                xaxis=dict(gridcolor="#2a2d3a"),
                yaxis=dict(gridcolor="#2a2d3a", title="Size ($)"),
                showlegend=False
            )
            st.plotly_chart(fig_dir, use_container_width=True)

        # Risk per position bar chart
        fig_risk = go.Figure()
        fig_risk.add_trace(go.Bar(
            x=pdf["Pos #"] + " " + pdf["Symbol"],
            y=pdf["Risk ($)"],
            name="Risk ($)",
            marker_color="#ff6b6b",
            hovertemplate="<b>%{x}</b><br>Risk: $%{y:,.2f}<extra></extra>"
        ))
        fig_risk.add_trace(go.Bar(
            x=pdf["Pos #"] + " " + pdf["Symbol"],
            y=pdf["Reward ($)"],
            name="Reward ($)",
            marker_color="#00d4aa",
            hovertemplate="<b>%{x}</b><br>Reward: $%{y:,.2f}<extra></extra>"
        ))
        fig_risk.update_layout(
            title="Risk vs Reward per Position",
            barmode="group",
            paper_bgcolor="#1a1d27", plot_bgcolor="#0e1117", font_color="white",
            height=320, margin=dict(t=50, b=20, l=20, r=20),
            xaxis=dict(gridcolor="#2a2d3a"),
            yaxis=dict(gridcolor="#2a2d3a", title="Amount ($)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig_risk, use_container_width=True)

        # Leverage per position
        lev_colors = ["#ff4b4b" if l >= 20 else "#ffa500" if l >= 10 else "#00d4aa"
                      for l in pdf["Leverage"]]
        fig_lev = go.Figure(go.Bar(
            x=pdf["Pos #"] + " " + pdf["Symbol"],
            y=pdf["Leverage"],
            marker_color=lev_colors,
            hovertemplate="<b>%{x}</b><br>Leverage: %{y}x<extra></extra>"
        ))
        fig_lev.add_hline(y=10, line_dash="dot", line_color="#ffa500",
                          annotation_text="10x", annotation_font_color="#ffa500")
        fig_lev.add_hline(y=20, line_dash="dot", line_color="#ff4b4b",
                          annotation_text="20x (high risk)", annotation_font_color="#ff4b4b")
        fig_lev.update_layout(
            title="Leverage per Position",
            paper_bgcolor="#1a1d27", plot_bgcolor="#0e1117", font_color="white",
            height=300, margin=dict(t=50, b=20, l=20, r=80),
            xaxis=dict(gridcolor="#2a2d3a"),
            yaxis=dict(gridcolor="#2a2d3a", title="Leverage (x)"),
            showlegend=False
        )
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
            colors = ["#ff4b4b" if f > 0 else "#00d4aa" for f in fdf["Funding Rate (%)"]]

            fig = go.Figure(go.Bar(
                x=fdf["Symbol"],
                y=fdf["Funding Rate (%)"],
                marker_color=colors,
                hovertemplate="<b>%{x}</b><br>Funding: %{y:+.4f}%<extra></extra>"
            ))
            fig.add_hline(y=0, line_color="white", line_width=0.5)
            fig.update_layout(
                title="Funding Rates — Positive (Longs pay) | Negative (Shorts pay)",
                paper_bgcolor="#1a1d27",
                plot_bgcolor="#0e1117",
                font_color="white",
                height=350,
                margin=dict(t=60, b=20, l=20, r=20),
                xaxis=dict(gridcolor="#2a2d3a"),
                yaxis=dict(gridcolor="#2a2d3a", title="Funding Rate (%)")
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.caption(f"✅  Live data from `{PRICES_ENDPOINT}` — {len(prices)} markets loaded.")
