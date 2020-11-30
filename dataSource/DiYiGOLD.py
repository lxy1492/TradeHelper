import requests,json,time
from Moudle.Retry import retry
from Moudle.dataType import DataType

"""
第一黄金网获取的数据
"""

headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "8",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "cdn.yifuls.com",
    "Origin": "http://www.dyhjw.com",
    "Referer": "http://www.dyhjw.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}

# 伦敦金
LondonGold_URL = "http://www.dyhjw.com/index.php?s=/tools/goldprice&from=USD&to=CNY&fromVal=1000&init=1"
# 美元对人民币
USDtoCNY_URL = "http://www.dyhjw.com/index.php?s=/tools/rate&from=USD&to=CNY&fromVal=100"

@ retry
def getRequestFromGet(url,headers=None,data=None):
    return requests.get(url,headers=headers,data=data)

def getLondonGold():
    r = getRequestFromGet(LondonGold_URL)
    # r = requests.get(LondonGold_URL)
    data = json.loads(r.content)
    price = data["price"]
    info = data["info"]
    timeStamp = time.time()
    t = time.localtime(timeStamp)
    date = time.strftime("%Y-%m-%d",t)
    time_ = time.strftime("%H:%M:%S",t)
    LondonGoldData = DataType("LondonGold", value=price, type_=float, valueType="price", info={"CNY": info},dataDate=date,dataTime=time_,timeStamp=timeStamp)
    LondonGoldData.setDataSource(LondonGold_URL)
    return LondonGoldData

def getUSDtoCNY():
    r = getRequestFromGet(USDtoCNY_URL)
    # r = requests.get(USDtoCNY_URL)
    data = json.loads(r.content)
    rate = data["rate"]
    info = data["info"]
    info = {"info":info}
    timeStamp = time.time()
    t = time.localtime(timeStamp)
    date = time.strftime("%Y-%m-%d", t)
    time_ = time.strftime("%H:%M:%S", t)
    USDtoCNYData = DataType("USDtoCNY", value=rate, type_=float, valueType="rate", info=info, timeStamp=timeStamp, dataDate=date, dataTime=time_)
    USDtoCNYData.setDataSource(USDtoCNY_URL)
    return USDtoCNYData

if __name__ == '__main__':
    print(getUSDtoCNY())