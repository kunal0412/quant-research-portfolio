import pandas as pd
import numpy as np

def calculate_position_size(capital, risk_pct, entry_price, atr, atr_multiplier=2):
    """
    Calculates position size based on risk per trade.
    """

    risk_amount = capital * risk_pct

    stop_loss_distance = atr * atr_multiplier

    position_size = risk_amount / stop_loss_distance

    return position_size


# ================================
# POSITION GENERATION
# ================================

def generate_positions(df, initial_capital=1, risk_pct=0.01):
    df = df.copy()

    capital = initial_capital
    position = 0
    entry_price = 0
    position_size = 0

    positions = []
    capital_curve = []

    for i in range(len(df)):
        row = df.iloc[i]

        signal = row['signal']
        price = row['close']
        atr = row['atr']

        # ========================
        # ENTRY
        # ========================
        if position == 0 and signal == 1:
            position = 1
            entry_price = price

            position_size = calculate_position_size(
                capital, risk_pct, price, atr
            )

        # ========================
        # EXIT CONDITIONS
        # ========================
        elif position == 1:

            stop_loss = entry_price - 2 * atr

            # SL hit
            if price <= stop_loss:
                pnl = position_size * (price - entry_price)
                capital += pnl
                position = 0

            # Momentum exit
            elif row['stoch_k'] < row['stoch_d']:
                pnl = position_size * (price - entry_price)
                capital += pnl
                position = 0

        # ========================
        # TRACKING
        # ========================
        positions.append(position)
        capital_curve.append(capital)

    df['position'] = positions
    df['capital'] = capital_curve

    return df

# ================================
# TRANSACTION COST MODEL
# ================================

def apply_transaction_costs(df, spread=0.0001, commission=0.0001):
    """
    Applies transaction costs ONLY when position changes.
    Total cost = spread + commission
    """

    df = df.copy()

    # Identify trades (entry/exit)
    df['trade'] = df['position'].diff().fillna(0)

    df['trade_flag'] = df['trade'].abs()

    # Cost applied when trade happens
    cost_per_trade = spread + commission

    df['cost'] = df['trade_flag'] * cost_per_trade
    
    return df


# ================================
# BACKTEST CORE
# ================================

def run_backtest(df):
    df = df.copy()

    # Equity curve
    df['equity_curve'] = df['capital'] / df['capital'].iloc[0]
    df.loc[df.index[0], 'equity_curve'] = 1  # Start with $1
    
    return df