"""
多单swap-12.09与空单swap6.527取自2019年2月某刻数据
"""
import sys
sys.path.append('E:/TheSecondElement/Program/TheSecondElement001/')
from Strategy import *
from Transactions import *
import pandas as pd

result = pd.DataFrame()
s = Strategy(pd.read_csv('E:/TheSecondElement/History/XAUUSD60.csv'), 30, 100, -12.09, 6.527, 300000)
s.setStrategyAugment(1.6, 12, 26, 24, 19, 0.1)
transactions = s.getTransactions()
t = Transactions(transactions)
t.caculateDetails()
t.caculateAboutDrawDown()
openTradesHistory = s.openTradesHistory
days = t.days
drawDown = t.drawDown
result.at[0, 'R'] = 1.6
result.at[0, 'lossLimit'] = 19
result.at[0, '年收益'] = t.netProfitPerYear
result.at[0, '最大衰落金额'] = drawDown.describe().loc['max']['drawDown']
result.at[0, 'MAR'] = result.at[0, '年收益'] / result.at[0, '最大衰落金额']
result.at[0, '期望'] = t.expectedPayOff
result.at[0, '最大衰落期'] = drawDown.describe().loc['max']['drawDownPeriod']
result.at[0, '胜率'] = t.profitTradesRate
result.at[0, '盈利月占比'] = len(t.profitPerMonth[t.profitPerMonth.profitPerMonth > 0]) / len(
    t.profitPerMonth)
result.at[0, '盈利单均盈利'] = t.profitTradesAverageProfit
result.at[0, '亏损单均亏损'] = t.lossTradesAverageLoss
result.at[0, '月均交易'] = t.tradesPerMonth
result.at[0, '多单数'] = t.longTrades
result.at[0, '多单胜率'] = t.longTradesWinRate
result.at[0, '空单数'] = t.shortTrades
result.at[0, '空单胜率'] = t.shortTradesWinRate
result.at[0, '获利因子'] = t.profitFactor

result.at[0, '平均同时开仓数'] = openTradesHistory.describe().loc['mean']['openTradesHistory']
result.at[0, '25%同时开仓数'] = openTradesHistory.describe().loc['25%']['openTradesHistory']
result.at[0, '50%同时开仓数'] = openTradesHistory.describe().loc['50%']['openTradesHistory']
result.at[0, '75%同时开仓数'] = openTradesHistory.describe().loc['75%']['openTradesHistory']
result.at[0, '最大同时开仓数'] = openTradesHistory.describe().loc['max']['openTradesHistory']

result.at[0, '平均持仓天数'] = days.describe().loc['mean']['days']
result.at[0, '25%持仓天数'] = days.describe().loc['25%']['days']
result.at[0, '50%持仓天数'] = days.describe().loc['50%']['days']
result.at[0, '75%持仓天数'] = days.describe().loc['75%']['days']
result.at[0, '最大持仓天数'] = days.describe().loc['max']['days']

result.at[0, '平均衰落金额'] = drawDown.describe().loc['mean']['drawDown']
result.at[0, '25%衰落金额'] = drawDown.describe().loc['25%']['drawDown']
result.at[0, '50%衰落金额'] = drawDown.describe().loc['50%']['drawDown']
result.at[0, '75%衰落金额'] = drawDown.describe().loc['75%']['drawDown']
result.at[0, '最大衰落金额(副本)'] = drawDown.describe().loc['max']['drawDown']

result.at[0, '平均衰落率'] = drawDown.describe().loc['mean']['drawDownRate']
result.at[0, '25%衰落率'] = drawDown.describe().loc['25%']['drawDownRate']
result.at[0, '50%衰落率'] = drawDown.describe().loc['50%']['drawDownRate']
result.at[0, '75%衰落率'] = drawDown.describe().loc['75%']['drawDownRate']
result.at[0, '最大衰落率'] = drawDown.describe().loc['max']['drawDownRate']

result.at[0, '平均衰落期'] = drawDown.describe().loc['mean']['drawDownPeriod']
result.at[0, '25%衰落期'] = drawDown.describe().loc['25%']['drawDownPeriod']
result.at[0, '50%衰落期'] = drawDown.describe().loc['50%']['drawDownPeriod']
result.at[0, '75%衰落期'] = drawDown.describe().loc['75%']['drawDownPeriod']
result.at[0, '最大衰落期(副本)'] = drawDown.describe().loc['max']['drawDownPeriod']

result.at[0, '平均每单获利'] = transactions.describe().loc['mean']['profit']
result.at[0, '25%每单获利'] = transactions.describe().loc['25%']['profit']
result.at[0, '50%每单获利'] = transactions.describe().loc['50%']['profit']
result.at[0, '75%每单获利'] = transactions.describe().loc['75%']['profit']
result.at[0, '最小每单获利'] = transactions.describe().loc['min']['profit']
result.at[0, '最大每单获利'] = transactions.describe().loc['max']['profit']

if os.path.exists('./result.csv'):
    os.remove('./result.csv')
result.to_csv('./result.csv')
