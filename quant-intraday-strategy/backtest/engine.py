import numpy as np
import pandas as pd


def run_backtest(
    df,
    initial_capital=1.0,
    risk_per_trade=0.01,   # FIXED risk (1%)
    sl_pct=0.006,          # 0.6% SL
    tp_pct=0.012,          # 1.2% TP
    max_positions=3
):

    df = df.copy()

    capital = initial_capital

    open_trades = []
    closed_trades = []

    position_arr = []
    capital_arr = []
    equity_arr = []

    for i in range(len(df)):

        row = df.iloc[i]
        price = row['close']
        signal = row['signal']
        current_time = df.index[i]

        # =========================
        # NEW TRADE ENTRY
        # =========================
        if signal == 1 and len(open_trades) < max_positions:

            entry_price = price

            sl_price = entry_price * (1 - sl_pct)
            tp_price = entry_price * (1 + tp_pct)

            risk_per_unit = entry_price - sl_price

            if risk_per_unit > 0:
                position_size = risk_per_trade / risk_per_unit

                open_trades.append({
                    'entry_price': entry_price,
                    'sl': sl_price,
                    'tp': tp_price,
                    'size': position_size,
                    'entry_time': current_time
                })

        # =========================
        # MANAGE OPEN TRADES
        # =========================
        remaining_trades = []

        for trade in open_trades:

            exit_flag = False
            exit_price = price

            # STOP LOSS
            if row['low'] <= trade['sl']:
                exit_price = trade['sl']
                exit_flag = True

            # TAKE PROFIT
            elif row['high'] >= trade['tp']:
                exit_price = trade['tp']
                exit_flag = True

            # INTRADAY SQUARE OFF (2nd last candle)
            elif i < len(df) - 1:
                next_day = df.index[i + 1].date()
                if current_time.date() != next_day:
                    exit_flag = True
                    exit_price = price

            if exit_flag:

                pnl = (exit_price - trade['entry_price']) * trade['size']
                capital += pnl

                ret = pnl / risk_per_trade

                closed_trades.append({
                    'entry_time': trade['entry_time'],
                    'exit_time': current_time,
                    'entry_price': trade['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'return': ret,
                    'holding_minutes': (current_time - trade['entry_time']).total_seconds() / 60
                })

            else:
                remaining_trades.append(trade)

        open_trades = remaining_trades

        # =========================
        # STORE STATE
        # =========================
        position_arr.append(len(open_trades))
        capital_arr.append(capital)
        equity_arr.append(capital)

    df['position'] = position_arr
    df['capital'] = capital_arr
    df['equity_curve'] = equity_arr

    trades_df = pd.DataFrame(closed_trades)

    # =========================
    # METRICS
    # =========================
    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    results = {
        'final_equity': float(equity.iloc[-1]),
        'max_drawdown': float(drawdown.min()),
        'total_trades': len(trades_df)
    }

    return df, trades_df, results