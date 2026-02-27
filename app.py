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

is_long = direction.startswith("Long")

st.write("")

# ── Input Fields (2 columns) ─────────────────────────────────
left, right = st.columns(2)

with left:
    balance       = st.number_input("Account Balance ($)",  min_value=1.0,  value=1000.0, step=100.0)
    entry_price   = st.number_input("Entry Price ($)",       min_value=0.01, value=100.0,  step=1.0)

with right:
    position_size = st.number_input("Position Size ($)",     min_value=1.0,  value=5000.0, step=100.0)
    stop_loss     = st.number_input("Stop Loss Price ($)",   min_value=0.01, value=95.0,   step=1.0)

st.write("")

# ── Leverage — Single slider only (1x to 1000x) ──────────────
# Using session_state so quick-select buttons can update the slider
if "leverage" not in st.session_state:
    st.session_state.leverage = 5

st.write("**Leverage**")

# Quick select buttons — clicking these updates session_state
b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
if b1.button("5x"):   st.session_state.leverage = 5
if b2.button("10x"):  st.session_state.leverage = 10
if b3.button("20x"):  st.session_state.leverage = 20
if b4.button("50x"):  st.session_state.leverage = 50
if b5.button("100x"): st.session_state.leverage = 100
if b6.button("125x"): st.session_state.leverage = 125
if b7.button("500x"): st.session_state.leverage = 500

# Single slider — reads from and writes to session_state
leverage = st.slider(
    "Drag to set leverage (1x – 1000x)",
    min_value=1,
    max_value=1000,
    value=st.session_state.leverage,
    step=1
)

# Keep session_state in sync with slider
st.session_state.leverage = leverage

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

    # Warn if leverage is dangerously high
    if leverage >= 100:
        st.warning(f"⚠️  You are using {leverage}x leverage. Liquidation price is very close to entry.")


    # ── Calculations ─────────────────────────────────────────

    # Absolute price gap between entry and stop loss
    price_diff     = abs(entry_price - stop_loss)

    # Percentage move required to hit stop loss
    pct_to_sl      = (price_diff / entry_price) * 100

    # Dollar amount at risk if stop loss is triggered
    risk_amount    = (pct_to_sl / 100) * position_size

    # Risk as a share of total account balance
    risk_pct       = (risk_amount / balance) * 100

    # How many times larger position is vs balance
    exposure_ratio = position_size / balance

    # Estimated liquidation price
    # Long:  liquidated when price falls (100 / leverage)% from entry
    # Short: liquidated when price rises (100 / leverage)% from entry
    liq_drop  = 100 / leverage
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
    c1.metric("Risk Amount",          f"${risk_amount:,.2f}")
    c2.metric("Risk % of Balance",    f"{risk_pct:.2f}%")
    c3.metric("Exposure Ratio",       f"{exposure_ratio:.2f}x")

    st.write("")

    # Row 2: Price metrics
    p1, p2, p3 = st.columns(3)
    p1.metric("Price to Stop Loss",   f"${price_diff:,.4f}")
    p2.metric("% Move to Stop Loss",  f"{pct_to_sl:.2f}%")
    p3.metric("Est. Liquidation",     f"${liq_price:,.2f}")

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
    st.caption(
        f"What happens if price {move_label} against your "
        f"{'Long' if is_long else 'Short'} position?"
    )

    # Build table rows — hide index by using st.dataframe with hide_index
    rows = []
    for pct in [1, 2, 3]:

        # New price after adverse move
        new_price = (
            entry_price * (1 - pct / 100) if is_long
            else entry_price * (1 + pct / 100)
        )

        pnl         = -1 * (pct / 100) * position_size
        new_balance = balance + pnl

        rows.append({
            "Adverse Move"      : f"-{pct}%",
            "New Price"         : f"${new_price:,.4f}",
            "Estimated Loss"    : f"-${abs(pnl):,.2f}",
            "Remaining Balance" : f"${new_balance:,.2f}"
        })

    # Use dataframe with hide_index=True to remove the 0,1,2 index column
    import pandas as pd
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True
    )

    st.divider()
    st.info("💡 Discipline in risk management is the key to surviving the market.")
