import json,config,os
from getData.getHistory import getHistoryData

def transportForDate(conn,name,date,end=True):
    history = getHistoryData()
    data = history.readHistoryData(name,date,loads=False)
    i = 0
    if date != None:
        filename = name + " " + date + ".tbs"
        filedate = date
    else:
        filedate = name.split(" ")[1].split(".")[0]
    for each in data:
        r = {"data":each,"num":i,"name":name,"date":date}
        conn.send(json.dumps(r).encode())
        r = conn.recv(1024)
        # print(r)
    if end:
        conn.send(json.dumps({"data":None,"num":-1,"name":filename,"date":filedate}).encode())

def transportData(conn,name):
    history = getHistoryData()
    history.getDataFileList()
    files = history.fileList[name]
    for each in files:
        transportForDate(conn,name=each,date=None,end=False)
    conn.send(json.dumps({"data": None, "num": -1, "name": name, "date": None}).encode())

def transportAllHistory(conn):
    history = getHistoryData()
    history.getDataFileList()
    for name in history:
        for file in history[name]:
            transportForDate(conn,name=file,date=None,end=False)
    conn.send(json.dumps({"data": None, "num": -1, "name": name, "date": None}).encode())

def loadData(path=None):
    if path==None:
        return None
    else:
        if os.path.exists(path):
            data = []
            with open(path,"r") as f:
                for eachLine in f.read().split("\n"):
                    if eachLine!="":
                        data.append(eachLine)
            if len(data)>0:
                return data
    return None

def downloadDataForOneDay(conn,name,date,batch=10):
    for each in [" ","-",",",";","|","/","\\"]:
        if each in date:
            date = date.replace(each,"_")
    fileName = name+" "+date+".tbs"
    filePath = os.path.join(config.DataBase,"Original",fileName).replace("\\","/")
    # print(filePath)
    if os.path.exists(filePath):
        # print(filePath)
        oneDayData = loadData(filePath)
        if oneDayData!=None:
            transPortData = []
            dataLength = len(oneDayData)
            i = 0
            while True:
                end = i+batch
                # print(i,end,dataLength)
                if end>=dataLength:
                    end = dataLength
                transPortData = oneDayData[i:end]
                conn.send(json.dumps({"result":"success","info":str(i)+"-"+str(end)+"/"+str(dataLength),"data":transPortData,"name":name,"date":date}).encode())
                _ = conn.recv(1024)
                i = end
                if end>=dataLength:
                    break
        else:
            return -1
    return None

def downloadData(conn,r):
    mess = r.split(" ")
    while "" in mess:
        mess.remove("")
    if len(mess)<=1:
        conn.send(json.dumps({"result":"failed","info":"指令参数不足","data":None}).encode())
        return -1
    if len(mess)>=2:
        name = mess[1]
        date = None
        batch = 10
    if len(mess)>=3:
        name = mess[1]
        date = [mess[2]]
        batch  = 10
        try:
            date = int(date[0])
            if date<100:
                batch = date
            date = None
        except:
            date = [mess[2]]
    if len(mess)>=4:
        name = mess[1]
        date = [mess[2]]
        batch = mess[3]
        try:
            batch = int(batch)
        except:
            batch = 10
    # date = mess
    # print(date)
    if isinstance(date,list):
        if len(date)<=0:
            date = None
    # print(date)
    if date==None:
        date = []
        for each in os.listdir(config.DataBase+"/Original"):
            if ".tbs" in each:
                try:
                    if each.split(" ")[0] == name:
                        date.append(each.split(" ")[1].split(".")[0])
                except:
                    pass
    # print(name,date,batch)
    if isinstance(date,list):
        if len(date)>0:
            for each in date:
                # print(each)
                r = downloadDataForOneDay(conn,name,each,batch)
                # if r==None:
                #     conn.send(json.dumps({"result":"filished","info":"完成","data":None}).encode())
                # else:
                #     conn.send(json.dumps({"result":"failed","info":"文件传输失败","data":None}).encode())
            conn.send(json.dumps({"result":"finished","info":"传输完成","data":None}).encode())
        else:
            conn.send(json.dumps({"result":"failed","info":"没有日期指定","data":None}).encode())
    else:
        conn.send(json.dumps({"result":'failed',"info":"没有获取到日期","date":None}).encode())
    return None

if __name__ == '__main__':
    pass