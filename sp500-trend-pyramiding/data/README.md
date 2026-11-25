# Data

Raw market data is not stored in this repository.

| File to place here | Contents |
| --- | --- |
| `global_financial_markets_2000_Now.csv` | Daily OHLCV for global indices from 2000, one row per asset per day. Columns include `date` (DD-MM-YYYY), `asset_name`, `open`, `high`, `low`, `close`, `volume` |

This is a Kaggle dataset of global financial markets since 2000. `main.py` filters it to `asset_name == "S&P500"`.
