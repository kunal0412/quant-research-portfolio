import pandas as pd
import numpy as np


# =========================================
# POSITION SIZE CALCULATION
# =========================================

def calculate_position_size(capital, risk_pct, price, atr, atr_multiplier=2):
    """
    Position sizing based on risk per trade.

    Position Size = (Capital * Risk %) / (ATR * multiplier)

    Caps position to max 100% capital exposure.
    """

    risk_amount = capital * risk_pct
    stop_loss_distance = atr * atr_multiplier

    if stop_loss_distance == 0 or np.isnan(stop_loss_distance):
        return 0

    position_size = risk_amount / stop_loss_distance

    # Cap position size (no leverage beyond 100%)
    max_position = capital / price
    position_size = min(position_size, max_position)

    return position_size


# =========================================
# POSITION GENERATION + CAPITAL TRACKING
# =========================================

def generate_positions(df, initial_capital=1, risk_pct=0.01, cost_per_trade=0.0001):
    """
    Core backtest engine with:
    - Single position at a time
    - Risk-based sizing
    - ATR stop loss
    - Momentum exit
    - Mark-to-market capital tracking
    - Transaction cost modeling
    """

    df = df.copy()

    capital = initial_capital
    position = 0
    entry_price = 0
    position_size = 0

    positions = []
    capital_curve = []

    for i in range(len(df)):

        row = df.iloc[i]
        price = row['close']
        atr = row['atr']
        signal = row['signal']

        # =========================
        # HANDLE NaN ATR
        # =========================
        if np.isnan(atr):
            positions.append(0)
            capital_curve.append(capital)
            continue

        # =========================
        # ENTRY
        # =========================
        if position == 0 and signal == 1:

            position = 1
            entry_price = price

            position_size = calculate_position_size(
                capital, risk_pct, price, atr
            )

            # Apply transaction cost (entry)
            capital -= capital * cost_per_trade

        # =========================
        # EXIT CONDITIONS
        # =========================
        elif position == 1:

            stop_loss = entry_price - 2 * atr

            exit_flag = False

            # Stop loss
            if price <= stop_loss:
                exit_flag = True

            # Trend breakdown exit
            elif row['ema_50'] < row['ema_200']:
                exit_flag = True

            # Trail stop using EMA
            trailing_stop = row['ema_50']

            if price < trailing_stop:
               exit_flag = True

            if exit_flag:
                pnl = position_size * (price - entry_price)
                capital += pnl

                # Apply transaction cost (exit)
                capital -= capital * cost_per_trade

                position = 0
                position_size = 0

        # =========================
        # MARK-TO-MARKET EQUITY
        # =========================
        if position == 1:
            unrealized_pnl = position_size * (price - entry_price)
            capital_marked = capital + unrealized_pnl
        else:
            capital_marked = capital

        positions.append(position)
        capital_curve.append(capital_marked)

    df['position'] = positions
    df['capital'] = capital_curve

    return df


# =========================================
# BACKTEST WRAPPER
# =========================================

def run_backtest(df):
    """
    Computes equity curve from capital.
    """

    df = df.copy()

    df['equity_curve'] = df['capital'] / df['capital'].iloc[0]
    df.loc[df.index[0], 'equity_curve'] = 1

    return df