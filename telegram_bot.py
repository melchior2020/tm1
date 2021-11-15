import telegram
from pytz import timezone
import pandas as pd


chat_token = '1405175287:AAHffNyMPso-mJLpwkBtukjrrepzOzJKq_4'
bot = telegram.Bot(token=chat_token)
# 메세지 보내기
def send_message(text):
    bot.sendMessage(chat_id = "-707346856", text=text)
# 그룹방 -575143119
# 나 995177083
# showbu -707346856


#received_data = bot.getUpdates()[-1].message
#received_data = bot.getUpdates()[-2]
#print(received_data)
#send_message("hello fucking world")

'''
send_message("dkdkfenfksldnfklsdnfd\n"
             "klsfnskldnfnkdlsnefkld\n"
             "dekfkdskdkf: dkfkefkn\n"
             "dddddddddddddddddddddddd\n"
             "efdfsdfjkeljdfi\n")
다섯줄만 한번에 보인다.
'''

# 메세지 로그를 만들고 새로운 메세지가 없으면 0 있으면 1 을 반환
def check_message_log():
    try:
        received_data = bot.getUpdates()[-1].message
    except:
        received_data = bot.getUpdates()[-1].message
    message_data = [received_data.date.astimezone(timezone('Asia/Seoul')),received_data.from_user.id,received_data.text]

    message_log = pd.read_csv('untitled\data\message_log.csv', index_col=0)
    length_data_before = len(message_log)
    last_message_time = message_log['time'][len(message_log)-1]
    new_sign = []

    if last_message_time == str(message_data[0]):
        None
    else:
        message_log.loc[len(message_log)] = message_data

    length_data_after = len(message_log)

    if length_data_after > length_data_before:
        message_log.to_csv("untitled\data\message_log.csv")
        new_sign = [1,message_log['message'][len(message_log)-1]]
    else:
        None

    #print(message_log)
    #print(new_sign)

    return new_sign



'''
def new_message_check():
    received_data = bot.getUpdates()[-1].message
    last_message_time = received_data.date.astimezone(timezone('Asia/Seoul'))
    present_time = datetime.datetime.now(timezone('Asia/Seoul'))
    time_value = present_time - last_message_time
    print(last_message_time)
    print(present_time)
    print(time_value)

new_message_check()
'''