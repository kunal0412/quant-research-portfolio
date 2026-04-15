import os
import pandas as pd

from strategy.signals import generate_intraday_signals
from backtest.engine import run_backtest


# =========================================
# CONFIG
# =========================================

INITIAL_CAPITAL = 1.0
RISK_PER_TRADE = 0.02
SLIPPAGE = 0.0005


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
# DATETIME (BLOOMBERG FIX)
# =========================================

df['Date-Time'] = pd.to_datetime(df['Date-Time'])
df.set_index('Date-Time', inplace=True)

# Convert UTC → naive (cleaner for pandas ops)
df.index = df.index.tz_convert(None)


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


# =========================================
# DROP UNUSED COLUMN
# =========================================

if '#RIC' in df.columns:
    df.drop(columns=['#RIC'], inplace=True)


# =========================================
# CLEAN DATA
# =========================================

df = df.sort_index()

for col in ['open', 'high', 'low', 'close']:
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
    risk_pct=RISK_PER_TRADE,
    slippage=SLIPPAGE
)


# =========================================
# PERFORMANCE METRICS
# =========================================

def compute_performance(df, trades_df):

    equity = df['equity_curve']

    # Time calculation
    total_minutes = (df.index[-1] - df.index[0]).total_seconds() / 60
    days = total_minutes / (60 * 24)
    years = days / 365 if days > 0 else 1

    # CAGR
    cagr = (equity.iloc[-1] ** (1 / years)) - 1 if years > 0 else 0

    # Sharpe (intraday approx)
    returns = equity.pct_change().fillna(0)
    sharpe = (returns.mean() / (returns.std() + 1e-9)) * (252 ** 0.5)

    # Drawdown
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    # Trade stats
    total_trades = len(trades_df)

    if total_trades > 0:
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] < 0]

        win_rate = len(wins) / total_trades
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        avg_holding = trades_df['holding_minutes'].mean()
    else:
        win_rate = avg_win = avg_loss = expectancy = avg_holding = 0

    return {
        'final_equity': float(equity.iloc[-1]),
        'cagr': float(cagr),
        'sharpe': float(sharpe),
        'max_drawdown': float(max_dd),
        'total_trades': total_trades,
        'win_rate': float(win_rate),
        'avg_win': float(avg_win),
        'avg_loss': float(avg_loss),
        'expectancy': float(expectancy),
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

# trades_df.to_csv("gc_intraday_trades.csv", index=False)
# df.to_csv("gc_intraday_equity.csv")