"""
版本号：_turtle_2
集成函数：details
details函数功能：
计算
1.
    print('平均每月交易次数：      ', round(trades_per_month, 1))
    print('总单数：                ', total_trades)
    print('总多单数(获利比)：      ', long_position, '(', round(long_position_win*100, 1), '%', ')')
    print('总空单数(获利比)：      ', short_position, '(', round(short_position_win*100, 1), '%', ')')
    print('总获利单数（占比）：    ', profit_trades, '(', round(profit_trades_rate*100, 1), '%', ')')
    print('总亏损单数（占比）：    ', loss_trades, '(', round(loss_trades_rate*100, 1), '%', ')')
    print('平均每年收益：          ', round(profit_per_year, 1))
    print('盈利月占比：            ', round(win_month / months * 100, 1), '%')
    print('获利因子：              ', round(profit_factor, 2))
    print('每笔交易期望收益：      ', round(expected_payoff, 1))
    print('盈利单平均每单盈利：    ', round(average_profit_trade, 1))
    print('亏损单平均每单亏损：    ', round(average_loss_trade, 1))
    print('单笔最大盈利：          ', largest_profit_trade)
    print('单笔最大亏损：          ', largest_loss_trade)
    print('连续单亏损发生时均单数：', round(average_continue_loss_trades, 1))
    print('最大连续单亏损单数：    ', trades_continue_loss_max)
    print('最大衰落：              ', draw_down_rate_max, '%')
    print('最大衰落（金额数）：    ', draw_down_max)
    print('最长衰落期(交易日)：    ', draw_down_period_max)
    print('盈利单平均反向波动：    ', round((transactions_win.f_loss_max.sum()/len(transactions_win)), 1))
    print('盈利单最大反向波动：    ', round(max(transactions_win.f_loss_max), 1))
2.
    计算交易流水，输出到D:/graduate/history/currency_history/transactions.csv文件中
3.
   计算每年每月的月收益，输出到D:/graduate/history/currency_history/profit_table.csv文件中（注意：13行为每年收益总额，14行为每年月收益均值）
4.
    给出每笔盈利交易的最大反向波动，输出到D:/graduate/history/currency_history/transactions_win.csv文件中
5.
    为了计算最大衰落期的副产物，输出到D:/graduate/history/currency_history/transactions_new.csv文件中
6.
    绘制每月盈利直方图
7.
    绘制收益曲线
输入数据要求：
1.dataframe结构，包含每笔交易的具体信息：开仓日期，开仓时间，开仓方向，交易手数，开仓价格，平仓日期，平仓时间，平仓价格
2.最后一笔交易可以还未平仓（该笔未平仓交易不计入总计结果）
3.transactions的index要从0开始
品种适用性：
1.当使用不同的交易品种时，profit的方法不一定相同，要注意details()函数形参中的nums_per_size值是否正确：当计算GBPUSD与EURUSD时应为100000（十万），
    当计算XAUUSD时应为100（一百），或者说注意details()函数调用时是否正确传入了参数nums_per_size
周期适用性：
1.cal_transactions_new函数中最后draw_down_period_max的计算方式中除数24需要替换，不除时计算的是最长衰落期间的数据数，当为某交易产品的1h数据时，
除以24就会得到这些index间隔了多少的交易日；比如当数据为某交易产品的日线数据，那么计算最大衰落期（交易日）时，就除以1就好了（也就是不除任何数）
其他适用性：
1.注意details()函数调用时是否正确传入了参数fee,20180506目前eightcap交易商GBPUSD为*18(最大)，EURUSD为*12(最大)
"""


import pandas as pd
import matplotlib.pyplot as plt


# 将date与time两列化为一个具体时间‘Time’列，并将值类型从string转为Timestamp
def str2timestamp(transactions):
    # 下面这句话不加也不影响结果，但不加会出现一个警告，加了之后返回的transactions只剩下open_date,open_time,profit,Time列了
    transactions = transactions.loc[:, ['open_date', 'open_time', 'profit']]
    for i in range(len(transactions)):
        transactions_date_temp = transactions.at[i, 'open_date'][5:7] + '/' + transactions.at[i, 'open_date'][
                                                                                  8:10] + '/' + transactions.at[
                                                                                                    i, 'open_date'][
                                                                                                :4]
        if len(transactions.at[i, 'open_time']) == 4:
            transactions_date_temp = transactions_date_temp + '/' + transactions.at[i, 'open_time'][0]+':' + \
                                      transactions.at[i, 'open_time'][2:]
        elif len(transactions.at[i, 'open_time']) == 5:
            transactions_date_temp = transactions_date_temp + '/' + transactions.at[i, 'open_time'][:2] + ':' + \
                                      transactions.at[i, 'open_time'][3:]
        transactions.at[i, 'Time'] = pd.to_datetime(transactions_date_temp)
    # 返回的仍然是一个DataFrame数据类型
    return transactions


