import pandas as pd
import numpy as np


def run_backtest(df, initial_capital=1.0, risk_pct=0.02, slippage=0.0005):

    df = df.copy()

    n = len(df)

    position_arr = np.zeros(n)
    capital_arr = np.zeros(n)
    equity_arr = np.zeros(n)

    capital = float(initial_capital)

    position = 0
    entry_price = 0
    stop_loss = 0
    position_size = 0
    risk_per_unit = 0

    trades = []

    capital_arr[0] = capital
    equity_arr[0] = capital
    position_arr[0] = 0   # 🔥 FORCE clean start

    for i in range(1, n):

        price = df['close'].iloc[i]
        signal = df['signal'].iloc[i]
        atr = df['atr'].iloc[i]

        # ======================================
        # ENTRY (ONLY VALID WAY TO ENTER)
        # ======================================
        if position == 0:

            if signal == 1:

                entry_price = price * (1 + slippage)

                stop_loss = entry_price - (1.0 * atr)
                risk_per_unit = entry_price - stop_loss

                if risk_per_unit > 0:

                    risk_amount = capital * risk_pct
                    position_size = risk_amount / risk_per_unit

                    position = 1
                    entry_index = df.index[i]

        # ======================================
        # POSITION MANAGEMENT
        # ======================================
        elif position == 1:

            current_R = (price - entry_price) / risk_per_unit

            # trailing
            if current_R >= 2:
                new_stop = entry_price + (current_R - 2) * risk_per_unit
                stop_loss = max(stop_loss, new_stop)

            # exit
            if price <= stop_loss:

                exit_price = stop_loss * (1 - slippage)

                pnl = (exit_price - entry_price) * position_size
                capital += pnl

                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'holding_days': (df.index[i] - entry_index).days
                })

                position = 0
                position_size = 0

        # ======================================
        # STORE CLEAN STATE
        # ======================================
        position_arr[i] = position
        capital_arr[i] = capital
        equity_arr[i] = capital

    df['position'] = position_arr
    df['capital'] = capital_arr
    df['equity_curve'] = equity_arr

    # ======================================
    # METRICS
    # ======================================
    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    trades_df = pd.DataFrame(trades)

    results = {
        'final_equity': equity.iloc[-1],
        'max_drawdown': max_dd,
        'total_trades': len(trades_df)
    }

    return df, trades_df, results