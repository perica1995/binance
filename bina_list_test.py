import ccxt
from datetime import datetime
import time
import requests
import hashlib
import hmac
import json
binance = ccxt.binance()
binance.apiKey='test111'
binance.secret='test1112'
binance.options['defaultType']='future'

##this is test scrypt kyo 2023/09/03

apikey='test111'
secret='test1112'

def staking(current):
    timestamp = round(datetime.now().timestamp()) * 1000

    endpoint = ' https://api.binance.com/'
    
    api_key = "test111"
    secret_key = "test1112"
    
    path = 'sapi/v1/staking/productList?';
    side = "BUY"
    price = 20000
    quantity = 0.01
    query = 'product=' + "STAKING"+ "&current="+str(current) + '&timestamp=' + str(timestamp);
    
    signature = hmac.new(bytearray(secret_key.encode('utf-8')), query.encode('utf-8') , digestmod = hashlib.sha256 ).hexdigest()
    
    url = endpoint + path + query + '&signature=' + signature
    
    headers = {
        'X-MBX-APIKEY': api_key
    }
    res = requests.get(url, headers=headers)
    datas = json.loads(res.text)
    return datas

def bina_list():
    while True:
        try:
            
            #params = {"symbol":symbol}#round(close_time-60*interval*200)}
            response = requests.get("https://api.binance.com/sapi/v1/margin/allPairs")
            #print(datetime.now().strftime('%H:%M:%S'),response.status_code)
            response = response.json()
            return response
            
            break
        except requests.exceptions.RequestException as e:
            print("bitのポジ取得でエラー発生 : ",e)
            print("10秒待機してやり直します")

def staking1():
    timestamp = (round(time.time()*1000-1000))
    print(timestamp)
    param_str = "product="+"STAKING"+"&timestamp="+str(timestamp)
    sign = hmac.new(bytes(secret,'utf-8'), bytes(param_str,'utf-8') , digestmod = hashlib.sha256 ).hexdigest()
    while True:
        try:
            #curl "https://api.bybit.com/v2/private/position/list?api_key={api_key}&symbol=BTCUSDT&timestamp={timestamp}&sign={sign}"
            params = {"product":"STAKING","timestamp":str(timestamp),"sign":sign}#,"position_idx":0}
            response = requests.get("https://api.binance.com/",params,
                headers = {"X-MBX-APIKEY" : apikey,
                }
            )
            response1 = response.json()
            print(response1)
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),"Order",response1["result"]["side"],response1["result"]["price"])
            try:
                return response1["result"]
            except IndentationError:
                return 0
        except requests.exceptions.RequestException as e:
            print("bitのポジ取得でエラー発生 : ",e)
            print("10秒待機してやり直します")
            time.sleep(2)

print(bina_list())
