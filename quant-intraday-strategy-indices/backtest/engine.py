import numpy as np
import pandas as pd


def run_backtest(
    df,
    initial_capital=10_000_000,   # ₹1 crore example
    risk_per_trade=0.01,

    # Execution realism
    sl_pct=0.007,   # 0.7% stop loss
    tp_pct=0.02,  # 2% take profit
    slippage_pct=0.0002,   # 0.02%

    # Market constraints
    lot_size=50,
    margin_per_lot=150000,   # approx NIFTY futures

    # Cost model (India)
    brokerage_per_order=5,   # ₹5/order
    stt_rate=0.000125,        # 0.0125% (sell side futures)
    exchange_txn_rate=0.00002,
    sebi_rate=0.000001,
    gst_rate=0.18,

    max_positions=1
):

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

    for i in range(n):

        price = close[i]
        current_time = time_index[i]

        # =========================
        # ENTRY
        # =========================
        if signal[i] != 0 and len(open_trades) < max_positions:

            direction = signal[i]

            entry_price = price * (1 + slippage_pct * direction)

            if direction == 1:
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                risk_per_unit = entry_price - sl_price
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                risk_per_unit = sl_price - entry_price

            if risk_per_unit > 0:

                # Risk-based position sizing
                capital_at_risk = capital * risk_per_trade
                units = capital_at_risk / risk_per_unit

                # Convert to lots
                lots = int(units // lot_size)

                if lots > 0:

                    required_margin = lots * margin_per_lot

                    if capital >= required_margin:

                        size = lots * lot_size

                        open_trades.append({
                            'direction': direction,
                            'entry_price': entry_price,
                            'sl': sl_price,
                            'tp': tp_price,
                            'size': size,
                            'lots': lots,
                            'entry_time': current_time
                        })

        # =========================
        # EXIT
        # =========================
        remaining_trades = []

        for trade in open_trades:

            direction = trade['direction']
            exit_flag = False
            exit_price = price

            # SL/TP
            if direction == 1:
                if low[i] <= trade['sl']:
                    exit_price = trade['sl']
                    exit_flag = True
                elif high[i] >= trade['tp']:
                    exit_price = trade['tp']
                    exit_flag = True
            else:
                if high[i] >= trade['sl']:
                    exit_price = trade['sl']
                    exit_flag = True
                elif low[i] <= trade['tp']:
                    exit_price = trade['tp']
                    exit_flag = True

            # EOD exit
            # FORCE EXIT WHEN DATE CHANGES (stronger than time check)
            if not exit_flag:
                if i < n - 1:
                  if current_time.date() != time_index[i + 1].date():
                   exit_flag = True
                   exit_price = price

            if exit_flag:

                exit_price = exit_price * (1 - slippage_pct * direction)

                # =========================
                # PnL
                # =========================
                gross_pnl = (
                    (exit_price - trade['entry_price']) *
                    trade['size'] *
                    direction
                )

                turnover = (
                    trade['entry_price'] * trade['size'] +
                    exit_price * trade['size']
                )

                # =========================
                # COSTS (INDIA MODEL)
                # =========================

                # Brokerage
                brokerage = 2 * brokerage_per_order

                # STT (only on sell side)
                if direction == 1:
                    stt = exit_price * trade['size'] * stt_rate
                else:
                    stt = trade['entry_price'] * trade['size'] * stt_rate

                # Exchange + SEBI
                exchange_txn = turnover * exchange_txn_rate
                sebi = turnover * sebi_rate

                # GST (on brokerage + exchange)
                gst = gst_rate * (brokerage + exchange_txn)

                total_cost = brokerage + stt + exchange_txn + sebi + gst

                pnl = gross_pnl - total_cost

                capital += pnl

                closed_trades.append({
                    'entry_time': trade['entry_time'],
                    'exit_time': current_time,
                    'direction': direction,
                    'entry_price': trade['entry_price'],
                    'exit_price': exit_price,
                    'lots': trade['lots'],
                    'size': trade['size'],
                    'gross_pnl': gross_pnl,
                    'cost': total_cost,
                    'net_pnl': pnl,
                    'return': pnl / (capital * risk_per_trade),
                    'holding_minutes': (current_time - trade['entry_time']).total_seconds() / 60
                })

            else:
                remaining_trades.append(trade)

        open_trades = remaining_trades

        # =========================
        # EQUITY
        # =========================
        unrealized_pnl = 0

        for trade in open_trades:
            unrealized_pnl += (
                (price - trade['entry_price']) *
                trade['size'] *
                trade['direction']
            )

        equity = capital + unrealized_pnl

        position_arr[i] = len(open_trades)
        capital_arr[i] = capital
        equity_arr[i] = equity

    # FINALIZE
    df['position'] = position_arr
    df['capital'] = capital_arr
    df['equity_curve'] = equity_arr

    trades_df = pd.DataFrame(closed_trades)

    peak = df['equity_curve'].cummax()
    drawdown = (df['equity_curve'] - peak) / peak

    results = {
        'final_equity': float(df['equity_curve'].iloc[-1]),
        'max_drawdown': float(drawdown.min()),
        'total_trades': len(trades_df)
    }

    return df, trades_df, results