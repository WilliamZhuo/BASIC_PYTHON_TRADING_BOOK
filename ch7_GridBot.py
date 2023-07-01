#########################################
#Ch7 網格交易機器人
###########################################

import pandas as pd
import shioaji
import shioaji.order as stOrder
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import ShioajiLogin
from  ShioajiLogin import shioajiLogin
import os
import logging
import pickle
import datetime
import threading, time
from threading import Thread, Lock
from shioaji import BidAskFOPv1, Exchange
from shioaji import TickFOPv1, Exchange

REBOOT_HOUR=16
END_WEEKDAY=4 # Friday
api=shioajiLogin(simulation=False)
initmoney=0
g_settlement=0
g_upperid='0052'
g_lowerid='00662'
trigger=2000 #最低交易金額門檻,避免交易金額太小,錢被手續費低消吃光光
ENABLE_PREMARKET=True
ans=''
logging.basicConfig(filename='gridbotlog.log', level=logging.DEBUG)
msglist=[]

def GridbotBody():
    class GridBot:
        upperid=g_upperid
        lowerid=g_lowerid
        
        parameters={'BiasUpperLimit':1.0,\
             'UpperLimitPosition':0.4,\
             'BiasLowerLimit':0.85,\
             'LowerLimitPosition':0.9,\
             'BiasPeriod':81}
        year=0
        month=0
        day=0
        
        stockPrice={}
        stockBid={}
        stockAsk={}        
        upperprice=0
        uppershare=0
        lowerprice=0
        lowershare=0
        uppershareTarget=0
        lowershareTarget=0
        money=0
        contractUpper = api.Contracts.Stocks[upperid]
        contractLower = api.Contracts.Stocks[lowerid]
            
    #########################################
    #7.1 計算策略目標部位(百分比)
    ###########################################
        def UpdateMA(self):
            now = datetime.datetime.now()
            #如果有換日就更新均線,或者第一次呼叫的時候也會更新均線
            if(now.year!=self.year or now.month!= self.month or  now.day!=self.day):
                #從Yfinance抓取資料
                upper = yf.Ticker(self.upperid+".tw")
                upper_hist = upper.history(period="3mo")
                #計算均線
                period=self.parameters['BiasPeriod']       
                upper_close=upper_hist['Close']
                #1.如果是做 股票 / TWD 的網格那就只要股票價格取平均
                #2.如果是做 股票A / 股票B 的相對價值網格那就需要
                #先計算 股票A / 股票B 的收盤價，再取平均
                if(self.lowerid!='Cash'):                
                    lower = yf.Ticker(self.lowerid+".tw")
                    lower_hist = lower.history(period="3mo")
                    lower_close=lower_hist['Close']
                    close=(upper_close/lower_close).dropna()
                else:
                    close=upper_close.dropna()
                self.MA=close[-period:].sum()/period
                self.year=now.year 
                self.month=now.month 
                self.day=now.day
                s=str(datetime.datetime.now())
                s=s+'MA:'+str(self.MA)
                logging.debug(s)   
                
    #########################################
    #7.2 抓取庫存部位大小
    ###########################################
        def getPositions(self):
            api.update_status()
            portfolio=api.list_positions(unit=shioaji.constant.Unit.Share)
            #df_positions = pd.DataFrame(portfolio)
            df_positions = pd.DataFrame(s.__dict__ for s in portfolio)
            quantity=df_positions.loc[df_positions['code'] == self.upperid]['quantity']
            if(quantity.size==0):
                self.uppershare=0
            else:
                self.uppershare=int(quantity)
            if(self.lowerid!='Cash'):
                quantity=df_positions.loc[df_positions['code'] == self.lowerid]['quantity']
                if(quantity.size==0):
                    self.lowershare=0
                else:
                    self.lowershare=int(quantity)
        
        def calculateSharetarget(self,upperprice,lowerprice):
            #計算目標部位百分比
            shareTarget=self.calculateGrid(upperprice,lowerprice)
            
            self.money=initmoney+g_settlement            
            uppershare=self.uppershare
            lowershare=self.lowershare
            money=self.money
    
            #計算機器人裡面有多少資產(現金+股票)
            capitalInBot=money+uppershare*upperprice+lowershare*lowerprice
    
            #計算目標部位(股數)
            uppershareTarget=int(shareTarget*capitalInBot/upperprice)
            lowershareTarget=int((1.0-shareTarget)*capitalInBot/lowerprice)

            #紀錄目標部位(股數)
            self.uppershareTarget=uppershareTarget
            self.lowershareTarget=lowershareTarget
            self.upperprice=upperprice
            self.lowerprice=lowerprice
            logging.debug('uppershareTarget:'+str(uppershareTarget))
            logging.debug('lowershareTarget:'+str(lowershareTarget))
            logging.debug('upperprice:'+str(upperprice))
            logging.debug('lowerprice:'+str(lowerprice))
    
        def calculateGrid(self,upperprice,lowerprice):
            MA=self.MA        
            #計算目標部位百分比     
            BiasUpperLimit=self.parameters['BiasUpperLimit']
            UpperLimitPosition=self.parameters['UpperLimitPosition']
            BiasLowerLimit=self.parameters['BiasLowerLimit']
            LowerLimitPosition=self.parameters['LowerLimitPosition']
            BiasPeriod=self.parameters['BiasPeriod']
            
            Bias=(upperprice/lowerprice)/MA               
            shareTarget=(Bias-BiasLowerLimit)/(BiasUpperLimit-BiasLowerLimit)
            shareTarget=shareTarget*(UpperLimitPosition-LowerLimitPosition)+LowerLimitPosition
            shareTarget=max(shareTarget,UpperLimitPosition)
            shareTarget=min(shareTarget,LowerLimitPosition)
            return shareTarget
    #########################################
    #7.3. 實際掛單
    ###########################################    
        def updateOrder(self):
            try:
                #################################
                #0.更新日均線資料
                #################################
                self.UpdateMA()
                #################################
                #1.刪除掛單
                ############################
                self.cancelOrders()
                #################################
                #2.更新庫存
                ############################
                self.getPositions()
                ####################################
                #3.更新目標部位
                ##############################
                self.calculateSharetarget(upperprice=self.stockPrice[g_upperid]\
                                          ,lowerprice=self.stockPrice[g_lowerid])
                #######################################
                #4.掛單
                ############################################                
                self.sendOrders()
            except Exception as e: # work on python 3.x
                logging.debug(str(datetime.datetime.now())+' updateOrder Error Message: '+ str(e))

        def cancelOrders(self):
            api.update_status()
            #列出所有的訂單
            tradelist=api.list_trades()
            tradeUpper=[]
            tradeLower=[]
            for i in range(0,len(tradelist),1):
                thistrade=tradelist[i]
                thisstatus=thistrade.status.status
                #單子的狀態太多種,先列出來
                isCancelled=( thisstatus == stOrder.Status.Cancelled)
                isFailed=( thisstatus == stOrder.Status.Failed)
                isFilled=( thisstatus ==  stOrder.Status.Filled)
                isInactive=( thisstatus ==  stOrder.Status.Inactive)
                isPartFilled=( thisstatus ==  stOrder.Status.PartFilled)
                isPendingSubmit=( thisstatus ==  stOrder.Status.PendingSubmit)
                isPreSubmitted=( thisstatus ==  stOrder.Status.PreSubmitted)            
                isSubmitted=( thisstatus ==  stOrder.Status.Submitted)
                
                #把交易股票種類跟交易機器人一樣的有效訂單取消
                cond1=not(\
                          isCancelled\
                          or  isFailed\
                          or  isFilled\
                          ) 
                cond2=thistrade.contract.code==self.upperid
                cond3=thistrade.contract.code==self.lowerid
                cond4=self.lowerid!='Cash'
                if(cond1 and cond2):
                    tradeUpper.append(thistrade)
                if(cond1 and cond3 and cond4):
                    tradeLower.append(thistrade)
            
            #實際取消訂單的部分
            for i in range(0,len(tradeUpper),1):
                api.update_status()
                api.cancel_order(trade=tradeUpper[i])
            if(self.lowerid!='Cash'):
                for i in range(0,len(tradeLower),1):
                    api.update_status()
                    api.cancel_order(trade=tradeLower[i])
                    
        def sendOrders(self):
            #計算要掛多少股
            quantityUpper=self.uppershareTarget-self.uppershare
            quantityLower=self.lowershareTarget-self.lowershare            
            quantityUpper=min(quantityUpper,999)
            quantityUpper=max(quantityUpper,-999)
            quantityLower=min(quantityLower,999)
            quantityLower=max(quantityLower,-999)            
            #確保掛單的量不會把交割款用完
            code=self.upperid
            money=self.money
            if(quantityUpper>0):
                cost=self.stockBid[code]*quantityUpper
                if(money<cost):
                    quantityUpper=max(int(money/self.stockBid[code]),0)
            quantityUpperValid=abs(quantityUpper)>0
            #這邊做掛單,前面做了掛單量==0股的特殊檢查
            if(quantityUpperValid):
                #產生買單物件
                if(quantityUpper>0):
                    order = api.Order(
                        price=self.stockBid[code],
                        quantity=quantityUpper,
                        action=shioaji.constant.Action.Buy,
                        price_type=shioaji.constant.StockPriceType.LMT,
                        order_type=shioaji.constant.OrderType.ROD,     
                        order_lot=shioaji.constant.StockOrderLot.IntradayOdd, 
                        account=api.stock_account,
                    )
                #產生賣單物件
                else:
                    order = api.Order(
                        price=self.stockAsk[code],
                        quantity=abs(quantityUpper),
                        action=shioaji.constant.Action.Sell,
                        price_type=shioaji.constant.StockPriceType.LMT,
                        order_type=shioaji.constant.OrderType.ROD,
                        order_lot=shioaji.constant.StockOrderLot.IntradayOdd, 
                        account=api.stock_account,
                    )
                #在交易金額大於trigger的時候掛單
                if(abs(quantityUpper)*self.stockPrice[code]>=trigger):    
                    contract = api.Contracts.Stocks[code]
                    cost=self.stockBid[code]*quantityUpper
                    #掛買單的話,要把交割款扣掉買單的金額
                    #避免後面掛分母的單的時候交割款不夠
                    if(quantityUpper>0):
                        if(money>cost):
                            money=money-cost #local money int
                            trade = api.place_order(contract, order)
                            s=str(datetime.datetime.now())
                            s=s+'buy upper'                
                            logging.debug(s)
                    else:
                        trade = api.place_order(contract, order) 
                        s=str(datetime.datetime.now())
                        s=s+'sell upper'                
                        logging.debug(s)
            #這邊開始掛分母的單
            #首先確保掛單的量不會把交割款用完
            code=self.lowerid
            if(quantityLower>0):
                cost=self.stockBid[code]*quantityLower
                if(money<cost):
                    quantityLower=max(int(money/self.stockBid[code]),0)
            quantityLowerValid=abs(quantityLower)>0
            #這邊做掛單,前面做了掛單量==0股的特殊檢查
            if(self.lowerid!='Cash' and quantityLowerValid):
                #產生買單物件
                if(quantityLower>0):
                    order = api.Order(
                        price=self.stockBid[code],
                        quantity=quantityLower,
                        action=shioaji.constant.Action.Buy,
                        price_type=shioaji.constant.StockPriceType.LMT,
                        order_type=shioaji.constant.OrderType.ROD,     
                        order_lot=shioaji.constant.StockOrderLot.IntradayOdd, 
                        account=api.stock_account,
                    )
                #產生賣單物件
                else:
                    order = api.Order(
                        price=self.stockAsk[code],
                        quantity=-quantityLower,
                        action=shioaji.constant.Action.Sell,
                        price_type=shioaji.constant.StockPriceType.LMT,
                        order_type=shioaji.constant.OrderType.ROD,     
                        order_lot=shioaji.constant.StockOrderLot.IntradayOdd, 
                        account=api.stock_account,
                    )
                #在交易金額大於trigger的時候掛單
                if(abs(quantityLower)*self.stockPrice[code]>=trigger):    
                    contract = api.Contracts.Stocks[code]
                    cost=self.stockBid[code]*quantityLower
                    if(quantityLower>0):
                        trade = api.place_order(contract, order)
                        s=str(datetime.datetime.now())
                        s=s+'buy lower'
                        logging.debug(s)
                    else:
                        trade = api.place_order(contract, order)
                        s=str(datetime.datetime.now())
                        s='sell lower'
                        logging.debug(s)
           
    #成交價             
    snaprice={}
    snaprice[g_upperid] = api.snapshots([api.Contracts.Stocks[g_upperid]])
    snaprice[g_lowerid] = api.snapshots([api.Contracts.Stocks[g_lowerid]])
    stockPrice={g_upperid:snaprice[g_upperid][0]['close'],\
                g_lowerid:snaprice[g_lowerid][0]['close']}
    #最高買價
    stockBid={g_upperid:snaprice[g_upperid][0]['close'],\
              g_lowerid:snaprice[g_lowerid][0]['close']}
    #最低賣價
    stockAsk={g_upperid:snaprice[g_upperid][0]['close'],\
              g_lowerid:snaprice[g_lowerid][0]['close']}
    
    #創建交易機器人物件
    bot1=GridBot()
    #更新交易機器人裡的股票數量
    bot1.getPositions()
    
    #把資料寫到硬碟和從硬碟讀取資料用的函數 
    def pickle_dump(filename,obj):
        with open(filename, 'wb') as handle:
            pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)        
    def pickle_read(filename):
        with open(filename, 'rb') as handle:
            return pickle.load(handle)
    try:
        initmoney=pickle_read('money.p')
    except:
        initmoney=0
    totalcapital=initmoney+stockPrice[g_upperid]*bot1.uppershare+stockPrice[g_lowerid]*bot1.lowershare
    #更新Trigger大小,在資產很多的時候固定2000會有點少
    trigger=max(2000,totalcapital*0.005)
    print("money:"+str(initmoney))
    print("upper:"+str(stockPrice[g_upperid]*bot1.uppershare))
    print("lower:"+str(stockPrice[g_lowerid]*bot1.lowershare))
    print("totalcapital is "+str(totalcapital))
    #決定要不要新增更多資金進交易機器人裡
    global ans
    if(ans==''):
        ans=input("perform withdraw or deposit(y/n):\n")
        if(ans=='y'):
            amount=input("withdraw or deposit amount(>0:deposit,<0:withdraw):\n")
            initmoney=initmoney+int(amount)
    bot1.money=initmoney
    
    #用來處理多線程的變數,在更新價格和訂單成交回報時會用到
    mutexDict ={g_upperid:Lock(),g_lowerid:Lock()}
    mutexBidAskDict ={g_upperid:Lock(),g_lowerid:Lock()}    
    mutexmsg =Lock()
    mutexstat =Lock()
    mutexgSettle =Lock()
    statlist=[]
    
    #處理訂單成交的狀況,用來更新交割款
    def place_cb(stat, msg):
        if "trade_id" in msg:
            code=msg['code']
            isUpper= (code==g_upperid)
            isLower= (code==g_lowerid)
            if(isUpper or isLower):
                global g_settlement
                action=msg['action']
                price=msg['price']
                quantity=msg['quantity']
                mutexgSettle.acquire()
                if(action=='Buy'):
                    g_settlement-=price*quantity
                elif(action=='Sell'):
                    g_settlement+=price*quantity
                else:
                    pass
                mutexgSettle.release()
        mutexmsg.acquire()
        try:
            msglist.append(msg)
        except Exception as e: # work on python 3.x
            logging.error('place_cb  Error Message A: '+ str(e))
        mutexmsg.release()
        mutexstat.acquire()
        try:
            statlist.append(stat)
        except Exception as e: # work on python 3.x
            logging.error('place_cb  Error Message B: '+ str(e))
        mutexstat.release()
    
    api.set_order_callback(place_cb)
       
    
    #告訴系統要訂閱
    #1.ticks資料(用來看成交價)
    #2.買賣價資料
    contract_Upper = api.Contracts.Stocks[g_upperid]
    contract_Lower = api.Contracts.Stocks[g_lowerid]
    
    api.quote.subscribe(\
        contract_Upper,\
        quote_type = shioaji.constant.QuoteType.Tick,\
        version = shioaji.constant.QuoteVersion.v1,\
        intraday_odd = True
    )
    api.quote.subscribe(\
        contract_Upper,\
        quote_type = shioaji.constant.QuoteType.BidAsk,\
        version = shioaji.constant.QuoteVersion.v1,\
        intraday_odd=True
    )
    
    api.quote.subscribe(\
        contract_Lower,\
        quote_type = shioaji.constant.QuoteType.Tick,\
        version = shioaji.constant.QuoteVersion.v1,\
        intraday_odd = True
    )
    api.quote.subscribe(\
        contract_Lower,\
        quote_type = shioaji.constant.QuoteType.BidAsk,\
        version = shioaji.constant.QuoteVersion.v1,\
        intraday_odd=True
    )    
        
    #處理ticks即時資料更新的部分
    from shioaji import BidAskSTKv1, Exchange,TickSTKv1
    @api.on_tick_stk_v1()
    def STKtick_callback(exchange: Exchange, tick:TickSTKv1):
        code=tick['code']
        mutexDict[code].acquire()
        stockPrice[code]=float(tick['close'])
        mutexDict[code].release()
    api.quote.set_on_tick_stk_v1_callback(STKtick_callback)
    
    #處理bidask即時資料更新的部分
    @api.on_bidask_stk_v1()
    def STK_BidAsk_callback(exchange: Exchange, bidask:BidAskSTKv1):
        code=bidask['code']
        mutexBidAskDict[code].acquire()
        bidlist=[float(i) for i in bidask['bid_price']]
        asklist=[float(i) for i in bidask['ask_price']]
        stockBid[code]=bidlist[0]
        stockAsk[code]=asklist[0]
        mutexBidAskDict[code].release()
    api.quote.set_on_bidask_stk_v1_callback(STK_BidAsk_callback)
    
    @api.quote.on_event
    def event_callback(resp_code: int, event_code: int, info: str, event: str):
        s=str(datetime.datetime.now())
        s=s+f'Event code: {event_code} | Event: {event}'
        logging.debug(s)
        #print(f'Event code: {event_code} | Event: {event}')
    api.quote.set_event_callback(event_callback)
    
    #用來更新買賣訊號和下單的迴圈        
    while(1):
        current_time = time.time()
        cooldown=60
        #sleep to n seconds 
        til_second=20
        time_to_sleep = til_second + cooldown - (current_time % cooldown)
        time.sleep(time_to_sleep)
        
        now = datetime.datetime.now()
        hour=now.hour
        minute=now.minute
        second=now.second
        #modify/send order
        #1.every 3 minutes
        #2.between 15 second to 45 second
        if(minute%3!=0):
            continue
        if(hour==13 and minute>20):
            try:
                bot1.cancelOrders()
            except Exception as e:
                logging.error('jobs_per1min  Error Message A: '+ str(e))
            continue
        if(hour>=14 and hour<=15):
            pickle_dump( "money.p",bot1.money)
            break
        if(not ENABLE_PREMARKET):
            if(hour<9 or (hour>13)):
                continue
            
        #處理成交價不在買賣價中間的狀況
        mutexDict[g_upperid].acquire()
        mutexDict[g_lowerid].acquire()
        mutexBidAskDict[g_upperid].acquire()
        mutexBidAskDict[g_lowerid].acquire()
        if(stockPrice[g_upperid]>stockAsk[g_upperid] or stockPrice[g_upperid]<stockBid[g_upperid]):
            stockPrice[g_upperid]=(stockAsk[g_upperid]+stockBid[g_upperid])/2
        if(stockPrice[g_lowerid]>stockAsk[g_lowerid] or stockPrice[g_lowerid]<stockBid[g_lowerid]):
            stockPrice[g_lowerid]=(stockAsk[g_lowerid]+stockBid[g_lowerid])/2
        bot1.stockPrice[g_upperid]=stockPrice[g_upperid]
        bot1.stockPrice[g_lowerid]=stockPrice[g_lowerid]
        bot1.stockBid[g_upperid]=stockBid[g_upperid]
        bot1.stockBid[g_lowerid]=stockBid[g_lowerid]
        bot1.stockAsk[g_upperid]=stockAsk[g_upperid]
        bot1.stockAsk[g_lowerid]=stockAsk[g_lowerid]
        mutexDict[g_lowerid].release()
        mutexDict[g_upperid].release()
        mutexBidAskDict[g_lowerid].release()
        mutexBidAskDict[g_upperid].release()   
        #更新買賣單
        bot1.updateOrder()

GridbotBody()
import datetime
import time
while(1):         
    #check reboot once per 30 minutes
    current_time = time.time()
    cooldown=60*30
    time_to_sleep = cooldown - (current_time % cooldown)
    time.sleep(time_to_sleep)
    
    #check weekday and hour
    now = datetime.datetime.now()
    hour=now.hour
    weekday= now.weekday()
    print('hour:',hour)
    if(hour==REBOOT_HOUR):
        print('reboot bot')
        api.logout()
        api=ShioajiLogin.shioajiLogin(simulation=False)
        GridbotBody()
    if(END_WEEKDAY==weekday):
        break