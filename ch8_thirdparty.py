######################################################
#8.1 以下單大師為例示範下單機的用法
######################################################
import datetime 

def Write_OM_Signal(
        filepath
        ,position
        ,price):
    now = datetime.datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    int_p=int(position)
    with open(filepath, 'w') as f:
        f.write(dt_string+','+str(int_p)+','+str(price))
        f.close()
Write_OM_Signal(
        'c:/OM_Signals/OM_Example.txt'
        ,1
        ,8500)
######################################################
#8.2 以Touchance為例示範外部訊號源的用法
######################################################
import read_touchance
df_result=read_touchance.read_data_to_df(
    contractName='FITX'
    ,StrTim='2021031600'
    ,EndTim='2021031700'
    )
df_clean=read_touchance.removeUnuesdData(df_result)
print('使用touchance讀取1分k結果')
print(df_clean.head())