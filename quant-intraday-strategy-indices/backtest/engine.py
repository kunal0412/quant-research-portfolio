import numpy as np
import pandas as pd


def run_backtest(
    df,
    initial_capital=1.0,
    risk_per_trade=0.01,
    sl_pct=0.006,
    tp_pct=0.012,
    max_positions=1
):

    # =========================================
    # PRE-EXTRACT ARRAYS (FAST)
    # =========================================
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    signal = df['signal'].values
    time_index = df.index

    n = len(df)

    capital = initial_capital

    open_trades = []
    closed_trades = []

    position_arr = np.zeros(n)
    capital_arr = np.zeros(n)
    equity_arr = np.zeros(n)

    # =========================================
    # MAIN LOOP
    # =========================================
    for i in range(n):

        price = close[i]
        current_time = time_index[i]

        # =========================
        # ENTRY (LONG + SHORT)
        # =========================
        if signal[i] != 0 and len(open_trades) < max_positions and capital > 0:

            direction = signal[i]  # +1 or -1
            entry_price = price

            # -------------------------
            # SL / TP (direction-aware)
            # -------------------------
            if direction == 1:  # LONG
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                risk_per_unit = entry_price - sl_price

            else:  # SHORT
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                risk_per_unit = sl_price - entry_price

            if risk_per_unit > 0:
                size = risk_per_trade / risk_per_unit

                open_trades.append({
                    'direction': direction,
                    'entry_price': entry_price,
                    'sl': sl_price,
                    'tp': tp_price,
                    'size': size,
                    'entry_time': current_time
                })

        # =========================
        # EXIT LOGIC
        # =========================
        remaining_trades = []

        for trade in open_trades:

            direction = trade['direction']
            exit_flag = False
            exit_price = price

            # -------------------------
            # STOP LOSS / TAKE PROFIT
            # -------------------------
            if direction == 1:  # LONG
                if low[i] <= trade['sl']:
                    exit_price = trade['sl']
                    exit_flag = True

                elif high[i] >= trade['tp']:
                    exit_price = trade['tp']
                    exit_flag = True

            else:  # SHORT
                if high[i] >= trade['sl']:
                    exit_price = trade['sl']
                    exit_flag = True

                elif low[i] <= trade['tp']:
                    exit_price = trade['tp']
                    exit_flag = True

            # -------------------------
            # NSE END-OF-DAY EXIT
            # -------------------------
            if not exit_flag:
                if current_time.time() >= pd.to_datetime("15:25").time():
                    exit_flag = True
                    exit_price = price

            # -------------------------
            # EXECUTE EXIT
            # -------------------------
            if exit_flag:

                pnl = (exit_price - trade['entry_price']) * trade['size'] * direction
                capital += pnl

                closed_trades.append({
                    'entry_time': trade['entry_time'],
                    'exit_time': current_time,
                    'direction': direction,
                    'entry_price': trade['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'return': pnl / risk_per_trade,
                    'holding_minutes': (current_time - trade['entry_time']).total_seconds() / 60
                })

            else:
                remaining_trades.append(trade)

        open_trades = remaining_trades

        # =========================
        # MARK-TO-MARKET EQUITY
        # =========================
        unrealized_pnl = 0

        for trade in open_trades:
            unrealized_pnl += (
                (price - trade['entry_price']) *
                trade['size'] *
                trade['direction']
            )

        equity = capital + unrealized_pnl

        # =========================
        # STORE STATE
        # =========================
        position_arr[i] = len(open_trades)
        capital_arr[i] = capital
        equity_arr[i] = equity

    # =========================================
    # FINALIZE DF
    # =========================================
    df['position'] = position_arr
    df['capital'] = capital_arr
    df['equity_curve'] = equity_arr

    trades_df = pd.DataFrame(closed_trades)

    # =========================================
    # BASIC METRICS
    # =========================================
    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    results = {
        'final_equity': float(equity.iloc[-1]),
        'max_drawdown': float(drawdown.min()),
        'total_trades': len(trades_df)
    }

    return df, trades_df, results