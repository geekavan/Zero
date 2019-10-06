"""
版本号：_turtle_3
版本功能：
1.根据某一个产品的某一个周期给出海龟交易法则的交易记录
note:
1.这里产生的transactions的最后一笔交易可能还未平仓
2.这里产生的transactions的index是从0开始的
3.这里的海龟交易法则：
#1若本时刻的收盘价超过本时刻的前num1个时刻开盘和收盘最高价（不包括本时刻），则在下一个时刻的开盘时买入
#2若本时刻的收盘价低于本时刻的前num2个时刻开盘和收盘最低价（不包括本时刻），则在下一个时刻的开盘时平仓
#3卖出情况类同
新版功能（比对currency_trading_turtle_2）：
1.加入止损优化
品种适用性：
1.read_data()中文件地址需要修改，fee买卖价差需要修改,nums_per_size需要修改
周期适用性：
1.无需修改
其他适用性：
1.注意修改投资资金capital,手数size
"""
import pandas as pd
from cal_details_turtle_2 import details


def read_data():
    read_currency_data = pd.read_csv('D:/graduate/history/currency_history/GBPUSD/GBPUSD60.csv')
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


def history_test(currency_data, period_for_open=43, period_for_close=25, loss_limit_min=300,
                 loss_limit_max=1900, capital=3000, fee=30, nums_per_size=100000, size=0.01):
    for loss_limit_i in range(int(loss_limit_min/100), int(loss_limit_max/100+1)):
        loss_limit = loss_limit_i*100
        print('开仓周期：', period_for_open)
        print('平仓周期：', period_for_close)
        print('单笔最大亏损限定：', loss_limit*size)
        print('初始资金：', capital)
        print('交易价差：', fee, '(每手)')
        print('交易手数：', size)
        print('__________________________________')
        transactions = pd.DataFrame()
        account = 0
        ticket = -1
        for i in range(len(currency_data)-1):
            if i >= max(period_for_open, period_for_close):
                if account == 0:
                    same_time = 0
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
                        same_time += 1
                    elif transactions.at[ticket, 'type'] == 'sell' and currency_data.at[i, 'close'] > price_max:
                        transactions = send_close_order(transactions, ticket, currency_data.at[i+1, 'date'],
                                                        currency_data.at[i+1, 'time'],
                                                        currency_data.at[i+1, 'open'])
                        account = 0
                        same_time += 1
                    #  是否达到最大止损判断及处理（止损优化）
                    if transactions.at[ticket, 'type'] == 'buy':
                        if (transactions.at[ticket, 'open_price'] - currency_data.at[i, 'open']) > (
                                loss_limit / nums_per_size) or \
                                (transactions.at[ticket, 'open_price'] - currency_data.at[i, 'high']) > (
                                loss_limit / nums_per_size) or \
                                (transactions.at[ticket, 'open_price'] - currency_data.at[i, 'low']) > (
                                loss_limit / nums_per_size) or \
                                (transactions.at[ticket, 'open_price'] - currency_data.at[i, 'close']) > (
                                loss_limit / nums_per_size):
                            transactions = send_close_order(transactions, ticket, currency_data.at[i, 'date'],
                                                            currency_data.at[i, 'time'],
                                                            transactions.at[
                                                                    ticket, 'open_price'] - loss_limit / nums_per_size)
                            if same_time == 1:
                                account = 0
                            elif same_time == 0:
                                account = 'waiting'
                    elif transactions.at[ticket, 'type'] == 'sell':
                        if (currency_data.at[i, 'open'] - transactions.at[ticket, 'open_price']) > (
                                loss_limit / nums_per_size) or \
                                (currency_data.at[i, 'high'] - transactions.at[ticket, 'open_price']) > (
                                loss_limit / nums_per_size) or \
                                (currency_data.at[i, 'low'] - transactions.at[ticket, 'open_price']) > (
                                loss_limit / nums_per_size) or \
                                (currency_data.at[i, 'close'] - transactions.at[ticket, 'open_price']) > (
                                loss_limit / nums_per_size):
                            transactions = send_close_order(transactions, ticket, currency_data.at[i, 'date'],
                                                            currency_data.at[i, 'time'],
                                                            transactions.at[
                                                                    ticket, 'open_price'] + loss_limit / nums_per_size)
                            if same_time == 1:
                                account = 0
                            elif same_time == 0:
                                account = 'waiting'
                    # 加上下面这段程序就可以实现，平仓的时刻还可以开仓；不然要等下一个时刻才能触发开仓交易
                    if account == 0:
                        same_time = 0
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
                elif account == 'waiting':
                    if transactions.at[ticket, 'type'] == 'buy':
                        open_temp_min = min(currency_data[i - period_for_open: i]['open'])
                        close_temp_min = min(currency_data[i - period_for_open: i]['close'])
                        price_min = min(open_temp_min, close_temp_min)
                        if currency_data.at[i, 'close'] < price_min:
                            account = 0
                    elif transactions.at[ticket, 'type'] == 'sell':
                        open_temp_max = max(currency_data[i - period_for_open: i]['open'])
                        close_temp_max = max(currency_data[i - period_for_open: i]['close'])
                        price_max = max(open_temp_max, close_temp_max)
                        if currency_data.at[i, 'close'] > price_max:
                            account = 0
                    # 加上下面这段程序就可以实现，平仓的时刻还可以开仓；不然要等下一个时刻才能触发开仓交易
                    if account == 0:
                        same_time = 0
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


currency_data = read_data()
history_test(currency_data)
