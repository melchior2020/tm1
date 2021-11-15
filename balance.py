import schedule
from method_grave import *

start_balance = 81.2579

def save_balance():
    try:
        balance = bybit.fetch_balance()['total']['USDT']
        while True:
            if balance == 0 or balance is None:
                time.sleep(5)
                balance = bybit.fetch_balance()['total']['USDT']
                continue
            else:
                break
        now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M")
        # print(now_time, balance)
        profit_rate = round(((balance - start_balance) / start_balance) * 100, 2)
        data_to_save = [now_time, balance, profit_rate]

        try:
            data = pd.read_csv('./balance/balance.csv', index_col=0)
            data.loc[len(data)] = data_to_save
            data.to_csv('./balance/balance.csv')
        except:
            data = pd.DataFrame(columns=['time', 'balance', 'profit_rate'])
            data.loc[len(data)] = data_to_save
            data.to_csv('./balance/balance.csv')
    except Exception as save_balance_error:
        now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        print(now_time, 'save balance error : ', save_balance_error)
        time.sleep(1)
        save_balance()


def job():
    save_balance()


def balance_saver():
    try:
        schedule.every().day.at("00:00:00").do(job)
        schedule.every().day.at("01:00:00").do(job)
        schedule.every().day.at("02:00:00").do(job)
        schedule.every().day.at("03:00:00").do(job)
        schedule.every().day.at("04:00:00").do(job)
        schedule.every().day.at("05:00:00").do(job)
        schedule.every().day.at("06:00:00").do(job)
        schedule.every().day.at("07:00:00").do(job)
        schedule.every().day.at("08:00:00").do(job)
        schedule.every().day.at("09:00:00").do(job)
        schedule.every().day.at("10:00:00").do(job)
        schedule.every().day.at("11:00:00").do(job)
        schedule.every().day.at("12:00:00").do(job)
        schedule.every().day.at("13:00:00").do(job)
        schedule.every().day.at("14:00:00").do(job)
        schedule.every().day.at("15:00:00").do(job)
        schedule.every().day.at("16:00:00").do(job)
        schedule.every().day.at("17:00:00").do(job)
        schedule.every().day.at("18:00:00").do(job)
        schedule.every().day.at("19:00:00").do(job)
        schedule.every().day.at("20:00:00").do(job)
        schedule.every().day.at("21:30:00").do(job)
        schedule.every().day.at("22:00:00").do(job)
        schedule.every().day.at("23:00:00").do(job)

        while True:
            schedule.run_pending()
            time.sleep(0.1)

    except Exception as balance_save_error:
        now_time = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d %H:%M:%S")
        print(now_time, 'balance save error : ', balance_save_error)
        time.sleep(3)
        balance_saver()

