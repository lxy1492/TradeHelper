import requests

headers={
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    # Cookie: __utma=31846910.1414559134.1591836924.1591836924.1591836924.1; __utmc=31846910; __utmz=31846910.1591836924.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=31846910.1.10.1591836924
    "Host": "111.230.177.71:2019",
    "Referer": "http://111.230.177.71:2019/Lxy/TradeHelperLastResult/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "X-Requested-With": "XMLHttpRequest",
}

def getcontent(url="http://111.230.177.71:2019/Lxy/TradeHelper/"):
    r = requests.post(url,{"info":"getLastResult"},headers=headers)
    print(r.content.decode())

if __name__ == '__main__':
    getcontent()