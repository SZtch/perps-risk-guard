# ============================================================
#  PERPS RISK GUARD
#  Phase 3A — Analytics & Data with Tabs Navigation
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

# ── Session State — Trade History ────────────────────────────
if "trade_history" not in st.session_state:
    st.session_state.trade_history = []
if "trade_counter" not in st.session_state:
    st.session_state.trade_counter = 0

# ── Header ───────────────────────────────────────────────────
st.title("⚡ Perps Risk Guard")
st.caption("Know your risk before you enter the trade.")
st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🔍  Calculator", "📊  Analytics"])


# ════════════════════════════════════════════════════════════
#  TAB 1 — CALCULATOR
# ════════════════════════════════════════════════════════════

with tab1:

    # ── Section 1: Inputs ────────────────────────────────────
    st.subheader("① Trade Details")

    direction = st.radio(
        "Position Direction",
        options=["Long 📈", "Short 📉"],
        horizontal=True
    )

    is_long = direction.startswith("Long")

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        balance       = st.number_input("Account Balance ($)",   min_value=1.0,    value=1000.0,     step=100.0)
        stop_loss     = st.number_input("Stop Loss Price ($)",    min_value=0.01,   value=95.0,       step=1.0)

    with col2:
        position_size = st.number_input("Position Size ($)",      min_value=1.0,    value=5000.0,     step=100.0)
        take_profit   = st.number_input("Take Profit Price ($)",  min_value=0.01,   value=110.0,      step=1.0)

    with col3:
        entry_price   = st.number_input("Entry Price ($)",        min_value=0.01,   value=100.0,      step=1.0)
        leverage      = st.number_input("Leverage",               min_value=1.0,    max_value=1000.0, value=5.0, step=1.0)

    st.divider()

    # ── Section 2: Calculate Button ──────────────────────────
    if st.button("🔍 Calculate Risk", use_container_width=True):

        # ── Validation ───────────────────────────────────────
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

        if leverage >= 100:
            st.warning(f"⚠️  You are using {int(leverage)}x leverage. Liquidation price is very close to entry.")

        # ── Calculations ─────────────────────────────────────
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

        # ── Save to Trade History ─────────────────────────────
        st.session_state.trade_counter += 1
        st.session_state.trade_history.append({
            "Trade #"            : f"#{st.session_state.trade_counter}",
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

        # ── Section 3: Results ───────────────────────────────
        direction_label = "Long 📈" if is_long else "Short 📉"
        st.subheader(f"② Risk Analysis — {direction_label}")

        c1, c2, c3 = st.columns(3)
        c1.metric("Risk Amount",         f"${risk_amount:,.2f}")
        c2.metric("Risk % of Balance",   f"{risk_pct:.2f}%")
        c3.metric("Est. Liquidation",    f"${liq_price:,.2f}")

        st.write("")

        r1, r2, r3 = st.columns(3)
        r1.metric("Potential Reward",    f"${reward_amount:,.2f}")
        r2.metric("Risk / Reward Ratio", f"1 : {rr_ratio:.2f}")
        r3.metric("Leverage Used",       f"{int(leverage)}x")

        st.write("")

        e1, e2, e3 = st.columns(3)
        e1.metric("Capital Utilization", f"{capital_utilization:.2f}x")
        e2.metric("Effective Leverage",  f"{effective_leverage:.2f}x")
        e3.metric("Margin Used",         f"${margin_used:,.2f}")

        st.caption(
            f"📌  **Capital Utilization {capital_utilization:.2f}x** — "
            f"your position is {capital_utilization:.2f}x your total balance.   "
            f"**Effective Leverage {effective_leverage:.2f}x** — "
            f"your actual leveraged exposure based on margin used (${margin_used:,.2f})."
        )

        st.write("")

        p1, p2, p3 = st.columns(3)
        p1.metric("% Move to Stop Loss",   f"{pct_to_sl:.2f}%")
        p2.metric("% Move to Take Profit", f"{pct_to_tp:.2f}%")
        p3.metric("Max Position Allowed",  f"${balance * leverage:,.2f}")

        st.divider()

        # ── Section 4: Risk Classification ───────────────────
        st.subheader("③ Risk Classification")

        if risk_pct < 5:
            st.success("✅  SAFE — Risk is within a healthy range (< 5% of balance).")
        elif risk_pct <= 15:
            st.warning("⚠️  MEDIUM RISK — Consider reducing your position size (5–15%).")
        else:
            st.error("🔴  HIGH RISK — This trade risks too much of your balance (> 15%).")

        st.divider()

        # ── Section 5: Adverse Move Simulation ───────────────
        st.subheader("④ Adverse Move Simulation")

        move_label = "falls" if is_long else "rises"
        st.caption(
            f"What happens if price {move_label} against your "
            f"{'Long' if is_long else 'Short'} position?"
        )

        rows = []
        for pct in [1, 2, 3]:
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

        st.table(pd.DataFrame(rows).set_index("Adverse Move"))

        st.divider()
        st.info("💡 Discipline in risk management is the key to surviving the market.")

        # Hint to user to check Analytics tab
        if len(st.session_state.trade_history) >= 2:
            st.success(f"📊  You now have {len(st.session_state.trade_history)} trades saved. Check the **Analytics** tab to compare them!")


# ════════════════════════════════════════════════════════════
#  TAB 2 — ANALYTICS
# ════════════════════════════════════════════════════════════

with tab2:

    if len(st.session_state.trade_history) == 0:
        # Show placeholder if no trades yet
        st.info("📭  No trades yet. Go to the **Calculator** tab, enter a trade, and click Calculate Risk.")

    else:
        df = pd.DataFrame(st.session_state.trade_history)

        st.subheader("📋 Trade History")
        st.caption(f"{len(df)} trade(s) analyzed this session.")

        # ── Trade Summary Table ───────────────────────────────
        summary_cols = [
            "Trade #", "Direction", "Entry", "Stop Loss", "Take Profit",
            "Leverage", "Risk Amount", "Risk %", "Reward Amount",
            "RR Ratio", "Classification"
        ]

        st.dataframe(
            df[summary_cols].set_index("Trade #"),
            hide_index=False,
            use_container_width=True
        )

        st.divider()

        # ── Session Analytics ─────────────────────────────────
        st.subheader("📈 Session Analytics")

        total_trades = len(df)
        avg_risk_pct = df["Risk %"].mean()
        avg_rr       = df["RR Ratio"].mean()
        best_rr      = df["RR Ratio"].max()
        worst_risk   = df["Risk %"].max()
        safe_count   = len(df[df["Classification"] == "SAFE"])
        medium_count = len(df[df["Classification"] == "MEDIUM RISK"])
        high_count   = len(df[df["Classification"] == "HIGH RISK"])

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Total Trades",      total_trades)
        a2.metric("Avg Risk %",        f"{avg_risk_pct:.2f}%")
        a3.metric("Avg RR Ratio",      f"1 : {avg_rr:.2f}")
        a4.metric("Best RR Ratio",     f"1 : {best_rr:.2f}")

        st.write("")

        b1, b2, b3 = st.columns(3)
        b1.metric("✅  Safe Trades",      safe_count)
        b2.metric("⚠️  Medium Trades",    medium_count)
        b3.metric("🔴  High Risk Trades", high_count)

        st.divider()

        # ── Charts ────────────────────────────────────────────
        st.subheader("📉 Risk vs Reward per Trade")
        st.caption("Comparing risk amount against potential reward for each trade.")

        chart_df = df[["Trade #", "Risk Amount", "Reward Amount"]].set_index("Trade #")
        st.bar_chart(chart_df, use_container_width=True)

        st.write("")

        st.subheader("📊 Risk % per Trade")
        st.caption("How much of your balance is at risk per trade. Healthy range is below 5%.")

        risk_chart_df = df[["Trade #", "Risk %"]].set_index("Trade #")
        st.line_chart(risk_chart_df, use_container_width=True)

        st.write("")

        st.subheader("⚖️ RR Ratio per Trade")
        st.caption("Higher is better. A ratio above 1:2 is generally considered good.")

        rr_chart_df = df[["Trade #", "RR Ratio"]].set_index("Trade #")
        st.bar_chart(rr_chart_df, use_container_width=True)

        st.divider()

        # ── Clear History ─────────────────────────────────────
        if st.button("🗑️  Clear Trade History", use_container_width=False):
            st.session_state.trade_history = []
            st.session_state.trade_counter = 0
            st.rerun()
