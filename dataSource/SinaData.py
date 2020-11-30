import requests,time
from lxml import etree
import re
# from Tool.ReTry import retry
from Moudle.Retry import retry
from Moudle.dataType import DataType

# 新浪数据地址
URL_SINA = "http://hq.sinajs.cn/rn=817of&list=SGE_AG99_9,SGE_AG99_99,SGE_AU100G,SGE_AU99_99,SGE_AU995,SGE_AUTN06,SGE_AUTN12,SGE_AGTD,SGE_AG9999,SGE_AUTD,SGE_AUTN1,SGE_AUTN2,SGE_AU100,SGE_AU50G,SGE_AU9995,SGE_AU9999,SGE_IAU100G,SGE_IAU99_5,SGE_IAU99_99,SGE_MAUTD,SGE_PGC30G,SGE_PT99_95,SGE_PT9995,SGE_SHAG,SGE_SHAU"
# 请求头
HEADER_SINA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
    "Referer": "http://vip.stock.finance.sina.com.cn/mkt/",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Host":"hq.sinajs.cn",
    "Connection": "keep-alive",
    "Cookie":"U_TRS1=000000a0.1b1d7fc3.5d3312cf.ccc95bae; U_TRS2=000000a0.1b257fc3.5d3312cf.c4d0a577; UOR=www.baidu.com,blog.sina.com.cn,; SINAGLOBAL=221.11.20.106_1563628244.595058; Apache=221.11.20.106_1563628244.595060; ULV=1564403315311:2:2:1:221.11.20.106_1563628244.595060:1563628245133; gr_user_id=987492d1-c659-4096-a91b-78261912171a; grwng_uid=82d48407-3671-4442-9cae-ad7897ef1ccf; rotatecount=2; hqEtagMode=0; lxlrttp=1572512346; sinaH5EtagStatus=y; SUB=_2AkMqmpjlf8NxqwJRmP0WyWnkbY12zQ_EieKcxmk-JRMyHRl-yD92qnJftRB6ARq2Chj-pr9ad9JKE_WX4jbN4VzhEWM5; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WhfEEUQUvDIi14Ope_p2fnX",
}

# 美元指数
USD_URL = "https://hq.sinajs.cn/rn=1586835432077list=DINIW"

# 新浪数据的伦敦银地址
LondonAGURL = "https://hq.sinajs.cn/?_=1587787457148/&list=hf_XAG"

# 新浪财经获取伦敦金地址
LondonAUURL = "https://hq.sinajs.cn/?_=1587788206162/&list=hf_XAU"

@ retry
def getUSD():
    r = requests.get(USD_URL)
    try:
        r = r.content.decode("gbk")
    except:
        try:
            r = r.content.decode()
        except:
            r = r.content.decode("gb2312")
    r = r.split("=")[-1][:-1][1:-2]
    data = r.split(",")
    dataTime = data[0]
    dataDate = data[-1]
    dataName = data[-2]
    dataValue = data[1]
    timeStamp = time.time()
    USDData = DataType(dataName,value=dataValue,type_=float,valueType="美元指数",dataTime=dataTime,dataDate=dataDate,timeStamp=timeStamp,dataSource=USD_URL)
    return USDData

@ retry
def get_original_data(url=URL_SINA,headers=HEADER_SINA,encodindg="gb2312"):
    r = requests.get(url,headers=headers)
    r = r.content.decode(encoding=encodindg)
    market = r.split("\n")
    data = []
    for each in market:
        if(len(each)<5):
            continue
        d = each.split(";")[0].split(",")
        d = d[1:-1]
        data.append(
            {
                "品种":d[0],
                "名称":d[1],
                "最新价":d[2],
                "同期":d[4],
                "开盘价":d[5],
                "最高价":d[6],
                "最低价":d[7],
                "昨收":d[8],
                "总成交量":d[13],
                "总成交额":d[14],
                "更新时间":d[15],
            }
        )
    return data


