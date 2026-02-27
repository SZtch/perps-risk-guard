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
    balance       = st.number_input("Account Balance ($)",   min_value=1.0,    value=1000.0,  step=100.0)
    stop_loss     = st.number_input("Stop Loss Price ($)",    min_value=0.01,   value=95.0,    step=1.0)

with col2:
    position_size = st.number_input("Position Size ($)",      min_value=1.0,    value=5000.0,  step=100.0)
    take_profit   = st.number_input("Take Profit Price ($)",  min_value=0.01,   value=110.0,   step=1.0)

with col3:
    entry_price   = st.number_input("Entry Price ($)",        min_value=0.01,   value=100.0,   step=1.0)
    leverage      = st.number_input("Leverage",               min_value=1.0,    max_value=1000.0, value=5.0, step=1.0)

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
    sl_diff       = abs(entry_price - stop_loss)
    pct_to_sl     = (sl_diff / entry_price) * 100
    risk_amount   = (pct_to_sl / 100) * position_size
    risk_pct      = (risk_amount / balance) * 100

    # --- Reward (Take Profit side) ---
    tp_diff       = abs(take_profit - entry_price)
    pct_to_tp     = (tp_diff / entry_price) * 100
    reward_amount = (pct_to_tp / 100) * position_size

    # --- Risk / Reward Ratio ---
    rr_ratio      = reward_amount / risk_amount

    # --- Exposure Metrics ---

    # Capital Utilization: how much of your total balance is deployed
    # Example: $5,000 position on $1,000 balance = 5.00x
    # This tells you: your position is 5x your account size
    capital_utilization = position_size / balance

    # Effective Leverage: your actual leveraged exposure
    # margin_used = collateral locked for this position = position_size / leverage
    # Example: $5,000 position at 100x leverage → margin = $5,000 / 100 = $50
    # Effective leverage = $5,000 / $50 = 100x ✅
    margin_used        = position_size / leverage
    effective_leverage = position_size / margin_used

    # --- Liquidation Price ---
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
    c3.metric("Est. Liquidation",     f"${liq_price:,.2f}")

    st.write("")

    # Row 2: Reward metrics
    r1, r2, r3 = st.columns(3)
    r1.metric("Potential Reward",     f"${reward_amount:,.2f}")
    r2.metric("Risk / Reward Ratio",  f"1 : {rr_ratio:.2f}")
    r3.metric("Leverage Used",        f"{int(leverage)}x")

    st.write("")

    # Row 3: Exposure metrics — both shown side by side
    e1, e2, e3 = st.columns(3)
    e1.metric("Capital Utilization",  f"{capital_utilization:.2f}x")
    e2.metric("Effective Leverage",   f"{effective_leverage:.2f}x")
    e3.metric("Margin Used",          f"${margin_used:,.2f}")

    st.caption(
        f"📌  **Capital Utilization {capital_utilization:.2f}x** — "
        f"your position is {capital_utilization:.2f}x your total balance.   "
        f"**Effective Leverage {effective_leverage:.2f}x** — "
        f"your actual leveraged exposure based on margin used (${margin_used:,.2f})."
    )

    st.write("")

    # Row 4: Distance metrics
    p1, p2, p3 = st.columns(3)
    p1.metric("% Move to Stop Loss",   f"{pct_to_sl:.2f}%")
    p2.metric("% Move to Take Profit", f"{pct_to_tp:.2f}%")
    p3.metric("Max Position Allowed",  f"${balance * leverage:,.2f}")

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
            "New Price"         : f"${new_price:,.2f}",
            "Estimated Loss"    : f"(${abs(pnl):,.2f})",
            "Remaining Balance" : f"${new_balance:,.2f}"
        })

    # st.table with Adverse Move as index — clean, no toolbar
    st.table(pd.DataFrame(rows).set_index("Adverse Move"))

    st.divider()
    st.info("💡 Discipline in risk management is the key to surviving the market.")
