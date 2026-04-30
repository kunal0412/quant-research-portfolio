import numpy as np
import pandas as pd


def compute_performance(df, trades_df):
    equity = df['equity_curve']

    # =========================================
    # RETURNS
    # =========================================
    returns = equity.pct_change().fillna(0)

    # =========================================
    # TIME CALCULATION (INTRADAY SAFE)
    # =========================================
    total_minutes = (df.index[-1] - df.index[0]).total_seconds() / 60
    days = total_minutes / (60 * 24)
    years = days / 365 if days > 0 else 1

    # =========================================
    # CAGR
    # =========================================
    final_equity = equity.iloc[-1]
    cagr = (final_equity ** (1 / years)) - 1 if years > 0 else 0

    # =========================================
    # SHARPE (INTRADAY ADJUSTED)
    # =========================================
    sharpe = (returns.mean() / (returns.std() + 1e-9)) * np.sqrt(252)

    # =========================================
    # DRAWDOWN
    # =========================================
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    # =========================================
    # TRADE STATS
    # =========================================
    total_trades = len(trades_df)

    if total_trades > 0:
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] < 0]

        win_rate = len(wins) / total_trades

        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        # Handle both intraday + daily gracefully
        if 'holding_minutes' in trades_df.columns:
            avg_holding = trades_df['holding_minutes'].mean()
        elif 'holding_days' in trades_df.columns:
            avg_holding = trades_df['holding_days'].mean()
        else:
            avg_holding = 0

    else:
        win_rate = avg_win = avg_loss = expectancy = avg_holding = 0

    # =========================================
    # OUTPUT
    # =========================================
    return {
        "final_equity": float(final_equity),
        "cagr": float(cagr),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
        "total_trades": int(total_trades),
        "win_rate": float(win_rate),
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "expectancy": float(expectancy),
        "avg_holding": float(avg_holding),
    }