# 输入这个函数的transactions只是包含基本买卖时间，买卖手数，买卖价格的transactions而这个函数计算每笔收益，目前账户资金，每笔交易的回撤百分比
def cal_transactions(transactions, capital, fee, nums_per_size):
    for i in range(len(transactions.iloc[:, 0])-1):
        if i == 0:
            if transactions.at[i, 'type'] == 'buy':
                transactions.at[i, 'profit'] = (-(transactions.at[i, 'open_price']
                                                  - transactions.at[i, 'close_price'])) * nums_per_size * transactions.at[
                                                   i, 'size'] - fee * transactions.at[i, 'size']
                # GBPUSD,EURUSD等*100000（十万）；XAUUSD*100(一百)
                transactions.at[i, 'capital'] = (-(transactions.at[i, 'open_price']
                                                   - transactions.at[i, 'close_price'])) * nums_per_size* transactions.at[
                                                    i, 'size'] - fee * transactions.at[i, 'size'] + capital
                if transactions.at[i, 'capital'] <= 0:
                    print('爆仓！！！')
                    print('爆仓位置：', i)
                    exit()
                transactions.at[i, 'draw_down_rate'] = round((transactions.at[i, 'capital']-capital)/capital*100, 1)
                transactions.at[i, 'draw_down'] = (transactions.at[i, 'capital']-capital)
            elif transactions.at[i, 'type'] == 'sell':
                transactions.at[i, 'profit'] = (transactions.at[i, 'open_price']
                                                - transactions.at[i, 'close_price']) * nums_per_size * transactions.at[
                                                   i, 'size'] - fee * transactions.at[i, 'size']
                transactions.at[i, 'capital'] = (transactions.at[i, 'open_price']
                                                 - transactions.at[i, 'close_price']) * nums_per_size * transactions.at[
                                                    i, 'size'] - fee * transactions.at[i, 'size'] + capital
                if transactions.at[i, 'capital'] <= 0:
                    print('爆仓！！！')
                    print('爆仓位置：', i)
                    exit()
                transactions.at[i, 'draw_down_rate'] = round((transactions.at[i, 'capital'] - capital) / capital*100, 1)
                transactions.at[i, 'draw_down'] = (transactions.at[i, 'capital'] - capital)
        elif i != 0:
            if transactions.at[i, 'type'] == 'buy':
                transactions.at[i, 'profit'] = (-(transactions.at[i, 'open_price']
                                                  - transactions.at[i, 'close_price'])) * nums_per_size * transactions.at[
                                                   i, 'size'] - fee * transactions.at[i, 'size']
                # 用来储存不包括i的capital最大值
                capital_max = max(transactions.capital)
                # GBPUSD,EURUSD等*100000（十万）；XAUUSD*100(一百)
                transactions.at[i, 'capital'] = (-(transactions.at[i, 'open_price']
                                                   - transactions.at[i, 'close_price'])) * nums_per_size * transactions.at[
                                                    i, 'size'] - fee * transactions.at[i, 'size'] + transactions.at[
                                                    i - 1, 'capital']
                if transactions.at[i, 'capital'] <= 0:
                    print('爆仓！！！')
                    print('爆仓位置：', i)
                    exit()
                transactions.at[i, 'draw_down_rate'] = round(
                    (transactions.at[i, 'capital'] - capital_max) / capital_max * 100, 1)
                transactions.at[i, 'draw_down'] = transactions.at[i, 'capital'] - capital_max
            elif transactions.at[i, 'type'] == 'sell':
                transactions.at[i, 'profit'] = (transactions.at[i, 'open_price']
                                                - transactions.at[i, 'close_price']) * nums_per_size * transactions.at[
                                                   i, 'size'] - fee * transactions.at[i, 'size']
                capital_max = max(transactions.capital)
                # 用来储存不包括i的capital最大值
                transactions.at[i, 'capital'] = (transactions.at[i, 'open_price']
                                                 - transactions.at[i, 'close_price']) * nums_per_size * transactions.at[
                                                    i, 'size'] - fee * transactions.at[i, 'size'] + transactions.at[
                                                    i - 1, 'capital']
                if transactions.at[i, 'capital'] <= 0:
                    print('爆仓！！！')
                    print('爆仓位置：', i)
                    exit()
                transactions.at[i, 'draw_down_rate'] = round(
                    (transactions.at[i, 'capital'] - capital_max) / capital_max * 100, 1)
                transactions.at[i, 'draw_down'] = transactions.at[i, 'capital'] - capital_max
    # 通过该条语句将最后一笔未平仓交易删去
    transactions = transactions.dropna()
    # 将交易流水输出到.csv文件中
    transactions.to_csv('D:/graduate/history/currency_history/transactions.csv')
    return transactions


