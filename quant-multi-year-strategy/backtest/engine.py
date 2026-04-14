import pandas as pd
import numpy as np


def run_backtest(df, initial_capital=1.0, risk_pct=0.02, slippage=0.0005):

    df = df.copy()

    n = len(df)

    # Initialize columns
    df['position'] = 0.0
    df['capital'] = 0.0
    df['equity_curve'] = 0.0

    capital = float(initial_capital)

    position = 0
    entry_price = 0
    stop_loss = 0
    position_size = 0
    base_position_size = 0
    risk_per_unit = 0

    pyramid_level = 0  # counts how many R achieved

    trades = []

    df.loc[df.index[0], 'capital'] = capital
    df.loc[df.index[0], 'equity_curve'] = capital

    for i in range(1, n):

        price = df['close'].iloc[i]
        signal = df['signal'].iloc[i]
        atr = df['atr'].iloc[i]

        # =========================
        # ENTRY
        # =========================
        if position == 0:

            if signal == 1 and not np.isnan(atr):

                entry_price = price * (1 + slippage)

                stop_loss = entry_price - (1 * atr)
                risk_per_unit = entry_price - stop_loss

                if risk_per_unit > 0:

                    risk_amount = capital * risk_pct
                    base_position_size = risk_amount / risk_per_unit

                    position_size = base_position_size
                    position = 1

                    pyramid_level = 0
                    entry_index = df.index[i]

        # =========================
        # POSITION MANAGEMENT
        # =========================
        elif position == 1:

            current_R = (price - entry_price) / risk_per_unit

            # =========================
            # TRAIL + PYRAMID EVERY 1R
            # =========================
            if current_R >= (pyramid_level + 1):

                # Move SL up by 1R
                stop_loss = entry_price + (pyramid_level) * risk_per_unit

                # Add same size
                add_price = price * (1 + slippage)
                position_size += base_position_size

                pyramid_level += 1

            # =========================
            # EXIT
            # =========================
            if price <= stop_loss:

                exit_price = stop_loss * (1 - slippage)

                pnl = (exit_price - entry_price) * position_size
                capital += pnl

                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'holding_days': (df.index[i] - entry_index).days,
                    'pyramids': pyramid_level
                })

                position = 0
                position_size = 0
                base_position_size = 0

        # =========================
        # STORE STATE
        # =========================
        df.loc[df.index[i], 'position'] = position
        df.loc[df.index[i], 'capital'] = capital
        df.loc[df.index[i], 'equity_curve'] = capital

    # =========================
    # METRICS
    # =========================
    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak

    trades_df = pd.DataFrame(trades)

    results = {
        'final_equity': equity.iloc[-1],
        'max_drawdown': drawdown.min(),
        'total_trades': len(trades_df)
    }

    return df, trades_df, results