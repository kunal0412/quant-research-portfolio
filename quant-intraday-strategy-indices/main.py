import os
import pandas as pd
import numpy as np

from strategy.signals import generate_intraday_signals
from backtest.engine import run_backtest


# =========================================
# CONFIG
# =========================================

CONFIG = {
    "data_file": "NIFTY50_minute.csv",
    "data_folder": "data",

    "initial_capital": 10_000_000,   # ₹1 crore
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
# LOAD DATA
# =========================================

def load_data(file_path):

    print(f"\n📂 Loading file from: {file_path}\n")

    df = pd.read_csv(file_path)

    df.columns = [col.lower().strip() for col in df.columns]

    print("Columns detected:", df.columns.tolist())

    if 'date' not in df.columns:
        raise ValueError("Expected 'date' column in CSV")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    df.set_index('date', inplace=True)

    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)

    df.sort_index(inplace=True)

    required_cols = ['open', 'high', 'low', 'close']

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    if 'volume' not in df.columns:
        print("⚠️ Volume missing → using dummy volume")
        df['volume'] = 1

    df[required_cols + ['volume']] = df[
        required_cols + ['volume']
    ].apply(pd.to_numeric, errors='coerce')

    df.dropna(inplace=True)

    print("\n✅ Data Loaded Successfully")
    print("Rows:", len(df))
    print(df.head())

    return df


# =========================================
# PERFORMANCE (FIXED CAGR)
# =========================================

def compute_performance(df, trades_df):

    equity = df['equity_curve']

    initial_capital = equity.iloc[0]
    final_equity = equity.iloc[-1]

    # =========================
    # TIME (FIXED)
    # =========================
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25 if days > 0 else 1

    # =========================
    # RETURNS
    # =========================
    returns = equity.pct_change().dropna()

    annual_factor = np.sqrt(252 * 375)

    sharpe = (returns.mean() / returns.std()) * annual_factor if returns.std() > 0 else 0

    downside = returns[returns < 0]
    sortino = (returns.mean() / downside.std()) * annual_factor if downside.std() > 0 else 0

    # =========================
    # CAGR (FIXED)
    # =========================
    cagr = (final_equity / initial_capital) ** (1 / years) - 1 if years > 0 else 0

    # =========================
    # DRAWDOWN
    # =========================
    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    # =========================
    # TRADE METRICS
    # =========================
    total_trades = len(trades_df)

    if total_trades > 0:

        wins = trades_df[trades_df['net_pnl'] > 0]
        losses = trades_df[trades_df['net_pnl'] < 0]

        win_rate = len(wins) / total_trades

        avg_win = wins['net_pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['net_pnl'].mean() if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        avg_holding = trades_df['holding_minutes'].mean()
        total_cost = trades_df['cost'].sum()

    else:
        win_rate = avg_win = avg_loss = expectancy = avg_holding = total_cost = 0

    return {
        'final_equity': float(final_equity),
        'cagr': float(cagr),
        'sharpe': float(sharpe),
        'sortino': float(sortino),
        'max_drawdown': float(drawdown.min()),
        'total_trades': total_trades,
        'win_rate': float(win_rate),
        'avg_win_₹': float(avg_win),
        'avg_loss_₹': float(avg_loss),
        'expectancy_₹': float(expectancy),
        'total_costs_₹': float(total_cost),
        'avg_holding_minutes': float(avg_holding)
    }


# =========================================
# EXPORT
# =========================================

def export_results(df, trades_df, results):

    output_path = CONFIG["output_file"]

    equity_export = df[['equity_curve']].reset_index()
    summary_export = pd.DataFrame(list(results.items()), columns=['Metric', 'Value'])

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        trades_df.to_excel(writer, sheet_name='Trades', index=False)
        equity_export.to_excel(writer, sheet_name='Equity Curve', index=False)
        summary_export.to_excel(writer, sheet_name='Summary', index=False)

    print(f"\n📊 Results exported to: {output_path}")


# =========================================
# MAIN
# =========================================

def main():

    print("\n🚀 NIFTY Backtest (Corrected & Realistic)\n")

    df = load_data(get_data_path())

    df = generate_intraday_signals(df)

    print("\n📡 Signals Generated:", int(df['signal'].abs().sum()))

    df, trades_df, _ = run_backtest(
        df,
        initial_capital=CONFIG["initial_capital"],
        risk_per_trade=CONFIG["risk_per_trade"]
    )

    results = compute_performance(df, trades_df)

    print("\n================ RESULTS ================\n")
    for k, v in results.items():
        print(f"{k:<25}: {v:.4f}" if isinstance(v, float) else f"{k:<25}: {v}")

    print("\n--- Last 5 Rows ---")
    print(df[['close', 'signal', 'position', 'capital', 'equity_curve']].tail())

    export_results(df, trades_df, results)


if __name__ == "__main__":
    main()