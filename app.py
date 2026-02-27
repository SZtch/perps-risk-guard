# ============================================================
# PERPS RISK GUARD - Phase 1: Risk Engine (Terminal Version)
# Pacifica Hackathon | Analytics & Data Track
# ============================================================

# ----------------------------------------------------------
# SECTION 1: GET INPUTS FROM THE USER
# ----------------------------------------------------------

print("=" * 50)
print("   PERPS RISK GUARD - Risk Engine v1.0")
print("=" * 50)
print()

# Ask the user to type in their trade details
# float() converts the typed text into a decimal number

balance = float(input("Enter your account balance ($): "))
position_size = float(input("Enter your position size ($): "))
entry_price = float(input("Enter your entry price ($): "))
stop_loss_price = float(input("Enter your stop loss price ($): "))
leverage = float(input("Enter your leverage (e.g. 5 for 5x): "))

print()  # Print a blank line for spacing

# ----------------------------------------------------------
# SECTION 2: CALCULATIONS
# ----------------------------------------------------------

# A) Price difference between entry and stop loss
#    abs() makes sure the result is always positive,
#    whether the stop loss is above or below entry
price_difference = abs(entry_price - stop_loss_price)

# B) Percentage move from entry to stop loss
#    Example: entry=100, stop=95 → (5/100)*100 = 5%
percent_move = (price_difference / entry_price) * 100

# C) Risk amount in dollars
#    How many dollars you would LOSE if price hits stop loss
#    The percent_move tells us how much the price moves,
#    and we apply that to the full position size
risk_amount = (percent_move / 100) * position_size

# D) Risk percentage relative to account balance
#    How big is your loss compared to your total balance?
#    Example: lose $200 on a $1000 account = 20% risk
risk_percentage = (risk_amount / balance) * 100

# E) Effective exposure ratio
#    How much bigger is your position than your balance?
#    Example: $5000 position on $1000 balance = 5.0x exposure
exposure_ratio = position_size / balance

# ----------------------------------------------------------
# SECTION 3: RISK CLASSIFICATION
# ----------------------------------------------------------

# Check the risk percentage and assign a label
if risk_percentage < 5:
    risk_label = "✅ SAFE"
elif risk_percentage <= 15:
    risk_label = "⚠️  MEDIUM RISK"
else:
    risk_label = "🔴 HIGH RISK"

# ----------------------------------------------------------
# SECTION 4: PRINT THE RESULTS
# ----------------------------------------------------------

print("=" * 50)
print("         RISK ANALYSIS RESULTS")
print("=" * 50)

# round() limits decimal places so output looks clean
print(f"Price Difference:    ${round(price_difference, 4)}")
print(f"% Move to Stop Loss: {round(percent_move, 2)}%")
print(f"Risk Amount:         ${round(risk_amount, 2)}")
print(f"Risk % of Balance:   {round(risk_percentage, 2)}%")
print(f"Exposure Ratio:      {round(exposure_ratio, 2)}x")
print()
print(f"Risk Classification: {risk_label}")

# ----------------------------------------------------------
# SECTION 5: ADVERSE MOVE SIMULATION
# ----------------------------------------------------------
# This simulates what happens if the price moves AGAINST you
# by 1%, 2%, or 3% from your entry price.

print()
print("=" * 50)
print("     ADVERSE MOVE SIMULATION")
print("=" * 50)
print(f"{'Move':<10} {'Est. PnL':<15} {'New Balance'}")
print("-" * 45)

# We loop through 3 scenarios: 1%, 2%, 3% adverse move
for move_pct in [1, 2, 3]:

    # Calculate how much money is lost for this move size
    # A 1% adverse move on your position = 1% of position_size lost
    estimated_pnl = -1 * (move_pct / 100) * position_size

    # New balance = old balance + the PnL (which is negative = a loss)
    new_balance = balance + estimated_pnl

    # Print the row, formatted neatly
    print(f"-{move_pct}%{'':<8} -${abs(round(estimated_pnl, 2)):<13} ${round(new_balance, 2)}")

print("=" * 50)
print()
print("Analysis complete. Stay disciplined. Manage your risk.")
print()
