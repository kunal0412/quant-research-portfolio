import pandas as pd
import numpy as np


# ================================
# INDICATORS
# ================================

def EMA(series, span):
    return series.ewm(span=span, adjust=False).mean()


def ATR(df, period=14):
    """
    Standard ATR using rolling mean of True Range
    """
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift(1))
    low_close = np.abs(df['low'] - df['close'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    return tr.rolling(period).mean()


def RSI(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def stochastic_RSI(close, period=14, smooth_k=3, smooth_d=3):
    rsi = RSI(close, period)

    min_rsi = rsi.rolling(period).min()
    max_rsi = rsi.rolling(period).max()

    stoch = (rsi - min_rsi) / (max_rsi - min_rsi)

    k = stoch.rolling(smooth_k).mean()
    d = k.rolling(smooth_d).mean()

    return k, d


# ================================
# SIGNAL GENERATION
# ================================

def generate_signals(df):
    df = df.copy()

    # Indicators
    df['ema_50'] = EMA(df['close'], 50)
    df['ema_200'] = EMA(df['close'], 200)
    df['atr'] = ATR(df)

    df['stoch_k'], df['stoch_d'] = stochastic_RSI(df['close'])

    # ================================
    # CONDITIONS
    # ================================

    # Trend filter
    trend = df['ema_50'] > df['ema_200']

    # Breakout (no lookahead)
    breakout = df['close'] > df['high'].shift(1) + 0.5 * df['atr']

    # Momentum confirmation
    momentum = df['stoch_k'] > df['stoch_d']

    # ================================
    # SIGNAL
    # ================================

    df['signal'] = 0

    # Long signal
    df.loc[trend & breakout & momentum, 'signal'] = 1

    # IMPORTANT: shift signal to next bar (no lookahead bias)
    df['signal'] = df['signal'].shift(1).fillna(0)

    return df