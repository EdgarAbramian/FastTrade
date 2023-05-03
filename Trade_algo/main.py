from binance.client import Client
import pandas as pd
import json
import numpy as np
import time
import matplotlib.pyplot as plt
import pandas_ta as ta
from key import api_key as api_key
from key import api_secret as api_secret
from binance.enums import*

ASSET = 'BTCUSDT'
BUY_PRICE =lambda asset: float((client.get_symbol_ticker(symbol = asset)['price']))
BUY_INIT = 0
client = Client(api_key, api_secret)
print("STARTED")

def top_coin():
    all_tickers = pd.DataFrame(client.get_ticker())
    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    work = usdt[~((usdt.symbol.str.contains('UP')) | (usdt.symbol.str.contains('DOWN')))]
    top_coin = work[work.priceChangePercent == work.priceChangePercent.max()]
    top_coin = top_coin.symbol.values[0]
    return top_coin

def get_last_data(symbol, interval,filename):
    candles = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_15MINUTE , "1 day ago UTC")
    df = pd.DataFrame(candles)
    with open(filename,'+w') as file:
        for i in range (0,500):
            file.write(str([df[0][i],df[1][i],df[2][i],df[3][i],df[4][i],df[5][i]])+'\n')
    df = df.iloc[:, :7]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume','Close_Time']
    df.iloc[1:, :6] = df.iloc[1:, :6].astype(float)
    df['Time'] = df['Time'].astype(int)
    df['Close_Time'] = df['Close_Time'].astype(int)
    return df

def get_recent_trades():
    recent_trades =pd.DataFrame(client.get_recent_trades(symbol='BNBBTC'))
    return recent_trades

def signal_generator(df):
    open = float(df.Open.iloc[-1])
    close = float(df.Close.iloc[-1])
    previous_open = float(df.Open.iloc[-2])
    previous_close = float(df.Close.iloc[-2])
    previous_open1 = float(df.Open.iloc[-3])
    previous_close1 = float(df.Close.iloc[-3])
    print(f'open: {open} {df.Time.iloc[-1]}')
    print(f'close: {close}  {df.Time.iloc[-1]}')
    print(f'previous_open: {previous_open} {df.Time.iloc[-2]}')
    print(f'previous_close: {previous_close} {df.Time.iloc[-2]}')
    print(f'previous_open: {previous_open1} {df.Time.iloc[-3]}')
    print(f'previous_close: {previous_close1} {df.Time.iloc[-3]}')
    
    # Bearish Pattern
    if (open>close and 
    previous_open<previous_close and 
    close<previous_open and
    open>=previous_close):
        return 1

    # Bullish Pattern
    elif (open<close and 
        previous_open>previous_close and 
        close>previous_open and
        open<=previous_close):
        return 2
    
    # No clear pattern
    else:
        return 0


def three_star_pattern(df):
    open = float(df.Open.iloc[-1])
    close = float(df.Close.iloc[-1])
    previous_open = float(df.Open.iloc[-2])
    previous_close = float(df.Close.iloc[-2])
    previous_open1 = float(df.Open.iloc[-3])
    previous_close1 = float(df.Close.iloc[-3])
    if (open < previous_open and close < previous_close and
        previous_close < previous_close1 and
        previous_open < previous_open1):
        return 1
    else:
        return -1

def three_solders_pattern(df):
    open = float(df.Open.iloc[-1])
    close = float(df.Close.iloc[-1])
    previous_open = float(df.Open.iloc[-2])
    previous_close = float(df.Close.iloc[-2])
    previous_open1 = float(df.Open.iloc[-3])
    previous_close1 = float(df.Close.iloc[-3])
    if (open > previous_open and close > previous_close and
        previous_close > previous_close1 and
        previous_open > previous_open1):
        return 1
    else:
        return -1
    

df =  get_last_data(ASSET, Client.KLINE_INTERVAL_3MINUTE, 'KLINE.txt')

def rec_to_BUY(frame):
    BOUGHT = False
    if (signal_generator(frame) == 1):
        print(f'Bullish Pattern was spotted in {ASSET}\n Recommended to buy {ASSET}')
        BOUGHT = True
    if (three_star_pattern(frame)):
        print(f'Three Star Pattern was spotted in {ASSET}\n Recommended to buy {ASSET}')
        BOUGHT = True
    elif(three_solders_pattern(frame)):
        print(f'Three Solders Pattern was spotted in {ASSET}\n Recommended to buy {ASSET}')
        BOUGHT = True
    BUY_INIT = BUY_PRICE(ASSET)
    
    print(f'BUY_INIT: {BUY_INIT}')
    order = client.create_test_order(
    symbol='BNBBTC',
    side=SIDE_BUY,
    type=ORDER_TYPE_LIMIT,
    timeInForce=TIME_IN_FORCE_GTC,
    quantity=100,
    price='0.00001')
    while(BOUGHT):
        frame =  get_last_data(ASSET, Client.KLINE_INTERVAL_3MINUTE, '/workspaces/Individual-HW/Trading_bot/KLINE.txt')
        if(rec_to_SELL(frame,BUY_INIT)):
            BOUGHT = not(BOUGHT)
           


def rec_to_SELL(frame,INITIAL):
    RISING = True
    BUYPRICE = float(BUY_PRICE(ASSET))
    print(BUYPRICE)
    if ((BUYPRICE - INITIAL) <= -5  or (BUYPRICE - INITIAL) >= 2):
        print(f'Bearish Pattern was spotted in {ASSET}\n Recommended to SELL {ASSET}') 
        RISING = not(RISING)
        print(f'SELL_PRICE: {BUYPRICE}')
        print(f'Profit: {BUYPRICE - INITIAL}')
        print('-----------------------------------------')
        print(f'BUYPRICE: {BUYPRICE}')
        print(f'INITIAL: {INITIAL}')


        return 1
    else:
        return 0

print(top_coin())
rec_to_BUY(df)
# BUY_INIT: 28001.26
# print(float(str(BUY_PRICE(ASSET))))
# print(ASSET)
# print(signal_generator(df))
# print(three_star_pattern(df))
# print(three_solders_pattern(df))



             