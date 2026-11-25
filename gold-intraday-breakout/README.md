# Gold Intraday Breakout (GC, 1-minute)

A long-only intraday breakout system on COMEX gold futures. It buys when a short-term uptrend breaks a 15-minute high with enough volatility and momentum, and exits at a fixed stop, a fixed target or the end of the session.

## Strategy

**Entry (long only)**, all of these on the previous bar (no look-ahead):
- Trend: EMA 9 above EMA 21, and price above VWAP
- Breakout: close above the highest high of the last 15 bars
- Volatility: bar range above 0.15% of price
- Momentum: close above the close 3 bars earlier

**Exit**: stop loss 0.6% below entry, take profit 1.2% above entry, or flat at the end of the trading day.

**Sizing**: 1% of capital risked per trade.

## Results

Run on 25 Nov 2026 with the code as it stands. Data: GC continuous contract (`GCcv1`), 1-minute bars, 3 Apr 2024 to 12 Apr 2026.

| Metric | Value |
| --- | --- |
| Final equity (start = 1.0) | 1.61 |
| CAGR | 26.3% |
| Sharpe | 1.59 |
| Max drawdown | −11.2% |
| Trades | 601 |
| Win rate | 43.8% |
| Expectancy | 0.10 R per trade |
| Average holding time | about 4.5 hours |

**These results are before costs.** The engine has no commissions, exchange fees or slippage.

## Known limitations

- No transaction costs or slippage (see above). With 601 trades in two years, costs will matter.
- VWAP is cumulative over the whole dataset instead of resetting each session.
- Stops and targets fill exactly at their price, even if the bar gapped through them.

## Files

| Path | What it does |
| --- | --- |
| `main.py` | Loads data, generates signals, runs the backtest, prints metrics, writes `backtest_results.xlsx` |
| `strategy/signals.py` | Entry signal rules |
| `backtest/engine.py` | Trade simulation: stop, target, end-of-day exit |
| `analytics/performance.py` | Performance metrics |
| `analysis_mfe_mae.py` | Maximum favourable / adverse excursion study |
| `notebooks/analysis.ipynb` | Exploratory analysis |
| `results/gc_intraday_trades.csv` | Trade list from an earlier run |
| `data/README.md` | The data file this project expects |

## Run

```bash
pip install -r requirements.txt
python main.py
```
