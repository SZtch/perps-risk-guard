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
st.caption("Know your risk before you enter the trade.")
st.divider()


# ════════════════════════════════════════════════════════════
#  SECTION 1 — TRADE INPUTS
# ════════════════════════════════════════════════════════════

st.subheader("① Trade Details")

# Direction toggle — Long or Short
direction = st.radio(
    "Position Direction",
    options=["Long 📈", "Short 📉"],
    horizontal=True
)

# Extract "Long" or "Short" without the emoji
is_long = direction.startswith("Long")

st.write("")

left, right = st.columns(2)

with left:
    balance       = st.number_input("Account Balance ($)",  min_value=1.0,  value=1000.0, step=100.0)
    entry_price   = st.number_input("Entry Price ($)",       min_value=0.01, value=100.0,  step=1.0)
    leverage      = st.number_input("Leverage",              min_value=1.0,  value=5.0,    step=1.0)

with right:
    position_size = st.number_input("Position Size ($)",     min_value=1.0,  value=5000.0, step=100.0)
    stop_loss     = st.number_input("Stop Loss Price ($)",   min_value=0.01, value=95.0,   step=1.0)

st.divider()


# ════════════════════════════════════════════════════════════
#  SECTION 2 — CALCULATE BUTTON
# ════════════════════════════════════════════════════════════

if st.button("🔍 Calculate Risk", use_container_width=True):

    # ── Validation ───────────────────────────────────────────

    if entry_price == stop_loss:
        st.error("❌  Entry price and stop loss cannot be the same.")
        st.stop()

    if position_size > balance * leverage:
        st.error("❌  Position size exceeds your balance × leverage limit.")
        st.stop()

    if is_long and stop_loss >= entry_price:
        st.error("❌  Long position: stop loss must be below entry price.")
        st.stop()

    if not is_long and stop_loss <= entry_price:
        st.error("❌  Short position: stop loss must be above entry price.")
        st.stop()


    # ── Core Calculations ────────────────────────────────────

    # Price gap between entry and stop loss
    price_diff     = abs(entry_price - stop_loss)

    # Percentage move required to hit stop loss
    pct_to_sl      = (price_diff / entry_price) * 100

    # Dollar amount at risk if stop loss is triggered
    risk_amount    = (pct_to_sl / 100) * position_size

    # Risk as a share of total account balance
    risk_pct       = (risk_amount / balance) * 100

    # Ratio of position size to account balance
    exposure_ratio = position_size / balance

    # Estimated liquidation price (simplified)
    # Long:  liquidated when price falls (100 / leverage)% from entry
    # Short: liquidated when price rises (100 / leverage)% from entry
    liq_drop = 100 / leverage
    liq_price = (
        entry_price * (1 - liq_drop / 100) if is_long
        else entry_price * (1 + liq_drop / 100)
    )


    # ════════════════════════════════════════════════════════
    #  SECTION 3 — RESULTS
    # ════════════════════════════════════════════════════════

    direction_label = "Long 📈" if is_long else "Short 📉"
    st.subheader(f"② Risk Analysis — {direction_label}")

    # Row 1: Core risk metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Amount",          f"${round(risk_amount, 2)}")
    c2.metric("Risk % of Balance",    f"{round(risk_pct, 2)}%")
    c3.metric("Exposure Ratio",       f"{round(exposure_ratio, 2)}x")

    st.write("")

    # Row 2: Price metrics
    p1, p2, p3 = st.columns(3)
    p1.metric("Price to Stop Loss",   f"${round(price_diff, 4)}")
    p2.metric("% Move to Stop Loss",  f"{round(pct_to_sl, 2)}%")
    p3.metric("Est. Liquidation",     f"${round(liq_price, 2)}")

    st.divider()


    # ════════════════════════════════════════════════════════
    #  SECTION 4 — RISK CLASSIFICATION
    # ════════════════════════════════════════════════════════

    st.subheader("③ Risk Classification")

    if risk_pct < 5:
        st.success("✅  SAFE — Risk is within a healthy range (< 5% of balance).")
    elif risk_pct <= 15:
        st.warning("⚠️  MEDIUM RISK — Consider reducing your position size (5–15%).")
    else:
        st.error("🔴  HIGH RISK — This trade risks too much of your balance (> 15%).")

    st.divider()


    # ════════════════════════════════════════════════════════
    #  SECTION 5 — ADVERSE MOVE SIMULATION
    # ════════════════════════════════════════════════════════

    st.subheader("④ Adverse Move Simulation")

    move_label = "falls" if is_long else "rises"
    st.caption(f"What happens if price {move_label} against your {direction_label.split()[0]} position?")

    rows = []
    for pct in [1, 2, 3]:

        # Simulate new price after adverse move
        new_price = (
            entry_price * (1 - pct / 100) if is_long
            else entry_price * (1 + pct / 100)
        )

        # Estimated loss and remaining balance
        pnl         = -1 * (pct / 100) * position_size
        new_balance = balance + pnl

        rows.append({
            "Adverse Move"      : f"-{pct}%",
            "New Price"         : f"${round(new_price, 4)}",
            "Estimated Loss"    : f"-${abs(round(pnl, 2))}",
            "Remaining Balance" : f"${round(new_balance, 2)}"
        })

    st.table(rows)

    st.divider()
    st.info("💡 Discipline in risk management is the key to surviving the market.")
