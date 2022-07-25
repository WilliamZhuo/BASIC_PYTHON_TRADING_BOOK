#########################################
#Ch6 均線交易機器人
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
import kbars
import talib
import threading, time
from threading import Thread, Lock

END_WEEKDAY=5 # Saturday
REBOOT_HOUR=6
ENABLE_TRADING_NIGHT=False
ENABLE_SEND_ORDER=True
ENABLE_SHORT=False
api=shioajiLogin(simulation=False)
contractName='PUF'
ContractCount=1 #口數
contractObj=kbars.getFrontMonthContract(api,contractName)
contractCode=contractObj.code
logging.basicConfig(filename='MAbotlog.log', level=logging.DEBUG)

def MABotBody():
    class MABot:
        parameters={'PeriodShort':160,\
             'PeriodLong':274}
        contract = contractObj    
        contractName = contractName    
    
    #########################################
    #6.1 計算策略目標部位
    ###########################################
        def UpdateMA(self):
            #獲得今天日期
            now = datetime.datetime.now()
            today=str(now.date())
            #用Shioaji下載kbars歷史資料和當日ticks資料
            #歷史資料使用90天,對短線交易應該夠用,需要的話可以再增加天數
            #要用日線交易的話可以直接呼叫yfinance
            thecontract=self.contract
            #30天大概1xx根小時線
            history=kbars.getKbars(api,thecontract,str(kbars.sub_N_Days(90)),today)
            ticks=kbars.getTicks(api,thecontract,today,str(kbars.add_N_Days(2)))
            if(len(ticks)>0):
                #把ticks資料和歷史資料重複的部分刪掉
                lasttime=history.index[-1]
                lasttime=lasttime+datetime.timedelta(seconds=1)
                ticks=ticks[ticks.index>lasttime]
                #ticks轉1m kbar資料
                today_1min=kbars.ticksTo1mkbars(ticks)
                #把歷史資料和當日資料結合在一起        
                kbars_1m=history.append(today_1min)
            else:
                kbars_1m=history
            #轉換成小時線
            df_kbars=kbars.resampleKbars(kbars_1m,period='1h')
            #計算長短均線
            close=df_kbars['Close']
            period_short=self.parameters['PeriodShort']
            period_long=self.parameters['PeriodLong']
            MA_short=talib.SMA(close,timeperiod=period_short)
            MA_long=talib.SMA(close,timeperiod=period_long)
            #計算買賣訊號,只做多不做空,避免除權息造成回測測不出來的虧損
            short=MA_short[-1]
            long=MA_long[-1]        
            s=str(datetime.datetime.now())
            s=s+'MA_short:'+str(short)
            logging.debug(s)        
            s=str(datetime.datetime.now())
            s=s+'MA_long:'+str(long)
            logging.debug(s)               
            if(ENABLE_SHORT):
                self.signal=int(short>long)-int(short<long)  
            else:
                self.signal=int(short>long)
            s=str(datetime.datetime.now())
            s=s+'signal:'+str(self.signal)
            logging.debug(s)   
            
    #########################################
    #6.2 抓取目前部位大小
    ###########################################
        def getPositions(self):
            api.update_status()
            portfolio = api.get_account_openposition(query_type='1', account=api.futopt_account)
            df_positions = pd.DataFrame(portfolio.data())     
            
            thecontract=self.contract
            codes=[]
            codeNames=[]
            months=[]
            buysells=[]
            volumes=[]
            l=len(df_positions)
            for i in range(0,l,1):
                onerow=df_positions.iloc[i]
                #針對沒部位的情況進行檢查
                if(len(onerow)==0):
                    continue
                #期貨商品代號
                code=onerow['Code']
                if(code[0:3]==thecontract.category):
                    codes.append(code)
                    #中文+月份 的商品名稱
                    codeName=onerow['CodeName']
                    codeNames.append(codeName)
                    #月份
                    tradeMonth=codeName.split(' ')[1]
                    months.append(tradeMonth)
                    #買進或賣出
                    buysell=onerow['OrderBS']
                    buysells.append(buysell)
                    #口數
                    volume=onerow['Volume']
                    volumes.append(volume)
                    
            #計算多單-空單
            len_v=len(volumes)
            netvolume=0
            for i in range(0,len_v,1):
                if(buysells[i]=='S'):
                    netvolume=round(netvolume-float(volumes[i]))
                else:
                    netvolume=round(netvolume+float(volumes[i]))
                    
            self.codes=codes
            self.codeNames=codeNames
            self.months=months
            self.buysells=buysells
            self.volumes=volumes
            self.netvolume=netvolume
            
        def calculateSharetarget(self,price):
    
            #紀錄目標部位(口數)
            self.shareTarget=ContractCount*self.signal
            #紀錄最新的成交價,雖然均線交易會用市價單,應該不需要
            self.price=price
    
    #########################################
    #6.3. 實際掛單
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
                self.calculateSharetarget(price=self.futurePrice)
                #######################################
                #4.掛單
                ############################################                
                self.sendOrders()
            except Exception as e: # work on python 3.x
                print('updateOrder Error Message: '+ str(e))
                
        def cancelOrders(self):
            api.update_status()
            #列出所有的訂單
            tradelist=api.list_trades()
            tradeCancel=[]
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
                cond2=thistrade.contract.category==contractName
                if(cond1 and cond2):
                    tradeCancel.append(thistrade)
            
            #實際取消訂單的部分
            for i in range(0,len(tradeCancel),1):
                api.update_status()
                api.cancel_order(trade=tradeCancel[i])
                    
        def sendOrders(self):
            #計算要掛多少口
            quantityTrade=self.shareTarget-self.netvolume  
            #確保掛單的量不會把交割款用完
            quantityTradeValid=abs(quantityTrade)>0
            thecontract=kbars.getFrontMonthContract(
                api,self.contractName,True)
            #這邊做掛單,前面做了掛單量==0股的特殊檢查
            if(quantityTradeValid):
                #產生買單物件
                if(quantityTrade>0):
                    order = api.Order(
                        price=self.futureBid,
                        quantity=quantityTrade,
                        action=shioaji.constant.Action.Buy,
                		price_type=shioaji.constant.FuturesPriceType.MKP,
                		order_type=shioaji.constant.TFTOrderType.IOC,   
                		octype = shioaji.constant.FuturesOCType.Auto,
                		account=api.futopt_account,
                    )    
                    s=str(datetime.datetime.now())
                    s=s+'buy order'
                    logging.debug(s)      
                #產生賣單物件
                else:
                    order = api.Order(
                        price=self.futureAsk,
                        quantity=abs(quantityTrade),
                        action=shioaji.constant.Action.Sell,
                		price_type=shioaji.constant.FuturesPriceType.MKP,
                		order_type=shioaji.constant.TFTOrderType.IOC,     
                		octype = shioaji.constant.FuturesOCType.Auto,
                		account=api.futopt_account,
                    )
                    s=str(datetime.datetime.now())
                    s=s+'sell order'
                    logging.debug(s)   
                #掛單
                if(ENABLE_SEND_ORDER):
                    trade = api.place_order(thecontract, order)       
    

    #成交價     
    snaprice= api.snapshots([api.Contracts.Futures[contractCode]])
    futurePrice=snaprice[0]['close']
    #最高買價
    futureBid=snaprice[0]['close']
    #最低賣價
    futureAsk=snaprice[0]['close']
    
    #創建交易機器人物件
    bot1=MABot()
               
    #告訴系統要訂閱
    #1.ticks資料(用來看成交價)
    #2.買賣價資料(最佳五檔)    
    
    api.quote.subscribe(\
        contractObj,\
        quote_type = shioaji.constant.QuoteType.Tick,\
        version = shioaji.constant.QuoteVersion.v1,\
    )
    api.quote.subscribe(\
        contractObj,\
        quote_type = shioaji.constant.QuoteType.BidAsk,\
        version = shioaji.constant.QuoteVersion.v1,\
    )
    
        
    #處理ticks即時資料更新的部分
    mutexPrice =Lock()
    from shioaji import BidAskSTKv1, Exchange,TickSTKv1
    @api.on_tick_stk_v1()
    def STKtick_callback(exchange: Exchange, tick:TickSTKv1):
        mutexPrice.acquire()
        futurePrice=float(tick['close'])
        mutexPrice.release()
    api.quote.set_on_tick_stk_v1_callback(STKtick_callback)
    
    #處理bidask即時資料更新的部分
    mutexBidAsk =Lock()
    @api.on_bidask_stk_v1()
    def STK_BidAsk_callback(exchange: Exchange, bidask:BidAskSTKv1):
        mutexBidAsk.acquire()           
        bidlist=[float(i) for i in bidask['bid_price']]
        asklist=[float(i) for i in bidask['ask_price']]
        futureBid=bidlist[0]
        futureAsk=asklist[0]
        mutexBidAsk.release()        
    api.quote.set_on_bidask_stk_v1_callback(STK_BidAsk_callback)
    
    @api.quote.on_event
    def event_callback(resp_code: int, event_code: int, info: str, event: str):
        print(f'Event code: {event_code} | Event: {event}')
    api.quote.set_event_callback(event_callback)
    
    
    #用來更新買賣訊號和下單的迴圈        
    while(1):
        current_time = time.time()
        cooldown=60
        time_to_sleep = cooldown - (current_time % cooldown)
        time.sleep(time_to_sleep)
        
        now = datetime.datetime.now()
        hour=now.hour
        minute=now.minute
        second=now.second
        cond_continue=False
        #以下是用小時線交易
        #只在整點零分時交易
        if(minute>0):
            cond_continue=True
        #日盤開盤特例
        if(minute==45) and(hour==8):
            cond_continue=False
            
        #夜盤開盤特例,其實不加這個也沒差,但這樣看起來比較對稱
        if(minute==0) and (hour==15):
            cond_continue=False
        
        #收盤時間
        if(hour>=5 and hour <8 ):
            cond_continue=True
        if(hour ==8  and minute<45):
            cond_continue=True
        if(hour==14):
            cond_continue=True
        if(hour ==13  and minute>45):
            cond_continue=True
            
        #夜盤交易時間
        if(not ENABLE_TRADING_NIGHT):
            if(hour>=15 or hour<=5):
                cond_continue=True
        
        #夜盤收盤取消掛單
        if(minute==0) and (hour==5):
            try:
                bot1.cancelOrders()
            except Exception as e:
                logging.error('jobs_per1min  Error Message A: '+ str(e))
            break
            
        #日盤收盤取消掛單
        if(hour==13 and minute==30):
            try:
                bot1.cancelOrders()
            except Exception as e:
                logging.error('jobs_per1min  Error Message A: '+ str(e))
            continue
        
        if(cond_continue):
            continue
        
        #處理成交價不在買賣價中間的狀況
        mutexPrice.acquire()
        mutexBidAsk.acquire()
        if(futurePrice>futureAsk) or (futurePrice<futureBid):
            futurePrice=(futureAsk+futureBid)/2
        bot1.futurePrice=futurePrice
        bot1.futureBid=futureBid
        bot1.futureAsk=futureAsk
        mutexPrice.release()
        mutexBidAsk.release()
        #更新買賣單
        bot1.updateOrder()


MABotBody()
import datetime
import time
while(1):         
    #check reboot once per minute
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
        MABotBody()
    if(END_WEEKDAY==weekday):
        break