# 🚀 Quant Trend-Following Strategy with Pyramiding

## 📌 Overview

This project implements a systematic trend-following trading strategy designed to capture large market moves using:

* Risk-based position sizing
* Volatility-adjusted stop losses
* Dynamic trailing exits
* Pyramiding for convex payoff

The strategy focuses on **asymmetric returns**, where losses are tightly controlled and winners are allowed to grow significantly.

---

## 🧠 Strategy Philosophy

“Cut losses fast. Let winners grow. Add to strength.”

The system is built on:

* 📉 Loss minimization via strict stop-loss discipline
* 📈 Trend capture through delayed exits
* 📦 Capital allocation to winning trades using pyramiding

---

## ⚙️ Strategy Logic

### Entry

* Trend identified using EMA structure
* Breakout confirms momentum

### Risk Management

* Stop loss based on ATR
* Fixed risk per trade (1–2%)
* Define R (risk unit per trade)

### Trade Management

* +1R → Move stop to breakeven
* +2R → Lock in profits
* Continue trailing stop at 1R distance

### Pyramiding

* Add positions as trade moves in favor
* No averaging down
* Exposure increases only when trade works

### Exit

* Exit when trailing stop is hit

---

## 📊 Performance Snapshot

| Metric             | Value    |
| ------------------ | -------- |
| Final Equity       | 2.41x    |
| Max Drawdown       | -4.08%   |
| Total Trades       | 56       |
| Win Rate           | 19.6%    |
| Avg Win            | 15.1%    |
| Avg Loss           | -0.55%   |
| Expectancy         | 2.53%    |
| Avg Holding Period | ~82 days |

---

## 📈 Key Insights

* Low win rate but high payoff asymmetry
* Strategy profits from large trends
* Majority of returns come from a small number of trades
* Pyramiding enhances return profile significantly
* Dynamic stops reduce realized losses

---

## ⚠️ Risk Characteristics

* Low win rate (~20%)
* Performance depends on trending markets
* Longer holding periods

However:

* Positive expectancy
* Controlled drawdowns
* Convex payoff structure

---

## 📂 Project Structure

quant-intraday-strategy/

│
├── data/
│   └── global_financial_markets_2000_Now.csv

├── strategy/
│   └── signals.py

├── backtest/
│   └── engine.py

├── analytics/
│   └── performance.py

├── notebooks/
│   └── analysis.ipynb

├── main.py
├── requirements.txt
└── README.md

---

## ▶️ How to Run

Install dependencies:

pip install -r requirements.txt

Run the backtest:

python main.py

---

## 📊 Analytics

The system computes:

* Equity Curve
* Drawdown
* CAGR
* Sharpe Ratio
* Win Rate
* Average Win / Loss
* Expectancy
* Holding Period

---

## 🚀 Future Improvements

* Multi-asset portfolio
* Walk-forward validation
* Volatility scaling
* Transaction cost modeling
* Intraday execution

---

## 🎯 Takeaway

This project demonstrates:

* A professional backtesting framework
* Strong risk management principles
* Realistic execution modeling
* Convex strategy design

---

## 👨‍💻 Author

Kunal Singla
Quantitative Trader | CQF (Distinction)
