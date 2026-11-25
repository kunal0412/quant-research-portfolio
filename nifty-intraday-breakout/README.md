# Nifty 50 Intraday Breakout (1-minute)

A long/short intraday breakout system on the Nifty 50 index, with a full Indian futures cost model. It trades breakouts of the last 30 minutes' range in the direction of a three-EMA trend, inside the 09:20–15:15 session.

## Strategy

**Entry**, all on the previous bar (no look-ahead):
- Trend: EMA 9, 21 and 50 stacked in the trade's direction, price beyond EMA 9
- Breakout: close beyond the highest high (long) or lowest low (short) of the last 30 bars
- Volatility: 14-bar ATR above 0.08% of price
- Trend strength: EMA 9–21 spread above 0.05% of price
- Momentum: close beyond the close 3 bars earlier
- Session: 09:20 to 15:15 only; repeated signals in the same direction are dropped

**Exit**: stop loss 0.7%, take profit 2%, or flat at the end of the day.

**Sizing**: 1% of capital risked per trade, in Nifty lots (lot size 50, margin ₹1.5 lakh per lot), one position at a time.

**Costs**: ₹5 brokerage per order, STT 0.0125% on the sell side, exchange charges 0.002%, SEBI fee 0.0001%, GST 18% on brokerage and exchange charges, slippage 0.02% each way.

## Results

Run on 25 Nov 2026 with the code as it stands. Data: Nifty 50 1-minute bars, 9 Jan 2015 to 8 Apr 2026. Starting capital ₹1 crore.

| Metric | Value |
| --- | --- |
| Final equity | ₹85.4 lakh |
| CAGR | −1.4% |
| Sharpe | −0.08 |
| Max drawdown | −44.4% |
| Trades | 1,471 |
| Win rate | 43.9% |
| Total costs | ₹37.6 lakh |
| Average holding time | about 3.5 hours |

After realistic costs the strategy loses money: costs of ₹37.6 lakh exceed its gross edge. The research scripts below study where the edge goes and how stop and target choices change it.

## Research

| Script | Question it answers | Output in `results/` |
| --- | --- | --- |
| `research/run_mae_mfe.py` | How far trades move for and against before exit | `mae_mfe_analysis.xlsx` |
| `research/sl_tp_optimizer.py` | Which stop and target pair works best | `sl_tp_optimization.xlsx` |
| `research/regime_analysis.py` | How results differ across market regimes | `regime_analysis.xlsx` |
| `research/run_all_research.py` | Runs all three | all of the above |

## Known limitations

- The lot size is fixed at 50; NSE has changed the Nifty lot size several times since 2015.
- The backtest trades the index price as a proxy for futures; futures basis and roll costs are not modelled.
- Stops and targets fill at their price plus slippage, even if the bar gapped through them.

## Run

```bash
pip install -r requirements.txt
python main.py                     # backtest
python research/run_all_research.py   # research studies
```
