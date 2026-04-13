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


def generate_signals(df):

    df = df.copy()

    # Indicators
    df['ema_20'] = EMA(df['close'], 20)
    df['ema_50'] = EMA(df['close'], 50)
    df['atr'] = ATR(df)

    # Trend
    trend = df['ema_20'] > df['ema_50']

    # Moderate trend strength (relaxed)
    trend_strength = (df['ema_20'] - df['ema_50']) / df['ema_50']
    strong_trend = trend_strength > 0.005   # reduced from 1% → 0.5%

    # Breakout (relaxed from 20 → 10)
    breakout = df['close'] > df['high'].rolling(10).max().shift(1)

    # REMOVE volume filter (important)
    # REMOVE pullback filter for now

    df['signal'] = 0

    df.loc[
        trend & strong_trend & breakout,
        'signal'
    ] = 1

    # Avoid lookahead bias
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df