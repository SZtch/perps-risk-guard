# ============================================================
#  PERPS RISK GUARD
#  Phase 2 — Streamlit Web App
#  Pacifica Hackathon | Analytics & Data Track
# ============================================================

import streamlit as st

# ── Page Configuration ───────────────────────────────────────
st.set_page_config(
    page_title="Perps Risk Guard",
    page_icon="⚡",
    layout="centered"
)

# ── Header ───────────────────────────────────────────────────
st.title("⚡ Perps Risk Guard")
st.caption("Calculate your trade risk before entering a position.")
st.divider()


# ── Section 1: Inputs ────────────────────────────────────────
st.subheader("Trade Details")

col_a, col_b = st.columns(2)

with col_a:
    balance       = st.number_input("Account Balance ($)",  min_value=1.0,    value=1000.0, step=100.0)
    entry_price   = st.number_input("Entry Price ($)",       min_value=0.01,   value=100.0,  step=1.0)
    leverage      = st.number_input("Leverage",              min_value=1.0,    value=5.0,    step=1.0)

with col_b:
    position_size = st.number_input("Position Size ($)",     min_value=1.0,    value=5000.0, step=100.0)
    stop_loss     = st.number_input("Stop Loss Price ($)",   min_value=0.01,   value=95.0,   step=1.0)

st.divider()


# ── Section 2: Calculate Button ──────────────────────────────
calculate = st.button("Calculate Risk", use_container_width=True)

if calculate:

    # ── Input Validation ─────────────────────────────────────
    if entry_price == stop_loss:
        st.error("Entry price and stop loss price cannot be the same.")
        st.stop()

    if position_size > balance * leverage:
        st.error("Position size is too large for your balance and leverage.")
        st.stop()

    # ── Calculations ─────────────────────────────────────────

    # Absolute price gap between entry and stop loss
    price_diff      = abs(entry_price - stop_loss)

    # How far (in %) price needs to move to hit stop loss
    pct_move        = (price_diff / entry_price) * 100

    # Dollar amount you lose if stop loss is hit
    risk_amount     = (pct_move / 100) * position_size

    # Risk as a percentage of your total account balance
    risk_pct        = (risk_amount / balance) * 100

    # How many times larger your position is vs your balance
    exposure_ratio  = position_size / balance


    # ── Section 3: Results ───────────────────────────────────
    st.subheader("Risk Analysis")

    m1, m2, m3 = st.columns(3)
    m1.metric("Risk Amount",       f"${round(risk_amount, 2)}")
    m2.metric("Risk % of Balance", f"{round(risk_pct, 2)}%")
    m3.metric("Exposure Ratio",    f"{round(exposure_ratio, 2)}x")

    st.write("")

    d1, d2, d3 = st.columns(3)
    d1.metric("Price Difference",    f"${round(price_diff, 4)}")
    d2.metric("% Move to Stop Loss", f"{round(pct_move, 2)}%")
    d3.metric("Leverage Used",       f"{int(leverage)}x")

    st.divider()


    # ── Section 4: Risk Classification ───────────────────────
    st.subheader("Risk Classification")

    if risk_pct < 5:
        st.success("✅  SAFE — Your risk is within a healthy range.")
    elif risk_pct <= 15:
        st.warning("⚠️  MEDIUM RISK — Consider reducing your position size.")
    else:
        st.error("🔴  HIGH RISK — This trade risks too much of your balance.")

    st.divider()


    # ── Section 5: Adverse Move Simulation ───────────────────
    st.subheader("Adverse Move Simulation")
    st.caption("Estimated loss if price moves against your position.")

    rows = []
    for pct in [1, 2, 3]:
        pnl         = -1 * (pct / 100) * position_size
        new_balance = balance + pnl
        rows.append({
            "Adverse Move"    : f"-{pct}%",
            "Estimated PnL"   : f"-${abs(round(pnl, 2))}",
            "Remaining Balance": f"${round(new_balance, 2)}"
        })

    st.table(rows)

    st.divider()
    st.info("💡 Discipline in risk management is the key to surviving the market.")
