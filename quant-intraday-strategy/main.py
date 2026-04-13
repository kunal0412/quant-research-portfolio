import os
import pandas as pd
from data.data_loader import load_kaggle_data
from strategy.signals import generate_signals
from backtest.engine import generate_positions, apply_transaction_costs, run_backtest


# Build absolute path (prevents path issues)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(
    BASE_DIR,
    "data",
    "global_financial_markets_2000_Now.csv"
)


# Load data
df = load_kaggle_data(
    file_path,
    symbol="S&P500"   # You can change this later
)


# Preview data
print("\n--- HEAD ---")
print(df.head())

print("\n--- TAIL ---")
print(df.tail())

print("\n--- INFO ---")
print(df.info())


df = generate_signals(df)

print(df[['close', 'ema_50', 'ema_200', 'signal']].tail(20))

print("Total signals:", df['signal'].sum())

df = generate_positions(df)
df = apply_transaction_costs(df)
df = run_backtest(df)

print("\n--- FINAL OUTPUT ---")
print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())

print("Final Equity:", df['equity_curve'].iloc[-1])

def compute_trades(df):
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

    trades_df = pd.DataFrame(trades)

    return trades_df

trades_df = compute_trades(df)

print("Total Trades:", len(trades_df))

df['peak'] = df['equity_curve'].cummax()
df['drawdown'] = (df['equity_curve'] - df['peak']) / df['peak']

max_dd = df['drawdown'].min()
print("Max Drawdown:", max_dd)