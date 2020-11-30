import json,config,os
import socket
from Moudle.dataType import DataType
import pickle
from threading import Thread

def downloaddata(name,date,ip="111.230.177.71",port=8001,batchsize=10,recvSize=1024000):
    c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    c.connect((ip,port))
    print(c.recv(1024).decode())
    mess = "downloaddata "+name+" "+date+" "+str(batchsize)
    c.send(mess.encode())
    r = c.recv(recvSize)
    data = r.decode("gbk")
    datas = []
#     print(data)
    data = json.loads(data)
    if data["result"]=="success":
        datas.extend(data["data"])
    else:
#         print(data)
        return -1
    while(True):
        c.send(b"next data")
        data = c.recv(recvSize)
        data = json.loads(data.decode("gbk"))
        if data["result"]=="success":
            datas.extend(data["data"])
            # print(data["info"],data["name"],data["date"])
        else:
            # print(data)
            break
    return datas

def getList(ip="111.230.177.71",port=8001,recvSize=102400):
    c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    c.connect((ip,port))
    print(c.recv(1024).decode())
    mess = "databaselist"
    c.send(mess.encode())
    r = c.recv(recvSize)
    return json.loads(r.decode())

def writeToFile(data,eachName,date):
    fileName = eachName + " " + date + ".tbs"
    fileDIR = config.DataBase + "/Download"
    if not os.path.exists(fileDIR):
        os.makedirs(fileDIR)
    filePath = os.path.join(fileDIR, fileName).replace("\\", "/")
    with open(filePath, "w") as f:
        for each in data:
            f.write(json.dumps(each) + "\n")
    print("已写入文件>>>", filePath)


# 涉及网速问题，没有必要多线程并发下载数据，只需要多线程存储数据就可以了
def downloadAll(ip="111.230.177.71",port=8001):
    datalist = getList(ip=ip,port=port)
    for eachName in datalist:
        for eachDate in datalist[eachName]:
            date = eachDate[0].split(" ")[1].split(".")[0]
            data = downloaddata(name=eachName,date=date,ip=ip,port=port,batchsize=40)
            # fileName = eachName+" "+date+".tbs"
            # fileDIR = config.DataBase+"/Download"
            # if not os.path.exists(fileDIR):
            #     os.makedirs(fileDIR)
            # filePath = os.path.join(fileDIR,fileName).replace("\\","/")
            # with open(filePath,"w") as f:
            #     for each in data:
            #         f.write(json.dumps(each)+"\n")
            # print("已写入文件>>>",filePath)
            Thread(target=writeToFile,args=(data,eachName,date)).start()

if __name__ == '__main__':
    os.chdir("../")
    downloadAll()