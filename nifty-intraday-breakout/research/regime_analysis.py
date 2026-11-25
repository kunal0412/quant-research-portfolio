import pandas as pd
import numpy as np


# =========================================
# REGIME DETECTION
# =========================================

def classify_regime(df):
    """
    Classifies each row into:
    - 'trend'
    - 'chop'
    """

    df = df.copy()

    # EMA-based trend strength
    df['ema_fast'] = df['close'].ewm(span=9).mean()
    df['ema_slow'] = df['close'].ewm(span=21).mean()

    df['ema_spread'] = (df['ema_fast'] - df['ema_slow']) / df['close']

    # ATR-based volatility
    df['range'] = (df['high'] - df['low']) / df['close']

    # Regime classification
    df['regime'] = 'chop'

    df.loc[
        (df['ema_spread'].abs() > 0.0007) &
        (df['range'] > 0.001),
        'regime'
    ] = 'trend'

    return df


# =========================================
# ASSIGN REGIME TO TRADES
# =========================================

def tag_trades_with_regime(df, trades_df):
    """
    Assigns regime at entry time to each trade
    """

    trades_df = trades_df.copy()

    regimes = []

    for _, trade in trades_df.iterrows():
        entry_time = trade['entry_time']

        if entry_time in df.index:
            regimes.append(df.loc[entry_time, 'regime'])
        else:
            regimes.append('unknown')

    trades_df['regime'] = regimes

    return trades_df


# =========================================
# ANALYSIS
# =========================================

def analyze_by_regime(trades_df):
    """
    Computes metrics per regime
    """

    results = []

    for regime in trades_df['regime'].unique():

        subset = trades_df[trades_df['regime'] == regime]

        if len(subset) == 0:
            continue

        win_rate = (subset['net_pnl'] > 0).mean()

        avg_win = subset[subset['net_pnl'] > 0]['net_pnl'].mean()
        avg_loss = subset[subset['net_pnl'] < 0]['net_pnl'].mean()

        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

        results.append({
            'regime': regime,
            'trades': len(subset),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'expectancy': expectancy,
            'total_pnl': subset['net_pnl'].sum()
        })

    return pd.DataFrame(results)


# =========================================
# PRINT
# =========================================

def print_regime_summary(results_df):

    print("\n📊 REGIME ANALYSIS\n")

    print(results_df.sort_values(by='expectancy', ascending=False))