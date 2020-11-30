import requests
import json
import time
from Moudle.dataType import DataType

URL = "https://hq.sinajs.cn/?_=1591590166263/&list=gds_AGTD"

def getOriginal(url=URL):
    res = requests.get(url)
    html = None
    try:
        html = res.content.decode()
    except:
        try:
            html = res.content.decode("gb2312")
        except:
            pass
    return html

def getAGTD(url=URL):
    content = getOriginal(url)
    AGTD = None
    if content!=None:
        data = content.split("=")[-1][1:-3]
        data = data.split(",")
        price = data[0]
        try:
            price = float(price)
        except:
            pass
        buy = data[1]
        try:
            buy = float(buy)
        except:
            pass
        sell = data[2]
        try:
            sell = float(sell)
        except:
            pass
        high = data[3]
        try:
            high = float(high)
        except:
            pass
        low = data[4]
        try:
            low = float(low)
        except:
            pass
        time_ = data[5]
        yesterday = data[6]
        open = data[7]
        try:
            open = float(open)
        except:
            pass
        try:
            yesterday = float(yesterday)
        except:
            pass
        holdon = data[8]
        try:
            holdon = float(holdon)
        except:
            pass
        date = data[-2]
        origianlname = data[-1]
        name = "Ag(T+D)"
        AGTD = DataType(name=name,dataTime=time_,dataDate=date,timeStamp=time.time())
        if isinstance(price,float):
            AGTD.setValue(price)
            AGTD.setValueType(origianlname)
        AGTD.setDataSource(url)
        AGTD.setUnit("kg")
        info = {"buy":buy,"sell":sell,"yesterday":yesterday,"open":open,"high":high,"low":low,"hold":holdon}
        AGTD.setInfo(info)
        return AGTD
    return None




if __name__ == '__main__':
    r = getAGTD()
    print(r)