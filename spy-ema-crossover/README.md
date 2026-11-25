# SPY EMA Crossover (1-hour baseline)

The simplest trend baseline: long when the 20-period EMA is above the 50-period EMA on hourly SPY bars, short when it is below. It exists as a benchmark for the filtered strategies in this portfolio.

- **Data**: SPY hourly bars from Yahoo Finance (`yfinance`), from 1 May 2024 to today.
- **Signal**: +1 when EMA 20 > EMA 50, −1 when below, applied on the next bar.
- **Costs**: none.

```bash
pip install -r requirements.txt
python backtest.py     # downloads the data and plots the equity curve
```
