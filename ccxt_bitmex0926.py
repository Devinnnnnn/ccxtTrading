# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 10:25:11 2018


"""

import pandas as pd
import json
import ccxt
from setting import *

testnet = 'https://testnet.bitmex.com'
bitmex_shipan  = 'https://www.bitmex.com'

if test_trading:
    BITMEX_PARAMS={
        'api_key':api_key, #这里改BITMEX的API名称
        'SECRET_KEY':SECRET_KEY,#这里改BITMEX的API密钥
        'URL':testnet, #这里储存的是bitmex的实盘URL
        'BTC_ADDRESS':''
    }
else:
    BITMEX_PARAMS={
        'api_key':api_key, #这里改BITMEX的API名称
        'SECRET_KEY':SECRET_KEY,#这里改BITMEX的API密钥
        'URL':bitmex_shipan, #这里储存的是bitmex的实盘URL
        'BTC_ADDRESS':''
    }
    

def connection():  #返会一个CCXT.bitmex类的对象 所有CCXT中关于BITMEX的方法都存在这里面
    bitmex = ccxt.bitmex()
    bitmex.apiKey = BITMEX_PARAMS['api_key']
    bitmex.secret = BITMEX_PARAMS['SECRET_KEY']
    #区分是否使用了测试连接
    if BITMEX_PARAMS['URL'] == 'https://testnet.bitmex.com':
        bitmex.urls["api"] = bitmex.urls["test"]    
        print('模拟盘交易')
    else:
        print ('实盘交易')
    return bitmex


class bitmex_ccxt:
    
    def __init__(self,*args,**kwargs):
        self._BitmexConnect = connection()
        
    def get_all_symbol(self):  #返回一个储存所有在BITMEX中交易的合约的编号的list
        symbolList = []
        bitmex_symbol = []
        contracts = self._BitmexConnect.fetchMarkets ()
#        contracts = bitmex.fetchMarkets ()
        
        tickSize = []
        for contract in contracts:
            if not contract['symbol'].startswith('.'):
                symbolList.append(contract['symbol'])
                bitmex_symbol.append(contract['info']['symbol'])
                tickSize.append(contract['info']['tickSize'])
        
        print ('bitmex_symbol:',bitmex_symbol )
        print ('ccxt_symbol:', symbolList )
        
        return bitmex_symbol, symbolList, tickSize
            
    def get_all_id(self): #返回一个储存所有在BITMEX中交易的合约id的list
        idList = []
        contracts = self._BitmexConnect.fetchMarkets ()
        for contract in contracts:
            if not contract['id'].startswith('.'):
                idList.append(contract['id'])
        return idList
    
    
    def describe(self,*args,**kwargs):  #对ccxt.bitmex类中所有信息的总览(字典形式)
        result = self._BitmexConnect.describe(*args,**kwargs)
        return result
    
    
    def fetch_balance(self,*args, **kwargs):  #返回一个包含当前账户信息的字典形式变量
        balannce = self._BitmexConnect.fetch_balance()
        return balannce
    
    
    def fetch_order_book(self, symbol,*args,**kargs):  #返回前25档买卖订单的字典 字典中元素的格式为[price,volume]
        orderList = self._BitmexConnect.fetch_order_book(symbol,*args,**kargs)
        return orderList
    
    def ticker(self, symbol, *args,**kargs): #返回一个symbol的ticker字典变量
        ticker = self._BitmexConnect.fetch_ticker(symbol,*args,**kargs)
        return ticker
    
    def kline(self,symbol,timeframe,limit,*arg,**args): #获取参数指定的k线信息        
        
        if limit == None:
            limit = 750
        
        bitmex = self._BitmexConnect
        now = bitmex.milliseconds()
       
        if timeframe == '1m':
            since = now - (limit) * 60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='1m', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.index = pd.to_datetime(df['time'], unit='ms')
            del df['time']
        
        elif timeframe == '5m':
            since = now - limit *  60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='5m', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.index = pd.to_datetime(df['time'], unit='ms')
            del df['time']
        
        elif timeframe == '10m':
            since = now - limit *  60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='5m', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.index = pd.to_datetime(df['time'], unit='ms')
            df = df.resample('10min', closed=None, label='left').mean()
            del df['time']
        
        elif timeframe == '30m':
            since = now - limit * 60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='5m', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
           # df.drop([len(df)-1,len(df)-1])
            df.index = pd.to_datetime(df['time'], unit='ms')
            df = df.resample('30min',closed=None, label='left').mean()
            del df['time']
        
        elif timeframe == '1h':
            #最大limit 只能获取13小时的数据
            since = now - limit * 60 *60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='1h', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.index = pd.to_datetime(df['time'], unit='ms')
            del df['time']
        
        elif timeframe == '4h':
            since = now - limit  * 60 * 60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='1h', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.index = pd.to_datetime(df['time'], unit='ms')
            df = df.resample('4h',closed=None, label='left').mean()
            del df['time']
        
        elif timeframe == '12h':
            since = now - limit * 60 * 60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='1h', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.drop([len(df)-1])
            df.index = pd.to_datetime(df['time'], unit='ms')
            df = df.resample('12h',closed=None, label='left').mean()
            del df['time']
        
        elif timeframe == '1d':
            #最多只能返回一天的
            since = now - limit * 1440 *60 * 1000  # 当前时间之前多少毫秒数的K线,时间为UTC时间,与中国时间差8h
            df = pd.DataFrame(bitmex.fetch_ohlcv(symbol, timeframe='1d', limit=limit, since=since),
                              columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df.drop([len(df)-1])
            df.index = pd.to_datetime(df['time'], unit='ms')
            del df['time']
     
        return df
    
    
    def get_uesr_market_position(self,ID,*args,**kwargs): #获取参数ID合约的市价仓位信息
         user_pos = self._BitmexConnect.private_get_position(({'filter': json.dumps({"symbol": ID})}))
         return user_pos
     
    
    def get_user_active_position(self,ID,*args,**kwargs): #获取当前用户活动仓位信息(limit,stopLimit and etc)
         if ID is not None:
             act_orders = self._BitmexConnect.private_get_order(({'filter': json.dumps({"open": True,"symbol": ID})}))
         else:
              act_orders = self._BitmexConnect.private_get_order()
         return act_orders
     
    def create_buy_market_order(self,symbol,amount,*args,**kwargs): #创建市价买单 输入symbol 和 amount 即可
        
        order = self._BitmexConnect.create_order(symbol = symbol, type='market', side = 'buy', amount = amount,*args,**kwargs)
        print('order is successfully created')
        print('********************************************************************************')
        print(order)    
        return order

    def create_sell_market_order(self,symbol,amount,*args,**kwargs):#创建市价卖单 输入symbol 和 amount 即可
        order = self._BitmexConnect.create_order(symbol = symbol, type='market', side = 'sell', amount = amount,*args,**kwargs)
        print('order is successfully created')
        print('********************************************************************************')
        print(order)
    
    
    def limit_order(self,symbol,amount,price,direction,*args,**kwargs):#创建市价卖单 输入symbol, amount 以及 limitprice 即可
        order = self._BitmexConnect.create_order(symbol = symbol, type='limit', side = direction, amount = amount, price = price,*args,**kwargs)
#        print('order successful')
        print('********************************************************************************')
        order_info = ['amount','filled','datetime','id','side','status','symbol','timestamp','type']
        values = [order[info] for info in order_info] #字典信息
        info = dict(zip(order_info,values))
        print(info)
        return order
    
    def create_sell_limit_order(self,symbol,amount,price,*args,**kwargs):#创建市价卖单 输入symbol, amount 以及 limitprice 即可
        order = self._BitmexConnect.create_order(symbol = symbol, type='limit', side = 'sell', amount = amount, price = price,*args,**kwargs)
        print('********************************************************************************')
        print('order is successfully created')
        print('********************************************************************************')
        print(order)
        
    def create_order(self, *args, **kwargs):
        order = self._BitmexConnect.create_order(*args, **kwargs)
        print('order is successfully created')
        print('********************************************************************************')
        print(order)
        
    def edit_limit_buy_order(self,order_id,symbol,price,amount,*args,**kwargs):  #需要参数 order_id; symbol,price,amout
        order = self._BitmexConnect.edit_order(id = order_id,symbol = symbol,type = 'limit', side = 'buy',amount = amount,price = price, *args , **kwargs)
        print('order is successfully created')
        print('********************************************************************************')
        print(order)
    
    def edit_limit_sell_order(self,order_id,symbol,price,amount,*args,**kwargs):  #需要参数 order_id; symbol,price,amout
        order = self._BitmexConnect.edit_order(id = order_id,symbol = symbol,type = 'limit', side = 'sell',amount = amount,price = price, *args , **kwargs)
        print('order is successfully created')
        print('********************************************************************************')
        print(order)
    
    def cancel_order(self, order_id, *args , **kwargs):  #根据订单ID取消某一个订单
        self._BitmexConnect.cancel_order(id = order_id,*args,**kwargs)
        
    
    def cancel_all_orders(self): #直接取消所有活动订单
        self._BitmexConnect.privateDeleteOrderAll()
        
    def open_orders(self, *args, **kwargs):
        #未成交的订单
        return self._BitmexConnect.fetchOpenOrders( *args, **kwargs)
    
    def close_orders(self, *args, **kwargs):
        #未成交的订单
        return self._BitmexConnect.fetchClosedOrders( *args, **kwargs)
    
    def get_order(self,orderid):
        return self._BitmexConnect.fetchOrder(orderid)
        
    def all_position(self):
        all_position2 = self._BitmexConnect.private_get_position()
        all_position = [current_position for current_position in all_position2 if current_position['currentQty'] != 0 ]
        return all_position
    
        
        
        
if __name__ == '__main__':
    run = bitmex_ccxt()
    #dir(bitmex)
    bitmex = run._BitmexConnect
    bitmex.fetchMarkets ()
    tester.get_all_symbol()
    symbol = 'LTCZ18'
#    bitmex.symbols
#    bitmex.market(symbol)
    
    bitmex = tester._BitmexConnect
    symbol = 'BTC/USD'
    amount = 1000
    price = 5000
    
    params2={
           "stopPx": 6000
           }
           
           
    order = bitmex.create_order(symbol = symbol, type='StopLimit', side = 'buy', amount = amount, price = price, params = {"stopPx":6500} )

    
    
    order = bitmex.create_order(symbol = symbol, type='StopLimit', side = 'sell', amount = amount, price = 7000, params = {"stopPx":6500} )


    
    run.limit_order(symbol,amount,price,'buy')
    

    
    
    symbolList = []
    contracts =  bitmex.fetchMarkets ()
    for contract in contracts:
        if contract['active'] == True:
#        if not contract['symbol'].startswith('.'):
            symbolList.append(contract['symbol'])

    tester.get_all_symbol()
    [contract for contract in contracts if contract['baseId'] == 'XBT']
    
    open_order = tester.open_orders()
    pd.DataFrame(open_order)

    order_id = open_order[0]['id']
    
    now = bitmex.milliseconds()
    since = now - (750) * 60 * 1000
    orders = bitmex.fetchOrders(since = since)
    
    import time
    timeStamp = since/1000
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

    bitmex.fetchOrder('ecb85a2f-5663-4599-aac1-03c8681cb00f')
    bitmex.fetchOpenOrders() #未成交的订单
    bitmex.fetchClosedOrders(since = since)  #成交的订单
    
#    bitmex.fetchTrades('BTC/USD')
#    bitmex.fetchMyTrades('BTC/USD')
    
    import time
    timeArray = time.localtime(since/1000)
    print (timeArray)
    import time
    timeStamp = 1381419600
    bitmex.fetchClosedOrders(since = since)
    # keep last hour of history in cache
    before = bitmex.milliseconds () - 1 * 60 * 60 * 1000
    # purge all closed and canceled orders "older" or issued "before" that time
    bitmex.purge_cached_orders (since)
    
    # print(tester.get_all_symbol())
    # print(tester.get_all_id())
    tester.fetch_balance()
    print(tester.fetch_balance())
    # print(len(tester.fetch_order_book('BTC/USD')['asks']))
    # print(tester.fetch_ticker('BTC/USD'))
#     print(tester.fetch_ohlcv('BTC/USD', '1m',None))
    print(tester.get_uesr_market_position())
    print(tester.get_user_active_position('XBTUSD'))
#    tester.create_buy_market_order('BTC/USD',100)
    #tester.create_sell_market_order('BTC/USD',100)
    #tester.create_buy_limit_order('BTC/USD',100,6000)
    #tester.create_buy_limit_order('BTC/USD',100,7700)
    #tester.create_order(symbol = 'BTC/USD' , type = 'market' , side = 'buy' , amount = 10)
    #tester.edit_limit_buy_order('dbbc4314-3600-831f-bf08-29a8bff5971a','BTC/USD',price = 4000, amount = 200)
    #tester.cancel_order('dbbc4314-3600-831f-bf08-29a8bff5971a')
    tester.cancea_all_orders()
    
    
    
    
    
    