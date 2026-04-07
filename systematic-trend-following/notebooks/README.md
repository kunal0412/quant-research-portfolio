# Systematic Trend Following Strategy (SPY)

## Strategy Snapshot

* Asset: SPY (S&P 500 ETF)
* Type: Systematic Trend Following
* Timeframe: Intraday (5-min / 15-min)
* Core Idea: Capture sustained trends using EMA crossover with volatility and momentum filters

---

## Performance Highlights

| Metric            | Value |
| ----------------- | ----- |
| Cumulative Return | 144%  |
| Sharpe Ratio      | 1.51  |
| Max Drawdown      | 21%   |

---

## Key Edge

Unlike naive EMA crossover systems, this strategy integrates:

* ATR-based volatility filtering (avoids low-volatility traps)
* Stochastic RSI confirmation (reduces false entries)
* Ratio-based trend strength filter (cuts whipsaws)

This significantly improves signal quality in choppy markets.


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

## Results

![Equity Curve](results/cumm_returns.png)
![Kelly Equity Curve](results/cumm_kelly_returns.png)

---

## Future Work

* Test on multiple indices (NIFTY, NASDAQ, commodities)
* Add pyramiding logic
* Portfolio-level risk management
* Execution optimization (VWAP/TWAP)

---

## Disclaimer

This project is for research purposes only. Not financial advice.
