import pandas as pd


def analyze_mae_mfe(df):
    """
    Computes Maximum Favorable Excursion (MFE)
    and Maximum Adverse Excursion (MAE) for each signal
    until end-of-day (no SL/TP applied)
    """

    trades = []

    signal_idx = df.index[df['signal'] != 0]

    for idx in signal_idx:

        entry_time = idx
        direction = df.loc[idx, 'signal']
        entry_price = df.loc[idx, 'close']

        # Get same-day data AFTER entry
        same_day = df.loc[idx:]
        same_day = same_day[same_day.index.date == entry_time.date()]

        if len(same_day) < 2:
            continue

        highs = same_day['high']
        lows = same_day['low']

        if direction == 1:  # LONG
            mfe = (highs.max() - entry_price) / entry_price
            mae = (lows.min() - entry_price) / entry_price

        else:  # SHORT
            mfe = (entry_price - lows.min()) / entry_price
            mae = (entry_price - highs.max()) / entry_price

        trades.append({
            'entry_time': entry_time,
            'direction': direction,
            'mfe_pct': mfe * 100,
            'mae_pct': mae * 100
        })

    return pd.DataFrame(trades)


def print_summary(mae_mfe_df):
    """
    Prints useful statistics for SL/TP calibration
    """

    print("\n📊 MAE/MFE SUMMARY\n")

    print("MFE Percentiles:")
    print(mae_mfe_df['mfe_pct'].quantile([0.5, 0.7, 0.8, 0.9]))

    print("\nMAE Percentiles:")
    print(mae_mfe_df['mae_pct'].quantile([0.5, 0.7, 0.8, 0.9]))

    print("\nOverall Stats:")
    print(mae_mfe_df.describe())