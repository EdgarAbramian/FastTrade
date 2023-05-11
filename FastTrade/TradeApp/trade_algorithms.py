from binance.client import Client
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas_ta as ta
from keys import api_key as api_key
from keys import api_secret as api_secret
from binance.enums import*
from tradingview_ta import TA_Handler, Interval, Exchange
from patterns_list import patterns
from candlestick import candlestick
import plotly.graph_objects as go
import datetime
 
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

print('Start')

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

#ПОДБИРАЕМ КРИПТУ
def top_coin():
   all_tickers = pd.DataFrame(client.get_ticker())
   asset = all_tickers[all_tickers.symbol.str.contains('USDT')]
   for i in asset['symbol']:
        try:
            handler = TA_Handler(
                    screener="crypto",
                    interval= Interval.INTERVAL_15_MINUTES,
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

def get_patter(asset):
    handler = TA_Handler(
        screener="crypto",
        interval= Interval.INTERVAL_15_MINUTES,
        symbol= asset,
        exchange="binance",
    )
    handler.add_indicators(patterns)
    analysis = handler.get_analysis()

    pattern_count = 0

    for key, value in analysis.indicators.items():
        if "Candle" in key:
            if value == 1:
                print(key)
                print("{} candlestick pattern detected".format(key))
                pattern_count += 1

    if pattern_count == 0:
        print("No candlestick patterns detected")

#https://pastebin.com/1DjWv2Hd
def def_pattern(asset):
    df = last_data(asset, '1m', '3')
    df = df.drop(['Volume'],axis = 1)
    df = candlestick.inverted_hammer(df, target='inverted_hammer')
    df = candlestick.bearish_engulfing(df,target='bearish_engulfing')
    df = candlestick.bearish_harami(df,target='bearish_harami')
    plt.figure(figsize=(20, 10),edgecolor='r',facecolor='b')
    plt.plot(df.index,df['close'])
    plt.plot(df.index,df['open'])
    plt.plot(df.index,df['high'])
    plt.plot(df.index,df['low'])
    plt.scatter(df.index[df.inverted_hammer],df[df.inverted_hammer].close,marker='^',color = 'g')
    # plt.scatter(df.index[df.bearish_engulfing],df[df.bearish_engulfing].close,marker='^',color = 'r')
    # plt.scatter(df.index[df.bearish_harami],df[df.bearish_harami].close,marker='^',color = 'y')
    plt.savefig('fig.png')
    print(df)

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
    # try:
    #                 #           DRAWING
    #         plt.rcParams['axes.facecolor'] = '#161a1e'
    #         plt.rcParams['figure.facecolor'] = '#161a1e'
    #         plt.figure(figsize=(20,10))
    #         plt.plot(df[['close','SMA','Upper','Lower']])
    #         plt.scatter(df.index[df.Buy_Signal],df[df.Buy_Signal].close,marker ='^',color = 'g' )
    #         plt.scatter(df.index[df.Sell_Signal],df[df.Sell_Signal].close,marker ='*',color = 'r' )
    #         plt.fill_between(df.index,df.Upper,df.Lower,color = 'yellow',alpha =0.3)
    #         plt.grid(color = '#464c56', alpha=0.5)
    #         plt.savefig('zline_boli.png')
    #         #         DRAWING FINISH
    # except:
    #         Exception 
        

    
    if((Last_Sell_Signals[-1] == 'True') or
       count(Last_Sell_Signals,'True') >= 2 ):
        return False#  TO SELL
    return True#  NOT TO SELL

def autopilot():
    TOP_COIN_INFO = top_coin()
    COIN = TOP_COIN_INFO['coin']
    buy = CURR_PRICE(COIN)
    print(datetime.datetime.now())
    print(f'BUY:{COIN} for {buy} ')
    
    SELL = False
    while(not SELL):
        df = last_data(COIN, '1m', '120')
        
        try:
            handler = TA_Handler(
                    screener="crypto",
                    interval= Interval.INTERVAL_5_MINUTES,
                    symbol= COIN,
                    exchange="binance",
                )
            # analysis = handler.get_analysis().summary
            if (((REC_IS_SELL(handler)and buy<CURR_PRICE(COIN)) 
            or (boll_lines(df) and buy < CURR_PRICE(COIN))
            and buy!=CURR_PRICE(COIN))
                or (CURR_PRICE(COIN))/buy <= 0.975 ):
                print(f'SOLD: {CURR_PRICE(COIN)}')
                print(f'Profit: {(CURR_PRICE(COIN)/buy-1)*100} %')
                print(datetime.datetime.now())
                return "SELL"
        except:
            Exception 
      
        time.sleep(15) 

if __name__ == "__main__":
    autopilot()



#   'BNBBUSD'                 
#    'BTCBUSD'              
#    'ETHBUSD'                
#    'LTCBUSD'                 
#   'TRXBUSD'                 
#    'XRPBUSD'                 
#    'BNBUSDT'                 
#    'BTCUSDT'              
#    'ETHUSDT'                
#    'LTCUSDT'                 
#   'TRXUSDT'                 
#   'XRPUSDT'                 
#    'BNBBTC'                  
#    'ETHBTC'                 
#    'LTCBTC'                  
#    'TRXBTC'                  
#    'XRPBTC'                 
#   'LTCBNB'     
#    'TRXBNB'                 
#    'XRPBNB'