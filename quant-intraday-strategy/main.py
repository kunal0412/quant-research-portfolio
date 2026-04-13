import os
import pandas as pd

from data.data_loader import load_kaggle_data
from strategy.signals import generate_signals
from backtest.engine import run_backtest
from analytics.performance import compute_performance


# =========================================
# CONFIG
# =========================================

SYMBOL = "S&P500"
INITIAL_CAPITAL = 1.0
RISK_PER_TRADE = 0.02   # 2% risk


# =========================================
# LOAD DATA
# =========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(
    BASE_DIR,
    "data",
    "global_financial_markets_2000_Now.csv"
)

df = load_kaggle_data(file_path, symbol=SYMBOL)


# =========================================
# GENERATE SIGNALS
# =========================================

df = generate_signals(df)


# =========================================
# RUN BACKTEST
# =========================================

df, trades, engine_results = run_backtest(
    df,
    initial_capital=INITIAL_CAPITAL,
    risk_pct=RISK_PER_TRADE
)


# =========================================
# PERFORMANCE ANALYTICS
# =========================================

results = compute_performance(df, trades)


# =========================================
# OUTPUT
# =========================================

print("\n================ BACKTEST RESULTS ================\n")

for key, value in results.items():
    if isinstance(value, float):
        print(f"{key:25}: {value:.4f}")
    else:
        print(f"{key:25}: {value}")


print("\n--- Last 5 Rows ---")
print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())


# =========================================
# OPTIONAL: SAVE OUTPUTS
# =========================================

# Uncomment if needed
# df.to_csv("output_backtest.csv")
# trades.to_csv("output_trades.csv", index=False)