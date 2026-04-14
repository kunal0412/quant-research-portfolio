import pandas as pd
import numpy as np


def EMA(series, span):
    return series.ewm(span=span, adjust=False).mean()


def ATR(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def generate_signals(
    df,
    fast_ema=10,
    slow_ema=25,
    long_ema=100,
    atr_period=14,
    vol_threshold=0.008
):

    df = df.copy()

    # Indicators
    df['ema_fast'] = EMA(df['close'], fast_ema)
    df['ema_slow'] = EMA(df['close'], slow_ema)
    df['ema_long'] = EMA(df['close'], long_ema)
    df['atr'] = ATR(df, atr_period)

    # Trend
    trend = df['ema_fast'] > df['ema_slow']

    # Trend strength
    trend_strength = (df['ema_fast'] - df['ema_slow']) / df['ema_slow']
    strong_trend = trend_strength > 0.002

    # Breakout
    breakout = df['close'] > df['high'].rolling(5).max().shift(1)

    # Regime filters
    bullish_regime = df['close'] > df['ema_long']
    volatility = df['atr'] / df['close']
    high_vol = volatility > vol_threshold

    # Signal
    df['signal'] = 0

    df.loc[
        trend & strong_trend & breakout & bullish_regime & high_vol,
        'signal'
    ] = 1

    # No lookahead bias
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df