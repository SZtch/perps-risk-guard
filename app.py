import streamlit as st
import pandas as pd
import requests

# ==========================================
# CONFIG
# ==========================================

st.set_page_config(page_title="Perps Risk Guard", layout="wide")

PRICES_ENDPOINT  = "https://api.pacifica.exchange/prices"
MARKETS_ENDPOINT = "https://api.pacifica.exchange/markets"

# ==========================================
# INITIAL SESSION STATE
# ==========================================

if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

if "trade_counter" not in st.session_state:
    st.session_state.trade_counter = 0

# ==========================================
# API FUNCTIONS
# ==========================================

def fetch_prices():
    try:
        response = requests.get(PRICES_ENDPOINT, timeout=5)
        data = response.json()
        return data
    except:
        return {}

def fetch_markets():
    try:
        response = requests.get(MARKETS_ENDPOINT, timeout=5)
        data = response.json()
        return data
    except:
        return {}

# ==========================================
# HEADER
# ==========================================

st.title("🛡️ Perps Risk Guard")
st.caption("Risk analytics & trade intelligence dashboard for perpetual traders.")

tab1, tab2, tab3 = st.tabs(["📊 Risk Calculator", "📋 Trade Analytics", "🌐 Live Market"])

# ==========================================
# TAB 1 — RISK CALCULATOR
# ==========================================

with tab1:

    balance       = st.number_input("Account Balance ($)", min_value=0.0)
    position_size = st.number_input("Position Size ($)", min_value=0.0)
    entry         = st.number_input("Entry Price ($)", min_value=0.0)
    stop          = st.number_input("Stop Loss ($)", min_value=0.0)
    take_profit   = st.number_input("Take Profit ($)", min_value=0.0)
    leverage      = st.number_input("Leverage", min_value=1.0)

    if st.button("Calculate Risk"):

        if entry == 0 or balance == 0:
            st.error("Entry price and balance must be greater than 0.")
            st.stop()

        price_diff = abs(entry - stop)
        move_pct   = (price_diff / entry) * 100
        risk_amt   = (move_pct / 100) * position_size
        risk_pct   = (risk_amt / balance) * 100
        exposure   = position_size / balance

        reward_amt = abs(take_profit - entry) / entry * position_size if take_profit > 0 else 0
        rr_ratio   = reward_amt / risk_amt if risk_amt != 0 else 0

        if risk_pct < 5:
            classification = "SAFE"
            st.success("SAFE")
        elif risk_pct <= 15:
            classification = "MEDIUM RISK"
            st.warning("MEDIUM RISK")
        else:
            classification = "HIGH RISK"
            st.error("HIGH RISK")

        st.write("### 📊 Results")
        st.write(f"Price Difference: ${price_diff:.4f}")
        st.write(f"% Move to Stop: {move_pct:.2f}%")
        st.write(f"Risk Amount: ${risk_amt:.2f}")
        st.write(f"Risk % of Balance: {risk_pct:.2f}%")
        st.write(f"Exposure Ratio: {exposure:.2f}x")
        st.write(f"Reward Amount: ${reward_amt:.2f}")
        st.write(f"Risk/Reward Ratio: 1 : {rr_ratio:.2f}")

        st.divider()

        st.write("### 📉 Adverse Move Simulation")

        for pct in [1, 2, 3]:
            pnl = -(pct / 100) * position_size
            new_balance = balance + pnl
            st.write(f"-{pct}% move → PnL: ${pnl:.2f} | New Balance: ${new_balance:.2f}")

        # Save trade
        st.session_state.trade_counter += 1

        st.session_state.trade_history.append({
            "Trade #": st.session_state.trade_counter,
            "Entry": entry,
            "Stop Loss": stop,
            "Take Profit": take_profit,
            "Leverage": leverage,
            "Risk Amount": risk_amt,
            "Risk %": risk_pct,
            "Reward Amount": reward_amt,
            "RR Ratio": rr_ratio,
            "Classification": classification
        })

# ==========================================
# TAB 2 — TRADE ANALYTICS
# ==========================================

with tab2:

    if not st.session_state.trade_history:
        st.info("No trades analyzed yet.")
        st.stop()

    df = pd.DataFrame(st.session_state.trade_history)

    st.subheader("Trade History")
    st.dataframe(df.set_index("Trade #"), use_container_width=True)

    st.divider()

    st.subheader("Session Analytics")

    total_trades = len(df)
    avg_risk_pct = df["Risk %"].mean()
    avg_rr       = df["RR Ratio"].mean()
    best_rr      = df["RR Ratio"].max()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", total_trades)
    col2.metric("Avg Risk %", f"{avg_risk_pct:.2f}%")
    col3.metric("Avg RR", f"1 : {avg_rr:.2f}")
    col4.metric("Best RR", f"1 : {best_rr:.2f}")

    st.divider()

    st.subheader("Risk vs Reward")
    st.bar_chart(df[["Trade #", "Risk Amount", "Reward Amount"]].set_index("Trade #"))

    st.subheader("Risk % per Trade")
    st.line_chart(df[["Trade #", "Risk %"]].set_index("Trade #"))

    if st.button("Clear History"):
        st.session_state.trade_history = []
        st.session_state.trade_counter = 0
        st.rerun()

# ==========================================
# TAB 3 — LIVE MARKET (Pacifica API)
# ==========================================

with tab3:

    st.subheader("Live Market Data")

    prices  = fetch_prices()
    markets = fetch_markets()

    if not prices:
        st.error("Could not connect to Pacifica API.")
    else:
        rows = []

        for symbol, mark_price in prices.items():
            market_data = markets.get(symbol, {})
            funding = float(market_data.get("funding_rate") or 0)

            rows.append({
                "Symbol": symbol,
                "Mark Price": f"${float(mark_price):,.4f}",
                "Max Leverage": f"{market_data.get('max_leverage', '-')}",
                "Funding Rate": f"{funding * 100:.4f}%"
            })

        market_df = pd.DataFrame(rows).set_index("Symbol")
        st.dataframe(market_df, use_container_width=True)

        st.caption(f"{len(rows)} markets loaded from Pacifica API.")
