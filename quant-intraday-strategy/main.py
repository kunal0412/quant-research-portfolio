import os
import pandas as pd
import numpy as np

from strategy.signals import generate_intraday_signals
from backtest.engine import run_backtest


# =========================================
# CONFIG
# =========================================

INITIAL_CAPITAL = 1.0
RISK_PER_TRADE = 0.01   # 🔥 1% risk per trade


# =========================================
# LOAD DATA
# =========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(
    BASE_DIR,
    "data",
    "GCcv1.csv"
)

df = pd.read_csv(file_path)

print("Columns in CSV:", df.columns.tolist())


# =========================================
# DATETIME HANDLING
# =========================================

if 'Date-Time' in df.columns:
    df['Date-Time'] = pd.to_datetime(df['Date-Time'])
    df.set_index('Date-Time', inplace=True)
else:
    raise ValueError("CSV must contain 'Date-Time' column")

# Remove timezone if present
if df.index.tz is not None:
    df.index = df.index.tz_convert(None)

df = df.sort_index()


# =========================================
# RENAME COLUMNS
# =========================================

df.rename(columns={
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Last': 'close',
    'Volume': 'volume'
}, inplace=True)

if '#RIC' in df.columns:
    df.drop(columns=['#RIC'], inplace=True)


# =========================================
# CLEAN DATA
# =========================================

for col in ['open', 'high', 'low', 'close', 'volume']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(inplace=True)


# =========================================
# DEBUG INFO
# =========================================

print("\n--- DATA CHECK ---")
print(df.head())
print("\nColumns:", df.columns.tolist())
print("Total rows:", len(df))
print("Timezone:", df.index.tz)


# =========================================
# GENERATE SIGNALS
# =========================================

df = generate_intraday_signals(df)

print("\nTotal Signals Generated:", int(df['signal'].sum()))


# =========================================
# RUN BACKTEST
# =========================================

df, trades_df, results = run_backtest(
    df,
    initial_capital=INITIAL_CAPITAL,
    risk_per_trade=RISK_PER_TRADE
)


# =========================================
# PERFORMANCE METRICS
# =========================================

def compute_performance(df, trades_df):

    equity = df['equity_curve']

    # -------------------------
    # Time calculation
    # -------------------------
    total_minutes = (df.index[-1] - df.index[0]).total_seconds() / 60
    days = total_minutes / (60 * 24)
    years = days / 365 if days > 0 else 1

    # -------------------------
    # CAGR
    # -------------------------
    cagr = (equity.iloc[-1] ** (1 / years)) - 1 if years > 0 else 0

    # -------------------------
    # RETURNS (TIME-BASED)
    # -------------------------
    returns = equity.pct_change().dropna()

    # -------------------------
    # SHARPE RATIO (REAL)
    # -------------------------
    if returns.std() > 0:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252 * 24 * 60)
    else:
        sharpe = 0

    # -------------------------
    # SORTINO RATIO
    # -------------------------
    downside_returns = returns[returns < 0]

    if downside_returns.std() > 0:
        sortino = (returns.mean() / downside_returns.std()) * np.sqrt(252 * 24 * 60)
    else:
        sortino = 0

    # -------------------------
    # DRAWDOWN
    # -------------------------
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    # -------------------------
    # TRADE STATS
    # -------------------------
    total_trades = len(trades_df)

    if total_trades > 0:
        wins = trades_df[trades_df['return'] > 0]
        losses = trades_df[trades_df['return'] < 0]

        win_rate = len(wins) / total_trades

        avg_win = wins['return'].mean() if len(wins) > 0 else 0
        avg_loss = losses['return'].mean() if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        avg_holding = trades_df['holding_minutes'].mean()
    else:
        win_rate = avg_win = avg_loss = expectancy = avg_holding = 0

    return {
        'final_equity': float(equity.iloc[-1]),
        'cagr': float(cagr),
        'sharpe': float(sharpe),
        'sortino': float(sortino),
        'max_drawdown': float(max_dd),
        'total_trades': total_trades,
        'win_rate': float(win_rate),
        'avg_win_R': float(avg_win),
        'avg_loss_R': float(avg_loss),
        'expectancy_R': float(expectancy),
        'avg_holding_minutes': float(avg_holding)
    }


results = compute_performance(df, trades_df)


# =========================================
# OUTPUT
# =========================================

print("\n================ BACKTEST RESULTS ================\n")

for k, v in results.items():
    if isinstance(v, float):
        print(f"{k:<25}: {v:.4f}")
    else:
        print(f"{k:<25}: {v}")

print("\n--- Last 5 Rows ---")
print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())


# =========================================
# OPTIONAL SAVE
# =========================================

#trades_df.to_csv("gc_intraday_trades.csv", index=False)
#df.to_csv("gc_intraday_equity.csv")