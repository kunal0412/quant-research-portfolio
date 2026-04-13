import os
import pandas as pd

from data.data_loader import load_kaggle_data
from strategy.signals import generate_signals
from backtest.engine import generate_positions, run_backtest


# =========================================
# CONFIG
# =========================================

SYMBOL = "S&P500"
INITIAL_CAPITAL = 1
RISK_PER_TRADE = 0.01   # 1% risk


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
# RUN BACKTEST ENGINE
# =========================================

df = generate_positions(
    df,
    initial_capital=INITIAL_CAPITAL,
    risk_pct=RISK_PER_TRADE
)

df = run_backtest(df)


# =========================================
# TRADE ANALYTICS
# =========================================

def compute_trades(df):
    """
    Extracts completed trades with return and holding period.
    """

    trades = []

    in_trade = False
    entry_price = 0
    entry_time = None

    for i in range(len(df)):
        pos = df['position'].iloc[i]

        # ENTRY
        if not in_trade and pos == 1:
            in_trade = True
            entry_price = df['close'].iloc[i]
            entry_time = df.index[i]

        # EXIT
        elif in_trade and pos == 0:
            exit_price = df['close'].iloc[i]
            exit_time = df.index[i]

            ret = (exit_price / entry_price) - 1
            duration = (exit_time - entry_time).days

            trades.append({
                'return': ret,
                'duration_days': duration
            })

            in_trade = False

    return pd.DataFrame(trades)


trades_df = compute_trades(df)


# =========================================
# PERFORMANCE METRICS
# =========================================

# Final equity
final_equity = df['equity_curve'].iloc[-1]

# Drawdown
df['peak'] = df['equity_curve'].cummax()
df['drawdown'] = (df['equity_curve'] - df['peak']) / df['peak']
max_dd = df['drawdown'].min()

# Trade stats
total_trades = len(trades_df)

if total_trades > 0:
    win_rate = (trades_df['return'] > 0).mean()
    avg_win = trades_df[trades_df['return'] > 0]['return'].mean()
    avg_loss = trades_df[trades_df['return'] < 0]['return'].mean()
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    avg_holding = trades_df['duration_days'].mean()
else:
    win_rate = avg_win = avg_loss = expectancy = avg_holding = 0


# =========================================
# OUTPUT
# =========================================

print("\n================ BACKTEST RESULTS ================\n")

print("Final Equity        :", round(final_equity, 4))
print("Max Drawdown        :", round(max_dd, 4))
print("Total Trades        :", total_trades)

print("\n--- Trade Stats ---")
print("Win Rate            :", round(win_rate, 4))
print("Avg Win             :", round(avg_win, 4))
print("Avg Loss            :", round(avg_loss, 4))
print("Expectancy          :", round(expectancy, 4))
print("Avg Holding (days)  :", round(avg_holding, 2))

print("\n--- Last 5 Rows ---")
print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())