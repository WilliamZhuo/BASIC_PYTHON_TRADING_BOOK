# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 20:55:00 2022

@author: user
"""

import talib
import kbars
import ShioajiLogin
import matplotlib.pyplot as plt
import pandas as pd
import numpy
import backtesttool
ENABLEDEBUG=0

#########################################
#MACD指標
###########################################
#使用快慢線交叉當作買賣訊號
def createSignalMACD(close,
                 periodFast,
                 periodSlow,
                 periodSignal):
    macd, macdsignal, macdhist =talib.MACD(close
       ,fastperiod=periodFast 
       ,slowperiod=periodSlow 
       ,signalperiod=periodSignal)
    ENABLESHORT=False
    #允許放空的訊號寫法
    if(ENABLESHORT): 
        BuySignal=(macdhist>0).astype(int)
        ShortSignal=(macdhist<0).astype(int)
        return BuySignal-ShortSignal    
    #不允許放空的訊號寫法，兩個差在允許放空的部分多了ShortSignal            
    else:
        BuySignal=(macdhist>0).astype(int)
        return BuySignal
#找出MACD買賣訊號的最佳化參數
def OptimizeMACD(
        df,
        rangeFast,#=numpy.arange(2,100,1,dtype=int)
        rangeSlow,#=numpy.arange(2,100,1,dtype=int)
        rangeSignal#=numpy.arange(2,100,1,dtype=int)
        ):

    openPrice=df['Open']
    closePrice=df['Close']  
    bestret=0
    bestret_series=[]
    bestperiodFast=0
    bestperiodSlow=0
    bestperiodSignal=0
    for periodFast in rangeFast:
        for periodSlow in rangeSlow:
            for periodSignal in rangeSignal:
                if(ENABLEDEBUG):
                    print("periodFast:"+str(periodFast))
                    print("periodSlow:"+str(periodSlow))
                    print("periodSignal:"+str(periodSignal))
                #錯誤檢查,快線週期要比慢線短
                if(periodFast>=periodSlow):
                    continue
                #製作買賣訊號
                BuySignal=createSignalMACD(closePrice,
                                       periodFast,
                                       periodSlow,
                                       periodSignal)
                #對訊號進行回測
                retStrategy,ret_series=backtesttool.backtest_signal(
                    openPrice
                    ,BuySignal)
                #如果結果比之前更好,就記錄下來
                if(bestret<retStrategy):
                    bestret=retStrategy
                    bestret_series=ret_series
                    bestperiodFast=periodFast
                    bestperiodSlow=periodSlow
                    bestperiodSignal=periodSignal
                    
    return bestret,bestret_series,(bestperiodFast,bestperiodSlow,bestperiodSignal)
#########################################
#KD指標
###########################################
#使用KD交叉當作買賣訊號
def createSignalKD(high,low,close,
                 fastk=5,
                 slowk=3,
                 slowd=3):
    slowk, slowd = talib.STOCH(high, low, close,
                     fastk_period=fastk,
                     slowk_period=slowk, 
                     slowk_matype=talib.MA_Type.SMA,
                     slowd_period=slowd,
                     slowd_matype=talib.MA_Type.SMA
                     )
    ENABLESHORT=False
    #允許放空的訊號寫法
    if(ENABLESHORT): 
        BuySignal=(slowk>slowd).astype(int)
        ShortSignal=(slowk<slowd).astype(int)
        return BuySignal-ShortSignal    
    #不允許放空的訊號寫法，兩個差在允許放空的部分多了ShortSignal            
    else:
        BuySignal=(slowk>slowd).astype(int)
        return BuySignal
#找出KD買賣訊號的最佳化參數
def OptimizeKD(
        df,
        range_fastk,#=numpy.arange(2,100,1,dtype=int)
        range_slowk,#=numpy.arange(2,100,1,dtype=int)
        range_slowd#=numpy.arange(2,100,1,dtype=int)
        ):

    openPrice=df['Open']
    closePrice=df['Close']  
    highPrice=df['High']  
    lowPrice=df['Low']  
    bestret=0
    bestret_series=[]
    best_fastk=0
    best_slowk=0
    best_slowd=0
    for fastk in range_fastk:
        for slowk in range_slowk:
            for slowd in range_slowd:
                if(ENABLEDEBUG):
                    print("fastk:"+str(fastk))
                    print("slowk:"+str(slowk))
                    print("slowd:"+str(slowd))

                #製作買賣訊號
                BuySignal=createSignalKD(highPrice,lowPrice,closePrice,
                                       fastk,
                                       slowk,
                                       slowd)
                #對訊號進行回測
                retStrategy,ret_series=backtesttool.backtest_signal(
                    openPrice
                    ,BuySignal)
                #如果結果比之前更好,就記錄下來
                if(bestret<retStrategy):
                    bestret=retStrategy
                    bestret_series=ret_series
                    best_fastk=fastk
                    best_slowk=slowk
                    best_slowd=slowd
                    
    return bestret,bestret_series,(best_fastk,best_slowk,best_slowd)

#########################################
#RSI指標
###########################################
#使用RSI往上穿越longTH做多,往下穿越shortTH做空的買賣策略
#longTH>shortTH,longTH預設值為70,shortTH預設值為30
def createSignalRSI(close,
                 timeperiod=14,
                 longTH=70,
                 shortTH=30):
    real = talib.RSI(close, timeperiod=timeperiod)  

    ENABLESHORT=False
    if(ENABLESHORT):
        BuySignal=(real>longTH).astype(int)
        ShortSignal=(real<shortTH).astype(int)
        return BuySignal-ShortSignal
    else:
        BuySignal=(real>longTH).astype(int)
        return BuySignal
#找出RSI買賣訊號的最佳化參數
def OptimizeRSI(
        df,
        range_period,#=numpy.arange(2,100,1,dtype=int)
        range_longTH,#=numpy.arange(2,100,1,dtype=int)
        range_shortTH#=numpy.arange(2,100,1,dtype=int)
        ):

    openPrice=df['Open']
    closePrice=df['Close']  
    bestret=0
    bestret_series=[]
    best_period=0
    best_longTH=0
    best_shortTH=0
    for period in range_period:
        for longTH in range_longTH:
            for shortTH in range_shortTH:
                if(ENABLEDEBUG):
                    print("period:"+str(period))
                    print("longTH:"+str(longTH))
                    print("shortTH:"+str(shortTH))
                if(longTH<=shortTH):
                    continue
                #製作買賣訊號
                BuySignal=createSignalRSI(closePrice,
                                       period,
                                       longTH,
                                       shortTH)
                #對訊號進行回測
                retStrategy,ret_series=backtesttool.backtest_signal(
                    openPrice
                    ,BuySignal)
                #如果結果比之前更好,就記錄下來
                if(bestret<retStrategy):
                    bestret=retStrategy
                    bestret_series=ret_series
                    best_period=period
                    best_longTH=longTH
                    best_shortTH=shortTH
                    
    return bestret,bestret_series,(best_period,best_longTH,best_shortTH)

#########################################
#布林通道
###########################################
#這邊的布林通道交易訊號使用以下連結的
#https://www.investopedia.com/trading/using-bollinger-bands-to-gauge-trends/#:~:text=Bollinger%20Bands%C2%AE%20are%20a%20trading%20tool%20used%20to%20determine,lot%20of%20other%20relevant%20information.
#Create Multiple Bands for Greater Insight
def createSignalBBAND(close,
                 timeperiod=20,
                 SmallStdDev=1.0,
                 LargeStdDev=2.0):
    upperband_Small, middleband_Small, lowerband_Small = \
        talib.BBANDS(close, 
                     timeperiod=timeperiod,
                     nbdevup=SmallStdDev,
                     nbdevdn=SmallStdDev, 
                     matype=talib.MA_Type.SMA)
    upperband_Large, middleband_Large, lowerband_Large = \
        talib.BBANDS(close, 
                     timeperiod=timeperiod,
                     nbdevup=LargeStdDev,
                     nbdevdn=LargeStdDev, 
                     matype=talib.MA_Type.SMA)    
    ENABLESHORT=True
    #允許放空的訊號寫法
    if(ENABLESHORT): 
        BuySignal=((close>=upperband_Small) & (close<=upperband_Large)).astype(int)
        ShortSignal=((close>=lowerband_Large) & (close<=lowerband_Small)).astype(int)
        return BuySignal-ShortSignal    
    #不允許放空的訊號寫法，兩個差在允許放空的部分多了ShortSignal            
    else:
        BuySignal=((close>=upperband_Small) & (close<=upperband_Large)).astype(int)
        return BuySignal    
#找出BBAND買賣訊號的最佳化參數
def OptimizeBBAND(
        df,
        range_period,#=numpy.arange(2,100,1,dtype=int)
        range_SmallStdDev,#=numpy.arange(0.5,5,0.5,dtype=float)
        range_LargeStdDev#=numpy.arange(0.5,5,0.5,dtype=float)
        ):

    openPrice=df['Open']
    closePrice=df['Close']  
    bestret=0
    bestret_series=[]
    best_period=0
    best_SmallStdDev=0
    best_LargeStdDev=0
    for period in range_period:
        for SmallStdDev in range_SmallStdDev:
            for LargeStdDev in range_LargeStdDev:
                if(ENABLEDEBUG):
                    print("period:"+str(period))
                    print("SmallStdDev:"+str(SmallStdDev))
                    print("LargeStdDev:"+str(LargeStdDev))
                if(LargeStdDev<=SmallStdDev):
                    continue
                #製作買賣訊號
                BuySignal=createSignalBBAND(closePrice,
                                       timeperiod=period,
                                       SmallStdDev=SmallStdDev,
                                       LargeStdDev=LargeStdDev)
                #對訊號進行回測
                retStrategy,ret_series=backtesttool.backtest_signal(
                    openPrice
                    ,BuySignal)
                #如果結果比之前更好,就記錄下來
                if(bestret<retStrategy):
                    bestret=retStrategy
                    bestret_series=ret_series
                    best_period=period
                    best_SmallStdDev=SmallStdDev
                    best_LargeStdDev=LargeStdDev
                    
    return bestret,bestret_series,(best_period,best_SmallStdDev,best_LargeStdDev)

#########################################
#價格通道
###########################################
#當最高價創新高的時候做多,最低價創新低的時候做空
def createSignalPriceChannel(
        df,period):
    high=df['High']
    low=df['Low']
    #創新高買進訊號
    BuySignal=(high==high.rolling(period).max()).astype(int)
    #創新低買進訊號
    SellSignal=(low==low.rolling(period).min()).astype(int)
    signal=BuySignal-SellSignal
    #上面的買賣訊號只有在穿過通道線的時候才有值,這邊用一些小技巧把中間的數值也填上去
    signal[signal==0]=float("NaN")
    signal[0]=0
    signal=signal.fillna(method="ffill")
    ENABLESHORT=False
    if(not ENABLESHORT):
        signal[signal<0]=0
    return signal
#找出價格通道買賣訊號的最佳化參數
def OptimizePriceChannel(
        df,
        range_period#=numpy.arange(2,100,1,dtype=int)
        ):
    openPrice=df['Open']
    closePrice=df['Close']  
    bestret=0
    bestret_series=[]
    best_period=0
    for period in range_period:
        if(ENABLEDEBUG):
            print("period:"+str(period))
        #製作買賣訊號
        BuySignal=createSignalPriceChannel(df,period)
        #對訊號進行回測
        retStrategy,ret_series=backtesttool.backtest_signal(
            openPrice
            ,BuySignal)
        #如果結果比之前更好,就記錄下來
        if(bestret<retStrategy):
            bestret=retStrategy
            bestret_series=ret_series
            best_period=period
            
    return bestret,bestret_series,(best_period)

#########################################
#網格交易策略
###########################################
#根據乖離率低買高賣的策略
def createGridSignal(df,
                     BiasUpperLimit,
                     UpperLimitPosition,
                     BiasLowerLimit,
                     LowerLimitPosition,
                     BiasPeriod):

    close=df['Close']
    
    Bias=close/close.rolling(window=BiasPeriod).mean()
    Bias=Bias.fillna(method='bfill')
    
    positiondiff=UpperLimitPosition-LowerLimitPosition
    biasdiff=BiasUpperLimit-BiasLowerLimit
    position=LowerLimitPosition+(Bias-BiasLowerLimit)*positiondiff/biasdiff
    position[Bias<=BiasLowerLimit]=LowerLimitPosition
    position[Bias>=BiasUpperLimit]=UpperLimitPosition
    return position
def OptimizeGrid(
        df,
        range_BiasUpper,#=numpy.arange(1.0,2.0,0.1,dtype=float)
        range_UpperPosition,#=numpy.arange(0.1,0.5,0.1,dtype=float)        
        range_BiasLower,#=numpy.arange(0.5,1.0,0.1,dtype=float)
        range_LowerPosition,#=numpy.arange(0.5,1.0,0.1,dtype=float)
        range_period #=numpy.arange(2,100,1,dtype=int)
        ):
    openPrice=df['Open']
    closePrice=df['Close']  
    bestret=0
    bestret_series=[]
    best_BiasUpper=0
    best_UpperPosition=0
    best_BiasLower=0
    best_LowerPosition=0
    best_period=0
    for BiasUpper in range_BiasUpper:
        for UpperPosition in range_UpperPosition:
            for BiasLower in range_BiasLower:
                for LowerPosition in range_LowerPosition:
                    for period in range_period:
                        if(ENABLEDEBUG):
                            print("BiasUpper:"+str(BiasUpper))
                            print("UpperPosition:"+str(UpperPosition))
                            print("BiasLower:"+str(BiasLower))
                            print("LowerPosition:"+str(LowerPosition))
                            print("period:"+str(period))
                        if(BiasUpper<=BiasLower):
                            continue
                        if(UpperPosition>=LowerPosition):
                            continue
                        
                        #製作買賣訊號
                        BuySignal=createGridSignal(df,
                             BiasUpper,
                             UpperPosition,
                             BiasLower,
                             LowerPosition,
                             period)
                        #對訊號進行回測
                        retStrategy,ret_series=backtesttool.backtest_signal(
                            openPrice
                            ,BuySignal)
                        #如果結果比之前更好,就記錄下來
                        if(bestret<retStrategy):
                            bestret=retStrategy
                            bestret_series=ret_series
                            best_BiasUpper=BiasUpper
                            best_UpperPosition=UpperPosition
                            best_BiasLower=BiasLower
                            best_LowerPosition=LowerPosition
                            best_period=period
            
    return bestret,bestret_series,\
        (best_BiasUpper,best_UpperPosition,best_BiasLower,best_LowerPosition,best_period)
if __name__ == '__main__':
    #從資料庫讀取小型台指歷史資料
    df_MXFR1=kbars.readKbarsFromDB('MXFR1')
    df_MXFR1=kbars.resampleKbars(df_MXFR1,period='1h')
    close=df_MXFR1['Close']
    high=df_MXFR1['High']
    low=df_MXFR1['Low']
    #選項:
    #'MACD'
    #'KD'
    #'RSI'
    #'BBAND'
    #'PriceChannel'
    #'Grid'
    target='PriceChannel'
    if(target=='MACD'):
        #最佳化Fast,Slow,Signal
        rangeFast=numpy.arange(2,100,1,dtype=int)
        rangeSlow=numpy.arange(2,100,1,dtype=int)
        rangeSignal=numpy.arange(2,100,1,dtype=int)
        bestret,bestret_series,parameters=OptimizeMACD(
                df_MXFR1,
                rangeFast,#=numpy.arange(2,100,1,dtype=int)
                rangeSlow,#=numpy.arange(2,100,1,dtype=int)
                rangeSignal#=numpy.arange(2,100,1,dtype=int)
                )
        print('MACD bestret:'+str(bestret))
        print('MACD MDD:'+str(backtesttool.calculateMDD(bestret_series)))
    if(target=='KD'):
        #最佳化fastk,slowk,slowd
        range_fastk=numpy.arange(2,100,1,dtype=int)
        range_slowk=numpy.arange(2,100,1,dtype=int)
        range_slowd=numpy.arange(2,100,1,dtype=int)
        bestret,bestret_series,parameters=OptimizeKD(
            df_MXFR1,
            range_fastk,
            range_slowk,
            range_slowd
            )
        print('KD bestret:'+str(bestret))
        print('KD MDD:'+str(backtesttool.calculateMDD(bestret_series)))        
    if(target=='RSI'):
        #最佳化period,longTH,shortTH
        range_period=numpy.arange(2,100,1,dtype=int)
        range_longTH=numpy.arange(0,100,1,dtype=int)
        range_shortTH=numpy.arange(0,100,1,dtype=int)
        bestret,bestret_series,parameters=OptimizeRSI(
            df_MXFR1,
            range_period,
            range_longTH,
            range_shortTH
            )
        print('RSI bestret:'+str(bestret))
        print('RSI MDD:'+str(backtesttool.calculateMDD(bestret_series)))        
    if(target=='BBAND'):
        #最佳化period,SmallStdDev,LargeStdDev
        range_period=numpy.arange(2,100,1,dtype=int)
        range_SmallStdDev=numpy.arange(0.5,5,0.5,dtype=float)
        range_LargeStdDev=numpy.arange(0.5,5,0.5,dtype=float)
        bestret,bestret_series,parameters=OptimizeBBAND(
            df_MXFR1,
            range_period,
            range_SmallStdDev,
            range_LargeStdDev
            )
        print('BBAND bestret:'+str(bestret))
        print('BBAND MDD:'+str(backtesttool.calculateMDD(bestret_series)))        
    if(target=='PriceChannel'):
        #最佳化period
        range_period=numpy.arange(2,1000,1,dtype=int)
        bestret,bestret_series,parameters=OptimizePriceChannel(
            df_MXFR1,
            range_period
            )
        print('PriceChannel bestret:'+str(bestret))
        print('PriceChannel MDD:'+str(backtesttool.calculateMDD(bestret_series)))        
    if(target=='Grid'):
        import yfinance as yf    
        tw = yf.Ticker("0052.tw")
        TW_hist = tw.history(period="5y")
        us = yf.Ticker("00662.tw")
        US_hist = us.history(period="5y")
        #兩邊歷史資料長度不一樣,取交集
        idx = numpy.intersect1d(TW_hist.index, US_hist.index)
        TW_hist = TW_hist.loc[idx]
        US_hist = US_hist.loc[idx]
       
        
        TW_open=TW_hist['Open']
        TW_close=TW_hist['Close']
        TW_high=TW_hist['High']
        TW_low=TW_hist['Low']
        
        US_open=US_hist['Open']
        US_close=US_hist['Close']
        US_high=US_hist['High']
        US_low=US_hist['Low']
        
        kbars = pd.DataFrame(\
            {'ts':TW_close.index\
            ,'Close':TW_close/US_close\
            ,'Open':TW_open/US_open\
            ,'High':TW_high/US_low\
            ,'Low':TW_low/US_high}).dropna() 
        #最佳化 BiasUpper,BiasLower,period
        range_BiasUpper=numpy.arange(1.0,2.0,0.1,dtype=float)
        range_UpperPosition=numpy.arange(0.1,0.2,0.1,dtype=float)        
        range_BiasLower=numpy.arange(0.5,1.0,0.1,dtype=float)
        range_LowerPosition=numpy.arange(0.9,1.0,0.1,dtype=float)
        range_period=numpy.arange(2,100,1,dtype=int)
        bestret,bestret_series,parameters=OptimizeGrid(
            kbars,
            range_BiasUpper,
            range_UpperPosition,
            range_BiasLower,
            range_LowerPosition,
            range_period
            )
        (best_BiasUpper,\
         best_UpperPosition,\
         best_BiasLower,\
         best_LowerPosition,\
         best_period)=parameters
        
        #最佳化 range_UpperPosition,range_LowerPosition,range_period
        range_BiasUpper=numpy.arange(best_BiasUpper,best_BiasUpper+0.1,0.1,dtype=float)
        range_UpperPosition=numpy.arange(0.1,0.5,0.1,dtype=float)        
        range_BiasLower=numpy.arange(best_BiasLower,best_BiasLower+0.1,0.1,dtype=float)
        range_LowerPosition=numpy.arange(0.5,1.0,0.1,dtype=float)
        range_period=numpy.arange(2,100,1,dtype=int)
        bestret,bestret_series,parameters=OptimizeGrid(
            kbars,
            range_BiasUpper,
            range_UpperPosition,
            range_BiasLower,
            range_LowerPosition,
            range_period
            )
        (best_BiasUpper,\
         best_UpperPosition,\
         best_BiasLower,\
         best_LowerPosition,\
         best_period)=parameters
            
        
        #最佳化 BiasUpper,BiasLower,range_period
        range_BiasUpper=numpy.arange(1.0,2.0,0.1,dtype=float)
        range_UpperPosition=numpy.arange(best_UpperPosition,best_UpperPosition+0.1,0.1,dtype=float)        
        range_BiasLower=numpy.arange(0.5,1.0,0.1,dtype=float)
        range_LowerPosition=numpy.arange(best_LowerPosition,best_LowerPosition+0.1,0.1,dtype=float)
        range_period=numpy.arange(2,100,1,dtype=int)
        bestret,bestret_series,parameters=OptimizeGrid(
            kbars,
            range_BiasUpper,
            range_UpperPosition,
            range_BiasLower,
            range_LowerPosition,
            range_period
            )
        
        
        ### 跨市網格交易報酬計算 ###    
        (best_BiasUpper\
        ,best_UpperPosition\
        ,best_BiasLower\
        ,best_LowerPosition\
        ,best_period)=parameters
        
        position=createGridSignal(kbars,
                         best_BiasUpper,
                         best_UpperPosition,
                         best_BiasLower,
                         best_LowerPosition,
                         best_period)
        buyTW=position
        buyUS=1.0-position
        
        retTW,retseriesTW=backtesttool.backtest_signal(TW_open,buyTW,tradecost=0.0000176)
        retUS,retseriesUS=backtesttool.backtest_signal(US_open,buyUS,tradecost=0.0000176)
        retseries=(retseriesTW-1.0)+(retseriesUS-1.0)+1.0
        prefixProfit=backtesttool.prefixProd(retseries)
        #plt.plot(buyTW,color='red')
        print('strategyMDD:',backtesttool.calculateMDD(retseries))
        print('USMDD:',backtesttool.calculateMDD_fromClose(US_close))
        print('TWMDD:',backtesttool.calculateMDD_fromClose(TW_close))
        print('strategyProfit:',prefixProfit.tolist()[-1]/prefixProfit.tolist()[0])
        print('USProfit:',US_close.tolist()[-1]/US_close.tolist()[0])
        print('TWProfit:',TW_close.tolist()[-1]/TW_close.tolist()[0])
        plt.plot(numpy.log10(
            backtesttool.prefixProd(retseries))
            ,color='green')
        plt.title('Grid Profit(log)')
        plt.show()
        plt.plot(numpy.log10(TW_close/TW_close[0])
            ,color='green')
        plt.title('TW Profit(log)')
        plt.show()
        plt.plot(numpy.log10(US_close/US_close[0])
            ,color='green')
        plt.title('US Profit(log)')
        plt.show()