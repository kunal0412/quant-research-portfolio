import pandas as pd
import numpy as np


def simulate_trade(df, entry_idx, direction, sl_pct, tp_pct):
    """
    Simulates one trade until SL/TP/EOD
    """

    entry_price = df.loc[entry_idx, 'close']
    entry_date = entry_idx.date()

    future = df.loc[entry_idx:]
    future = future[future.index.date == entry_date]

    if len(future) < 2:
        return None

    if direction == 1:
        sl_price = entry_price * (1 - sl_pct)
        tp_price = entry_price * (1 + tp_pct)
    else:
        sl_price = entry_price * (1 + sl_pct)
        tp_price = entry_price * (1 - tp_pct)

    for i in range(1, len(future)):

        high = future['high'].iloc[i]
        low = future['low'].iloc[i]
        price = future['close'].iloc[i]

        if direction == 1:
            if low <= sl_price:
                return (sl_price - entry_price) / entry_price
            elif high >= tp_price:
                return (tp_price - entry_price) / entry_price

        else:
            if high >= sl_price:
                return (entry_price - sl_price) / entry_price
            elif low <= tp_price:
                return (entry_price - tp_price) / entry_price

    # EOD exit
    exit_price = future['close'].iloc[-1]

    if direction == 1:
        return (exit_price - entry_price) / entry_price
    else:
        return (entry_price - exit_price) / entry_price


def optimize_sl_tp(df, sl_values, tp_values):
    """
    Runs grid search over SL/TP combinations
    """

    results = []

    signal_idx = df.index[df['signal'] != 0]

    for sl in sl_values:
        for tp in tp_values:

            returns = []

            for idx in signal_idx:

                direction = df.loc[idx, 'signal']

                ret = simulate_trade(df, idx, direction, sl, tp)

                if ret is not None:
                    returns.append(ret)

            if len(returns) == 0:
                continue

            returns = np.array(returns)

            win_rate = np.mean(returns > 0)
            avg_win = returns[returns > 0].mean() if np.any(returns > 0) else 0
            avg_loss = returns[returns < 0].mean() if np.any(returns < 0) else 0

            expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

            results.append({
                'sl_pct': sl * 100,
                'tp_pct': tp * 100,
                'win_rate': win_rate,
                'avg_win': avg_win * 100,
                'avg_loss': avg_loss * 100,
                'expectancy': expectancy * 100
            })

    return pd.DataFrame(results)


def print_top_results(results_df, top_n=10):

    print("\n🔥 Top SL/TP combinations (by expectancy)\n")

    top = results_df.sort_values(by='expectancy', ascending=False).head(top_n)

    print(top)