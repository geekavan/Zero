"""
多单swap-12.09与空单swap6.527取自2019年2月某刻数据
"""
from Strategy import *
from Transactions import *
import pandas as pd

result = pd.DataFrame()
s = []
t = []
for i in range(0, 30):
    print(round((i + 1) * 0.1, 1))
    s.append(
        Strategy(pd.read_csv('D:/graduate/TheSecondElement/History/XAUUSD60.csv'), 30, 100, -12.09, 6.527,
                 300000))
    s[i].setStrategyAugment((i + 1) * 0.1, 12, 26, 24)
    transactions = s[i].getTransactions()
    t.append(Transactions(transactions))
    t[i].caculateDetails()
    t[i].caculateAboutDrawDown()
    openTradesHistory = s[i].openTradesHistory
    days = t[i].days
    drawDown = t[i].drawDown
    result.at[i, 'R'] = (i + 1) * 0.1
    result.at[i, '年收益'] = t[i].netProfitPerYear
    result.at[i, '最大衰落金额'] = drawDown.describe().loc['max']['drawDown']
    result.at[i, 'MAR'] = result.at[i, '年收益'] / result.at[i, '最大衰落金额']
    result.at[i, '期望'] = t[i].expectedPayOff
    result.at[i, '最大衰落期'] = drawDown.describe().loc['max']['drawDownPeriod']
    result.at[i, '胜率'] = t[i].profitTradesRate
    result.at[i, '盈利月占比'] = len(t[i].profitPerMonth[t[i].profitPerMonth.profitPerMonth > 0]) / len(t[i].profitPerMonth)
    result.at[i, '盈利单均盈利'] = t[i].profitTradesAverageProfit
    result.at[i, '亏损单均亏损'] = t[i].lossTradesAverageLoss
    result.at[i, '月均交易'] = t[i].tradesPerMonth
    result.at[i, '多单数'] = t[i].longTrades
    result.at[i, '多单胜率'] = t[i].longTradesWinRate
    result.at[i, '空单数'] = t[i].shortTrades
    result.at[i, '空单胜率'] = t[i].shortTradesWinRate
    result.at[i, '获利因子'] = t[i].profitFactor

    result.at[i, '平均同时开仓数'] = openTradesHistory.describe().loc['mean']['openTradesHistory']
    result.at[i, '25%同时开仓数'] = openTradesHistory.describe().loc['25%']['openTradesHistory']
    result.at[i, '50%同时开仓数'] = openTradesHistory.describe().loc['50%']['openTradesHistory']
    result.at[i, '75%同时开仓数'] = openTradesHistory.describe().loc['75%']['openTradesHistory']
    result.at[i, '最大同时开仓数'] = openTradesHistory.describe().loc['max']['openTradesHistory']

    result.at[i, '平均持仓天数'] = days.describe().loc['mean']['days']
    result.at[i, '25%持仓天数'] = days.describe().loc['25%']['days']
    result.at[i, '50%持仓天数'] = days.describe().loc['50%']['days']
    result.at[i, '75%持仓天数'] = days.describe().loc['75%']['days']
    result.at[i, '最大持仓天数'] = days.describe().loc['max']['days']

    result.at[i, '平均衰落金额'] = drawDown.describe().loc['mean']['drawDown']
    result.at[i, '25%衰落金额'] = drawDown.describe().loc['25%']['drawDown']
    result.at[i, '50%衰落金额'] = drawDown.describe().loc['50%']['drawDown']
    result.at[i, '75%衰落金额'] = drawDown.describe().loc['75%']['drawDown']
    result.at[i, '最大衰落金额(副本)'] = drawDown.describe().loc['max']['drawDown']

    result.at[i, '平均衰落率'] = drawDown.describe().loc['mean']['drawDownRate']
    result.at[i, '25%衰落率'] = drawDown.describe().loc['25%']['drawDownRate']
    result.at[i, '50%衰落率'] = drawDown.describe().loc['50%']['drawDownRate']
    result.at[i, '75%衰落率'] = drawDown.describe().loc['75%']['drawDownRate']
    result.at[i, '最大衰落率'] = drawDown.describe().loc['max']['drawDownRate']

    result.at[i, '平均衰落期'] = drawDown.describe().loc['mean']['drawDownPeriod']
    result.at[i, '25%衰落期'] = drawDown.describe().loc['25%']['drawDownPeriod']
    result.at[i, '50%衰落期'] = drawDown.describe().loc['50%']['drawDownPeriod']
    result.at[i, '75%衰落期'] = drawDown.describe().loc['75%']['drawDownPeriod']
    result.at[i, '最大衰落期(副本)'] = drawDown.describe().loc['max']['drawDownPeriod']

    result.at[i, '平均每单获利'] = transactions.describe().loc['mean']['profit']
    result.at[i, '25%每单获利'] = transactions.describe().loc['25%']['profit']
    result.at[i, '50%每单获利'] = transactions.describe().loc['50%']['profit']
    result.at[i, '75%每单获利'] = transactions.describe().loc['75%']['profit']
    result.at[i, '最小每单获利'] = transactions.describe().loc['min']['profit']
    result.at[i, '最大每单获利'] = transactions.describe().loc['max']['profit']

    t[i].printTransactions(round((i + 1) * 0.1, 1))
if os.path.exists('./result.csv'):
    os.remove('./result.csv')
result.to_csv('./result.csv')
