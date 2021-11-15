import ccxt
import time
from pprint import pprint as pp
import datetime
from telegram_bot import *

bybit = ccxt.bybit({
                    'api_key': 'thcItMKHlhAp1j5bM7',
                    'secret': '2X0DjV8HGH7W37KxRVgnGjMuTkbWLt006ElU'
})

binance = ccxt.binance()


def get_ma(ticker, timeframe, candles):
    try:
        data = bybit.fetch_ohlcv(ticker, timeframe=timeframe, limit = candles)
        if data is None:
            time.sleep(0.5)
            data = bybit.fetch_ohlcv(ticker, timeframe=timeframe, limit=candles)
        hap = 0
        for i in range(candles):
            hap += data[i][4]
        ma = hap / candles
        return ma
    except Exception as get_ma_error:
        print(get_ma_error)
        time.sleep(2)
        get_ma(ticker, timeframe, candles)


def check_position():
    position = bybit.fetch_positions()
    my_position = []
    for i in range(len(position)):
        if position[i]['data']['position_margin'] == '0':
            continue
        else:
            # print(position[i]['data'])
            symbol = position[i]['data']['symbol'].replace('USDT', '/USDT')
            side = position[i]['data']['side'].lower()
            entry_price = position[i]['data']['entry_price']
            size = position[i]['data']['size']
            position_value = position[i]['data']['position_value']
            position_margin = position[i]['data']['position_margin']
            occ_closing_fee = position[i]['data']['occ_closing_fee']
            stop_loss = position[i]['data']['stop_loss']
            take_profit = position[i]['data']['take_profit']
            my_position.append({'ticker': symbol,
                                'side': side,
                                'entry_price' : entry_price,
                                'qty' : size,
                                'position_value': position_value,
                                'position_margin': position_margin,
                                'occ_closing_fee': occ_closing_fee,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit
                                })
    return my_position


def is_holding_position(ticker, side):
    checked_position = check_position()
    return_bool = False
    for i in range(len(checked_position)):
        position_ticker = checked_position[i]['ticker']
        position_side = checked_position[i]['side']
        if position_ticker == ticker and position_side == side:
            return_bool = True
            break
        else:
            continue
    return return_bool


def cancel_order(order_id, order_ticker):
    bybit.cancel_order(order_id, order_ticker)


def get_total_balance():
    balance = bybit.fetch_balance()['USDT']['total']
    return balance


def get_min_qty(ticker):
    data = bybit.fetch_markets()
    for i in range(len(data)):
        if ticker == data[i]['symbol']:
            return float(data[i]['info']['lot_size_filter']['min_trading_qty'])
        else:
            continue
    print('There is no ticker name : ', ticker)


def get_min_price_tick(ticker):
    data = bybit.fetch_markets()
    for i in range(len(data)):
        if ticker == data[i]['symbol']:
            return float(data[i]['info']['price_filter']['tick_size'])
        else:
            continue
    print('There is no ticker name : ', ticker)

# pp(get_min_price_tick('BTC/USDT'))

def get_active_orders(ticker):
    orders = bybit.fetch_orders(ticker)
    active_orders = []
    for i in range(len(orders)):
        if orders[i]['status'] == 'open' and orders[i]['info']['reduce_only'] is True:
            order_id = orders[i]['id']
            order_price = float(orders[i]['price'])
            order_qty = float(orders[i]['remaining'])
            order_side = orders[i]['side']
            order_data = {
                'order_ticker' : ticker,
                'order_id': order_id,
                'order_price': order_price,
                'order_qty': order_qty,
                'order_side': order_side
            }
            active_orders.append(order_data)
        else:
            continue
    return active_orders


def send_order_message(strategy_name, ticker, side):
    send_message("New order submitted" + "\n" +
                 "Strategy name : " + strategy_name + "\n" +
                 "Ticker : " + ticker + "\n" +
                 "Side : " + side
                 )


def send_scale_order_message(ticker, side):
    send_message("Scale order submitted" + "\n" +
                 "Ticker : " + ticker + "\n" +
                 "Side : " + side
                 )


def get_atr(ticker, before_count=0):
    data = binance.fetch_ohlcv(ticker, timeframe='5m', limit=15+before_count)
    true_range_list = []
    for i in range(len(data)-1-before_count):
        prev_close = data[i][4]
        current_high = data[i+1][2]
        current_low = data[i+1][3]
        diff1 = current_high - current_low
        diff2 = current_high - prev_close
        diff3 = current_low - prev_close
        true_range = max(diff1, diff2, diff3)
        true_range_list.append(true_range)
    atr = sum(true_range_list)/len(true_range_list)
    return atr

# get_atr('BTC/USDT', 1)


def get_avg_atr(ticker, candles=100):
    atr_list = []
    for i in range(candles):
        atr_value = get_atr(ticker, i)
        atr_list.append(atr_value)
        time.sleep(0.1)
    avg_atr = sum(atr_list) / len(atr_list)
    return avg_atr


def is_activated(order_data, ticker): # 자꾸 루프걸기 개빡쳐서 만듦
    order_id = order_data['info']['order_id']
    order_ticker = order_data['info']['symbol'].replace('USDT', '/USDT')
    order_info = bybit.fetch_order(order_id, order_ticker)
    order_remaining = float(order_info['remaining'])
    if order_remaining == 0:
        return 1
    else:
        return 0