import pandas as pd
import numpy as np


def run_backtest(
    df,
    initial_capital=1.0,
    risk_pct=0.02,
    slippage=0.0005
):

    df = df.copy()
    n = len(df)

    position_arr = np.zeros(n)
    capital_arr = np.zeros(n, dtype=float)
    equity_arr = np.zeros(n, dtype=float)

    capital = float(initial_capital)

    # =========================
    # TRADE STATE
    # =========================
    in_position = False

    entry_price = 0
    stop_loss = 0
    risk_per_unit = 0

    lots = []
    entry_index = None

    trades = []

    capital_arr[0] = capital
    equity_arr[0] = capital

    # =========================
    # LOOP
    # =========================
    for i in range(2, n - 1):

        price = df['close'].iloc[i]
        signal = df['signal'].iloc[i]
        atr = df['atr'].iloc[i]

        # ======================================
        # DAY STRUCTURE DETECTION
        # ======================================
        current_date = df.index[i].date()
        next_date = df.index[i + 1].date()
        next_next_date = df.index[i + 2].date() if i + 2 < n else next_date

        is_last_bar = next_date != current_date
        is_second_last_bar = next_next_date != next_date

        # ======================================
        # ENTRY (ONLY ONE TRADE AT A TIME)
        # ======================================
        if not in_position and signal == 1:

            entry_price = price * (1 + slippage)

            stop_loss = entry_price - (1.5 * atr)
            risk_per_unit = entry_price - stop_loss

            if risk_per_unit > 0:

                risk_amount = capital * risk_pct
                position_size = risk_amount / risk_per_unit

                lots = [entry_price]
                in_position = True
                entry_index = df.index[i]

        # ======================================
        # POSITION MANAGEMENT
        # ======================================
        elif in_position:

            # ----------------------------------
            # PYRAMIDING (1R ADD)
            # ----------------------------------
            last_add_price = lots[-1]

            if price >= last_add_price + risk_per_unit:
                lots.append(price)

            # ----------------------------------
            # TRAILING STOP (1R)
            # ----------------------------------
            new_stop = price - risk_per_unit
            stop_loss = max(stop_loss, new_stop)

            # ----------------------------------
            # EXIT 1: STOP LOSS
            # ----------------------------------
            if price <= stop_loss:

                exit_price = stop_loss * (1 - slippage)

                total_pnl = sum([(exit_price - lp) for lp in lots])

                risk_amount = capital * risk_pct
                total_pnl *= (risk_amount / risk_per_unit)

                capital += total_pnl

                trades.append({
                    'entry_time': entry_index,
                    'exit_time': df.index[i],
                    'exit_type': 'SL',
                    'num_lots': len(lots),
                    'pnl': total_pnl,
                    'holding_minutes': (df.index[i] - entry_index).total_seconds() / 60
                })

                in_position = False
                lots = []

            # ----------------------------------
            # EXIT 2: SECOND LAST CANDLE (KEY RULE)
            # ----------------------------------
            elif is_second_last_bar:

                exit_price = price * (1 - slippage)

                total_pnl = sum([(exit_price - lp) for lp in lots])

                risk_amount = capital * risk_pct
                total_pnl *= (risk_amount / risk_per_unit)

                capital += total_pnl

                trades.append({
                    'entry_time': entry_index,
                    'exit_time': df.index[i],
                    'exit_type': 'EOD_2ND_LAST',
                    'num_lots': len(lots),
                    'pnl': total_pnl,
                    'holding_minutes': (df.index[i] - entry_index).total_seconds() / 60
                })

                in_position = False
                lots = []

        # ======================================
        # STORE STATE
        # ======================================
        position_arr[i] = 1 if in_position else 0
        capital_arr[i] = capital
        equity_arr[i] = capital

    # =========================
    # SAVE
    # =========================
    df['position'] = position_arr
    df['capital'] = capital_arr
    df['equity_curve'] = equity_arr

    # =========================
    # METRICS
    # =========================
    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    trades_df = pd.DataFrame(trades)

    results = {
        'final_equity': float(equity.iloc[-1]),
        'max_drawdown': float(max_dd),
        'total_trades': len(trades_df)
    }

    return df, trades_df, results