from common_method import *

checked_position = check_position()
for i in range(len(checked_position)):
    if checked_position[i]['ticker'] == 'BTC/USDT' and checked_position[i]['side'] == 'sell':
        print(checked_position[i]['entry_price'])
    else:
        continue