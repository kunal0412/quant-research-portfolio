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


def RSI(series, period=14):
    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


def StochRSI(series, period=14):
    rsi = RSI(series, period)
    min_rsi = rsi.rolling(period).min()
    max_rsi = rsi.rolling(period).max()

    return (rsi - min_rsi) / (max_rsi - min_rsi + 1e-9)


def generate_signals(
    df,
    fast_ema=10,
    slow_ema=50,
    long_ema=200,
    atr_period=14,
    vol_threshold=0.008
):

    df = df.copy()

    # =========================
    # INDICATORS
    # =========================
    df['ema_fast'] = EMA(df['close'], fast_ema)
    df['ema_slow'] = EMA(df['close'], slow_ema)
    df['ema_long'] = EMA(df['close'], long_ema)

    df['atr'] = ATR(df, atr_period)
    df['stoch_rsi'] = StochRSI(df['close'])

    # =========================
    # TREND CONDITIONS
    # =========================
    trend = df['ema_fast'] > df['ema_slow']

    # Remove over-restrictive strength filter (important)
    # Let pyramiding capture strength instead

    # =========================
    # BREAKOUT (STRONGER)
    # =========================
    breakout = df['close'] > df['high'].rolling(10).max().shift(1)

    # =========================
    # REGIME FILTER
    # =========================
    bullish_regime = df['close'] > df['ema_long']

    # =========================
    # VOLATILITY FILTER
    # =========================
    volatility = df['atr'] / df['close']
    high_vol = volatility > vol_threshold

    # =========================
    # MOMENTUM FILTER (OPTIONAL EDGE)
    # =========================
    momentum = df['stoch_rsi'] < 0.8   # avoid overextended entries

    # =========================
    # FINAL SIGNAL
    # =========================
    df['signal'] = 0

    df.loc[
        trend &
        breakout &
        bullish_regime &
        high_vol &
        momentum,
        'signal'
    ] = 1

    # =========================
    # NO LOOKAHEAD BIAS
    # =========================
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df