import socket,json
from Moudle.dataType import DataType
from config import remoteServerIP as IP
from config import remmoteServerPort as PORT

def getData(ip=IP,port=PORT):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((ip,port))
    _ = client.recv(1024)
    client.send(b"last")
    r = client.recv(1024000)
    r = r.decode()
    # print(r)
    r = json.loads(r)
    return r

def getDataOneByOne(ip=IP,port=PORT):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((ip,port))
    _ = client.recv(1024)
    client.send(b"listlast")
    r = client.recv(102400)
    r = r.decode()
    r = json.loads(r)
    # print(r["data"])
    l = []
    for each in r["data"]:
        l.append(each[0])
    data = []
    for each in l:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, port))
            _ = client.recv(1024)
            client.send(("last "+each).encode())
            r = client.recv(102400)
            r = r.decode()
            r = json.loads(r)["data"]
            data.append(r)
        except:
            pass
    return {"data":data}


def transformToDataType(data):
    if isinstance(data,list):
        r = []
        for each in data:
            r.append(transformToDataType(each))
        return r
    if isinstance(data,dict):
        if "name" in data and "value" in data:
            new = DataType(name=data["name"],value=data["value"])
            new.type == type(new.value)
            new.setDataDate(data["dataDate"])
            new.setDataTime(data["dataTime"])
            new.setTimeStamp(data["timeStamp"])
            new.setValueType(data["valueType"])
            new.setInfo(data["info"])
            new.setDataSource(data["dataSource"])
            new.setUnit(data["unit"])
            return new
    return None

def getEmail_From_Server(ip=IP,port=PORT):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    _ = client.recv(1024)
    client.send(b"getemail")
    r = client.recv(102400)
    r = r.decode()
    r = json.loads(r)
    if r["result"]=="success":
        return r["email"]
    else:
        return None

def getLine_From_Server(ip=IP,port=PORT):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))
    _ = client.recv(1024)
    client.send(b"getline")
    r = client.recv(102400)
    r = r.decode()
    r = json.loads(r)
    return r



if __name__ == '__main__':
    # r = getData()
    # print(r)
    # data = r["data"]
    # for each in data:
    #     print(each)
    #     print(transformToDataType(each))
    # print(getEmail_From_Server())
    # print(getLine_From_Server())
    r = getDataOneByOne()
    print(r)
