import shioaji

api=0
person_id=''#身分證字號
api_key=''#api_key
secret_key=''#secret_key
CA_passwd=''
def shioajiLogin(simulation=False):
    global api
    global api_key
    global secret_key
    global CA_passwd
    global person_id
    api = shioaji.Shioaji(simulation=simulation)

    if(person_id==''):
        person_id=input("Please input personal id:\n")
    if(api_key==''):
        api_key=input("Please input api_key:\n")
    if(secret_key==''):
        secret_key=input("Please input secret_key:\n")
    if(CA_passwd==''):
        CA_passwd=input("Please input CA PASSWORD:\n")
    api.login(
        api_key=api_key, 
        secret_key=secret_key, 
        contracts_timeout=10000,
        contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
    )
        
    
    CA='c:\ekey\\551\\'+person_id+'\\S\\Sinopac.pfx'
    result = api.activate_ca(\
        ca_path=CA,\
        ca_passwd=CA_passwd,\
        person_id=person_id,\
    )
    return api

#shioajiLogin(simulation=False)