import zmq
import json
import re
import threading

class TCoreZMQ():
    def __init__(self,APPID,SKey):
        self.context = zmq.Context()
        self.appid=APPID
        self.ServiceKey=SKey
        self.lock = threading.Lock()
        self.m_objZMQKeepAlive = None

    #连线登入
    def Connect(self, port):
        self.lock.acquire()
        login_obj = {"Request":"LOGIN","Param":{"SystemName":self.appid, "ServiceKey":self.ServiceKey}}
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://127.0.0.1:%s" % port)
        self.socket.send_string(json.dumps(login_obj))
        message = self.socket.recv()
        message = message[:-1]
        data = json.loads(message)
        self.lock.release()

        if data["Success"] == "OK":
            self.CreatePingPong(data["SessionKey"], data["SubPort"])

        return data

    def CreatePingPong(self, sessionKey, subPort):
        if self.m_objZMQKeepAlive != None:
            self.m_objZMQKeepAlive.Close()
        
        self.m_objZMQKeepAlive = KeepAliveHelper(subPort, sessionKey, self)
        
        return

    #连线登出
    def Logout(self, sessionKey):
        self.lock.acquire()
        obj = {"Request":"LOGOUT","SessionKey":sessionKey}
        self.socket.send_string(json.dumps(obj))
        self.lock.release()
        return

    #查询合约信息
    def QueryInstrumentInfo(self, sessionKey, symbol):
        self.lock.acquire()
        obj = {"Request" : "QUERYINSTRUMENTINFO" , "SessionKey" : sessionKey , "Symbol" : symbol}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #查询对应类型的所有合约
    #"Type":
    #期货：Future
    #期权：Options
    #证券：Stock
    def QueryAllInstrumentInfo(self, sessionKey, type):
        self.lock.acquire()
        obj = {"Request": "QUERYALLINSTRUMENT", "SessionKey": sessionKey, "Type": type}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #连线心跳（在收到"PING"消息时调用）
    def Pong(self, sessionKey, id = ""):
        self.lock.acquire()
        obj = {"Request":"PONG","SessionKey":sessionKey, "ID":id}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

class TradeAPI(TCoreZMQ):
    def __init__(self,APPID, SKey):
        super().__init__(APPID, SKey)

    #已登入资金账户
    def QryAccount(self, sessionKey):
        self.lock.acquire()
        obj = {"Request":"ACCOUNTS","SessionKey":sessionKey}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #查询当日委托回报
    def QryReport(self, sessionKey, qryIndex):
        self.lock.acquire()
        obj = {"Request":"RESTOREREPORT","SessionKey":sessionKey,"QryIndex":qryIndex}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #查询当日成交回报
    def QryFillReport(self, sessionKey, qryIndex):
        self.lock.acquire()
        obj = {"Request":"RESTOREFILLREPORT","SessionKey":sessionKey,"QryIndex":qryIndex}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #下单
    def NewOrder(self, sessionKey, param):
        self.lock.acquire()
        obj = {"Request":"NEWORDER","SessionKey":sessionKey}
        obj["Param"] = param
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #改单
    def ReplaceOrder(self, sessionKey, param):
        self.lock.acquire()
        obj = {"Request":"REPLACEORDER","SessionKey":sessionKey}
        obj["Param"] = param
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #删单
    def CancelOrder(self, sessionKey, param):
        self.lock.acquire()
        obj = {"Request":"CANCELORDER","SessionKey":sessionKey}
        obj["Param"] = param
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data
        
    #查询资金
    def QryMargin(self, sessionKey, accountMask):
        self.lock.acquire()
        obj = {"Request":"MARGINS","SessionKey":sessionKey,"AccountMask":accountMask}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #查询持仓
    def QryPosition(self, sessionKey, accountMask, qryIndex):
        self.lock.acquire()
        obj = {"Request":"POSITIONS","SessionKey":sessionKey,"AccountMask":accountMask,"QryIndex":qryIndex}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

