from trade import *


a = binance.fetch_ohlcv('SHIB/USDT', timeframe='1m', limit=100)
print(a)