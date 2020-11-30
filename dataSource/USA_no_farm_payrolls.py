import requests,json,os,time
from lxml import etree
from Moudle.Retry import retry

url = "http://www.dyhjw.com/data"
XPATH = "/html/body/div[10]/div[4]/div[2]/div[1]/table/tbody/tr//td//text()"

tempDIR = "./dataSource"
tempName = "nofarm payrolls for USA.json"

def test():
    r = requests.get(url)
    html = r.content.decode()
    el = etree.HTML(html)
    data = el.xpath(XPATH)
    print(data)

def getTempLace():
    """
    缓存文件格式{"timeStamp":float类型时间戳，"data":获取到的字典类型非农数据}
    :return:
    """
    if os.path.exists(os.path.join(tempDIR,tempName)):
        f = open(os.path.join(tempDIR,tempName),"r")
        try:
            data = json.loads(f.read())
            if isinstance(data,dict):
                if "timeStamp" in data:
                    t = time.localtime()
                    if isinstance(data["timeStamp"],float):
                        if t-data["timeStamp"]>60*60*24:
                            return None
                        else:
                            if "data" in data["data"]:
                                if isinstance(data["data"],dict):
                                    return data["data"]
                                else:
                                    return None
                            else:
                                return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        except:
            return None
    else:
        return None

def setTemp(data):
    d = {
        "timeStamp":time.time(),
        "data":data,
    }
    filePath = os.path.join(tempDIR,tempName)
    if not os.path.exists(tempDIR):
        os.makedirs(tempDIR)
    with open(filePath,"w") as f:
        f.write(json.dumps(d))

@ retry
def getNoFarmPayrolls_USA():
    r = getTempLace()
    if r!=None:
        return r
    r = requests.get(url)
    try:
        html = r.content.decode()
    except:
        try:
            html = r.content.decode("utf-8")
        except:
            try:
                html = r.content.decode("gbk")
            except:
                try:
                    html = r.content.decode("gb2312")
                except:
                    print("无法解析网页获取美非农数据："+url)
                    return None
    el = etree.HTML(html)
    data = el.xpath(XPATH)
    NoFarmPayrollsData = {}
    # print(len(data))
    lastDate = None
    for i in range(len(data)):
        if "-" in data[i] and len(data[i].split("-"))==3:
            if data[i] in NoFarmPayrollsData:
                pass
            else:
                NoFarmPayrollsData.update({data[i]:[]})
                lastDate = data[i]
        else:
            try:
                NoFarmPayrollsData[lastDate].append(float(data[i]))
            except:
                NoFarmPayrollsData[lastDate].append(data[i])
        print(i)
    setTemp(NoFarmPayrollsData)
    return NoFarmPayrollsData

if __name__ == '__main__':
    r = getNoFarmPayrolls_USA()
    for each in r:
        print(each,r[each])
