##################################################
## CH 3.1. 使用yfinance取得日線資料
#################################################
import yfinance as yf
#告訴yfinance,要取0050的資料
tw0050 = yf.Ticker("0050.tw")
#取所有歷史資料
tw0050_max = tw0050.history(period="max")
print('tw0050_max:')
print(tw0050_max)
#取五年歷史資料
tw0050_5y = tw0050.history(period="5y")
print('tw0050_5y:')
print(tw0050_5y)
#取七天分的一分線歷史資料
tw0050_1m = tw0050.history(period="7d", interval = "1m")
#取收盤價
close=tw0050_max['Close']
#畫收盤價
import matplotlib.pyplot as plt
plt.plot(close)
plt.title('Get 0050 close with yfinance')
plt.show()  

##################################################
## CH 3.2. 使用shioaji取得tick資料
#################################################
#登入Shioaji
import shioaji as sj
api = sj.Shioaji(simulation=False) 
person_id=''#你的身分證字號
passwd=''#你的永豐證券登入密碼
if(person_id==''):
    person_id=input("Please input ID:\n")
if(passwd==''):
    passwd=input("Please input PASSWORD:\n")
api.login(
    person_id=person_id, 
    passwd=passwd, 
    contracts_timeout=10000,
    contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
)
#登入永豐金證券的憑證
CA_passwd=''
if(CA_passwd==''):
    CA_passwd=input("Please input CA PASSWORD:\n")
CA='c:\ekey\\551\\'+person_id+'\\S\\Sinopac.pfx'
result = api.activate_ca(\
    ca_path=CA,\
    ca_passwd=CA_passwd,\
    person_id=person_id,\
)
#取得股票0050的物件
contract_0050 = api.Contracts.Stocks["0050"]
#取得小型台指近月的物件
contract_MXFR1 = api.Contracts.Futures['MXFR1']
#列出小型台指的不同月份的合約
print('api.Contracts.Futures.MXF content:')
print(api.Contracts.Futures.MXF)    

#取得tick資料
ticks_0050 = api.ticks(
    contract=contract_0050, 
    date="2021-12-15"
)
ticks_MXFR1 = api.ticks(
    contract=contract_MXFR1, 
    date="2021-12-15"
)

#把0050的ticks轉成dataframe，並且印出資料
import pandas as pd
df_0050_tick = pd.DataFrame({**ticks_0050})#轉成dataframe
df_0050_tick.index =pd.to_datetime(df_0050_tick.ts)


#把小型台指近月的ticks轉成dataframe
df_MXFR1_tick = pd.DataFrame({**ticks_MXFR1})#轉成dataframe
df_MXFR1_tick.index = pd.to_datetime(df_MXFR1_tick.ts)

print('df_MXFR1_tick:')
print(df_MXFR1_tick)

plt.plot(df_MXFR1_tick['close'])
plt.title('Get MXFR1 ticks with shioaji')
plt.show()  

#ticks轉1分K的範例程式
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
MXFR1_1m=ticksTo1mkbars(df_MXFR1_tick)

print('MXFR1_1m:')
print(MXFR1_1m)

plt.plot(MXFR1_1m['Close'])
plt.title('Convert to 1m data')
plt.show()  

##################################################
## CH 3.3. 使用shioaji取得1分線資料
#################################################

#取得kbars資料
kbars_0050 = api.kbars(
    contract_0050,
    start="2021-12-01", 
    end="2021-12-30")

kbars_MXFR1 = api.kbars(
    contract_MXFR1, 
    start="2021-12-01", 
    end="2021-12-30")


#把0050的kbars轉成dataframe，並且印出最前面的資料
import pandas as pd
df_0050 = pd.DataFrame({**kbars_0050})#轉成dataframe
df_0050.index =pd.to_datetime(df_0050.ts)
print('df_0050:')
print(df_0050)

#把小型台指近月的kbars轉成dataframe
df_MXFR1 = pd.DataFrame({**kbars_MXFR1})#轉成dataframe
df_MXFR1.index = pd.to_datetime(df_MXFR1.ts)
print('df_MXFR1:')
print(df_MXFR1)

