from django.shortcuts import render
import requests
from binance.client import Client
import pandas as pd
import numpy as np
import time
import datetime
from tradingview_ta import TA_Handler, Interval, Exchange
# from .models import UserInfo
from django.shortcuts import redirect 
api_key = 'V9GyIlfInl8eO3TKpVOXb13gvXs78ozMvKZC3xOpIIepfoYmXCgXhojazGwNWQK7'
api_secret = 'lAqnVmsseWXmcnDcceeC2tkjqoZXbiqKdxo5hD3hSOnZIfL7MgccYoSkvUln6DqY' 
COIN_LINK= 'https://www.binance.com/ru/futures/'
ASSET = []
#СОЗДАНИЕ КЛИЕНТА
client = Client(api_key, api_secret)

#ПОЛУЧЕНИЕ ТЕКУЩЕЙ ЦЕНЫ 
CURR_PRICE = lambda asset: float((client.get_symbol_ticker(symbol = asset)['price']))

REC_IS_SELL = lambda handler: handler.get_analysis().summary['RECOMMENDATION'] == 'SELL'

def count(ar,sym):
    count = 0
    for i in ar:
        if i == sym:
            count+=1
    return count

#ПОЛУЧЕНИЕ СВЕЧ
def last_data(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol, interval, lookback + 'min ago UTC'))
    frame = frame.iloc[:, :6]
    frame.columns = ['time', 'open', 'high', 'low', 'close', 'Volume']
    frame = frame.set_index('time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame
    #("BTCUSDT", '1m', '2')

def boll_lines(df):
    df['SMA'] = df.close.rolling(window=20).mean()
    df['stddev'] = df.close.rolling(window=20).std()
    df['Upper'] = df.SMA + 2*df.stddev
    df['Lower'] = df.SMA - 2*df.stddev
    df['Buy_Signal'] = np.where(df.Lower > df.close,True,False)
    df['Sell_Signal'] = np.where(df.Upper < df.close,True,False)
    df.dropna()
    Last_Buy_Signals = np.array((df['Buy_Signal'].to_numpy())[:-4:-1])
    Last_Sell_Signals = np.array((df['Sell_Signal'].to_numpy())[:-4:-1])


    
    if((Last_Sell_Signals[-1] == 'True') or
       count(Last_Sell_Signals,'True') >= 2 ):
        return False#  TO SELL
    return True#  NOT TO SELL

tickers = ['BNBBUSD', 
   'BTCBUSD',              
   'ETHBUSD',         
   'LTCBUSD',                 
  'TRXBUSD',                 
   'XRPBUSD',                 
   'BNBUSDT',                 
   'BTCUSDT',              
   'ETHUSDT' ,               
   'LTCUSDT',                
  'TRXUSDT' ,                
  'XRPUSDT',                
   'BNBBTC',                  
   'ETHBTC' ,                
   'LTCBTC' ,                 
   'TRXBTC' ,                 
   'XRPBTC' ,                
  'LTCBNB'  ,   
   'TRXBNB' ,                
   'XRPBNB']

#ПОДБИРАЕМ КРИПТУ
#Interval.INTERVAL_15_MINUTES
def top_coin(INTERVAL):
   client = Client(api_key, api_secret)
   #all_tickers = pd.DataFrame(client.get_ticker())
   asset = tickers
   for i in asset:
        try:
            handler = TA_Handler(
                    screener="crypto",
                    interval= INTERVAL,
                    symbol = i,
                    exchange="binance",
                )
            
            analysis = handler.get_analysis().summary
            if (analysis['RECOMMENDATION'] == 'BUY'):

                return {'coin':i,
                        'analysis':analysis,
                        'RSI':handler.get_indicators()['RSI'],
                        'MACD':handler.get_indicators()['MACD.signal'],
                        'volume':handler.get_indicators()['volume'],
                        'SMA10':handler.get_indicators()['SMA10'],}
        except:
            Exception

def index_page(requests):
    return render(requests, 'TradeApp/main.html',{'title':"FastTrade"})

def auto(requests):
    TOP_COIN_INFO = top_coin(Interval.INTERVAL_15_MINUTES)
    COIN = TOP_COIN_INFO['coin']
    buy = CURR_PRICE(COIN)
    opentime = (datetime.datetime.now())
    BUY = (f'{COIN} for {buy} ')
    print(datetime.datetime.now())
    print(f'BUY:{COIN} for {buy} ')
    SELL = False
    ASSET.append(COIN)
    while(not SELL):
        df = last_data(COIN, '1m', '120')
        
        try:
            handler = TA_Handler(
                    screener="crypto",
                    interval= Interval.INTERVAL_15_MINUTES,
                    symbol= COIN,
                    exchange="binance",
                )
            # analysis = handler.get_analysis().summary
            if (((REC_IS_SELL(handler)or buy<CURR_PRICE(COIN)) 
            or (boll_lines(df) and buy < CURR_PRICE(COIN))
            and buy!=CURR_PRICE(COIN))
                or (CURR_PRICE(COIN))/buy <= 0.975 ):
                SOLD= (f'SOLD: {CURR_PRICE(COIN)}')
                Profit = (f' {(CURR_PRICE(COIN)/buy-1)*100} %')
                closetime = (datetime.datetime.now())
                print(f'SOLD: {CURR_PRICE(COIN)}')
                print(f'Profit: {(CURR_PRICE(COIN)/buy-1)*100} %')
                print(datetime.datetime.now())
                return render(requests, 'TradeApp/auto.html',{'title': "AUTO", 'BUY': BUY, 'SOLD': SOLD,'OPEN':opentime,'CLOSE':closetime,'PROF':Profit})

        except:
            Exception 
      
        time.sleep(15) 

def rec_long(requests):
    res = top_coin(Interval.INTERVAL_1_MONTH)
    ASSET.append(res["coin"])
    return render(requests, 'TradeApp/rec.html',{'INTERVAL':"LONG",'COIN':res["coin"],'BUY':res['analysis']['BUY'],'SELL':res['analysis']['SELL']})

def rec_short(requests):
    res = top_coin(Interval.INTERVAL_15_MINUTES)
    ASSET.append(res["coin"])
    return render(requests, 'TradeApp/short.html',{'INTERVALs':"SHORT",'COINs':res["coin"],'BUYs':res['analysis']['BUY'],'SELLs':res['analysis']['SELL']})

def rec(requests):
    return render(requests, 'TradeApp/rec.html')

def LINK_TO_COIN(requests):
    response = redirect(COIN_LINK + ASSET[-1]) 
    return response


# https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT
