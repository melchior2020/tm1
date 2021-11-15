import balance
from trade import *
from threading import Thread


trade_worker = Thread(target=execute_trade)
balance_worker = Thread(target=balance.balance_saver)

trade_worker.start()
balance_worker.start()