def get_data():
    data = get_original_data(URL_SINA,HEADER_SINA,encodindg="gb2312")
    convert = ["最新价","开盘价","最高价","最低价","昨收","总成交量","总成交额","同期"]
    for i in range(len(data)):
        for each in convert:
            if not("-" in data[i][each]):
                try:
                    data[i][each] = float(data[i][each])
                except:
                    pass
            if(type(data[i]["同期"])==float and type(data[i]["最新价"])==float):
                try:
                    rate = (data[i]["同期"] - data[i]["最新价"])/data[i]["同期"]
                    rate = round(rate,4)
                    rate = str(rate*100)
                    if(data[i]["同期"]>data[i]["最新价"]):
                        rate = "-"+rate+"%"
                    else:
                        rate = rate+"%"
                    data[i].update({"增幅":rate})
                    data[i].update({"涨跌":data[i]["同期"]-data[i]["最新价"]})
                except:
                    data[i].update({"增幅":"--"})
                    data[i].update({"涨跌":"--"})
            else:
                data[i].update({"涨跌":"--"})
                data[i].update({"增幅":"--"})
    data = convertToDataType(data)
    return data

def convertToDataType(dic):
    result = []
    for each in dic:
        Data = DataType(each["名称"],valueType="最新价格")
        Data.setType(float)
        Data.setValue(each["最新价"])
        timeStamp = time.time()
        Data.setTimeStamp(timeStamp)
        info = {}
        # print(each)
        # info.update({"ticker":each["名称"]})
        # info.update({"last":each["最新价"]})
        info.update({"updown":each["涨跌"]})
        info.update({"updownrate":each["增幅"]})
        info.update({"high":each["最高价"]})
        info.update({"low":each["最低价"]})
        info.update({"lastday":each["昨收"]})
        info.update({"today":each["开盘价"]})
        info.update({"date":each["更新时间"]})
        try:
            info.update({"tradeNum":each["总成交量"]})
        except:
            pass
        try:
            info.update({"tradeMoney":each["总成交额"]})
        except:
            pass
        # result.append(new_dic)

        t = time.localtime(timeStamp)
        # date = time.strftime("%Y-%m-%d", t)
        date = info["date"].split(" ")[0]
        # time_ = time.strftime("%H:%M:%S", t)
        time_ = info["date"].split(" ")[1]

        Data.setDataTime(time_)
        Data.setDataDate(date)

        Data.setInfo(info)
        Data.setTimeStamp(timeStamp)

        if Data.name == "Ag(T+D)":
            Data.unit = "kg"
            Data.name = "白银延期"
        elif Data.name == "Au(T+D)":
            Data.unit = "g"
            Data.name = "黄金延期"
        elif Data.name == "Au99.99":
            Data.unit = "g"

        result.append(Data)

    return result

@ retry
def getLondonAg(useHeaders = False):
    if useHeaders:
        r = requests.get(LondonAGURL,headers = HEADER_SINA)
    else:
        r = requests.get(LondonAGURL)
    try:
        content = r.content.decode()
    except:
        try:
            content = r.content.decode("utf-8")
        except:
            try:
                content = r.content.decode("gb2312")
            except:
                try:
                    content = r.content.decode("gbk")
                except:
                    return None
    data = content.split('\"')[1].split(",")
    # print(data)
    price = data[0]
    try:
        price = float(price)
    except:
        pass
    time_ = data[6]
    date = data[12]
    name = "伦敦银"
    info = {"type":"伦敦银（现货白银）"}
    price = float(price)
    data = DataType(name=name,value=price,type_=float,valueType="现货白银",dataTime=time_,dataDate=date,timeStamp=time.time(),info=info,dataSource=LondonAGURL,unit="oz")
    return data

def getLondonAU(url = LondonAUURL,useheaders=False):
    if useheaders:
        r = requests.get(url,headers=HEADER_SINA)
    else:
        r = requests.get(url)
    try:
        content = r.content.decode()
    except:
        try:
            content = r.content.decode("utf-8")
        except:
            try:
                content = r.content.decode("gb2312")
            except:
                try:
                    content = r.content.decode("gbk")
                except:
                    return None
    data = content.split('\"')[1].split(",")
    price = data[0]
    try:
        price = float(price)
    except:
        pass
    date = data[-2]
    time_ = data[6]
    name = "伦敦金"
    info = {"type":"伦敦金（现货黄金）","description":"时间戳表示本系统获取数据时的时间戳"}
    data = DataType(
        name=name,
        dataTime=time_,
        dataDate=date,
        dataSource= url,
        info=info,
        value=price,
        type_=float,
        valueType="伦敦现货黄金",
        timeStamp=time.time(),
    )
    return data


if __name__ == '__main__':
    getLondonAU()