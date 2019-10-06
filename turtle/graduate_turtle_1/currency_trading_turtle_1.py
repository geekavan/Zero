"""
版本号：_turtle_1
版本功能：
1.为某一交易产品的某一个周期寻找合适的海龟交易法则周期
2.开仓所用周期为num1，平仓为num2；num1，num2的范围可调
note:
1.这里产生的transactions的最后一笔交易可能还未平仓
2.这里产生的transactions的index是从0开始的
3.这里的海龟交易法则：
#1若本时刻的收盘价超过本时刻的前num1个时刻开盘和收盘最高价（不包括本时刻），则在下一个时刻的开盘时买入
#2若本时刻的收盘价低于本时刻的前num2个时刻开盘和收盘最低价（不包括本时刻），则在下一个时刻的开盘时平仓
#3卖出情况类同
4.本程序的手数用的是0.1手
品种适用性：
1.address需要修改，fee买卖价差需要修改,nums_per_size需要修改
周期适用性：
1.无需修改
其他适用性：
1.注意修改投资资金capital,手数size
"""
import pandas as pd
from cal_details_turtle_2 import details


def read_data(address):
    read_currency_data = pd.read_csv(address)
    return read_currency_data


def send_open_order(transactions, ticket, open_date, open_time, Type, size, open_price):
    transactions.at[ticket, 'open_date'] = open_date
    transactions.at[ticket, 'open_time'] = open_time
    transactions.at[ticket, 'type'] = Type
    transactions.at[ticket, 'size'] = size
    transactions.at[ticket, 'open_price'] = open_price
    return transactions


def send_close_order(transactions, ticket, close_date, close_time, close_price):
    transactions.at[ticket, 'close_date'] = close_date
    transactions.at[ticket, 'close_time'] = close_time
    transactions.at[ticket, 'close_price'] = close_price
    return transactions


def history_test(currency_data, start_num1=10, end_num1=48, start_num2=10,
                 capital=10000, fee=30, nums_per_size=100, size=0.1):
    for num1 in range(start_num1, end_num1+1):
        for num2 in range(start_num2, num1+1):
            period_for_open = num1
            period_for_close = num2
            print('开仓周期：', period_for_open)
            print('平仓周期：', period_for_close)
            print('初始资金：', capital, '资金大是为了不爆仓')
            print('交易价差：', fee, '(每手)')
            print('交易手数：', size)
            print('__________________________________')
            transactions = pd.DataFrame()
            account = 0
            ticket = -1
            for i in range(len(currency_data)-1):
                if i >= max(period_for_open, period_for_close):
                    if account == 0:
                        open_temp_max = max(currency_data[i - period_for_open: i]['open'])
                        close_temp_max = max(currency_data[i - period_for_open: i]['close'])
                        open_temp_min = min(currency_data[i - period_for_open: i]['open'])
                        close_temp_min = min(currency_data[i - period_for_open: i]['close'])
                        price_max = max(open_temp_max, close_temp_max)
                        price_min = min(open_temp_min, close_temp_min)
                        if currency_data.at[i, 'close'] > price_max:
                            ticket += 1
                            transactions = send_open_order(transactions, ticket, currency_data.at[i+1, 'date'],
                                                   currency_data.at[i+1, 'time'], 'buy', size,
                                                   currency_data.at[i+1, 'open'])
                            account = 1
                        elif currency_data.at[i, 'close'] < price_min:
                            ticket += 1
                            transactions = send_open_order(transactions, ticket, currency_data.at[i+1, 'date'],
                                                   currency_data.at[i+1, 'time'], 'sell', size,
                                                   currency_data.at[i+1, 'open'])
                            account = 1
                    elif account == 1:
                        open_temp_max = max(currency_data[i - period_for_close: i]['open'])
                        close_temp_max = max(currency_data[i - period_for_close: i]['close'])
                        open_temp_min = min(currency_data[i - period_for_close: i]['open'])
                        close_temp_min = min(currency_data[i - period_for_close: i]['close'])
                        price_max = max(open_temp_max, close_temp_max)
                        price_min = min(open_temp_min, close_temp_min)
                        if transactions.at[ticket, 'type'] == 'buy' and currency_data.at[i, 'close'] < price_min:
                            transactions = send_close_order(transactions, ticket, currency_data.at[i+1, 'date'],
                                                    currency_data.at[i+1, 'time'],
                                                    currency_data.at[i+1, 'open'])
                            account = 0
                        elif transactions.at[ticket, 'type'] == 'sell' and currency_data.at[i, 'close'] > price_max:
                            transactions = send_close_order(transactions, ticket, currency_data.at[i+1, 'date'],
                                                    currency_data.at[i+1, 'time'],
                                                    currency_data.at[i+1, 'open'])
                            account = 0
                        # 加上下面这段程序就可以实现，平仓的时刻还可以开仓；不然要等下一个时刻才能触发开仓交易
                        if account == 0:
                            open_temp_max = max(currency_data[i - period_for_open: i]['open'])
                            close_temp_max = max(currency_data[i - period_for_open: i]['close'])
                            open_temp_min = min(currency_data[i - period_for_open: i]['open'])
                            close_temp_min = min(currency_data[i - period_for_open: i]['close'])
                            price_max = max(open_temp_max, close_temp_max)
                            price_min = min(open_temp_min, close_temp_min)
                            if currency_data.at[i, 'close'] > price_max:
                                ticket += 1
                                transactions = send_open_order(transactions, ticket, currency_data.at[i + 1, 'date'],
                                                       currency_data.at[i + 1, 'time'], 'buy', size,
                                                       currency_data.at[i + 1, 'open'])
                                account = 1
                            elif currency_data.at[i, 'close'] < price_min:
                                ticket += 1
                                transactions = send_open_order(transactions, ticket, currency_data.at[i + 1, 'date'],
                                                       currency_data.at[i + 1, 'time'], 'sell', size,
                                                       currency_data.at[i + 1, 'open'])
                                account = 1
            details(transactions, currency_data, capital, fee, nums_per_size)


address = 'D:/graduate/history/currency_history/XAUUSD/XAUUSD60.csv'
print('交易币种：', address[-12:-4])
currency_data = read_data(address)
history_test(currency_data)
