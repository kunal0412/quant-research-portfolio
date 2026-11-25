# Quant Research Portfolio

Systematic trading research by Kunal Singla: intraday breakout systems on gold and the Nifty 50, a long-horizon trend-following system on the S&P 500, and trend-following work on SPY.

Every project is self-contained: its own code, README, requirements and results. Raw market data is not stored in this repository; each project's `data/README.md` says which file it expects and where it comes from.

## Projects

| Project | Market | Style | Costs modelled | Status |
| --- | --- | --- | --- | --- |
| [nifty-intraday-breakout](nifty-intraday-breakout/) | Nifty 50 index, 1-minute | Long/short intraday breakout | Yes: brokerage, STT, exchange, SEBI, GST, slippage | Backtested 2015–2026 |
| [gold-intraday-breakout](gold-intraday-breakout/) | Gold futures (GC), 1-minute | Long-only intraday breakout | No | Backtested 2024–2026 |
| [sp500-trend-pyramiding](sp500-trend-pyramiding/) | S&P 500 index, daily | Trend following with pyramiding | Slippage only | Engine under review |
| [spy-trend-following](spy-trend-following/) | SPY ETF, 15-minute | EMA trend following with filters, Alpaca live trading | Slippage | Notebooks |
| [spy-ema-crossover](spy-ema-crossover/) | SPY ETF, 1-hour | 20/50 EMA crossover baseline | No | Simple baseline |

## Running a project

```bash
cd nifty-intraday-breakout
pip install -r requirements.txt
# put the data file named in data/README.md into data/
python main.py
```

## Notes

- Results in each README come from running that project's code as it stands, with the data period stated next to them.
- Each README lists the known limitations of its backtest. A result without costs is labelled as such.

## Author

Kunal Singla · MSc Mathematics (IIT Delhi) · CQF

*Research only; not investment advice.*
