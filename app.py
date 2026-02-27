# ============================================================
#  PERPS RISK GUARD
#  Phase 2 — Streamlit Web App
#  Pacifica Hackathon | Analytics & Data Track
# ============================================================

import streamlit as st
import pandas as pd

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

# ── Input Fields (3 columns x 2 rows) ────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    balance       = st.number_input("Account Balance ($)",  min_value=1.0,    value=1000.0,  step=100.0)
    stop_loss     = st.number_input("Stop Loss Price ($)",   min_value=0.01,   value=95.0,    step=1.0)

with col2:
    position_size = st.number_input("Position Size ($)",     min_value=1.0,    value=5000.0,  step=100.0)
    take_profit   = st.number_input("Take Profit Price ($)", min_value=0.01,   value=110.0,   step=1.0)

with col3:
    entry_price   = st.number_input("Entry Price ($)",       min_value=0.01,   value=100.0,   step=1.0)
    leverage      = st.number_input("Leverage",              min_value=1.0,    max_value=1000.0, value=5.0, step=1.0)

st.divider()


# ════════════════════════════════════════════════════════════
#  SECTION 2 — CALCULATE BUTTON
# ════════════════════════════════════════════════════════════

if st.button("🔍 Calculate Risk", use_container_width=True):

    # ── Validation ───────────────────────────────────────────

    if entry_price == stop_loss:
        st.error("❌  Entry price and stop loss cannot be the same.")
        st.stop()

    if entry_price == take_profit:
        st.error("❌  Entry price and take profit cannot be the same.")
        st.stop()

    if position_size > balance * leverage:
        st.error("❌  Position size exceeds your balance × leverage limit.")
        st.stop()

    if is_long and stop_loss >= entry_price:
        st.error("❌  Long position: stop loss must be below entry price.")
        st.stop()

    if is_long and take_profit <= entry_price:
        st.error("❌  Long position: take profit must be above entry price.")
        st.stop()

    if not is_long and stop_loss <= entry_price:
        st.error("❌  Short position: stop loss must be above entry price.")
        st.stop()

    if not is_long and take_profit >= entry_price:
        st.error("❌  Short position: take profit must be below entry price.")
        st.stop()

    # Warn if leverage is dangerously high
    if leverage >= 100:
        st.warning(f"⚠️  You are using {int(leverage)}x leverage. Liquidation price is very close to entry.")


    # ── Calculations ─────────────────────────────────────────

    # --- Risk (Stop Loss side) ---

    # Price gap from entry to stop loss
    sl_diff    = abs(entry_price - stop_loss)

    # Percentage move to hit stop loss
    pct_to_sl  = (sl_diff / entry_price) * 100

    # Dollar amount lost if stop loss is hit
    risk_amount = (pct_to_sl / 100) * position_size

    # Risk as a percentage of total balance
    risk_pct    = (risk_amount / balance) * 100

    # --- Reward (Take Profit side) ---

    # Price gap from entry to take profit
    tp_diff     = abs(take_profit - entry_price)

    # Percentage move to hit take profit
    pct_to_tp   = (tp_diff / entry_price) * 100

    # Dollar amount gained if take profit is hit
    reward_amount = (pct_to_tp / 100) * position_size

    # --- Risk / Reward Ratio ---
    # How much you gain vs how much you risk
    # Example: risk $100, reward $300 → RR = 3.0
    rr_ratio    = reward_amount / risk_amount

    # --- Other Metrics ---

    # Ratio of position size to account balance
    exposure_ratio = position_size / balance

    # Estimated liquidation price
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

    # Row 1: Risk metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Amount",         f"${risk_amount:,.2f}")
    c2.metric("Risk % of Balance",   f"{risk_pct:.2f}%")
    c3.metric("Exposure Ratio",      f"{exposure_ratio:.2f}x")

    st.write("")

    # Row 2: Reward + RR + Liquidation
    r1, r2, r3 = st.columns(3)
    r1.metric("Potential Reward",    f"${reward_amount:,.2f}")
    r2.metric("Risk / Reward Ratio", f"1 : {rr_ratio:.2f}")
    r3.metric("Est. Liquidation",    f"${liq_price:,.2f}")

    st.write("")

    # Row 3: Price distances
    p1, p2, p3 = st.columns(3)
    p1.metric("% Move to Stop Loss",    f"{pct_to_sl:.2f}%")
    p2.metric("% Move to Take Profit",  f"{pct_to_tp:.2f}%")
    p3.metric("Leverage Used",          f"{int(leverage)}x")

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

    # hide_index removes the 0, 1, 2 row numbers
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True
    )

    st.divider()
    st.info("💡 Discipline in risk management is the key to surviving the market.")
