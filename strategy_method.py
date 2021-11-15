import ccxt
import numpy as np
import time

binance = ccxt.binance()
bybit = ccxt.bybit({
                    'api_key': 'o3r5vAFgEGLX8JWNfN',
                    'secret': 'uXH1AdEE20UehJrz8lsDVQmX84nBvWkqmhWx'
})

def get_bollinger(ticker, timeframe, day_length, std_mul, day_before=0):  # day_before is not essential
    data = binance.fetch_ohlcv(ticker + '/USDT', timeframe = timeframe)
    data_length = len(data)
    close_data = []
    for i in range(day_length):
        close_data.append(data[data_length+i-day_length-day_before][4])
    # print(close_data)
    now_price = close_data[day_length - 1]
    ma = np.average(close_data)
    # print(ma)
    std = np.std(close_data)
    # print(std*2)
    upper = ma + (std_mul * std)
    lower = ma - (std_mul * std)
    result = {'ma': ma, 'upper': upper, 'lower': lower, 'price': now_price}
    return result


def get_ma(ticker, timeframe, candles):
    try:
        data = bybit.fetch_ohlcv(ticker + '/USDT', timeframe=timeframe, limit = candles)
        if data is None:
            time.sleep(0.5)
            data = bybit.fetch_ohlcv(ticker + '/USDT', timeframe=timeframe, limit=candles)
        hap = 0
        for i in range(candles):
            hap += data[i][4]
        ma = hap / candles
        return ma
    except Exception as get_ma_error:
        print(get_ma_error)
        time.sleep(2)
        get_ma(ticker, timeframe, candles)
