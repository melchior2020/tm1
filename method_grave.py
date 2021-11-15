import ccxt
import time
import datetime
from telegram_bot import *

bybit = ccxt.bybit({
                    'api_key': 'o3r5vAFgEGLX8JWNfN',
                    'secret': 'uXH1AdEE20UehJrz8lsDVQmX84nBvWkqmhWx'
})

def is_holding_position(ticker, side):
    pass

def check_position():
    position = bybit.fetch_positions()
    my_position = []
    for i in range(len(position)):
        if position[i]['data']['position_margin'] == '0':
            continue
        else:
            #print(position[i]['data'])
            symbol = position[i]['data']['symbol']
            side = position[i]['data']['side'].lower()
            entry_price = position[i]['data']['entry_price']
            size = position[i]['data']['size']
            position_value = position[i]['data']['position_value']
            position_margin = position[i]['data']['position_margin']
            occ_closing_fee = position[i]['data']['occ_closing_fee']
            stop_loss = position[i]['data']['stop_loss']
            take_profit = position[i]['data']['take_profit']
            my_position.append({'symbol': symbol,
                                'side': side,
                                'entry_price' : entry_price,
                                'size' : size,
                                'position_value': position_value,
                                'position_margin': position_margin,
                                'occ_closing_fee': occ_closing_fee,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit
                                })
    return my_position



def cancel_all_order():
    data = bybit.fetch_tickers()
    tickers = list(data.keys())
    for ticker in tickers:
        bybit.cancel_all_orders(ticker)

# cancel_all_order()


def cancel_all_order_of_ticker(ticker):
    bybit.cancel_all_orders(ticker)


def check_signal(signals):
    strategies = list(signals.keys())
    signal_on = []
    for strategy in strategies:
        if signals[strategy][1] == 1:
            signal_on.append(signals[strategy])
        else:
            continue
    print(signal_on)
    return signal_on

#check_signal(signals)


def cal_order_rate(take_profit=0, stop_loss=0, win_rate=0):
    return 0.05


def open_order(ticker, order_size, side, take_profit=0, stop_loss=0, expected_avg_price=0):
    if side == 'buy':
        orderbook = bybit.fetch_order_book(ticker)
        buy_price = orderbook['bids'][1][0]
        qty = (order_size / buy_price) * 10
        if qty < 0.001:
            qty = 0.001
        if expected_avg_price == 0:
            stop_price = round(buy_price * (1 - stop_loss), 2)
            profit_price = round(buy_price * (1 + take_profit), 2)
        else:
            stop_price = round(expected_avg_price * (1 - stop_loss), 1)
            profit_price = round(expected_avg_price * (1 + take_profit), 1)
        order_data = bybit.create_order(ticker, 'limit', 'buy', round(qty, 3), buy_price, params={'stop_loss': stop_price})
        if expected_avg_price == 0:
            send_order_message(ticker, 'buy')
        else:
            send_scale_order_message(ticker, 'buy')
        order_id = order_data['info']['order_id']
        order_side = order_data['info']['side'].lower() # 있는지 체크
        order_ticker = order_data['info']['symbol'].replace('USDT', '/USDT')
        order_qty = float(order_data['amount'])
        time.sleep(60)
        order_info = bybit.fetch_order(order_id, order_ticker)
        remaining = float(order_info['remaining'])
        if remaining == 0:
            if expected_avg_price == 0:
                bybit.create_order(order_ticker, 'limit', 'sell', order_qty, profit_price, params={'reduce_only': True})
            else:
                entry_data = get_entry_data(order_ticker, order_side)
                entry_price = entry_data[0]
                entry_qty = entry_data[1]
                profit_price = round(entry_price * (1 + take_profit), 1)
                bybit.create_order(order_ticker, 'limit', 'sell', entry_qty, profit_price, params={'reduce_only': True})
        else:
            if remaining == order_qty:
                cancel_order(order_data)
            else:
                partial_order_qty = order_qty - remaining
                if expected_avg_price == 0:
                    cancel_order(order_data)
                    bybit.create_order(order_ticker, 'limit', 'sell', partial_order_qty, profit_price, params={'reduce_only': True})
                else:
                    entry_data = get_entry_data(order_ticker, order_side)
                    entry_price = entry_data[0]
                    entry_qty = entry_data[1]
                    profit_price = round(entry_price * (1 + take_profit), 1)
                    cancel_order(order_data)
                    bybit.create_order(order_ticker, 'limit', 'sell', entry_qty, profit_price, params={'reduce_only': True})

    else:
        orderbook = bybit.fetch_order_book(ticker)
        sell_price = orderbook['asks'][1][0]
        qty = (order_size / sell_price) * 10
        print('price : ', sell_price)
        print('order qty : ', qty)
        if qty < 0.001:
            qty = 0.001
        if expected_avg_price == 0:
            profit_price = round(sell_price * (1 - take_profit), 2)
            stop_price = round(sell_price * (1 + stop_loss), 2)
        else:
            profit_price = round(expected_avg_price * (1 - take_profit), 1)
            stop_price = round(expected_avg_price * (1 + stop_loss), 1)
        order_data = bybit.create_order(ticker, 'limit', 'sell', round(qty, 3), sell_price, params={'stop_loss': stop_price})
        if expected_avg_price == 0:
            send_order_message(ticker, 'sell')
        else:
            send_scale_order_message(ticker, 'sell')
        order_id = order_data['info']['order_id']
        order_side = order_data['info']['side'].lower()
        order_ticker = order_data['info']['symbol'].replace('USDT', '/USDT')
        order_qty = float(order_data['amount'])
        time.sleep(60)
        order_info = bybit.fetch_order(order_id, order_ticker)
        remaining = float(order_info['remaining'])
        if remaining == 0:
            if expected_avg_price == 0:
                bybit.create_order(order_ticker, 'limit', 'buy', order_qty, profit_price, params={'reduce_only': True})
            else:
                entry_data = get_entry_data(order_ticker, order_side)
                entry_price = entry_data[0]
                entry_qty = entry_data[1]
                profit_price = round(entry_price * (1 - take_profit), 1)
                bybit.create_order(order_ticker, 'limit', 'buy', entry_qty, profit_price, params={'reduce_only': True})
        else:
            if remaining == order_qty:
                cancel_order(order_data)
            else:
                partial_order_qty = order_qty - remaining
                if expected_avg_price == 0:
                    cancel_order(order_data)
                    bybit.create_order(order_ticker, 'limit', 'buy', partial_order_qty, profit_price, params={'reduce_only': True})
                else:
                    entry_data = get_entry_data(order_ticker, order_side)
                    entry_price = entry_data[0]
                    entry_qty = entry_data[1]
                    profit_price = round(entry_price * (1 - take_profit), 1)
                    cancel_order(order_data)
                    bybit.create_order(order_ticker, 'limit', 'buy', entry_qty, profit_price, params={'reduce_only': True})


