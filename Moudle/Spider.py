# tbody标签是浏览器自己加上去的实际结果没有哦！

import requests
from lxml import etree
import re

URL = ""
HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
    "Referer": "http://www.dyhjw.com/jinjiaosuo.html", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9"}


class getHTML():
    def __init__(self, url=URL):
        self.url = url
        self.response = None
        self.header = HEADER
        self.xpath = ""

    def getResponse(self, url=URL):
        if (url != ""):
            self.url = url
        else:
            if (self.url == ""):
                self.url = input("请输入爬取地址")
                if (self.url == ""):
                    return 0
        try:
            self.response = requests.get(self.url, headers=self.header)
            return self.response
        except:
            print("地址错误")
            return 0

    def decodeResponse(self, response=None):
        if (response == None):
            if (self.response == None):
                self.getResponse(url=input("请输入爬取地址："))
                if (self.response == 0):
                    return 0
        if (self.response != 0 or None):
            return self.response.content.decode()

    def getContent(self, xpath=""):
        if (xpath != ""):
            self.xpath = xpath
        if (self.response != 0 or None):
            ret = self.response
            try:
                element = etree.HTML(ret.content.decode())
            except:
                element = etree.HTML(ret.content.decode(encoding="unicode_escape"))
            if (self.xpath != ""):
                pass
            else:
                self.xpath = input("请输入xpath路径：")
            try:
                content = element.xpath(self.xpath)
                return content
            except:
                print("解析错误！")
                return 0


def findValue(text, r):
    return re.findall(r, text)


if __name__ == "__main__":
    URL = "http://www.dyhjw.com/jinjiaosuo.html"
    xpath = '//div[@class="table_box"]/table[@class="gold_price_data"]/tr[@code="AGTD"]//span[@class="data_1 last"]/text()'
    a = getHTML()
    a.url = URL
    a.xpath = xpath
    a.getResponse()
    # print(a.decodeResponse())
    print(a.getContent())
    # print(findValue(a.decodeResponse(),r'<a  href="http://www.dyhjw.com/hjtd/" target="_blank">.*</a>'))