# ============================================================
# PERPS RISK GUARD - Phase 2: Streamlit Web App
# Pacifica Hackathon | Analytics & Data Track
# ============================================================

import streamlit as st

# ----------------------------------------------------------
# PAGE CONFIG - Harus di baris paling atas
# ----------------------------------------------------------

st.set_page_config(
    page_title="Perps Risk Guard",
    page_icon="⚡",
    layout="centered"
)

# ----------------------------------------------------------
# TITLE & DESCRIPTION
# ----------------------------------------------------------

st.title("⚡ Perps Risk Guard")
st.write("Hitung risiko trading kamu sebelum masuk posisi.")
st.write("---")

# ----------------------------------------------------------
# SECTION 1: INPUT FIELDS
# ----------------------------------------------------------

st.subheader("📥 Masukkan Detail Trade")

balance = st.number_input(
    "Account Balance ($)",
    min_value=1.0,
    value=1000.0,
    step=100.0
)

position_size = st.number_input(
    "Position Size ($)",
    min_value=1.0,
    value=5000.0,
    step=100.0
)

entry_price = st.number_input(
    "Entry Price ($)",
    min_value=0.01,
    value=100.0,
    step=1.0
)

stop_loss_price = st.number_input(
    "Stop Loss Price ($)",
    min_value=0.01,
    value=95.0,
    step=1.0
)

leverage = st.number_input(
    "Leverage (contoh: 5 untuk 5x)",
    min_value=1.0,
    value=5.0,
    step=1.0
)

st.write("---")

# ----------------------------------------------------------
# SECTION 2: TOMBOL HITUNG
# ----------------------------------------------------------

if st.button("🔍 Hitung Risiko"):

    # Validasi: stop loss tidak boleh sama dengan entry
    if entry_price == stop_loss_price:
        st.error("❌ Entry price dan stop loss price tidak boleh sama!")

    # Validasi: position size tidak boleh lebih besar dari balance x leverage
    elif position_size > balance * leverage:
        st.error("❌ Position size terlalu besar untuk balance dan leverage yang kamu masukkan.")

    else:

        # ------------------------------------------------------
        # KALKULASI
        # ------------------------------------------------------

        # A) Selisih harga entry dan stop loss
        price_difference = abs(entry_price - stop_loss_price)

        # B) Persentase pergerakan ke stop loss
        percent_move = (price_difference / entry_price) * 100

        # C) Jumlah uang yang berisiko (dalam dolar)
        risk_amount = (percent_move / 100) * position_size

        # D) Persentase risiko terhadap balance
        risk_percentage = (risk_amount / balance) * 100

        # E) Rasio exposure
        exposure_ratio = position_size / balance

        # ------------------------------------------------------
        # TAMPILKAN HASIL
        # ------------------------------------------------------

        st.subheader("📊 Hasil Analisis Risiko")

        # Tampilkan 3 metrik utama dalam 3 kolom
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Risk Amount", f"${round(risk_amount, 2)}")

        with col2:
            st.metric("Risk % of Balance", f"{round(risk_percentage, 2)}%")

        with col3:
            st.metric("Exposure Ratio", f"{round(exposure_ratio, 2)}x")

        # Info tambahan
        st.write(f"**Selisih Harga:** ${round(price_difference, 4)}")
        st.write(f"**% Gerak ke Stop Loss:** {round(percent_move, 2)}%")
        st.write(f"**Leverage Dipakai:** {leverage}x")

        st.write("---")

        # ------------------------------------------------------
        # SECTION 3: KLASIFIKASI RISIKO
        # ------------------------------------------------------

        st.subheader("🚦 Klasifikasi Risiko")

        if risk_percentage < 5:
            st.success("✅ SAFE — Risiko kamu masih dalam batas sehat.")
        elif risk_percentage <= 15:
            st.warning("⚠️ MEDIUM RISK — Pertimbangkan untuk kurangi position size.")
        else:
            st.error("🔴 HIGH RISK — Trade ini mempertaruhkan terlalu banyak dari balance kamu!")

        st.write("---")

        # ------------------------------------------------------
        # SECTION 4: SIMULASI ADVERSE MOVE
        # ------------------------------------------------------

        st.subheader("📉 Simulasi Pergerakan Negatif")
        st.write("Apa yang terjadi jika harga bergerak melawan posisi kamu?")

        # Buat data simulasi untuk ditampilkan sebagai tabel
        simulation_data = []

        for move_pct in [1, 2, 3]:
            # Kerugian estimasi untuk pergerakan sebesar move_pct%
            estimated_pnl = -1 * (move_pct / 100) * position_size

            # Balance baru setelah kerugian
            new_balance = balance + estimated_pnl

            # Tambahkan baris ke data simulasi
            simulation_data.append({
                "Pergerakan Negatif": f"-{move_pct}%",
                "Estimasi PnL ($)": f"-${abs(round(estimated_pnl, 2))}",
                "Balance Baru ($)": f"${round(new_balance, 2)}"
            })

        # Tampilkan tabel simulasi
        st.table(simulation_data)

        st.write("---")
        st.info("💡 Disiplin dalam manajemen risiko adalah kunci survival di pasar.")
