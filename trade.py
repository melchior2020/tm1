from strategy import *


class Worker:
    def __init__(self, strategy, ticker, take_profit_rate, stop_loss_rate, scale_rate, leverage):
        self.ticker = ticker
        self.strategy = strategy
        self.strategy_name = strategy.__name__
        self.init_margin_rate = 0.05
        self.take_profit_rate = take_profit_rate
        self.stop_loss_rate = stop_loss_rate
        self.scale_rate = scale_rate
        self.min_qty = get_min_qty(ticker)  # 이거 소수점 몇째자리인지 알아야한다 밑에 주문수량에 round 걸어줘야함
        self.min_price_tick = get_min_price_tick(ticker)
        self.leverage = leverage

    def check_signal(self):
        strategy_signal = self.strategy(self.ticker)
        holding_bool = False
        if strategy_signal == 0:
            pass
        elif strategy_signal == 1:
            holding_bool = is_holding_position(self.ticker, 'buy')
        elif strategy_signal == 2:
            holding_bool = is_holding_position(self.ticker, 'sell')
        elif strategy_signal == 3:
            long_holding_bool = is_holding_position(self.ticker, 'buy')
            short_holding_bool = is_holding_position(self.ticker, 'sell')
            if long_holding_bool is True or short_holding_bool is True:
                holding_bool = True
        else:
            print(self.strategy_name, 'There is something problem in signal')
            pass

        if holding_bool is True:
            strategy_signal = 0
            print('But already have position.')
        else:
            pass

        return strategy_signal

    def create_order(self, side, qty=float(0), scale_ticker=0):
        result = 0
        if side == 'buy':
            orderbook_side = 'bids'
            price_multiplier = 1
        else:
            orderbook_side = 'asks'
            price_multiplier = -1
        total_balance = get_total_balance()
        order_value = total_balance * self.init_margin_rate * self.leverage
        now_price = bybit.fetch_order_book(self.ticker)[orderbook_side][0][0]
        checked_position = check_position()
        prev_price = 0
        for i in range(len(checked_position)):
            if checked_position[i]['ticker'] == self.ticker and checked_position[i]['side'] == side:
                prev_price = float(checked_position[i]['entry_price'])
            else:
                continue
        if qty == 0:
            stop_price_raw = now_price * (1 - self.stop_loss_rate * price_multiplier)
            stop_price = round(stop_price_raw / self.min_price_tick, 0) * self.min_price_tick
        else:
            stop_price_raw = ((now_price + prev_price) / 2) * (1 - self.stop_loss_rate * price_multiplier)
            stop_price = round(stop_price_raw / self.min_price_tick, 0) * self.min_price_tick
            print('New stop_loss_price : ', stop_price)
        order_qty = order_value / now_price
        if order_qty >= self.min_qty:
            pass
        else:
            order_qty = self.min_qty

        if qty != 0:
            order_qty = qty
        else:
            pass

        print(self.ticker, side, now_price, order_qty, stop_price)
        if qty != 0:
            order_data = bybit.create_limit_order(scale_ticker, side, order_qty, now_price,
                                                  params={'stop_loss': stop_price})
            send_scale_order_message(self.ticker, side)
        else:
            order_data = bybit.create_limit_order(self.ticker, side, order_qty, now_price,
                                                  params={'stop_loss': stop_price})
            send_order_message(self.strategy_name, self.ticker, side)

        order_id = order_data['info']['order_id']
        order_ticker = order_data['info']['symbol'].replace('USDT', '/USDT')
        waiting_count = 0
        while True:
            time.sleep(2)
            waiting_count += 2
            order_info = bybit.fetch_order(order_id, order_ticker)
            remaining = float(order_info['remaining'])
            if remaining == 0:
                result = 1
                break
            else:
                if waiting_count >= 60:
                    cancel_order(order_id, order_ticker)
                    print("order cancelled")
                    send_message("previous order has been deactivated.")
                    break
                else:
                    continue
        return result

    def check_profit_order(self):
        positions = check_position()
        if len(positions) == 0:
            pass
        else:
            for i in range(len(positions)):
                # print(positions)
                ticker = positions[i]['ticker']
                if ticker != self.ticker:
                    continue
                side = positions[i]['side']
                # print(side)
                entry_price = float(positions[i]['entry_price'])
                qty = float(positions[i]['qty'])
                if side == 'buy':
                    profit_multiplier = 1
                elif side == 'sell':
                    profit_multiplier = -1
                else:
                    profit_multiplier = 1
                profit_price = entry_price * (1 + self.take_profit_rate * profit_multiplier)
                if side == 'buy':
                    opposite_side = 'sell'
                else:
                    opposite_side = 'buy'
                active_orders = get_active_orders(ticker)
                if len(active_orders) == 0:  # there is no active order # 주문을 제대로 읽어오지 못하는 경우가 있다.
                    bybit.create_order(ticker, 'limit', opposite_side, qty, profit_price, params={'reduce_only': True})
                elif len(active_orders) == 1:
                    if active_orders[0]['order_side'] == opposite_side:  # 사이드가 같으면
                        if float(active_orders[0]['order_qty']) == qty:  # 수량이 같으면
                            if profit_price * 0.99 <= active_orders[0]['order_price'] <= profit_price * 1.01:  # 가격도 같으면
                                pass
                            else:  # 가격이 다르면
                                bybit.edit_order(active_orders[0]['order_id'], ticker, 'limit', opposite_side,
                                                 price=profit_price)
                        else:  # 수량이 다르면
                            bybit.edit_order(active_orders[0]['order_id'], ticker, 'limit', opposite_side, amount=qty,
                                             price=profit_price)
                    else:
                        bybit.create_order(ticker, 'limit', opposite_side, qty, profit_price,
                                           params={'reduce_only': True})
                else:  # active orders 가 두개면
                    for j in range(len(active_orders)):
                        if active_orders[j]['order_side'] == opposite_side:
                            # print(active_orders[j])
                            if active_orders[j]['order_qty'] == qty:  # 수량이 같으면
                                # print(active_orders[j]['order_qty'], qty)
                                if profit_price * 0.99 <= \
                                        active_orders[j]['order_price'] <= \
                                        profit_price * 1.01:  # 가격이 같으면
                                    pass
                                else:  # 가격이 다르면
                                    bybit.edit_order(active_orders[j]['order_id'], ticker, 'limit', opposite_side,
                                                     price=profit_price)
                            else:  # 수량이 다르면
                                # print(1)
                                bybit.edit_order(active_orders[0]['order_id'], ticker, 'limit', opposite_side,
                                                 amount=qty,
                                                 price=profit_price)
                        else:
                            continue

    def check_scale_condition(self):
        positions = check_position()
        if len(positions) == 0:
            pass
        else:
            for i in range(len(positions)):
                ticker = positions[i]['ticker']
                if ticker == self.ticker:
                    qty = float(positions[i]['qty'])
                    entry_price = float(positions[i]['entry_price'])
                    side = positions[i]['side']
                    scale_rate = self.scale_rate
                    if side == 'buy':
                        price_multiplier = 1
                        orderbook_side = 'bids'
                    else:
                        price_multiplier = -1
                        orderbook_side = 'asks'
                    now_price = float(bybit.fetch_order_book(ticker)[orderbook_side][0][0])
                    total_balance = get_total_balance()
                    if now_price * qty / self.leverage >= total_balance * 0.15:
                        break
                    else:
                        pass
                    diff_rate = ((now_price - entry_price) / entry_price) * price_multiplier
                    # print(self.ticker, diff_rate)
                    if diff_rate <= scale_rate * -1:
                        while True:
                            scale_result = self.create_order(side, qty, ticker)
                            if scale_result == 0:
                                continue
                            else:
                                break
                    else:
                        pass
                else:
                    continue

    def execute(self):
        try:
            signal = self.check_signal()
            if signal == 0:
                pass
            elif signal == 1:
                self.create_order('buy')
            elif signal == 2:
                self.create_order('sell')
            elif signal == 3:
                # 양방향 주문 / 양쪽 주문 다 걸린 것 확인해야지 이탈
                # 지금 안쓰니 대강 해놓고 말자
                self.create_order('buy')
                self.create_order('sell')
            self.check_profit_order()
            self.check_scale_condition()

        except Exception as execute_inner_error:
            print(self.ticker, self.strategy_name, execute_inner_error)


breakthrough_1 = Worker(is_breakthrough, 'MANA/USDT', 0.03, 0.06, 0.04, 10)
breakthrough_2 = Worker(is_breakthrough, 'IOTX/USDT', 0.03, 0.06, 0.04, 10)
breakthrough_3 = Worker(is_breakthrough, 'SAND/USDT', 0.03, 0.06, 0.04, 10)
volume_1 = Worker(is_volume, 'MANA/USDT', 0.03, 0.06, 0.04, 10)
volume_2 = Worker(is_volume, 'IOTX/USDT', 0.03, 0.06, 0.04, 10)
volume_3 = Worker(is_volume, 'SAND/USDT', 0.03, 0.06, 0.04, 10)


def execute_trade():
    try:
        while True:
            breakthrough_1.execute()
            time.sleep(1)
            breakthrough_2.execute()
            time.sleep(1)
            breakthrough_3.execute()
            time.sleep(1)
            volume_1.execute()
            time.sleep(1)
            volume_2.execute()
            time.sleep(1)
            volume_3.execute()
            time.sleep(1)
            # print(datetime.datetime.now())
            time.sleep(2)
    except Exception as execute_error:
        print('execute error : ', execute_error)
        execute_trade()
