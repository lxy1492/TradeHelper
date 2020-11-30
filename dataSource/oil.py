import requests
import time
from Moudle.dataType import DataType
from Moudle.Retry import retry
url = "https://info.usd-cny.com/d.js"

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "__51cke__=; __tins__1067409=%7B%22sid%22%3A%201575705170924%2C%20%22vd%22%3A%208%2C%20%22expires%22%3A%201575707367248%7D; __51laig__=8",
    "Host": "info.usd-cny.com",
    "If-None-Match": 'W/"eb1b2265d4acd51:0"',
    "Referer": "https://info.usd-cny.com/",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}


def get_from_webSite(url,headers=None):
    resp = requests.get(url,headers=headers)
    content = resp.content
    try:
        content = content.decode("gbk")
    except:
        content = content.decode("utf-8")
    return content

def get_data(url,headers=None):
    data = get_from_webSite(url,headers)
    result = []
    if not data==None:
        data = data.split(";")
        while ("\n" in data):
            data.remove("\n")
        while ("" in data):
            data.remove("")
        for each in data:
            d = get_dict(each.split(","))
            result.append(d)
        return result
    return None


def get_dict(s):
    if isinstance(s,list):
        pass
    else:
        s = s.split(",")
    # print(s)
    info = {
        # "name": s[-2],
        # "price": float(s[0].split("=")[-1][1:]),
        "high": float(s[4]),
        "low": float(s[5]),
        "time": s[6],
        "yesterday": s[7],
        "today": s[8],
        "date": s[12]
    }
    name = s[-2]
    timeStamp = time.time()
    t = time.localtime(timeStamp)
    date = time.strftime("%Y-%m-%d", t)
    time_ = time.strftime("%H:%M:%S", t)
    price = float(s[0].split("=")[-1][1:])
    data = DataType(
        name = name,
        type_ = float,
        valueType = "原油价格",
        value = price,
        info = info,
        dataDate = date,
        dataTime = time_,
        timeStamp = timeStamp,
    )
    # print(data)
    return data

@retry
def get():
    return get_data(url,headers)


if __name__ == '__main__':
    data = get()
    print(data)