# 计算每年每月盈利统计表，写入.csv文件
def cal_profit_table(transactions):
    transactions = str2timestamp(transactions)
    start_date_str = transactions.at[0, 'open_date']
    end_date_str = transactions.at[len(transactions) - 1, 'open_date']
    transactions = transactions.set_index('Time')
    start_year = int(start_date_str[:4])
    end_year = int(end_date_str[:4])
    start_month = int(start_date_str[5:7])
    end_month = int(end_date_str[5:7])
    profit_table = pd.DataFrame(index=range(1, 13))
    total_month = 0
    win_month = 0
    for y in range(end_year - start_year + 1):
        y = y + start_year
        if y == start_year:
            m = start_month
            while m <= 12:
                total_month += 1
                profit_table.at[m, str(y)] = round(transactions[str(y) + '-' + str(m)]['profit'].sum(), 1)
                if profit_table.at[m, str(y)] > 0:
                    win_month += 1
                m = m + 1
            profit_table.at[13, str(y)] = round(profit_table.loc[:, str(y)].sum(), 1)
            profit_table.at[14, str(y)] = round(
                (profit_table.loc[:, str(y)].sum() - profit_table.at[13, str(y)]) / (13 - start_month), 1)
        elif y == end_year:
            m = 1
            while m <= end_month:
                total_month += 1
                profit_table.at[m, str(y)] = round(transactions[str(y) + '-' + str(m)]['profit'].sum(), 1)
                if profit_table.at[m, str(y)] > 0:
                    win_month += 1
                m = m + 1
            profit_table.at[13, str(y)] = round(profit_table.loc[:, str(y)].sum(), 1)
            profit_table.at[14, str(y)] = round(
                (profit_table.loc[:, str(y)].sum() - profit_table.at[13, str(y)]) / end_month, 1)
        else:
            m = 1
            while m <= 12:
                total_month += 1
                profit_table.at[m, str(y)] = round(transactions[str(y) + '-' + str(m)]['profit'].sum(), 1)
                if profit_table.at[m, str(y)] > 0:
                    win_month += 1
                m = m + 1
            profit_table.at[13, str(y)] = round(profit_table.loc[:, str(y)].sum(), 1)
            profit_table.at[14, str(y)] = round(((profit_table.loc[:, str(y)].sum()-profit_table.at[13, str(y)])/12), 1)
    profit_table.to_csv('D:/graduate/history/currency_history/profit_table.csv')
    return profit_table, win_month, total_month


# 本程序最为最要的一段，为graduate_turtle_3的止损优化提供依据, 计算盈利单的最大，平均反向波动
def cal_transactions_win(transactions, currency_data, nums_per_size):
    start_index = 0
    end_index = 0
    transactions_win = transactions[transactions.profit > 0]
    transactions_win.to_csv('D:/graduate/history/currency_history/transactions_win.csv')
    transactions_win = pd.read_csv('D:/graduate/history/currency_history/transactions_win.csv')
    for t in range(len(transactions_win)):
        for i in range(end_index, len(currency_data)):
            if currency_data.at[i, 'date'] == transactions_win.at[t, 'open_date'] and currency_data.at[i, 'time'] == \
                    transactions_win.at[t, 'open_time']:
                start_index = i
            if currency_data.at[i, 'date'] == transactions_win.at[t, 'close_date'] and currency_data.at[i, 'time'] == \
                    transactions_win.at[t, 'close_time']:
                end_index = i
                break
        if transactions_win.at[t, 'type'] == 'buy':
            open_price_min = min(currency_data[start_index:end_index + 1].open)
            high_price_min = min(currency_data[start_index:end_index + 1].high)
            low_price_min = min(currency_data[start_index:end_index + 1].low)
            close_price_min = min(currency_data[start_index:end_index + 1].close)
            price_min = min(open_price_min, high_price_min, low_price_min, close_price_min)
            transactions_win.at[t, 'f_loss_max'] = (transactions_win.at[t, 'open_price']
                                                    - price_min) * nums_per_size * transactions.at[t, 'size']
        elif transactions_win.at[t, 'type'] == 'sell':
            open_price_max = max(currency_data[start_index:end_index + 1].open)
            high_price_max = max(currency_data[start_index:end_index + 1].high)
            low_price_max = max(currency_data[start_index:end_index + 1].low)
            close_price_max = max(currency_data[start_index:end_index + 1].close)
            price_max = max(open_price_max, high_price_max, low_price_max, close_price_max)
            transactions_win.at[t, 'f_loss_max'] = (-(transactions_win.at[t, 'open_price']
                                                      - price_max)) * nums_per_size * transactions.at[t, 'size']
    transactions_win.to_csv('D:/graduate/history/currency_history/transactions_win.csv')
    return transactions_win


