"""
需求：
1.给定一个外汇走势的历史数据表与一个策略，求根据这个策略得出的交易表
程序必须考虑的兼容性：
1.能够调节损盈比
2.必须兼容所有的外汇币种
3.达到一定盈利目标能够设置保护止损
4.可以根据目前剩余资金量设置交易手数
注意：
0.本程序的成员变量self.openTradesHistory为pd.DataFrames数据结构，记录的是所有的持仓单数的变动，建议用.describe()方法提取均数，最大值等参数
1.本程序对于价差的处理方式为：每笔交易最后的获利'profit'减去买卖价差spread * size(其中spread的单位为：美金/每手)
2.本程序在最后会将没有结仓的单子以最后的收盘价平仓，并记录在self.__transactions中
3.生成的transactions第0行只有balance数值，交易从第1行开始！
4.contractSize为每手合约数量
5.swapLong为多单隔夜利率，单位为：美金/天/每手
6.swapShort为空单隔夜利率，单位为：美金/天/每手
7.balance为初始资金量
"""
import pandas as pd
import numpy as np
from pandas.tseries.offsets import *


class Strategy:
    def __init__(self, currencyData, spread, contractSize, swapLong, swapShort, balance):
        self.__currencyData = currencyData
        self.__spread = spread
        self.__contractSize = contractSize
        self.__swapLong = swapLong
        self.__swapShort = swapShort
        self.__balance = balance
        self.__transactions = pd.DataFrame()
        self.__transactionsInit()
        self.__openTrades = pd.DataFrame()
        self.openTradesHistory = pd.DataFrame()
        self.__R = 1.6
        self.__fastEMA = 12
        self.__slowEMA = 26
        self.__periodOfLossLimit = 24
        self.__percentForWOptimize = 0.5

    def setStrategyAugment(self, R, fastEMA, slowEMA, periodOfLossLimit, percentForWOptimize):
        self.__R = R
        self.__fastEMA = fastEMA
        self.__slowEMA = slowEMA
        self.__periodOfLossLimit = periodOfLossLimit
        self.__percentForWOptimize = percentForWOptimize

    def caculateSwap(self, startTime, endTime):
        swapDays = 0
        startDate = pd.to_datetime(startTime.date())
        endDate = pd.to_datetime(endTime.date())
        while startDate != endDate:
            if startDate.weekday() + 1 == 3:
                swapDays += 3
            elif startDate.weekday() + 1 == 6 or startDate.weekday() + 1 == 7:
                swapDays += 0
            else:
                swapDays += 1
            startDate += Day()
        return swapDays

    def getTransactions(self):
        self.__generateTransactions()
        return self.__transactions

    def __transactionsInit(self):
        self.__transactions.at[0, 'openTime'] = np.nan
        self.__transactions.at[0, 'type'] = ''
        self.__transactions.at[0, 'size'] = np.nan
        self.__transactions.at[0, 'openPrice'] = np.nan
        self.__transactions.at[0, 'S/L'] = np.nan
        self.__transactions.at[0, 'T/P'] = np.nan
        self.__transactions.at[0, 'closeTime'] = np.nan
        self.__transactions.at[0, 'closePrice'] = np.nan
        self.__transactions.at[0, 'swap'] = np.nan
        self.__transactions.at[0, 'profit'] = np.nan
        self.__transactions.at[0, 'balance'] = self.__balance

    def __caculateIndex(self):
        self.__currencyData.at[0, 'fastEMA'] = self.__currencyData.at[0, 'close']
        self.__currencyData.at[0, 'slowEMA'] = self.__currencyData.at[0, 'close']
        self.__currencyData.at[0, 'macd'] = self.__currencyData.at[0, 'fastEMA'] - self.__currencyData.at[0, 'slowEMA']
        for i in range(1, len(self.__currencyData)):
            self.__currencyData.at[i, 'fastEMA'] = self.__currencyData.at[i - 1, 'fastEMA'] * (
                    self.__fastEMA - 1) / (self.__fastEMA + 1) + self.__currencyData.at[i, 'close'] * 2 / (
                                                           self.__fastEMA + 1)
            self.__currencyData.at[i, 'slowEMA'] = self.__currencyData.at[i - 1, 'slowEMA'] * (
                    self.__slowEMA - 1) / (self.__slowEMA + 1) + self.__currencyData.at[i, 'close'] * 2 / (
                                                           self.__slowEMA + 1)
            self.__currencyData.at[i, 'macd'] = self.__currencyData.at[i, 'fastEMA'] - self.__currencyData.at[
                i, 'slowEMA']
            if (self.__currencyData.at[i - 1, 'macd'] > 0) and (self.__currencyData.at[i, 'macd'] < 0):
                self.__currencyData.at[i, 'index'] = -1
            elif (self.__currencyData.at[i - 1, 'macd'] < 0) and (self.__currencyData.at[i, 'macd'] > 0):
                self.__currencyData.at[i, 'index'] = 1
            else:
                self.__currencyData.at[i, 'index'] = 0

    def __openOrder(self, openDate, openTime, type, size, openPrice, stopLoss, takeProfit):
        position = len(self.__openTrades)
        openTradesHistoryPosition = len(self.openTradesHistory)
        self.openTradesHistory.at[openTradesHistoryPosition, 'openTradesHistory'] = len(self.__openTrades)
        self.__openTrades.at[position, 'openTime'] = pd.to_datetime(openDate.replace(":", "/") + "/" + openTime)
        self.__openTrades.at[position, 'type'] = type
        self.__openTrades.at[position, 'size'] = size
        self.__openTrades.at[position, 'openPrice'] = openPrice
        self.__openTrades.at[position, 'S/L'] = stopLoss
        self.__openTrades.at[position, 'T/P'] = takeProfit
        self.__openTrades.at[position, 'finish'] = np.nan
        self.__openTrades.at[position, 'finishForWOptimize'] = 0

    def __closeOrder(self, ot, closeDate, closeTime, closePrice):
        position = len(self.__transactions)
        self.__transactions.at[position, 'openTime'] = self.__openTrades.at[ot, 'openTime']
        self.__transactions.at[position, 'type'] = self.__openTrades.at[ot, 'type']
        self.__transactions.at[position, 'size'] = self.__openTrades.at[ot, 'size']
        self.__transactions.at[position, 'openPrice'] = self.__openTrades.at[ot, 'openPrice']
        self.__transactions.at[position, 'S/L'] = self.__openTrades.at[ot, 'S/L']
        self.__transactions.at[position, 'T/P'] = self.__openTrades.at[ot, 'T/P']
        self.__transactions.at[position, 'closeTime'] = pd.to_datetime(closeDate.replace(":", "/") + "/" + closeTime)
        self.__transactions.at[position, 'closePrice'] = closePrice
        swapDays = self.caculateSwap(self.__transactions.at[position, 'openTime'],
                                     self.__transactions.at[position, 'closeTime'])
        self.__transactions.at[position, 'swap'] = (self.__swapLong if self.__transactions.at[
                                                                           position, 'type'] == 'buy' else self.__swapShort) * swapDays * \
                                                   self.__transactions.at[position, 'size']
        self.__transactions.at[position, 'profit'] = (self.__transactions.at[position, 'closePrice'] -
                                                      self.__transactions.at[position, 'openPrice']) * (
                                                         1 if self.__transactions.at[
                                                                  position, 'type'] == 'buy' else -1) * \
                                                     self.__transactions.at[
                                                         position, 'size'] * self.__contractSize - self.__spread * \
                                                     self.__transactions.at[position, 'size'] - self.__transactions.at[
                                                         position, 'swap']
        self.__transactions.at[position, 'balance'] = self.__transactions.at[position - 1, 'balance'] + \
                                                      self.__transactions.at[position, 'profit']
        self.__openTrades.at[ot, 'finish'] = 1
        self.__balance = self.__balance + self.__transactions.at[position, 'profit']
        assert self.__balance > 0, '爆仓！请设置更多的资金(balance)重新测试！'

    def __getSize(self):
        return 1

    def __generateTransactions(self):
        self.__caculateIndex()
        for i in range(self.__periodOfLossLimit - 1, len(self.__currencyData)):
            closeDate = self.__currencyData.at[i, 'date']
            closeTime = self.__currencyData.at[i, 'time']
            for ot in range(len(self.__openTrades)):
                if (self.__openTrades.at[ot, 'finishForWOptimize'] == 0) and (
                        self.__openTrades.at[ot, 'type'] == 'buy') and (self.__currencyData.at[i, 'open'] > (
                        self.__openTrades.at[ot, 'openPrice'] + self.__percentForWOptimize * (
                        self.__openTrades.at[ot, 'openPrice'] - self.__openTrades.at[ot, 'S/L']))):
                    self.__openTrades.at[ot, 'S/L'] = (
                            self.__openTrades.at[ot, 'openPrice'] + self.__percentForWOptimize * (
                            self.__openTrades.at[ot, 'openPrice'] - self.__openTrades.at[ot, 'S/L']))
                    self.__openTrades.at[ot, 'finishForWOptimize'] = 1
                elif (self.__openTrades.at[ot, 'finishForWOptimize'] == 0) and (
                        self.__openTrades.at[ot, 'type'] == 'sell') and (self.__currencyData.at[i, 'open'] < (
                        self.__openTrades.at[ot, 'openPrice'] - self.__percentForWOptimize * (
                        self.__openTrades.at[ot, 'S/L'] - self.__openTrades.at[ot, 'openPrice']))):
                    self.__openTrades.at[ot, 'S/L'] = (
                            self.__openTrades.at[ot, 'openPrice'] - self.__percentForWOptimize * (
                            self.__openTrades.at[ot, 'S/L'] - self.__openTrades.at[ot, 'openPrice']))
                    self.__openTrades.at[ot, 'finishForWOptimize'] = 1
                stoploss = self.__openTrades.at[ot, 'S/L']
                takeProfit = self.__openTrades.at[ot, 'T/P']
                if (self.__openTrades.at[ot, 'type'] == 'buy') and (self.__currencyData.at[i, 'low'] < stoploss):
                    self.__closeOrder(ot, closeDate, closeTime, stoploss)
                elif (self.__openTrades.at[ot, 'type'] == 'buy') and (self.__currencyData.at[i, 'high'] > takeProfit):
                    self.__closeOrder(ot, closeDate, closeTime, takeProfit)
                elif (self.__openTrades.at[ot, 'type'] == 'sell') and (self.__currencyData.at[i, 'high']) > stoploss:
                    self.__closeOrder(ot, closeDate, closeTime, stoploss)
                elif (self.__openTrades.at[ot, 'type'] == 'sell') and (self.__currencyData.at[i, 'low'] < takeProfit):
                    self.__closeOrder(ot, closeDate, closeTime, takeProfit)
                if ot == len(self.__openTrades) - 1:
                    self.__openTrades = self.__openTrades[pd.isnull(self.__openTrades.finish)]
                    self.__openTrades.reset_index(drop=True, inplace=True)
            if (self.__currencyData.at[i, 'index'] == 1) and (i < (len(self.__currencyData) - 1)):
                openDate = self.__currencyData.at[i + 1, 'date']
                openTime = self.__currencyData.at[i + 1, 'time']
                openPrice = self.__currencyData.at[i + 1, 'open']
                openTempMin = min(self.__currencyData[i - self.__periodOfLossLimit + 1: i + 1]['open'])
                closeTempMin = min(self.__currencyData[i - self.__periodOfLossLimit + 1: i + 1]['close'])
                priceMin = min(openTempMin, closeTempMin)
                takeProfit = self.__currencyData.at[i + 1, 'open'] + self.__R * (
                        self.__currencyData.at[i + 1, 'open'] - priceMin)
                self.__openOrder(openDate, openTime, 'buy', self.__getSize(), openPrice, priceMin, takeProfit)
            elif (self.__currencyData.at[i, 'index'] == -1) and (i < (len(self.__currencyData) - 1)):
                openDate = self.__currencyData.at[i + 1, 'date']
                openTime = self.__currencyData.at[i + 1, 'time']
                openPrice = self.__currencyData.at[i + 1, 'open']
                openTempMax = max(self.__currencyData[i - self.__periodOfLossLimit + 1: i + 1]['open'])
                closeTempMax = max(self.__currencyData[i - self.__periodOfLossLimit + 1: i + 1]['close'])
                priceMax = max(openTempMax, closeTempMax)
                takeProfit = self.__currencyData.at[i + 1, 'open'] + self.__R * (
                        self.__currencyData.at[i + 1, 'open'] - priceMax)
                self.__openOrder(openDate, openTime, 'sell', self.__getSize(), openPrice, priceMax, takeProfit)
            if i == len(self.__currencyData) - 1:
                for ot in range(len(self.__openTrades)):
                    self.__closeOrder(ot, closeDate, closeTime,
                                      self.__currencyData.at[len(self.__currencyData) - 1, 'close'])
