import os
import pandas as pd
import numpy as np

from data.data_loader import load_kaggle_data
from strategy.signals import generate_signals
from backtest.engine import run_backtest


# =========================================
# CONFIG
# =========================================

SYMBOL = "S&P500"
INITIAL_CAPITAL = 1.0
RISK_PER_TRADE = 0.02


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

print("Total Signals Generated:", int(df['signal'].sum()))


# =========================================
# RUN BACKTEST
# =========================================

df, trades, results = run_backtest(
    df,
    initial_capital=INITIAL_CAPITAL,
    risk_pct=RISK_PER_TRADE
)


# =========================================
# EXTRA PERFORMANCE METRICS
# =========================================

equity = df['equity_curve']

# CAGR
years = (df.index[-1] - df.index[0]).days / 365
cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1

# Returns
df['returns'] = equity.pct_change().fillna(0)

# Sharpe
sharpe = np.sqrt(252) * df['returns'].mean() / (df['returns'].std() + 1e-9)

# Drawdown
peak = equity.cummax()
drawdown = (equity - peak) / peak
max_dd = drawdown.min()

# Trade stats
if len(trades) > 0:
    trades_df = trades.copy()

    wins = trades_df[trades_df['pnl'] > 0]
    losses = trades_df[trades_df['pnl'] <= 0]

    win_rate = len(wins) / len(trades_df)
    avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
    avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0

    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    avg_holding = trades_df['holding_days'].mean()
else:
    win_rate = avg_win = avg_loss = expectancy = avg_holding = 0


# =========================================
# OUTPUT
# =========================================

print("\n================ BACKTEST RESULTS ================\n")

print(f"{'Final Equity':25}: {equity.iloc[-1]:.4f}")
print(f"{'CAGR':25}: {cagr:.4f}")
print(f"{'Sharpe':25}: {sharpe:.4f}")
print(f"{'Max Drawdown':25}: {max_dd:.4f}")
print(f"{'Total Trades':25}: {len(trades)}")

print("\n--- Trade Stats ---")
print(f"{'Win Rate':25}: {win_rate:.4f}")
print(f"{'Avg Win':25}: {avg_win:.4f}")
print(f"{'Avg Loss':25}: {avg_loss:.4f}")
print(f"{'Expectancy':25}: {expectancy:.4f}")
print(f"{'Avg Holding Days':25}: {avg_holding:.2f}")

print("\n--- Last 5 Rows ---")
print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())