"""
注意：
0.本程序的self.days为pd.DataFrame数据结构，记录的是所有交易单的持仓时间，建议用.describe()方法提取参数
1.本程序的self.drawDown为pd.DataFrame数据结构，共分为三列，为'drawDown','drawDownRate','drawDownPeriod',分别记录着
    '回撤(衰落)金额'，'回撤(衰落)率'，'回撤(衰落)期'建议用.describe()方法提取参数
2.本程序的self.profitPerMonth为pd.DataFrame数据结构，记录着每月的盈利金额，可用于计算月胜率，季度胜率，年胜率等
3.上述三个参数在执行self.caculateAboutDrawDown后存在结果
4.其他成员变量在执行self.caculateDatails后存在结果
"""
import os
import pandas as pd


class Transactions(object):
    def __init__(self, transactions):
        self.__transactions = transactions
        self.__month = 30
        self.totalTrades = 0
        self.longTrades = 0
        self.longTradesWinRate = 0
        self.shortTrades = 0
        self.shortTradesWinRate = 0
        self.profitTrades = 0
        self.profitTradesRate = 0
        self.lossTrades = 0
        self.lossTradesRate = 0
        self.grossProfit = 0
        self.grossLoss = 0
        self.profitTradesAverageProfit = 0
        self.lossTradesAverageLoss = 0
        self.profitFactor = 0
        self.totalNetProfit = 0
        self.expectedPayOff = 0
        self.totalDays = 0
        self.tradesPerMonth = 0
        self.netProfitPerYear = 0
        self.days = pd.DataFrame()
        self.drawDown = pd.DataFrame()
        self.profitPerMonth = pd.DataFrame()

    def getTotalTrades(self):
        return len(self.__transactions) - 1

    def getLongTrades(self):
        return len(self.__transactions[self.__transactions['type'] == 'buy'])

    def getLongTradesWin(self):
        return len(self.__transactions[self.__transactions['type'] == 'buy'][
                       self.__transactions[self.__transactions['type'] == 'buy'].profit > 0])

    def getShortTrades(self):
        return len(self.__transactions[self.__transactions['type'] == 'sell'])

    def getShortTradesWin(self):
        return len(self.__transactions[self.__transactions['type'] == 'sell'][
                       self.__transactions[self.__transactions['type'] == 'sell'].profit > 0])

    def getProfitTrades(self):
        return len(self.__transactions[self.__transactions['profit'] > 0])

    def getLossTrades(self):
        return len(self.__transactions[self.__transactions['profit'] < 0])

    def getGrossProfit(self):
        return self.__transactions[self.__transactions['profit'] > 0]['profit'].sum()

    def getGrossLoss(self):
        return self.__transactions[self.__transactions['profit'] < 0]['profit'].sum()

    def getProfitTradesAverageProfit(self):
        return self.__transactions[self.__transactions.profit > 0].profit.mean()

    def getLossTradesAverageLoss(self):
        return self.__transactions[self.__transactions.profit < 0].profit.mean()

    def getTotalDays(self):
        totalDayString = str(
            self.__transactions.at[len(self.__transactions) - 1, 'closeTime'] - self.__transactions.at[1, 'openTime'])
        return int(totalDayString[:totalDayString.find(' ')])

    def caculateDaysBetweenTwoTimestamp(self, startTime, endTime):
        temp = str(endTime - startTime)
        return int(temp[:temp.find(' ')])

    def printTransactions(self, fileName):
        if os.path.exists('./Transactions%s.csv' % fileName):
            os.remove('./Transactions%s.csv' % fileName)
        self.__transactions.to_csv('./Transactions%s.csv' % fileName)

    def caculateDetails(self):
        self.totalTrades = self.getTotalTrades()
        self.longTrades = self.getLongTrades()
        self.longTradesWinRate = self.getLongTradesWin() / self.getLongTrades()
        self.shortTrades = self.getShortTrades()
        self.shortTradesWinRate = self.getShortTradesWin() / self.getShortTrades()
        self.profitTrades = self.getProfitTrades()
        self.profitTradesRate = self.getProfitTrades() / self.getTotalTrades()
        self.lossTrades = self.getLossTrades()
        self.lossTradesRate = self.getLossTrades() / self.getTotalTrades()
        self.grossProfit = self.getGrossProfit()
        self.grossLoss = self.getGrossLoss()
        self.profitTradesAverageProfit = self.getProfitTradesAverageProfit()
        self.lossTradesAverageLoss = self.getLossTradesAverageLoss()
        self.profitFactor = self.getGrossProfit() / self.getGrossLoss()
        self.totalNetProfit = self.getGrossProfit() + self.getGrossLoss()
        self.expectedPayOff = (self.getGrossProfit() + self.getGrossLoss()) / self.getTotalTrades()
        self.totalDays = self.getTotalDays()
        self.tradesPerMonth = self.getTotalTrades() / self.getTotalDays() * 30
        self.netProfitPerYear = (self.getGrossProfit() + self.getGrossLoss()) / self.getTotalDays() * 365

    def caculateAboutDrawDown(self):
        self.__transactions.at[1, 'days'] = self.caculateDaysBetweenTwoTimestamp(self.__transactions.at[1, 'openTime'],
                                                                                 self.__transactions.at[1, 'closeTime'])
        self.__transactions.at[1, 'drawDown'] = self.__transactions.at[0, 'balance'] - self.__transactions.at[
            1, 'balance']
        self.__transactions.at[1, 'drawDownRate'] = (self.__transactions.at[0, 'balance'] - self.__transactions.at[
            1, 'balance']) / self.__transactions.at[0, 'balance']
        self.__transactions.at[1, 'drawDownPeriod'] = 0
        self.days.at[0, 'days'] = self.__transactions.at[1, 'days']
        self.drawDown.at[0, 'drawDown'] = self.__transactions.at[1, 'drawDown']
        self.drawDown.at[0, 'drawDownRate'] = self.__transactions.at[1, 'drawDownRate']
        self.drawDown.at[0, 'drawDownPeriod'] = self.__transactions.at[1, 'drawDownPeriod']
        startTicketForProfitPerMonth = 1
        for i in range(2, len(self.__transactions)):
            self.__transactions.at[i, 'days'] = self.caculateDaysBetweenTwoTimestamp(
                self.__transactions.at[i, 'openTime'], self.__transactions.at[i, 'closeTime'])
            self.__transactions.at[i, 'drawDown'] = max(self.__transactions[0:i].balance) - self.__transactions.at[
                i, 'balance']
            self.__transactions.at[i, 'drawDownRate'] = (max(self.__transactions[0:i].balance) - self.__transactions.at[
                i, 'balance']) / max(self.__transactions[0:i].balance)
            if self.__transactions.at[i, 'balance'] <= max(self.__transactions[0:i].balance):
                drawDownPeriodIncreaseTemp = str(
                    self.__transactions.at[i, 'closeTime'] - self.__transactions.at[i - 1, 'closeTime'])
                self.__transactions.at[i, 'drawDownPeriod'] = self.__transactions.at[i - 1, 'drawDownPeriod'] + int(
                    drawDownPeriodIncreaseTemp[:drawDownPeriodIncreaseTemp.find(' ')])
            elif self.__transactions.at[i, 'balance'] > max(self.__transactions[0:i].balance):
                self.__transactions.at[i, 'drawDownPeriod'] = 0
            self.days.at[i - 1, 'days'] = self.__transactions.at[i, 'days']
            self.drawDown.at[i - 1, 'drawDown'] = self.__transactions.at[i, 'drawDown']
            self.drawDown.at[i - 1, 'drawDownRate'] = self.__transactions.at[i, 'drawDownRate']
            self.drawDown.at[i - 1, 'drawDownPeriod'] = self.__transactions.at[i, 'drawDownPeriod']
            daysForProfitPerMonth = self.caculateDaysBetweenTwoTimestamp(
                self.__transactions.at[startTicketForProfitPerMonth, 'closeTime'],
                self.__transactions.at[i, 'closeTime'])
            if daysForProfitPerMonth > self.__month:
                positionForProfitPerMonth = len(self.profitPerMonth)
                endTicketForProfitPerMonth = i
                self.profitPerMonth.at[positionForProfitPerMonth, 'profitPerMonth'] = self.__transactions[
                                                                                      startTicketForProfitPerMonth:endTicketForProfitPerMonth].profit.sum()
                startTicketForProfitPerMonth = endTicketForProfitPerMonth