plt.plot(df_MXFR1['Close'])
plt.title('Get 1m data with shioaji')
plt.show()  

df_MXFR1_fix=df_MXFR1.groupby(df_MXFR1.index).first()
plt.plot(df_MXFR1_fix['Close'])
plt.title('Fix error in shioaji 1m data')
plt.show()  

##################################################
## CH 3.4. 如何把1分線轉為小時線或其他週期
#################################################
#小型台指 1小時
period='1h'
kbars = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
kbars['Open'] = df_MXFR1['Open'].resample(period).first() #區間第一筆資料為開盤(Open)
kbars['High'] = df_MXFR1['High'].resample(period).max() #區間最大值為最高(High)
kbars['Low'] = df_MXFR1['Low'].resample(period).min() #區間最小值為最低(Low)
kbars['Close'] = df_MXFR1['Close'].resample(period).last() #區間最後一個值為收盤(Close)
kbars['Volume'] = df_MXFR1['Volume'].resample(period).sum() #區間所有成交量加總
kbars_1h=kbars.dropna()
print('MXFR1 1h:')
print(kbars_1h)

plt.plot(kbars_1h['Close'])
plt.title('Resample MXFR1 to 1h')
plt.show()  
#小型台指 日線
period='1d'
kbars = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
kbars['Open'] = df_MXFR1['Open'].resample(period).first() #區間第一筆資料為開盤(Open)
kbars['High'] = df_MXFR1['High'].resample(period).max() #區間最大值為最高(High)
kbars['Low'] = df_MXFR1['Low'].resample(period).min() #區間最小值為最低(Low)
kbars['Close'] = df_MXFR1['Close'].resample(period).last() #區間最後一個值為收盤(Close)
kbars['Volume'] = df_MXFR1['Volume'].resample(period).sum() #區間所有成交量加總
kbars_1d=kbars.dropna()
print('MXFR1 1d:')
print(kbars_1d)

plt.plot(kbars_1d['Close'])
plt.title('Resample MXFR1 to 1d')
plt.show()  

#小型台指 15分線
period='15min'
kbars = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
kbars['Open'] = df_MXFR1['Open'].resample(period).first() #區間第一筆資料為開盤(Open)
kbars['High'] = df_MXFR1['High'].resample(period).max() #區間最大值為最高(High)
kbars['Low'] = df_MXFR1['Low'].resample(period).min() #區間最小值為最低(Low)
kbars['Close'] = df_MXFR1['Close'].resample(period).last() #區間最後一個值為收盤(Close)
kbars['Volume'] = df_MXFR1['Volume'].resample(period).sum() #區間所有成交量加總
kbars_15m=kbars.dropna()
print('MXFR1 15m:')
print(kbars_15m)

plt.plot(kbars_15m['Close'])
plt.title('Resample MXFR1 to 15m')
plt.show()  

#寫成函數
def sjBarsToDf(sjBars):
    dfBars = pd.DataFrame({**sjBars})#轉成dataframe
    dfBars.index =pd.to_datetime(dfBars.ts)
    dfBars=dfBars.groupby(dfBars.index).first()
    return dfBars
def resampleKbars(kbars,period='1d'):
    kbars_out = pd.DataFrame(columns = ['Open','High','Low','Close','Volume'])
    kbars_out['Open'] = kbars['Open'].resample(period).first() #區間第一筆資料為開盤(Open)
    kbars_out['High'] = kbars['High'].resample(period).max() #區間最大值為最高(High)
    kbars_out['Low']  = kbars['Low'].resample(period).min() #區間最小值為最低(Low)
    kbars_out['Close'] = kbars['Close'].resample(period).last() #區間最後一個值為收盤(Close)
    kbars_out['Volume'] = kbars['Volume'].resample(period).sum() #區間所有成交量加總
    kbars_out=kbars_out.dropna()
    return kbars_out

df=sjBarsToDf(kbars_MXFR1)
df_resample=resampleKbars(df,period='1d')
print('MXFR1 1d (generated with function):')
print(df_resample)
