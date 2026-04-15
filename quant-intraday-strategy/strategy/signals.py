import pandas as pd
import numpy as np


# =========================================
# HELPER FUNCTIONS
# =========================================

def EMA(series, span):
    return series.ewm(span=span, adjust=False).mean()


def VWAP(df):
    tp = (df['high'] + df['low'] + df['close']) / 3
    vwap = (tp * df['volume']).cumsum() / df['volume'].cumsum()
    return vwap


# =========================================
# SIGNAL GENERATION
# =========================================

def generate_intraday_signals(df):

    df = df.copy()

    # ==============================
    # BASIC INDICATORS
    # ==============================

    df['ema_fast'] = EMA(df['close'], 9)
    df['ema_slow'] = EMA(df['close'], 21)
    df['vwap'] = VWAP(df)

    # ==============================
    # TREND FILTER
    # ==============================

    trend = (df['ema_fast'] > df['ema_slow']) & (df['close'] > df['vwap'])

    # ==============================
    # STRONG BREAKOUT (KEY UPGRADE)
    # ==============================

    breakout = df['close'] > df['high'].rolling(15).max().shift(1)

    # ==============================
    # VOLATILITY FILTER (CRITICAL)
    # ==============================

    df['range'] = (df['high'] - df['low']) / df['close']

    volatility = df['range'] > 0.0015

    # ==============================
    # MOMENTUM CONFIRMATION
    # ==============================

    momentum = df['close'] > df['close'].shift(3)

    # ==============================
    # FINAL SIGNAL
    # ==============================

    df['signal'] = 0

    df.loc[
        trend &
        breakout &
        volatility &
        momentum,
        'signal'
    ] = 1

    # ==============================
    # NO LOOKAHEAD BIAS
    # ==============================

    df['signal'] = df['signal'].shift(1).fillna(0)

    return df