def cal_transactions_new(transactions, currency_data):
    start_index = 0
    end_index = 0
    transactions_new = transactions[transactions.draw_down_rate > 0]
    transactions_new.to_csv('D:/graduate/history/currency_history/transactions_new.csv')
    transactions_new = pd.read_csv('D:/graduate/history/currency_history/transactions_new.csv')
    draw_down_period_max = 0
    for t in range(len(transactions_new)-1):
        for i in range(end_index, len(currency_data)):
            if currency_data.at[i, 'date'] == transactions_new.at[t, 'close_date'] and currency_data.at[i, 'time'] == \
                    transactions_new.at[t, 'close_time']:
                start_index = i
            if currency_data.at[i, 'date'] == transactions_new.at[t+1, 'close_date'] and currency_data.at[i, 'time'] ==\
                    transactions_new.at[t+1, 'close_time']:
                end_index = i
                draw_down_period_max = max(draw_down_period_max, (end_index - start_index))
                break
    draw_down_period_max = round(draw_down_period_max/24, 1)
    return draw_down_period_max


def cal_about_trades(transactions):
    # 计算总单数，多单数（盈利占比），空单数（盈利占比），获利单数（占总单数比），亏损单数（占总单数比）
    total_trades = len(transactions)
    short_position = len(transactions[transactions['type'] == 'sell'])
    if short_position != 0:
        short_position_win = len(transactions[transactions['type'] == 'sell']
                                 [transactions[transactions['type'] == 'sell'].profit > 0])/short_position
    elif short_position == 0:
        short_position_win = 0
    long_position = len(transactions[transactions['type'] == 'buy'])
    if long_position != 0:
        long_position_win = len(transactions[transactions['type'] == 'buy']
                                [transactions[transactions['type'] == 'buy'].profit > 0]) / long_position
    elif long_position == 0:
        long_position_win = 0
    profit_trades = len(transactions[transactions['profit'] > 0])
    profit_trades_rate = profit_trades/total_trades
    loss_trades = len(transactions[transactions['profit'] < 0])
    loss_trades_rate = loss_trades/total_trades
    return total_trades, short_position, short_position_win, long_position, long_position_win, profit_trades, profit_trades_rate, loss_trades, loss_trades_rate


def cal_about_profit(transactions):
    # 计算单笔最大盈利，最大亏损
    largest_profit_trade = transactions['profit'].max()
    largest_loss_trade = transactions['profit'].min()

    # 计算总收益，总亏损，净收益，获利因子指标，期望收益（总盈利除以总下单数）
    gross_profit = transactions[transactions['profit'] > 0]['profit'].sum()
    gross_loss = transactions[transactions['profit'] < 0]['profit'].sum()
    total_net_profit = gross_profit + gross_loss
    profit_factor = abs(gross_profit / gross_loss)
    expected_payoff = total_net_profit / len(transactions)
    average_profit_trade = transactions[transactions.profit > 0].profit.mean()
    average_loss_trade = transactions[transactions.profit < 0].profit.mean()
    return total_net_profit, profit_factor, expected_payoff, average_profit_trade, average_loss_trade, largest_profit_trade, largest_loss_trade


def cal_about_loss(transactions):
    # 计算最大连续亏损次数，平均连续亏损次数
    # continue_loss_num记录一共发生了多少次连续亏损
    continue_loss_num = 0
    # trades_continue_loss记录了连续亏损发生时一共交易了多少单
    trades_continue_loss = 0
    trades_continue_loss_max = 0
    for i in range(len(transactions) - 3):
        if (transactions.at[i, 'profit'] > 0) and (transactions.at[i + 1, 'profit'] < 0) and (
                transactions.at[i + 2, 'profit'] < 0):
            continue_loss_num += 1
            trades_continue_loss_i = 1
            j = i + 1
            while transactions.at[j, 'profit'] < 0 and transactions.at[j + 1, 'profit'] < 0:
                trades_continue_loss_i += 1
                j += 1
                if j > (len(transactions) - 2):
                    break
            if trades_continue_loss_i > trades_continue_loss_max:
                trades_continue_loss_max = trades_continue_loss_i
            trades_continue_loss += trades_continue_loss_i
    average_continue_loss_trades = trades_continue_loss/continue_loss_num
    return average_continue_loss_trades, trades_continue_loss_max


