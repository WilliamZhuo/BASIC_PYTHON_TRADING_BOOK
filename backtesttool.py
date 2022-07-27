# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 15:52:43 2022

@author: user
"""
import talib
import kbars
import matplotlib.pyplot as plt
import pandas as pd
import numpy
def period_profit(openprice,begin=0,end=10):
    #用來確認沒有出現開盤價為零的狀況
    if(openprice[begin]==0):
        print('div0')
    #買進持有的報酬=最後一天的開盤價/第一天的開盤價
    return (openprice[end]-openprice[begin])/openprice[begin]

G_spread=3.6280082234853065666948845084049e-4
G_tax=4.4109538687741224039698584818967e-5
G_commission=4.4109538687741224039698584818967e-5
G_tradecost=G_spread+G_tax+G_commission
def backtest_signal(
        openprice
        ,signal
        ,tradecost=G_tradecost
        ,sizing=1.0):
    buy=signal.astype(float)
    ####################################
    #把買賣訊號往後移一天,因為今天收盤的訊號下一天開盤才會買賣
    ####################################
    position=buy.shift(1)
    position[0]=0.0
    #list() io比series快
    openprice_l=openprice.tolist()
    position_l=position.tolist()    
    l=[]
    #用position.size-1,因為最後一天+1是沒東西的, period_profit那行會有error,雖然還是可以跑
    for i in range(0,position.size-1,1):
        try:
            profit=period_profit(openprice_l,begin=i,end=i+1)
            cost=0
            #單邊交易成本,單位是百分比
            try:
                #buy->sell or sell->buy
                positionchange=abs(position_l[i]-position_l[i-1])
                if(positionchange>0):
                    cost=tradecost*positionchange
            except:
                print('backtest_signal fail at calculate cost:',str(i))
                pass           
            
            ret=1.0+profit*position_l[i]*sizing-cost*sizing
            
            #faster than the origin one
            l.append(ret)
        except Exception as e: # work on python 3.x
             print('backtest_signal fail at:',str(i))
             pass
    ret_series = pd.Series(l)
    #list轉numpy比較快
    retStrategy=numpy.array(l).prod()    
    #NOTE:最後一天的報酬率還沒出來，要等隔天的開盤價出來才會知道
    return retStrategy-1,ret_series

def optimizeMA(
        df,
        period_range_Long,#=numpy.arange(2,100,1,dtype=int)
        period_range_Short#=numpy.arange(2,100,1,dtype=int)
        ):
    def createSignal(close,periodShort,periodLong):
        maShort=talib.EMA(close,periodShort)
        maLong=talib.EMA(close,periodLong)
        ENABLESHORT=False
        #允許放空的訊號寫法
        if(ENABLESHORT): 
            BuySignal=(maShort>maLong).astype(int)
            ShortSignal=(maShort<maLong).astype(int)
            return BuySignal-ShortSignal    
        #不允許放空的訊號寫法，兩個差在允許放空的部分多了ShortSignal            
        else:
            BuySignal=(maShort>maLong).astype(int)
            return BuySignal
    openPrice=df['Open']
    closePrice=df['Close']  
    bestret=0
    bestret_series=[]
    bestperiodLong=0
    bestperiodShort=0
    for periodLong in period_range_Long:
        for periodShort in period_range_Short:
            if(periodLong<=periodShort):
                continue
            #製作買賣訊號
            BuySignal=createSignal(closePrice,periodShort,periodLong)
            #對訊號進行回測
            retStrategy,ret_series=backtest_signal(
                openPrice
                ,BuySignal
                ,tradecost=G_tradecost
                ,sizing=1.0)
            #如果結果比之前更好,就記錄下來
            if(bestret<retStrategy):
                bestret=retStrategy
                bestret_series=ret_series
                bestperiodLong=periodLong
                bestperiodShort=periodShort
    return bestret,bestret_series,(bestperiodLong,bestperiodShort)

def prefixProd(retseries):
    clone=retseries.copy()
    prod=1
    for i in range(0,retseries.size,1):
        prod=prod*retseries[i]
        clone[i]=prod
    return clone
#計算MDD，最大虧損
def calculateMDD(retSeries):
    prefixProdSeries=prefixProd(retSeries)
    maxval=prefixProdSeries[0]
    MDD=0
    for i in range(0,prefixProdSeries.size,1):
        maxval=max(prefixProdSeries[i],maxval)
        temp=1.0-prefixProdSeries[i]/maxval
        if(temp>MDD):
            MDD=temp
    return MDD

#計算MDD，最大虧損
#也可以傳入return series的prefix product
def calculateMDD_fromClose(close):
    prefixProdSeries=close
    maxval=prefixProdSeries[0]
    MDD=0
    for i in range(0,prefixProdSeries.size,1):
        maxval=max(prefixProdSeries[i],maxval)
        temp=1.0-prefixProdSeries[i]/maxval
        if(temp>MDD):
            MDD=temp
    return MDD