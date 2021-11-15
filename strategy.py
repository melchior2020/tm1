from common_method import *


def is_breakthrough(ticker):
    try:
        while True:
            time.sleep(0.5)
            ma9 = get_ma(ticker, '5m', 9)
            time.sleep(0.5)
            ma20 = get_ma(ticker, '5m', 20)
            time.sleep(0.5)
            ma60 = get_ma(ticker, '5m', 60)
            time.sleep(0.5)
            try:
                data = bybit.fetch_ohlcv(ticker, timeframe='5m', limit=1)[0]
            except Exception as fetch_ohlcv_error:
                print(fetch_ohlcv_error)
                print(ma9, ma20, ma60)
                time.sleep(2)
                data = bybit.fetch_ohlcv(ticker, timeframe='5m', limit=1)[0]
            now_price = data[4]
            open_price = data[1]
            if ma60 >= ma20 * 1.003 >= ma9 * 1.003:
                if now_price > ma9 and open_price < now_price:
                    now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    print(now_time, 'Breakthrough strategy long sign on', ticker)
                    return 1
                else:
                    return 0
            elif ma9 >= ma20 * 1.003 >= ma60 * 1.003:     # sell 조건
                if now_price < ma9 and open_price > now_price:
                    now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
                    print(now_time, 'Breakthrough strategy short sign on', ticker)
                    return 2
                else:
                    return 0
            else:
                return 0
    except Exception as fast_breakthrough_error:
        print('fast breakthrough error : ', fast_breakthrough_error)
        time.sleep(1)
        is_breakthrough(ticker)


def is_volume(ticker):
    try:
        data = binance.fetch_ohlcv(ticker, timeframe='5m', limit=150)
        last_candle_diff = data[len(data)-2][4] - data[len(data)-2][1]
        now_vol = data[len(data)-1][5]
        highest_vol = 0
        for i in range(len(data)):
            if data[i][5] >= highest_vol:
                highest_vol = data[i][5]
            else:
                continue
        if now_vol >= highest_vol and last_candle_diff >= 0:
            now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
            print(now_time, 'Volume strategy long sign on', ticker)
            return 1
        elif now_vol >= highest_vol and last_candle_diff < 0:
            now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
            print(now_time, 'Volume strategy short sign on', ticker)
            return 2
        else:
            return 0
    except Exception as fast_volume_error:
        print('fast volume error : ', fast_volume_error)
        time.sleep(1)
        is_volume(ticker)


def is_covergence_enterance(ticker, candles=100):
    atr = get_atr(ticker)
    avg_atr = get_avg_atr(ticker, candles)
    decision_const = avg_atr * 0.7
    if atr < decision_const:
        return 3
    else:
        return 0