def details(transactions, currency_data, capital, fee, nums_per_size):
    # 计算每笔获利等数据
    transactions = cal_transactions(transactions, capital, fee, nums_per_size)

    # 计算每年每月盈利数据
    win_month = cal_profit_table(transactions)[1]
    months = cal_profit_table(transactions)[2]

    # 计算交易单数相关
    about_trades = cal_about_trades(transactions)
    total_trades = about_trades[0]
    trades_per_month = total_trades/months
    short_position = about_trades[1]
    short_position_win = about_trades[2]
    long_position = about_trades[3]
    long_position_win = about_trades[4]
    profit_trades = about_trades[5]
    profit_trades_rate = about_trades[6]
    loss_trades = about_trades[7]
    loss_trades_rate = about_trades[8]

    # 计算盈利相关
    about_profit = cal_about_profit(transactions)
    total_net_profit = about_profit[0]
    profit_per_year = total_net_profit/months*12
    profit_factor = about_profit[1]
    expected_payoff = about_profit[2]
    average_profit_trade = about_profit[3]
    average_loss_trade = about_profit[4]
    largest_profit_trade = about_profit[5]
    largest_loss_trade = about_profit[6]

    # 计算亏损相关
    about_loss = cal_about_loss(transactions)
    average_continue_loss_trades = about_loss[0]
    trades_continue_loss_max = about_loss[1]
    # 计算最大衰落
    draw_down_rate_max = min(transactions.draw_down_rate)
    # 计算最大衰落（金额数）
    draw_down_max = min(transactions.draw_down)
    # 计算最长衰落期（交易日）
    draw_down_period_max = cal_transactions_new(transactions, currency_data)
    # 计算盈利单最大反向波动，平均反向波动
    transactions_win = cal_transactions_win(transactions, currency_data, nums_per_size)

    # 绘制月收益直方图
    # 计算每月总收益
    profit_per_temp = str2timestamp(transactions)
    profit_per_month_bar_temp = profit_per_temp.set_index('Time')['profit'].resample('m').sum()
    # 将timestamp格式转换为字符串格式，生成序列
    profit_per_month_bar_temp_index = [str(x.strftime('%Y-%m')) for x in profit_per_month_bar_temp.index]
    profit_per_month_bar = pd.Series(profit_per_month_bar_temp.values, index=profit_per_month_bar_temp_index)
    # 制图
    plt.figure(figsize=(15, 8))
    profit_per_month_bar.plot.bar()
    # 添加横轴；颜色为'k'；半透明；
    plt.axhline(0, color='k', alpha=0.5)
    plt.show()

    # 绘制收益曲线图
    transactions['profit'].cumsum().plot()
    plt.show()

    print('平均每月交易次数：      ', round(trades_per_month, 1))
    print('总单数：                ', total_trades)
    print('总多单数(获利比)：      ', long_position, '(', round(long_position_win*100, 1), '%', ')')
    print('总空单数(获利比)：      ', short_position, '(', round(short_position_win*100, 1), '%', ')')
    print('总获利单数（占比）：    ', profit_trades, '(', round(profit_trades_rate*100, 1), '%', ')')
    print('总亏损单数（占比）：    ', loss_trades, '(', round(loss_trades_rate*100, 1), '%', ')')
    print('平均每年收益：          ', round(profit_per_year, 1))
    print('盈利月占比：            ', round(win_month / months * 100, 1), '%')
    print('获利因子：              ', round(profit_factor, 2))
    print('每笔交易期望收益：      ', round(expected_payoff, 1))
    print('盈利单平均每单盈利：    ', round(average_profit_trade, 1))
    print('亏损单平均每单亏损：    ', round(average_loss_trade, 1))
    print('单笔最大盈利：          ', largest_profit_trade)
    print('单笔最大亏损：          ', largest_loss_trade)
    print('连续单亏损发生时均单数：', round(average_continue_loss_trades, 1))
    print('最大连续单亏损单数：    ', trades_continue_loss_max)
    print('最大衰落：              ', draw_down_rate_max, '%')
    print('最大衰落（金额数）：    ', draw_down_max)
    print('最长衰落期(交易日)：    ', draw_down_period_max)
    print('盈利单平均反向波动：    ', round((transactions_win.f_loss_max.sum()/len(transactions_win)), 1))
    print('盈利单最大反向波动：    ', round(max(transactions_win.f_loss_max), 1))



