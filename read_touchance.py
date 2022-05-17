import time
from tcoreapi_mq import * 
import tcoreapi_mq
import threading
import pandas as pd
import datetime
from dateutil import tz
g_QuoteZMQ = None
g_QuoteSession = ""

#實時行情回補
def OnRealTimeQuote(symbol):
    print("商品：", symbol["Symbol"], "成交價:",symbol["TradingPrice"], "開:", symbol["OpeningPrice"], "高:", symbol["HighPrice"], "低:", symbol["LowPrice"])

#行情消息接收
def quote_sub_th(obj,sub_port,filter = ""):
    socket_sub = obj.context.socket(zmq.SUB)
    #socket_sub.RCVTIMEO=7000   #ZMQ超時設定
    socket_sub.connect("tcp://127.0.0.1:%s" % sub_port)
    socket_sub.setsockopt_string(zmq.SUBSCRIBE,filter)
    while(True):
        message = (socket_sub.recv()[:-1]).decode("utf-8")
        index =  re.search(":",message).span()[1]  # filter
        message = message[index:]
        message = json.loads(message)
        #for message in messages:
        if(message["DataType"]=="REALTIME"):
            OnRealTimeQuote(message["Quote"])
        elif(message["DataType"]=="GREEKS"):
            OnGreeks(message["Quote"])
        elif(message["DataType"]=="TICKS" or message["DataType"]=="1K" or message["DataType"]=="DK" ):
            #print("@@@@@@@@@@@@@@@@@@@@@@@",message)
            strQryIndex = ""
            while(True):
                s_history = obj.GetHistory(g_QuoteSession, message["Symbol"], message["DataType"], message["StartTime"], message["EndTime"], strQryIndex)
                historyData = s_history["HisData"]
                if len(historyData) == 0:
                    break

                last = ""
                for data in historyData:
                    last = data
                    #print("歷史行情：Time:%s, Volume:%s, QryIndex:%s" % (data["Time"], data["Volume"], data["QryIndex"]))
                
                strQryIndex = last["QryIndex"]                    
    return


def HisDataToDF(HisData):    
    #UTC+0 to UTC+8
# https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Taipei')
    #HisData to dataframe, and turn index to datetime
    df=pd.DataFrame(HisData)
    row=HisData[0]
    df_date=df['Date'].tolist()
    df_time=df['Time'].tolist()
    l=[]
    for i in range(0,len(df_time),1):
        date=df_date[i]
        time=df_time[i]
        if(len(time)==4):
            time='00'+time
        elif(len(time)==5):
            time='0'+time
        date_obj = datetime.datetime.strptime(date, '%Y%m%d')
        time_obj = datetime.datetime.strptime(time, '%H%M%S')
        date_time_obj=datetime.datetime.combine(date_obj.date(), 
                                  time_obj.time())
        date_time_obj = date_time_obj.replace(tzinfo=from_zone)        
        date_time_obj = date_time_obj.astimezone(to_zone)
        
        l.append(date_time_obj)
    df.index=l
    return df
def read_data_to_df(contractName,#'FITX'
         #time:YYYYMMDDHHmm 年/月/日/時/分
         StrTim,#開始時間,ex:'2021031600' 
         EndTim,#結束時間,ex:'2021031700'
         ):

    global g_QuoteZMQ
    global g_QuoteSession

    #登入(與 TOUCHANCE zmq 連線用，不可改)
    g_QuoteZMQ = QuoteAPI("ZMQ","8076c9867a372d2a9a814ae710c256e2")
    q_data = g_QuoteZMQ.Connect("51237")
    #print("q_data=",q_data)

    if q_data["Success"] != "OK":
        #print("[quote]connection failed")
        return

    g_QuoteSession = q_data["SessionKey"]


    #查詢指定合约訊息
    quoteSymbol = "TC.F.TWF."+contractName+".HOT"
    #print("查詢指定合約：",g_QuoteZMQ.QueryInstrumentInfo(g_QuoteSession, quoteSymbol))
    #查詢指定類型合約列表
    #期貨：Fut
    #期權：Opt
    #證券：Sto
    #print("查詢合約：",g_QuoteZMQ.QueryAllInstrumentInfo(g_QuoteSession,"Fut"))

#####################################################################行情################################################
    #建立一個行情線程
    t2 = threading.Thread(target = quote_sub_th,args=(g_QuoteZMQ,q_data["SubPort"],))
    t2.start()

    #資料週期
    type = "1K"
    #資料頁數
    QryInd = '0'

    #訂閱歷史資料
    SubHis = g_QuoteZMQ.SubHistory(g_QuoteSession,quoteSymbol,type,StrTim,EndTim)
    #print("訂閱歷史資料:",SubHis)
    #等待回補
    #獲取回補的資料
    i = 0
    while(1):  #等待訂閱回補
        i=i+1
        time.sleep(1)
        QPong = g_QuoteZMQ.Pong(g_QuoteSession)
       # print("第"+str(i)*5+"秒，Pong:",QPong)
        HisData = g_QuoteZMQ.GetHistory(g_QuoteSession, quoteSymbol, type, StrTim, EndTim, QryInd)
        if (len(HisData['HisData']) != 0):
            #print("回補成功")
            i = 0
            break
    df_result = pd.DataFrame()
    while (1):  # 獲取訂閱成功的全部歷史資料並另存
        i = i + 1
        HisData = g_QuoteZMQ.GetHistory(g_QuoteSession, quoteSymbol, type, StrTim, EndTim, QryInd)
        if (len(HisData['HisData']) != 0):
            HisData=HisData['HisData']            
            df_result=df_result.append(HisDataToDF(HisData))
            #print(HisData['HisData'][0])
            QryInd = str(int(QryInd) + 1)
        else:
            break
    return df_result
def removeUnuesdData(df_input):
    kbars_out = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
    kbars_out['Open']   = df_input['Open']
    kbars_out['High']   = df_input['High']
    kbars_out['Low']    = df_input['Low']
    kbars_out['Close']  = df_input['Close']
    kbars_out['Volume'] = df_input['Volume']
    kbars_out=kbars_out.dropna()
    return kbars_out
if __name__ == '__main__':
    df_result=read_data_to_df(contractName='FITX',
         StrTim='2021031600',
         EndTim='2021031700'
         )
    df_clean=removeUnuesdData(df_result)