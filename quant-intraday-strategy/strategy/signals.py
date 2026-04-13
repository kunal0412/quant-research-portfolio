import pandas as pd
import numpy as np


# =========================================
# INDICATORS
# =========================================

def EMA(series, span):
    return series.ewm(span=span, adjust=False).mean()


def ATR(df, period=14):
    """
    Average True Range (ATR)
    """

    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr


def RSI(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    return rsi


def stochastic_RSI(close, period=14, smooth_k=3, smooth_d=3):
    """
    Stochastic RSI with numerical stability fixes
    """

    rsi = RSI(close, period)

    min_rsi = rsi.rolling(period).min()
    max_rsi = rsi.rolling(period).max()

    # Avoid division by zero
    denominator = (max_rsi - min_rsi).replace(0, np.nan)

    stoch = (rsi - min_rsi) / denominator

    k = stoch.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()

    return k, d


# =========================================
# SIGNAL GENERATION
# =========================================

def generate_signals(df):
    """
    Generates trading signals using:
    - Trend (EMA 50 > EMA 200)
    - Breakout (price > previous high + ATR buffer)
    - Momentum (Stoch RSI confirmation)

    Ensures NO lookahead bias.
    """

    df = df.copy()

    # =========================
    # INDICATORS
    # =========================
    df['ema_50'] = EMA(df['close'], 50)
    df['ema_200'] = EMA(df['close'], 200)

    df['atr'] = ATR(df)

    df['stoch_k'], df['stoch_d'] = stochastic_RSI(df['close'])

    # =========================
    # CONDITIONS
    # =========================

    # Trend filter
    trend = (df['ema_50'] > df['ema_200']) & ((df['ema_50'] - df['ema_200']) / df['ema_200'] > 0.01)

    # Breakout (NO LOOKAHEAD)
    breakout = df['close'] > (df['high'].shift(1) + 0.5 * df['atr'])

    # Momentum confirmation
    momentum = df['stoch_k'] > df['stoch_d']

    # =========================
    # SIGNAL
    # =========================

    df['signal'] = 0

    df.loc[trend & breakout & momentum, 'signal'] = 1

    # Shift signal to next bar (CRUCIAL → no lookahead bias)
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df