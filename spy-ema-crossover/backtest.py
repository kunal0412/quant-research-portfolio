import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

#Fetch Data
data = yf.download("SPY", start="2024-05-01", interval="1h")

data = data[['Close']].rename(columns={'Close':'close'})
data.dropna(inplace=True)

data.head()

#EMA_20
data['ema_20'] = data['close'].ewm(span=20).mean()

#EMA_50
data['ema_50'] = data['close'].ewm(span=50).mean()

data['signal'] = 0

data.loc[data['ema_20'] > data['ema_50'], 'signal'] = 1
data.loc[data['ema_20'] < data['ema_50'], 'signal'] = -1

data['position'] = data['signal'].shift(1)

data['returns'] = data['close'].pct_change()
data['strategy_returns'] = data['returns'] * data['position']

data['cumulative'] = (1 + data['strategy_returns']).cumprod()

plt.figure(figsize=(12,6))
plt.plot(data['cumulative'], label='Strategy')
plt.title("Equity Curve")
plt.legend()
plt.show()
