import numpy as np
import pandas as pd


def run_backtest(df, initial_capital=1.0, risk_pct=0.02, slippage=0.0005):

    df = df.copy()

    n = len(df)

    # Arrays
    position_arr = np.zeros(n)
    capital_arr = np.zeros(n)
    equity_arr = np.zeros(n)

    # State variables
    capital = float(initial_capital)
    position = 0
    entry_price = 0
    stop_loss = 0
    position_size = 0
    risk_per_unit = 0
    entry_index = None

    trades = []

    capital_arr[0] = capital
    equity_arr[0] = capital
    position_arr[0] = 0

    # =========================================
    # MAIN LOOP
    # =========================================
    for i in range(1, n):

        price = df['close'].iloc[i]
        signal = df['signal'].iloc[i]
        atr = df['atr'].iloc[i]

        # ======================================
        # ENTRY
        # ======================================
        if position == 0:

            if signal == 1 and atr > 0:

                entry_price = price * (1 + slippage)

                stop_loss = entry_price - (1.5 * atr)
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

            # ===== TRAILING LOGIC =====
            current_R = (price - entry_price) / risk_per_unit

            if current_R >= 2:
                new_stop = entry_price + (current_R - 1) * risk_per_unit
                stop_loss = max(stop_loss, new_stop)

            # ===== STOP LOSS EXIT (SAFE) =====
            if price <= stop_loss:

                if position_size > 0 and entry_price > 0:

                    exit_price = stop_loss * (1 - slippage)

                    pnl = (exit_price - entry_price) * position_size
                    capital += pnl

                    trades.append({
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'pnl': pnl,
                        'holding_minutes': (df.index[i] - entry_index).total_seconds() / 60
                    })

                position = 0
                position_size = 0
                entry_price = 0
                stop_loss = 0

        # ======================================
        # FORCE EXIT ON LAST BAR (CRITICAL FIX)
        # ======================================
        is_last_bar = (i == n - 1)

        if position == 1 and is_last_bar:

            if position_size > 0 and entry_price > 0:

                exit_price = price * (1 - slippage)

                pnl = (exit_price - entry_price) * position_size
                capital += pnl

                trades.append({
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'holding_minutes': (df.index[i] - entry_index).total_seconds() / 60
                })

            position = 0
            position_size = 0
            entry_price = 0
            stop_loss = 0

        # ======================================
        # CAPITAL SAFETY (ANTI-BLOWUP)
        # ======================================
        capital = max(capital, 0)

        # ======================================
        # STORE STATE
        # ======================================
        position_arr[i] = position
        capital_arr[i] = capital
        equity_arr[i] = capital

    # =========================================
    # SAVE TO DATAFRAME
    # =========================================
    df['position'] = position_arr
    df['capital'] = capital_arr
    df['equity_curve'] = equity_arr

    # =========================================
    # PERFORMANCE SUMMARY
    # =========================================
    equity = df['equity_curve']

    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_dd = drawdown.min()

    trades_df = pd.DataFrame(trades)

    results = {
        'final_equity': float(equity.iloc[-1]),
        'max_drawdown': float(max_dd),
        'total_trades': int(len(trades_df))
    }

    return df, trades_df, results