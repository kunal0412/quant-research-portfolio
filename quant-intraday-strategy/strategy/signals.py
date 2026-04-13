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

    # =========================================
    # INDICATORS
    # =========================================
    df['ema_fast'] = EMA(df['close'], 10)
    df['ema_slow'] = EMA(df['close'], 25)
    df['atr'] = ATR(df)

    # =========================================
    # CONDITIONS
    # =========================================

    # Trend
    trend = df['ema_fast'] > df['ema_slow']

    # Optional trend strength (light filter)
    trend_strength = (df['ema_fast'] - df['ema_slow']) / df['ema_slow']
    strong_trend = trend_strength > 0.002   # 0.2%

    # Breakout
    breakout = df['close'] > df['high'].shift(1)

    # =========================================
    # SIGNAL
    # =========================================
    df['signal'] = 0

    df.loc[
        trend & strong_trend & breakout,
        'signal'
    ] = 1

    # Avoid lookahead bias
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df