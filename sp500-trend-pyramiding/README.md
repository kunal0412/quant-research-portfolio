# S&P 500 Trend Following with Pyramiding (daily)

A long-only, long-horizon trend-following system on the S&P 500 index that adds to winning positions. It cuts losers at one ATR and lets winners run, adding one unit each time the trade gains another 1R and trailing the stop behind.

## Strategy

- **Entry**: fast EMA above slow EMA, close above the long-term EMA, close above the 10-day high, ATR above a volatility threshold, and Stochastic RSI below 0.8 (not overextended); taken on the next bar.
- **Risk**: 2% of capital risked per trade; initial stop one 14-day ATR below entry.
- **Pyramiding**: at every further +1R, add one unit of the original size and raise the stop by 1R.
- **Exit**: when price falls to the trailing stop.
- **Costs**: 0.05% slippage on entries and exits; no commissions.

## Status: engine under review

Results are not quoted here until the engine issues below are fixed. On 25 Nov 2026 a date-parsing bug was fixed: the data's day-month-year dates were being read month-first, which silently dropped 61% of the rows and put the rest out of order. With correct dates the current engine reports results that are not credible for an index strategy, which points to these issues:

1. **Pyramid adds are booked at the first entry price.** Added units are bought at a higher price, but profit is calculated from the original entry.
2. **Equity is only updated when a trade closes,** so drawdowns during open trades are not measured.
3. **No cap on position size or leverage.**
4. **Stop exits fill exactly at the stop,** even when price gaps through it.

## Files

| Path | What it does |
| --- | --- |
| `main.py` | Loads data, generates signals, runs the backtest, prints metrics |
| `data/data_loader.py` | Loads and cleans the dataset for one asset |
| `strategy/signals.py` | Signal rules |
| `backtest/engine.py` | Trade simulation with pyramiding |
| `analytics/performance.py` | Performance metrics |
| `notebooks/analysis.ipynb` | Exploratory analysis |

## Run

```bash
pip install -r requirements.txt
python main.py
```
