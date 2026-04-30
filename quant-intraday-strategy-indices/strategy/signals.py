import pandas as pd
import numpy as np


# =========================================
# HELPER FUNCTIONS
# =========================================

def EMA(series, span):
    return series.ewm(span=span, adjust=False).mean()


def ATR(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr


def session_filter(index):
    return (index.time >= pd.to_datetime("09:20").time()) & \
           (index.time <= pd.to_datetime("15:15").time())


# =========================================
# SIGNAL GENERATION
# =========================================

def generate_intraday_signals(df):

    df = df.copy()

    # =========================================
    # SESSION FILTER
    # =========================================
    df = df[session_filter(df.index)]

    # =========================================
    # INDICATORS
    # =========================================
    df['ema_fast'] = EMA(df['close'], 9)
    df['ema_slow'] = EMA(df['close'], 21)
    df['ema_trend'] = EMA(df['close'], 50)

    df['atr'] = ATR(df, 14)
    df['atr_pct'] = df['atr'] / df['close']

    # =========================================
    # COMMON FILTERS
    # =========================================
    volatility = df['atr_pct'] > 0.0008

    ema_spread = (df['ema_fast'] - df['ema_slow']) / df['close']
    clean_trend_long = ema_spread > 0.0005
    clean_trend_short = ema_spread < -0.0005

    momentum_long = df['close'] > df['close'].shift(3)
    momentum_short = df['close'] < df['close'].shift(3)

    # =========================================
    # BREAKOUTS
    # =========================================
    rolling_high = df['high'].rolling(20).max().shift(1)
    rolling_low = df['low'].rolling(20).min().shift(1)

    breakout_long = df['close'] > rolling_high
    breakout_short = df['close'] < rolling_low

    # =========================================
    # TREND FILTERS
    # =========================================
    trend_long = (
        (df['ema_fast'] > df['ema_slow']) &
        (df['ema_slow'] > df['ema_trend']) &
        (df['close'] > df['ema_fast'])
    )

    trend_short = (
        (df['ema_fast'] < df['ema_slow']) &
        (df['ema_slow'] < df['ema_trend']) &
        (df['close'] < df['ema_fast'])
    )

    # =========================================
    # SIGNALS
    # =========================================
    df['signal'] = 0

    # LONG = +1
    df.loc[
        trend_long &
        breakout_long &
        volatility &
        momentum_long &
        clean_trend_long,
        'signal'
    ] = 1

    # SHORT = -1
    df.loc[
        trend_short &
        breakout_short &
        volatility &
        momentum_short &
        clean_trend_short,
        'signal'
    ] = -1

    # =========================================
    # NO LOOKAHEAD
    # =========================================
    df['signal'] = df['signal'].shift(1).fillna(0)

    # =========================================
    # REMOVE DUPLICATE SIGNALS
    # =========================================
    df['signal'] = np.where(
        (df['signal'] != 0) &
        (df['signal'].shift(1) == df['signal']),
        0,
        df['signal']
    )

    return df