class QuoteAPI(TCoreZMQ):
    def __init__(self,APPID, SKey):
        super().__init__(APPID, SKey)

    #订阅实时报价
    def SubQuote(self, sessionKey, symbol):
        self.lock.acquire()
        obj = {"Request":"SUBQUOTE","SessionKey":sessionKey}
        obj["Param"] ={"Symbol":symbol,"SubDataType":"REALTIME"}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #解订实时报价(每次订阅合约前，先调用解订，避免重复订阅)
    def UnsubQuote(self, sessionKey, symbol):
        self.lock.acquire()
        obj = {"Request":"UNSUBQUOTE","SessionKey":sessionKey}
        obj["Param"] = {"Symbol":symbol,"SubDataType":"REALTIME"}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #订阅实时greeks
    def SubGreeks(self, sessionKey, symbol, greeksType = "REAL"):
        self.lock.acquire()
        obj = {"Request":"SUBQUOTE","SessionKey":sessionKey}
        obj["Param"] = {"Symbol":symbol,"SubDataType":"GREEKS","GreeksType":greeksType}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #解订实时greeks(每次订阅合约前，先调用解订，避免重复订阅)
    def UnsubGreeks(self, sessionKey, symbol, greeksType = "REAL"):
        self.lock.acquire()
        obj = {"Request":"UNSUBQUOTE","SessionKey":sessionKey}
        obj["Param"] = {"Symbol":symbol,"SubDataType":"GREEKS","GreeksType":greeksType}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #订阅历史数据    
    #1：SessionKey，
    #2：合约代码，
    #3：数据周期:"TICKS","1K","DK"，
    #4: 历史数据开始时间,
    #5: 历史数据结束时间
    def SubHistory(self, sessionKey, symbol, type, startTime, endTime):
        self.lock.acquire()
        obj = {"Request":"SUBQUOTE","SessionKey":sessionKey}
        obj["Param"] = {"Symbol": symbol,"SubDataType":type,"StartTime" :startTime,"EndTime" :endTime}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data 

    #解订历史数据（遗弃，不再使用）
    #1：SessionKey，
    #2：合约代码，
    #3：数据周期"TICKS","1K","DK"，
    #4: 历史数据开始时间,
    #5: 历史数据结束时间   
    def UnsubHistory(self, sessionKey, symbol, type, startTime, endTime):
        self.lock.acquire()
        obj = {"Request":"UNSUBQUOTE","SessionKey":sessionKey}
        obj["Param"] = {"Symbol": symbol,"SubDataType":type,"StartTime" :startTime,"EndTime" :endTime}
        self.socket.send_string(json.dumps(obj))
        message = self.socket.recv()[:-1]
        data = json.loads(message)
        self.lock.release()
        return data

    #分页获取订阅的历史数据
    def GetHistory(self, sessionKey, symbol, type, startTime, endTime, qryIndex):
        self.lock.acquire()
        obj = {"Request":"GETHISDATA","SessionKey":sessionKey}
        obj["Param"] = {"Symbol": symbol,"SubDataType":type,"StartTime" :startTime,"EndTime" :endTime,"QryIndex" :qryIndex}
        self.socket.send_string(json.dumps(obj))
        message = (self.socket.recv()[:-1]).decode("utf-8")
        index =  re.search(":",message).span()[1]  # filter
        message = message[index:]
        message = json.loads(message)
        self.lock.release()
        return message

class KeepAliveHelper():
    def __init__(self, subPort, session, objZMQ):
        threading.Thread(target = self.ThreadProcess, args=(subPort, session, objZMQ)).start()
        self.IsTerminal = False

    def Close(self):
        self.IsTerminal = True

    def ThreadProcess(self, subPort, session, objZMQ):
        socket_sub = zmq.Context().socket(zmq.SUB)
        socket_sub.connect("tcp://127.0.0.1:%s" % subPort)
        socket_sub.setsockopt_string(zmq.SUBSCRIBE,"")
        while True:
            message = (socket_sub.recv()[:-1]).decode("utf-8")
            findText = re.search("{\"DataType\":\"PING\"}",message)

            if findText == None:
                continue

            if self.IsTerminal:
                return

            objZMQ.Pong(session, "TC")