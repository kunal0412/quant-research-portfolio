import pandas as pd
import numpy as np

from strategy.signals import generate_intraday_signals


# =========================================
# LOAD DATA
# =========================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(
    BASE_DIR,
    "data",
    "GCcv1.csv"
)

df = pd.read_csv(file_path)

df['Date-Time'] = pd.to_datetime(df['Date-Time'])
df.set_index('Date-Time', inplace=True)

df.rename(columns={
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Last': 'close',
    'Volume': 'volume'
}, inplace=True)

df = df.sort_index()
df.drop(columns=['#RIC'], errors='ignore', inplace=True)

for col in ['open', 'high', 'low', 'close']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(inplace=True)


# =========================================
# SIGNALS
# =========================================

df = generate_intraday_signals(df)


# =========================================
# MFE / MAE ANALYSIS
# =========================================

trades = []

for i in range(len(df)):

    if df['signal'].iloc[i] == 1:

        entry_price = df['close'].iloc[i]
        entry_time = df.index[i]

        # get same day data
        same_day = df[df.index.date == entry_time.date()]

        future = same_day[same_day.index >= entry_time]

        if len(future) == 0:
            continue

        max_high = future['high'].max()
        min_low = future['low'].min()

        max_up = (max_high - entry_price) / entry_price
        max_down = (min_low - entry_price) / entry_price

        trades.append({
            'entry_time': entry_time,
            'max_up': max_up,
            'max_down': max_down
        })


trades_df = pd.DataFrame(trades)


# =========================================
# RESULTS
# =========================================

print("\n===== MFE / MAE STATS =====\n")

print(trades_df.describe())

print("\n--- Quantiles ---\n")

print("Max Up:")
print(trades_df['max_up'].quantile([0.5, 0.7, 0.8, 0.9]))

print("\nMax Down:")
print(trades_df['max_down'].quantile([0.1, 0.2, 0.3, 0.5]))