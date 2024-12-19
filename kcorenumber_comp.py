#!/usr/bin/python3

import requests, time, os
import urllib.parse
import hashlib
import hmac
import base64

from datetime import date

def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def depth(direction):
    url = "https://api.kraken.com/0/public/Depth?pair=XBTUSDC&count=3"

    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers, data=payload).json()

    #print(response.text)
    return response['result']["XXBTZUSDC"][direction][0]

def buy(v,api_key,api_sec):
    data = {
        "nonce":str(int(1000 * time.time())),
        "ordertype": "market",
        "pair": "BTCUSDC",
        "type": "buy",
        "volume": v
    }

    resp = kraken_request("/0/private/AddOrder",data,api_key,api_sec)
    return resp
  

def sell(v, api_key,api_sec):
    data = {
        "nonce":str(int(1000 * time.time())),
        "ordertype": "market",
        "pair": "BTCUSDC",
        "type": "sell",
        "volume": v
    }
    resp = kraken_request("/0/private/AddOrder",data,api_key,api_sec)
    return resp
   

def kraken_request(urlpath, data,api_key,api_sec):
    retrytime = 5
    headers ={"API-Key": api_key,"API-Sign":get_kraken_signature(urlpath,data,api_sec) }
    
    
    try:
        resp = requests.post((api_url + urlpath), headers=headers,data=data)
        return resp
    except requests.ConnectionError:
        print('connection error. trade not complete')
    	

def price():
    retrytime = 5
    
    while True:  
        try:
            ticker = requests.get("http://api.kraken.com/0/public/Ticker?pair=BTCUSDC").json()
            ask = ticker['result']['XBTUSDC']['a']
            bid = ticker['result']['XBTUSDC']['b']
            last = ticker['result']['XBTUSDC']['c']
            return {'ask':ask, 'bid': bid}
        except requests.ConnectionError:
            print(f'connection error. retrying in {retrytime} minutes')
            time.sleep(retrytime * 60)

def get_balance(api_key,api_sec):
    resp = kraken_request("/0/private/Balance",{
        "nonce":str(int(1000 * time.time()))
    },api_key,api_sec)


    usdc_bal = float(resp.json()['result']['USDC'])
    btc_bal = float(resp.json()['result']['XXBT'])

    return usdc_bal,btc_bal

def time_stamp():
    return time.asctime(time.localtime(time.time()))

def log(s):
    today = date.today()
    d1 = today.strftime("%d-%m-%Y")
    filename = f"logs/{d1}.log"

    with open(filename,'a') as f:
        f.write(f'{s}\n')

def compound(core,usd):
    if usd >= (core * 1.05):
        with open('core.txt','w') as f:
            f.write(str(usd))
        print(f"corenumber changed to {usd}")
        return usd
    else:
        return core


def main():
    api_key = os.environ['API']
    api_sec = os.environ['SEC']

    usdc_bal,btc_bal = get_balance(api_key,api_sec)

    if os.path.isfile('core.txt'):
        with open('core.txt','r') as f:
            corenumber = float(f.read().strip())
    else:
        corenumber = input('corenumber file does not exist. Enter corenumber:')
        corenumber = float(corenumber)
        with open('core.txt','w') as f:
            f.write(str(corenumber))

    trigerpercent = 3/100

    wait_time = 600

    print(f"core number:{corenumber},buy/sell%:{trigerpercent},$trigger:{round(trigerpercent * corenumber,2)}")
    print("checking every {} mins".format(wait_time/60))

    passcount = 0

    while True:
        current = price()
        ask_price = float(current['ask'][0])
        bid_price = float(current['bid'][0])
        p = current['last'][0]
        
        ask_convert = ask_price * btc_bal
        bid_convert = bid_price * btc_bal

        print(f"price:{p}  BTC:{btc_bal}  $value:{round(bid_convert,2)}  USDC:{round(usdc_bal,2)} total:{round(bid_convert+usdc_bal,2)}")

    #check for bids price instead
        if bid_convert >= ((trigerpercent * corenumber) +corenumber):
            sell_amt = round((bid_convert - corenumber)/bid_price,8)
            print(f"selling {sell_amt}btc {time_stamp()}")
            resp = sell(sell_amt,api_key,api_sec).json()
            if not resp['error']:
                log(resp['result'])
                print(resp['result'])
            else:
                log(resp['error'])
                print(resp['error'])
            usdc_bal,btc_bal = get_balance(api_key,api_sec)
    #check for asks price instead
        elif ask_convert <= (corenumber - (trigerpercent * corenumber)):
            corenumber = compound(corenumber,usdc_bal)

            buy_amt = round((corenumber - ask_convert)/ask_price,8)
            print(f"buying {buy_amt}btc  {time_stamp()}")
            resp = buy(buy_amt,api_key,api_sec).json()
            if not resp['error']:
                log(resp['result'])
                print(resp['result'])
            else:
                log(resp['error'])
                print(resp['error'])
            usdc_bal,btc_bal = get_balance(api_key,api_sec)
        else:
            print('pass')
            passcount = passcount + 1

            if passcount == 6:
                print("updating balances")
                usdc_bal,btc_bal = get_balance(api_key,api_sec)
                passcount = 0

        time.sleep(wait_time)

if __name__ == "__main__":
    api_url = "https://api.kraken.com"
    main()

