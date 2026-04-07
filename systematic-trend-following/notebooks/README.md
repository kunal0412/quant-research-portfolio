# Systematic Trend Following Strategy (SPY)

## Overview

This project implements a systematic trend-following strategy on SPY using:

* EMA crossover (100/200)
* Stochastic RSI
* ATR (volatility filter)
* Ratio-based trend confirmation

The strategy is designed to capture sustained market trends while avoiding choppy conditions.

---

## Strategy Logic

### Entry Conditions (Long)

* EMA100 > EMA200
* Stochastic RSI rising
* ATR above threshold
* Trend ratio confirms direction

### Exit Conditions

* EMA crossover reversal
* Weak momentum or volatility

---

## Backtest Performance

* Cumulative Return: 144%
* Sharpe Ratio: 1.51
* Max Drawdown: 21%

---

## Features

* Backtesting engine using historical data
* Live trading integration using Alpaca API
* Real-time signal generation
* Risk management using ATR and Kelly Criterion

---

## Files

* `notebooks/backtest.ipynb` → Backtesting
* `notebooks/live.ipynb` → Live trading logic
* `notebooks/live_data.ipynb` → Data handling

---

## Future Work

* Test on multiple indices (NIFTY, NASDAQ, commodities)
* Add pyramiding logic
* Portfolio-level risk management
* Execution optimization (VWAP/TWAP)

---

## Disclaimer

This project is for research purposes only. Not financial advice.