#open_order('ETH/USDT', 2, 'buy', 0.03, 0.02)


def check_remain_order(ticker):
    data = bybit.fetch_open_orders(ticker)
    remains = []
    #print(data[0])
    for i in range(len(data)):
        remains.append([ticker, data[i]['remaining']])
    if len(remains) == 0:
        return 0
    else:
        return remains[0][1]


# remainings = check_remain_order('BTC/USDT')
# print(remainings)


def close_position(ticker, profit_rate):
    checked_position = check_position()
    print(checked_position)
    symbol = ticker.replace('/','')
    for i in range(len(checked_position)):
        if checked_position[i]['symbol'] == symbol:
            if checked_position[i]['side'] == 'buy':
                amount = checked_position[i]['size']
                entry_price = float(checked_position[i]['entry_price'])
                goal_price = entry_price * (1 + profit_rate)
                bybit.create_limit_order(ticker, 'sell', amount, goal_price)
            else:
                amount = checked_position[i]['size']
                entry_price = float(checked_position[i]['entry_price'])
                goal_price = entry_price * (1 - profit_rate)
                bybit.create_limit_order(ticker, 'buy', amount, goal_price)
        else:
            continue

# close_position('BTC/USDT', 0.01)


def get_remain_order():
    data = bybit.fetch_orders('BTC/USDT')
    current_order = []
    for i in range(len(data)):
        if data[i]['status'] == 'canceled':
            continue
        else:
            if data[i]['remaining'] == 0:
                continue
            else:
                current_order = data[i]['info']['order_id']
    remain_order = bybit.fetch_order(current_order, 'BTC/USDT')
    return remain_order


def cancel_order(order_info):
    order_id = order_info['info']['order_id']
    order_ticker = order_info['info']['symbol'].replace('USDT', '/USDT')
    bybit.cancel_order(order_id, order_ticker)


def get_closed_position():
    data = bybit.fetch_closed_orders('BTC/USDT')
    for i in range(len(data)):
        #print(data[i])
        if data[i]['info']['order_status'] == 'Cancelled':
            continue
        else:
            print(data[i]['info']['order_id'],
                  data[i]['info']['created_time'],
                  data[i]['info']['symbol'],
                  data[i]['info']['side'],
                  data[i]['info']['order_type'],
                  data[i]['info']['price'],
                  data[i]['info']['qty'],
                  data[i]['info']['order_status'],
                  data[i]['fees'])

