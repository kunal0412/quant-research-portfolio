import pandas as pd
import numpy as np


def run_backtest(df, initial_capital=1, risk_pct=0.02, slippage=0.0005):

    df = df.copy()

    capital = float(initial_capital)

    position = 0
    units = 0
    max_units = 2

    entry_price = 0
    stop_loss = 0
    position_size = 0
    risk_per_unit = 0

    df['position'] = 0
    df['capital'] = np.full(len(df), capital, dtype=float)
    df['equity_curve'] = np.full(len(df), capital, dtype=float)

    trades = []

    for i in range(1, len(df)):

        price = df['close'].iloc[i]

        prev_signal = df['signal'].iloc[i - 1]
        current_signal = df['signal'].iloc[i]

        # =========================================
        # ENTRY (FIXED)
        # =========================================
        if position == 0 and prev_signal == 0 and current_signal == 1:

            entry_price = price * (1 + slippage)

            stop_loss = entry_price - (1.5 * df['atr'].iloc[i])
            risk_per_unit = entry_price - stop_loss

            if risk_per_unit <= 0:
                continue

            risk_amount = capital * risk_pct
            position_size = risk_amount / risk_per_unit

            position = 1
            units = 1
            entry_index = df.index[i]

        # =========================================
        # POSITION MANAGEMENT
        # =========================================
        elif position == 1:

            current_R = (price - entry_price) / risk_per_unit

            # =====================================
            # PYRAMIDING
            # =====================================

            if current_R >= 1 and units == 1:

                add_size = (capital * risk_pct) / risk_per_unit
                position_size += add_size
                units += 1

                # Move stop to breakeven
                stop_loss = max(stop_loss, entry_price)

            elif current_R >= 2 and units == 2 and max_units >= 3:

                add_size = (capital * risk_pct) / risk_per_unit
                position_size += add_size
                units += 1

                # Lock profit
                stop_loss = max(stop_loss, entry_price + risk_per_unit)

            # =====================================
            # TRAILING STOP
            # =====================================
            if current_R >= 1:
                new_stop = entry_price + (current_R - 1) * risk_per_unit
                stop_loss = max(stop_loss, new_stop)

            # =====================================
            # EXIT
            # =====================================
            if price <= stop_loss:

                exit_price = stop_loss * (1 - slippage)

                pnl = (exit_price - entry_price) * position_size
                capital += pnl

                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'holding_days': (df.index[i] - entry_index).days,
                    'units': units
                })

                # RESET EVERYTHING
                position = 0
                position_size = 0
                units = 0

        # =========================================
        # UPDATE DF (SAFE)
        # =========================================
        df.loc[df.index[i], 'position'] = position
        df.loc[df.index[i], 'capital'] = float(capital)
        df.loc[df.index[i], 'equity_curve'] = float(capital)

    # =========================================
    # METRICS
    # =========================================

    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)

    if total_trades > 0:
        wins = trades_df[trades_df['pnl'] > 0]
        losses = trades_df[trades_df['pnl'] <= 0]

        win_rate = len(wins) / total_trades
        avg_win = wins['pnl'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl'].mean() if len(losses) > 0 else 0

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        avg_holding = trades_df['holding_days'].mean()
    else:
        win_rate = avg_win = avg_loss = expectancy = avg_holding = 0

    results = {
        'final_equity': equity.iloc[-1],
        'max_drawdown': max_dd,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'expectancy': expectancy,
        'avg_holding_days': avg_holding
    }

    return df, trades_df, results