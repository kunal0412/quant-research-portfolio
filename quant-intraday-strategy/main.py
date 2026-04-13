import os
import pandas as pd

from data.data_loader import load_kaggle_data
from strategy.signals import generate_signals
from backtest.engine import run_backtest


# =========================================
# CONFIG
# =========================================

SYMBOL = "S&P500"
INITIAL_CAPITAL = 1
RISK_PER_TRADE = 0.01   # 1% risk per trade


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

df, trades, results = run_backtest(df)


# =========================================
# OUTPUT RESULTS
# =========================================

print("\n================ BACKTEST RESULTS ================\n")

print(f"Final Equity        : {results['final_equity']:.4f}")
print(f"Max Drawdown        : {results['max_drawdown']:.4f}")
print(f"Total Trades        : {results['total_trades']}")

if results['total_trades'] > 0:
    print("\n--- Trade Stats ---")
    print(f"Win Rate            : {results['win_rate']:.4f}")
    print(f"Avg Win             : {results['avg_win']:.4f}")
    print(f"Avg Loss            : {results['avg_loss']:.4f}")
    print(f"Expectancy          : {results['expectancy']:.4f}")
    print(f"Avg Holding (days)  : {results['avg_holding_days']:.2f}")

# =========================================
# OPTIONAL: SAVE TRADES (FOR ANALYSIS)
# =========================================

# Uncomment if you want to inspect trades
# trades.to_csv(os.path.join(BASE_DIR, "trades.csv"), index=False)


# =========================================
# LAST FEW ROWS (SANITY CHECK)
# =========================================

print("\n--- Last 5 Rows ---")
print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())