# get_closed_position()


def get_total_balance():
    balance = bybit.fetch_balance()['USDT']['total']
    return balance

# get_total_balance()


def scale_trading(scale_goal):
    try:
        # basic position information
        position_data = check_position()
        if position_data == []:
            return 0
        else:
            ticker = position_data[0]['symbol'].replace('USDT', '/USDT')
            side = position_data[0]['side']
            if side == 'sell':
                rate_multiplier = -1
            else:
                rate_multiplier = 1
            size = float(position_data[0]['size'])
            position_margin = float(position_data[0]['position_margin'])
            occ_closing_fee = float(position_data[0]['occ_closing_fee'])
            position_total_margin = position_margin + occ_closing_fee
            entry_price = float(position_data[0]['entry_price'])
            take_profit_price = float(position_data[0]['take_profit'])
            stop_loss_price = float(position_data[0]['stop_loss'])
            take_profit_rate = 0.015 * rate_multiplier
            stop_loss_rate = ((entry_price - stop_loss_price) / entry_price) * rate_multiplier

            # basic balance information
            total_balance = get_total_balance()
            free_balance = total_balance - position_total_margin
            position_share = position_total_margin / total_balance

            scale_num = "0"
            # check number of scale trade by proportion of position and set proportion of scale trade
            if 0 < position_share < 0.10:
                scale_share = 0.1
                scale_num = "1"
            elif 0.13 < position_share < 0.2:
                scale_share = 0.15
                scale_num = "2"
            else:
                scale_share = 0  # means scale trading already done twice

            # calculate percent change of price
            # whether holding position is long or not, to express their percent change in same way
            now_price = bybit.fetch_ohlcv(ticker, '1m', limit=1)[0][4]
            if now_price is None:
                time.sleep(1)
                now_price = bybit.fetch_ohlcv(ticker, '1m', limit=1)[0][4]
            if side == 'buy':
                per_change = (now_price - entry_price) / entry_price
            elif side == 'sell':
                per_change = (entry_price - now_price) / entry_price
            else:
                print('error in per_change calculating')
                per_change = 0
            #print(position_share, per_change)
            # scale_share == 0 means scale trading already done twice
            # if situation is worser than expected(scale_goal), do scale trade. if it isn't, pass this algorithm
            if scale_share == 0:
                pass
            else:
                if per_change < scale_goal:
                    order_size = round(free_balance * scale_share, 2) # 달러사이즈로 넘기기
                    expected_avg_price = (entry_price * size + now_price * order_size) / (size + order_size) # 물탈 경우 생각해서 예상 평단 구하기
                    open_order(ticker, order_size, side, take_profit_rate, stop_loss_rate, expected_avg_price)
                else:
                    pass
    except Exception as scale_trading_error:
        now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        print(now_time, 'scale trading error : ', scale_trading_error)
        time.sleep(1)
        scale_trading(scale_goal)

#scale_trading(0.05)


def get_entry_data(ticker, side):
    data = bybit.fetch_positions(ticker)
    temp_ticker = ticker.replace('/USDT', 'USDT')
    position_data = []
    for i in range(len(data)):
        if data[i]['data']['symbol'] == temp_ticker and data[i]['data']['side'] == side.capitalize():
            position_data = data[i]
        else:
            continue
    position_entry_price = float(position_data['data']['entry_price'])
    position_qty = float(position_data['data']['size'])
    return [position_entry_price, position_qty]


def make_loss_cut():
    checked_position = check_position()[0]
    checked_side = checked_position['side']
    checked_size = checked_position['size']
    if checked_side == 'buy':
        orderbook_data = bybit.fetch_order_book('BTC/USDT')['asks']
        order_price = orderbook_data[0][0]
        bybit.create_limit_order('BTC/USDT', 'sell', checked_size, order_price)
    elif checked_side == 'sell':
        orderbook_data = bybit.fetch_order_book('BTC/USDT')['bids']
        order_price = orderbook_data[0][0]
        bybit.create_limit_order('BTC/USDT', 'buy', checked_size, order_price)
    else:
        print("try to make close order but there is no position have") # 혹시 오류 날까봐 메세지 띄움


def send_order_message(ticker, side):
    send_message("New order submitted" + "\n" +
                 "Ticker : " + ticker + "\n" +
                 "Side : " + side
                 )


def send_scale_order_message(ticker, side):
    send_message("Scale order submitted" + "\n" +
                 "Ticker : " + ticker + "\n" +
                 "Side : " + side
                 )