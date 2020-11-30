import requests
import json,time
from Moudle.Retry import retry
from Moudle.dataType import DataType

URL = "https://goldprice.org/gold-silver-ratio.html#gold_price_history"

USD_URL= "https://data-asg.goldprice.org/dbXRates/USD"

USD_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    'if-none-match': 'W/"f0-opj+E4LI7FLoDylPnIROQBsc/HA"',
    "origin": "https://goldprice.org",
    "referer": "https://goldprice.org/gold-silver-ratio.html",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
}

GetCalcData_URL = "https://data-asg.goldprice.org/GetCalcData/"

GetCalcData_HEADERS = {
    # ":authority": "data-asg.goldprice.org",
    # ":method": "GET",
    # ":path": "/GetCalcData/",
    # ":scheme": "https",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    "if-none-match": 'W/"720-JueoA+o6/jV5uTqW8v8slke1nBY"',
    "origin": "https://goldprice.org",
    "referer": "https://goldprice.org/gold-silver-ratio.html",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36"
}

@ retry
def spider(URL,HEADER=None):
    response = requests.get(url=URL,headers=HEADER)
    content = response.content.decode()
    return content

def get_data():
    USD_Data = spider(USD_URL,USD_HEADERS)
    timeStamp = time.time()
    CalacData = spider(GetCalcData_URL,GetCalcData_HEADERS)
    # print(USD_Data)
    # print(CalacData)
    usdData = json.loads(USD_Data)
    calacData = [CalacData.split("!")[0]]
    calacData.extend(CalacData.split("!")[1].split(";"))
    GoldSliver = DataType("GoldSliver",float)
    Gold = usdData["items"][0]["xauPrice"]
    Sliver = usdData["items"][0]["xagPrice"]
    t = time.localtime(timeStamp)
    date = time.strftime("%Y-%m-%d", t)
    time_ = time.strftime("%H:%M:%S", t)
    GoldSliver.setDataDate(date)
    GoldSliver.setDataTime(time_)
    rate = Gold/Sliver
    GoldSliver.setValue(rate)
    GoldSliver.setTimeStamp(timeStamp)
    info = {
        "Gold":Gold,
        "Sliver":Sliver,
        "update":usdData["date"],
        "ts":usdData["ts"],
        "tsj":usdData["tsj"],
        "curr":usdData["items"][0]["curr"],
        "chgXau": usdData["items"][0]["chgXau"],
        "chgXag": usdData["items"][0]["chgXag"],
        "pcXau": usdData["items"][0]["pcXau"],
        "pcXag": usdData["items"][0]["pcXag"],
        "xauClose": usdData["items"][0]["xauClose"],
        "xagClose": usdData["items"][0]["xagClose"],
    }
    GoldSliver.setInfo(info)
    GoldSliver.setDataSource([URL,USD_URL])
    return GoldSliver

    # for each in usdData:
    #     print(each,":",usdData[each])
    # for each in calacData:
    #     print(each)
    # print(float(usdData["items"][0]["xauPrice"])/float(usdData["items"][0]["xagPrice"]))

if __name__ == '__main__':
    print(get_data())