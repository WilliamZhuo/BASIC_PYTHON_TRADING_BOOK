# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 21:47:24 2022

@author: William Zhuo
"""
import shioaji as sj
import pandas as pd
from time import sleep
import datetime
import sqlite3
###############################################
#取得0050和小台近月的合約
##############################################
def getContract(
        api
        ,name#='MXFR1'
        ,the_type#='future'
        ):
    if(the_type=='future'):
        return api.Contracts.Futures[name]
    elif(the_type=='stock'):
        return api.Contracts.Stocks[name]
    else:
        print('Un-implemented type in getContract')
def getFrontMonthContract(
        api
        ,futureID#='UDF'
        ,removeR1R2=False #回傳物件要用來抓報價的時候設False,物件要用來下單的時候設True
        ,daysSwitch=7):
    l=list(api.Contracts.Futures[futureID])
    #移除近月和次月,近月次月只能抓報價無法下單
    if(removeR1R2):
        for i in range(len(l)-1,-1,-1):
            #近月和次月
            if(l[i].code[3]=='R'):
                l.pop(i)
            else:
                #移除即將結算的合約,或者已結算的合約
                delivery_date=datetime.datetime.strptime(
                    l[i].delivery_date,'%Y/%m/%d').date()
                today=get_today()
                diffdays=(delivery_date-today).days
                if(diffdays<=max(daysSwitch,0)):
                    l.pop(i)
    len_l=len(l)
    min_delivery_month='99999999999'
    min_i=0
    min_id=0
    for i in range(0,len_l,1):
        if(l[i].code==futureID+'R1'):
            min_delivery_month=l[i].delivery_month
            min_i=i
            min_id=l[i].code
            break
        valA=int(l[i].delivery_month)
        valB=int(min_delivery_month)
        if(valA<valB):
            min_delivery_month=l[i].delivery_month
            min_i=i
            min_id=l[i].code
    ret=api.Contracts.Futures[min_id]
    return ret

#######################################
#用datetime取得兩年前/一年前/昨天的日期
#######################################
def get_today():
    return datetime.date.today()

def sub_N_Days(
        days#=1
        ,date=datetime.date.today()
        ):
    return date - datetime.timedelta(days)

def add_N_Days(
        days#=1
        ,date=datetime.date.today()
        ):
    return date + datetime.timedelta(days)


#######################################
#給定日期時間範圍，回傳1分k的dataframe
#######################################
def getKbars(
        api
        ,contract
        ,start#='2022-01-01'
        ,end#='2022-01-20'
        ,timeout=100000):
    def remove_illegal_time(df):
    #futures
        cond_Sat=~((df.index.weekday==5) * (df.index.hour>5))
        cond_Sun=df.index.weekday!=6
        cond_Mon=~((df.index.weekday==0) * (df.index.hour<8))
        df=df[cond_Sat*cond_Sun*cond_Mon]
        return df
    #取得kbars資料
    if(timeout>0):
        kbars = api.kbars(
            contract,
            start=start, 
            end=end,
            timeout=timeout)
    else:
        kbars = api.kbars(
            contract,
            start=start, 
            end=end)
        
    #把0050的tick轉成dataframe，並且印出最前面的資料
    df = pd.DataFrame({**kbars})#轉成dataframe
    df.index =pd.to_datetime(df.ts)
    df=df.groupby(df.index).first()
    df=df.drop(columns='ts')
    df.drop(df.tail(1).index,inplace=True)
    df=remove_illegal_time(df)
    sleep(1)
    return df

#######################################
#給定日期時間範圍，回傳ticks的dataframe
#######################################
def getTicks(
        api
        ,contract
        ,start#='2022-01-01'
        ,end#='2022-01-20'
        ,timeout=100000
        ,Enable_print=False):

    list_ticks=[]
    enddate= datetime.datetime.strptime(end, '%Y-%m-%d').date()
    day= datetime.datetime.strptime(start, '%Y-%m-%d').date()
    while(day!=enddate):
        #取得ticks
        if(timeout>0):
            ticks = api.ticks(
                contract=contract, 
                date=str(day),
                timeout=timeout
            )
        else:
            ticks = api.ticks(
                contract=contract, 
                date=str(day),
                timeout=timeout
            )
        df_ticks = pd.DataFrame({**ticks})#轉成dataframe
        df_ticks.index =pd.to_datetime(df_ticks.ts)
        df_ticks=df_ticks.groupby(df_ticks.index).first()
        list_ticks.append(df_ticks)
        #加一天
        day=day+datetime.timedelta(days=1)
        if(Enable_print):
            print(day)
        #CD 50 miliseconds,避免抓太快被永豐ban掉
        sleep(0.05)
    if(len(list_ticks)>0):
        df_ticks_concat = pd.concat(list_ticks)
        df_ticks_concat=df_ticks_concat.drop(columns='ts')
    else:
        df_ticks_concat=[]
    return df_ticks_concat
#########################################################
#檢查Table存在與否
###########################################################
def checkTableExist(
        dbname#='kbars.db'
        ,tablename#='\'MXFR1\''
        ):    
    exist=False
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()            
    tablename=tablename
    
    #get the count of tables with the name
    SQL_lan=''' SELECT * FROM sqlite_master WHERE type='table' AND name='''
    SQL_lan=SQL_lan+tablename
    cur.execute(SQL_lan)
    ret=cur.fetchall()
    #if the count is 1, then table exists
    if len(ret)>0 : 
        exist=True
    
    #close the connection
    conn.close()
    return exist
#######################################
#用來看最後一筆日期
############################################
def checkLastTs(
        dbname#='kbars.db'
        ,tablename#='\'MXFR1\''
        ): 
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()        
    cur.execute('SELECT * FROM '+
                tablename+' WHERE ts IN (SELECT max(ts) FROM '+
                tablename+')')
    ret=cur.fetchall()
    conn.close()
    return ret[0][0]

#######################################
#更新資料庫的kbars
############################################
def backFillKbars(
        api
        ,contractObj#=contract_MXFR1
        ,contractName#='MXFR1'
        ):
    today=get_today()
    two_years_ago = sub_N_Days(days=365*2)
    one_years_ago = sub_N_Days(days=365)
    yesterday = sub_N_Days(days=1)
    
    dbName='kbars.db' 
    #push kbars data to table
    name='\''+contractName+'\''
    MXFR1_exist=checkTableExist(dbname=dbName,tablename=name)
    conn = sqlite3.connect(dbName)
    #create table
    if(MXFR1_exist):
        ret=checkLastTs(dbname=dbName,tablename=contractName)
        lastdatetime=datetime.datetime.strptime(ret,'%Y-%m-%d %H:%M:%S')
        start=add_N_Days(date=lastdatetime.date(),days=1) #date of last data
        end=today
        if(start<end):
            #push start~end
            kbars=getKbars(api
                  ,contractObj
                  ,start=str(start)
                  ,end=str(end))
            kbars.to_sql(name=contractName
                         ,con= conn
                         ,if_exists='append'
                         ,index=True)
        else:
            pass
    else:
        kbars=getKbars(api
              ,contractObj
              ,start=str(two_years_ago)
              ,end=str(yesterday))
        
        #create table
        kbars.to_sql(name=contractName,con= conn, if_exists='replace', index=True) 
    conn.close()

#######################################
#更新資料庫的ticks
############################################
def backFillTicks(
        api
        ,contractObj#=contract_MXFR1
        ,contractName#='MXFR1'
        ):
    today=get_today()
    two_years_ago = sub_N_Days(days=365*2)
    one_years_ago = sub_N_Days(days=365)
    yesterday = sub_N_Days(days=1)
     
    dbName='ticks.db'  #這個應該放在function
    #push kbars data to table
    name='\''+contractName+'\''
    MXFR1_exist=checkTableExist(dbname=dbName,tablename=name)
    conn = sqlite3.connect(dbName)
    #create table
    if(MXFR1_exist):
        ret=checkLastTs(dbname=dbName,tablename=contractName)
        lastdatetime=datetime.datetime.strptime(ret,'%Y-%m-%d %H:%M:%S.%f')
        start=add_N_Days(date=lastdatetime.date(),days=1) #date of last data
        end=today
        if(start<end):
            ticks=getTicks(api
                  ,contractObj
                  ,start=str(start)
                  ,end=str(end)
                  ,Enable_print=True)
            ticks.to_sql(name=contractName
                         ,con= conn
                         ,if_exists='append'
                         ,index=True)    
        else:
            pass
    else:
        ticks=getTicks(api
                  ,contractObj
                  ,start=str(one_years_ago)
                  ,end=str(yesterday)
                  ,Enable_print=True)
        #create table
        ticks.to_sql(name=contractName,con= conn, if_exists='replace', index=True) 
    conn.close()

#寫成函數
def sjBarsToDf(sjBars):
    dfBars = pd.DataFrame({**sjBars})#轉成dataframe
    dfBars.index =pd.to_datetime(dfBars.ts)
    dfBars=dfBars.groupby(dfBars.index).first()
    return dfBars
def ticksTo1mkbars(ticks):
    period='1min'
    kbars_out = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
    kbars_out['Open'] = ticks['close'].resample(period).first() #區間第一筆資料為開盤(Open)
    kbars_out['High'] = ticks['close'].resample(period).max() #區間最大值為最高(High)
    kbars_out['Low'] = ticks['close'].resample(period).min() #區間最小值為最低(Low)
    kbars_out['Close'] = ticks['close'].resample(period).last() #區間最後一個值為收盤(Close)
    kbars_out['Volume'] = ticks['volume'].resample(period).sum() #區間所有成交量加總
    kbars_out=kbars_out.dropna()
    return kbars_out
def resampleKbars(kbars,period='1d'):
    #period:1m => 1 month
    #period:1min => 1 minute
    
    kbars_out = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
    kbars_out['Open'] = kbars['Open'].resample(period).first() #區間第一筆資料為開盤(Open)
    kbars_out['High'] = kbars['High'].resample(period).max() #區間最大值為最高(High)
    kbars_out['Low'] = kbars['Low'].resample(period).min() #區間最小值為最低(Low)
    kbars_out['Close'] = kbars['Close'].resample(period).last() #區間最後一個值為收盤(Close)
    kbars_out['Volume'] = kbars['Volume'].resample(period).sum() #區間所有成交量加總
    kbars_out=kbars_out.dropna()
    return kbars_out
##################################
#從資料庫讀取kbars
#########################################
def readKbarsFromDB(contractName):
    dbName='kbars.db' 
    conn = sqlite3.connect(dbName)
    df=pd.read_sql(
        'SELECT * FROM '+contractName
        ,conn)
    df.index=pd.DatetimeIndex(df['ts'])
    return df
##################################
#從資料庫讀取ticks
#########################################
def readTicksFromDB(contractName):
    dbName='ticks.db' 
    conn = sqlite3.connect(dbName)
    df=pd.read_sql(
        'SELECT * FROM '+contractName
        ,conn)
    df.index=pd.DatetimeIndex(df['ts'])
    return df