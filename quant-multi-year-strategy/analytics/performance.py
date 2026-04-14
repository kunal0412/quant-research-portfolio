import numpy as np
import pandas as pd


def compute_performance(df, trades_df):
    equity = df['equity_curve']

    # Returns
    returns = equity.pct_change().fillna(0)

    # Sharpe Ratio (assuming daily data)
    sharpe = np.sqrt(252) * returns.mean() / (returns.std() + 1e-9)

    # Drawdown
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    # CAGR
    years = (df.index[-1] - df.index[0]).days / 365
    cagr = (equity.iloc[-1] ** (1 / years)) - 1

    # Trade stats
    total_trades = len(trades_df)

    if total_trades > 0:
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]

        win_rate = len(wins) / total_trades
        avg_win = wins['pnl'].mean()
        avg_loss = losses['pnl'].mean()

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        avg_holding = trades_df['holding_days'].mean()
    else:
        win_rate = avg_win = avg_loss = expectancy = avg_holding = 0

    return {
        "final_equity": equity.iloc[-1],
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "avg_holding_days": avg_holding
    }