# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 21:47:10 2022

@author: user
"""
import talib
import kbars
import ShioajiLogin
import matplotlib.pyplot as plt
import pandas as pd
import numpy
#########################################
#4.1 使用ta-lib製作均線訊號
###########################################
#畫均線
df_FXFR1=kbars.readKbarsFromDB('FXFR1')
df_MXFR1=kbars.readKbarsFromDB('MXFR1')
df_FXFR1=kbars.resampleKbars(df_FXFR1,'1h')
df_MXFR1=kbars.resampleKbars(df_MXFR1,'1h')
close_price=df_MXFR1['Close']
ma100=talib.EMA(close_price,100)
plt.plot(close_price,color='green')
plt.plot(ma100,color='red')
plt.title('Close data and moving average')
plt.show()  

#長短均線交叉的買賣訊號, 短均線大於長均買進, 短均線小於長均線賣出
#當短均週期設成1的時候就等於前面的收盤價和均線交叉的交易系統
ma50=talib.EMA(close_price,50)
BuySignal=ma50>ma100
print('Buysignal content:')
print(BuySignal)
plt.plot(ma50,color='red')
plt.plot(ma100,color='blue')
plt.title('ma50 vs ma100')
plt.show()  

########################################
#4.2 計算策略的投資報酬率
###############################
def period_profit(openprice,begin=0,end=10):
    #用來確認沒有出現開盤價為零的狀況
    if(openprice[begin]==0):
        print('div0')
    #買進持有的報酬=最後一天的開盤價/第一天的開盤價
    return (openprice[end]-openprice[begin])/openprice[begin]

#######################################
#4.2.1.計算買進持有的投資報酬率買進持有報酬率
######################################
open_price=df_MXFR1['Open']
profit=period_profit \
      (open_price \
        ,begin=0 \
        ,end=open_price.size-1)
print('買進持有報酬率:',profit)


#####################################
#4.2.2.計算均線訊號的投資報酬率
####################################
#小台成本
#價差:(買賣價差/2)/一口小台的金額
G_spread=3.6280082234853065666948845084049e-4
#交易稅:交易稅/一口小台的金額
G_tax=4.4109538687741224039698584818967e-5
#手續費:手續費/一口小台的金額
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

retStrategy,ret_series=backtest_signal(
        open_price
        ,BuySignal
        ,tradecost=G_tradecost
        ,sizing=1.0)
print('均線策略報酬率:',retStrategy)

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
MDD=calculateMDD(ret_series)
print('均線MDD:',MDD)
plt.plot(prefixProd(ret_series),color='green')
plt.title('Strategy profit')
plt.show()
plt.plot(numpy.log10(prefixProd(ret_series)),color='green')
plt.title('Strategy profit(log)')
plt.show()

HoldSignal=BuySignal.copy()
HoldSignal[:]=1
retStrategyHold,ret_seriesHold=backtest_signal(
        open_price
        ,HoldSignal
        ,tradecost=G_tradecost
        ,sizing=1.0)
MDD=calculateMDD(ret_seriesHold)
print('買進持有報酬率:',retStrategyHold)
print('買進持有MDD:',MDD)
plt.plot(numpy.log10(prefixProd(ret_seriesHold)),color='green')
plt.title('Hold profit(log)')
plt.show()

###########################################
#4.2.3.計算兩檔商品做成投資組合的報酬率
############################################
#a.選取時間範圍重複的資料
begin_time=min(df_FXFR1.index[0],df_MXFR1.index[0])
begin_time_s=str(begin_time)
df_FXFR1=df_FXFR1[begin_time_s:]
df_MXFR1=df_MXFR1[begin_time_s:]

#b.取出開盤收盤價
open_MXF=df_MXFR1['Open']
close_MXF=df_MXFR1['Close']
open_FXF=df_FXFR1['Open']
close_FXF=df_FXFR1['Close']

#c.計算買賣訊號
ma_FXF_50=talib.EMA(close_FXF,50)
ma_FXF_100=talib.EMA(close_FXF,100)
BuySignal_FXF=ma_FXF_50>ma_FXF_100
ma_MXF_50=talib.EMA(close_MXF,50)
ma_MXF_100=talib.EMA(close_MXF,100)
BuySignal_MXF=ma_MXF_50>ma_MXF_100

retStrategy_MXF,ret_series_MXF=backtest_signal(
        open_MXF
        ,BuySignal_MXF
        ,tradecost=G_tradecost
        ,sizing=0.5)
retStrategy_FXF,ret_series_FXF=backtest_signal(
        open_FXF
        ,BuySignal_FXF
        ,tradecost=G_tradecost
        ,sizing=0.5)
ret_series_MIX=(ret_series_MXF-1)+(ret_series_FXF-1)+1
retStrategy_MIX=retStrategy_MXF+retStrategy
MDD=calculateMDD(ret_series_MIX)
print('混合兩檔商品用均線交易的報酬率:',retStrategy_MIX)
print('混合兩檔商品用均線交易的MDD:',MDD)

plt.plot(numpy.log10(prefixProd(ret_series_MXF)),color='green')
plt.title('MXF profit(log)')
plt.show()
plt.plot(numpy.log10(prefixProd(ret_series_FXF)),color='green')
plt.title('FXF profit(log)')
plt.show()
plt.plot(numpy.log10(prefixProd(ret_series_MIX)),color='green')
plt.title('Portfolio profit(log)')
plt.show()
############################################
#4.3 均線訊號最佳化
###################################

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
ret,ret_series,bestperiod=\
    optimizeMA(df_MXFR1,\
               numpy.arange(2,100,1,dtype=int),\
               numpy.arange(2,100,1,dtype=int))

MDD=calculateMDD(ret_series)
print('最佳化的報酬率:',ret)
print('最佳化的MDD:',MDD)
        
plt.plot(numpy.log10(prefixProd(ret_series)),color='green')
plt.title('Profit after optimizing(log)')
plt.show()
############################################
#4.4.過擬合問題
###################################
#分出訓練集和測試集，四個月前的資料當訓練集，四個月內的資料當測試集
date=kbars.sub_N_Days(
        days=120
        ,date=df_MXFR1.index[-1]
        )
df_trainset=df_MXFR1[df_MXFR1.index<=date]
df_testset=df_MXFR1[df_MXFR1.index>date]
#用訓練集跑最佳化
ret_train,ret_series_train,bestperiod_train \
    =optimizeMA(df_trainset,\
                numpy.arange(2,100,1,dtype=int),\
               numpy.arange(2,100,1,dtype=int))

#用測試集測試最近四個月的績效
ma_short=talib.EMA(df_testset['Close'],bestperiod[1])
ma_long=talib.EMA(df_testset['Close'],bestperiod[0])
buy_signal=ma_short>ma_long
retStrategy_Outsample,ret_series_Outsample=backtest_signal(
    df_testset['Open']
    ,buy_signal
    ,tradecost=G_tradecost
    ,sizing=1.0)
#前面沒有分訓練集測試集的三個月內報酬
ret_insample=ret_series.tail(ret_series_Outsample.size)
ret_insample=ret_insample.reset_index(drop=True)

plt.plot(prefixProd(ret_insample),color='green')
plt.plot(prefixProd(ret_series_Outsample),color='red')
plt.show()  
