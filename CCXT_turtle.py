# -*- coding: utf-8 -*-
"""
Created on Sun Oct 07 20:48:07 2018

@author: jty9zer
"""

from ccxt_bitmex0926 import bitmex_ccxt
import time
import pandas as pd
import numpy as np
import schedule


class bitmex_strategy_turtle(bitmex_ccxt):
    def __init__(self,symbol):
        bitmex_ccxt.__init__(self)
        self.symbol = symbol
        self.position = None
        self.signal = None

        if self.fetch_balance()['used']['BTC'] == 0:
            self.position = False
        else:
            self.position = True


        print('当前运行时间', time.strftime("%Y-%m-%d %X", time.localtime()))
        print('初始化成功')

    def get_price_open(self):
        order_price_list = []
        for i in range(0, len(self.closed_order())):
            order_price_list.append(self.closed_order()[i]['price'])
        return np.mean(order_price_list)

    def get_order_counts(self):
        order_counts = []
        for i in range(0, len(self.closed_order())):
            order_counts.append(self.closed_order()[i]['amount'])
        return np.sum(order_counts)
            
    def turtleSignal(self, price, period=20):
        headTrack = max(self.kline(self.symbol, '1d')['high'][-period:])
        tailTrack = min(self.kline(self.symbol, '1d')['low'][-period:])
        if price > headTrack:
            return 1
        elif price < tailTrack:
            return -1
        else:
            return 0
        
    def get_ATR(self, period=20):
        data_kline = self.kline(self.symbol, '1d')
        TR_list = []
        for i in range(1,period):
            TR = max(data_kline['high'].iloc[-i]-data_kline['low'].iloc[-i], data_kline['high'].iloc[-i]-data_kline['close'].iloc[-(i+1)], data_kline['close'].iloc[-(i+1)]-data_kline['low'].iloc[-i])
            TR_list.append(TR)
        ATR = np.array(TR_list).mean()
        return ATR
        
    def getUnit(self, ATR):
        total_Value = self.fetch_balance()['free']['BTC'] * self.ticker(self.symbol)['last']
        return int(round((total_Value * 0.01)/ATR * self.ticker(self.symbol)['last'], 0))
            
    def Add_OR_Stop(self, price, last_price, ATR):
        if price>= last_price - 0.5*ATR:
            return 1
        elif price <= last_price - 2*ATR:
            return -1
        else:
            return 0
        
    def strategy(self):
        price = self.ticker(self.symbol)['last']
        print("当前价格:", price, " 时间:", time.strftime("%Y-%m-%d %X", time.localtime()))
        last_price = self.closed_order()[-1]['price']
        signal = self.turtleSignal(price)
        ATR = self.get_ATR()
        unit = self.getUnit(ATR)

        if self.position == False: #未入场
            if signal == 1:
                self.create_buy_market_order(self.symbol, unit)
                print("建仓, 数量:", unit, " 时间:", time.strftime("%Y-%m-%d %X", time.localtime()))
                self.position = True

        else: #已入场
            if signal == -1:
                self.create_sell_market_order(self.symbol, self.get_order_counts())
                print("全部卖出, 数量:", self.get_order_counts(), " 时间:", time.strftime("%Y-%m-%d %X", time.localtime()))
            if signal == 0:
                if self.Add_OR_Stop(price,last_price, ATR) == 1:
                    self.create_buy_market_order(self.symbol, unit)
                    print("加仓, 数量:", unit, " 时间:", time.strftime("%Y-%m-%d %X", time.localtime()))
                elif self.Add_OR_Stop(price,last_price, ATR) == -1:
                    self.create_sell_market_order(self.symbol, unit)
                    print("平仓, 数量:", " 时间:", time.strftime("%Y-%m-%d %X", time.localtime()))


if __name__ == '__main__':
    run = bitmex_strategy_turtle('BTC/USD')
    run.strategy()

    schedule.every(5).minutes.do(run.strategy)
    while True:
        schedule.run_pending()
        time.sleep(10)