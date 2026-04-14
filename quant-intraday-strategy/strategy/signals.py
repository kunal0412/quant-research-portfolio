import pandas as pd
import numpy as np


# =========================
# INDICATORS
# =========================

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


def STOCH_RSI(series, period=14):
    rsi = RSI(series, period)

    min_rsi = rsi.rolling(period).min()
    max_rsi = rsi.rolling(period).max()

    stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi + 1e-9)

    return stoch_rsi


# =========================
# MAIN SIGNAL FUNCTION
# =========================

def generate_intraday_signals(df):

    df = df.copy()

    # =========================
    # SESSION FILTER
    # =========================
    df = df.between_time("08:00", "20:00")  # adjust after timezone confirmation

    # =========================
    # INDICATORS
    # =========================
    df['ema_fast'] = EMA(df['close'], 5)
    df['ema_slow'] = EMA(df['close'], 20)

    df['atr'] = ATR(df, 14)
    df['stoch_rsi'] = STOCH_RSI(df['close'], 14)

    # =========================
    # TREND
    # =========================
    trend = df['ema_fast'] > df['ema_slow']

    # =========================
    # BREAKOUT
    # =========================
    breakout = df['close'] > df['high'].rolling(20).max().shift(1)

    # =========================
    # VOLATILITY FILTER
    # =========================
    volatility = df['atr'] / df['close']
    high_vol = volatility > 0.001

    # =========================
    # MOMENTUM RESET (KEY CHANGE)
    # =========================
    pullback = df['stoch_rsi'] < 0.4   # NOT oversold, just cooling

    # =========================
    # FINAL SIGNAL
    # =========================
    df['signal'] = 0

    df.loc[
        trend &
        breakout &
        high_vol &
        pullback,
        'signal'
    ] = 1

    # =========================
    # REMOVE LOOKAHEAD
    # =========================
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df