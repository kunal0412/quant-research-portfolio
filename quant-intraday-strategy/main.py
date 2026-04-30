import os
import pandas as pd
import numpy as np

from strategy.signals import generate_intraday_signals
from backtest.engine import run_backtest


# =========================================
# CONFIG
# =========================================

CONFIG = {
    "data_file": "NIFTY 50_minute.csv",
    "data_folder": "data",

    "initial_capital": 1.0,
    "risk_per_trade": 0.01,

    "output_file": "backtest_results.xlsx"
}


# =========================================
# PATH HANDLER
# =========================================

def get_data_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, CONFIG["data_folder"], CONFIG["data_file"])


# =========================================
# LOAD DATA (FAST + SAFE)
# =========================================

def load_data(file_path):

    df = pd.read_csv(file_path)

    print("Columns in CSV:", df.columns.tolist())

    if 'Date-Time' not in df.columns:
        raise ValueError("CSV must contain 'Date-Time' column")

    # ⚡ Faster datetime parsing
    df['Date-Time'] = pd.to_datetime(df['Date-Time'], errors='coerce')
    df.dropna(subset=['Date-Time'], inplace=True)

    df.set_index('Date-Time', inplace=True)

    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)

    df.sort_index(inplace=True)

    df.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Last': 'close',
        'Volume': 'volume'
    }, inplace=True)

    if '#RIC' in df.columns:
        df.drop(columns=['#RIC'], inplace=True)

    # ⚡ Vectorized numeric conversion
    df[['open', 'high', 'low', 'close', 'volume']] = df[
        ['open', 'high', 'low', 'close', 'volume']
    ].apply(pd.to_numeric, errors='coerce')

    df.dropna(inplace=True)

    return df


# =========================================
# PERFORMANCE ENGINE
# =========================================

def compute_performance(df, trades_df):

    equity = df['equity_curve']

    # -------------------------
    # TIME
    # -------------------------
    total_minutes = (df.index[-1] - df.index[0]).total_seconds() / 60
    years = (total_minutes / (60 * 24 * 365)) if total_minutes > 0 else 1

    # -------------------------
    # CAGR
    # -------------------------
    cagr = (equity.iloc[-1] ** (1 / years)) - 1 if years > 0 else 0

    # -------------------------
    # RETURNS
    # -------------------------
    returns = equity.pct_change().dropna()

    annual_factor = np.sqrt(252 * 24 * 60)

    sharpe = (returns.mean() / returns.std()) * annual_factor if returns.std() > 0 else 0

    downside = returns[returns < 0]
    sortino = (returns.mean() / downside.std()) * annual_factor if downside.std() > 0 else 0

    # -------------------------
    # DRAWDOWN
    # -------------------------
    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    # -------------------------
    # TRADE METRICS
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
        'max_drawdown': float(drawdown.min()),
        'total_trades': total_trades,
        'win_rate': float(win_rate),
        'avg_win_R': float(avg_win),
        'avg_loss_R': float(avg_loss),
        'expectancy_R': float(expectancy),
        'avg_holding_minutes': float(avg_holding)
    }


# =========================================
# EXPORT ENGINE
# =========================================

def export_results(df, trades_df, results):

    output_path = CONFIG["output_file"]

    trades_export = trades_df.copy()

    if 'R_multiple' not in trades_export.columns and 'pnl' in trades_export.columns:
        trades_export['R_multiple'] = trades_export['pnl'] / CONFIG["risk_per_trade"]

    equity_export = df[['equity_curve']].reset_index()
    summary_export = pd.DataFrame(list(results.items()), columns=['Metric', 'Value'])

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        trades_export.to_excel(writer, sheet_name='Trades', index=False)
        equity_export.to_excel(writer, sheet_name='Equity Curve', index=False)
        summary_export.to_excel(writer, sheet_name='Summary', index=False)

    print(f"\n✅ Excel exported to: {output_path}")


# =========================================
# MAIN PIPELINE
# =========================================

def main():

    print("\n🚀 Running Institutional Backtest Pipeline\n")

    # LOAD
    df = load_data(get_data_path())

    print("\n--- DATA CHECK ---")
    print(df.head())
    print("\nRows:", len(df))

    # SIGNALS
    df = generate_intraday_signals(df)
    print("\nSignals Generated:", int(df['signal'].sum()))

    # BACKTEST
    df, trades_df, _ = run_backtest(
        df,
        initial_capital=CONFIG["initial_capital"],
        risk_per_trade=CONFIG["risk_per_trade"]
    )

    # PERFORMANCE
    results = compute_performance(df, trades_df)

    # PRINT
    print("\n================ RESULTS ================\n")
    for k, v in results.items():
        print(f"{k:<25}: {v:.4f}" if isinstance(v, float) else f"{k:<25}: {v}")

    print("\n--- Last 5 Rows ---")
    print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())

    # EXPORT
    export_results(df, trades_df, results)


# =========================================
# ENTRY POINT
# =========================================

if __name__ == "__main__":
    main()