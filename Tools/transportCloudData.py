import os,json,socket,threading

class CloudeDataTransport():
    def __init__(self,ip="0.0.0.0",port=8001,dataBase="./CloudData"):
        self.ip=ip
        self.port=port
        self.dataBase = dataBase
        self.conn = None
        self.saving = False


    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.ip,self.port))
        r = self.conn.recv(1024)
        try:
            r = r.decode()
            return r
        except:
            return r

    def transport(self,name,date=None,saveName=None,savePoolLength=1000):
        if date!=None:
            order = "transport "+name+" "+date
        else:
            order = "transport "+name
        if self.conn==None:
            _ = self.connect()
        self.conn.send(order.encode())
        # print(order)
        savePool = []
        while(True):
            r = self.conn.recv(1024000)
            r = r.decode()
            r = json.loads(r)
            # print(r)
            if r["num"]<0:
                break
            else:
                self.conn.send(b"get")
            if saveName==None:
                r = json.loads(r["data"])
                f = name+" "+r["date"].replace("-","_")+".tbs"
                savePool.append([f,r])
            if len(savePool)>savePoolLength:
                if self.saving==False:
                    threading.Thread(target=self.saveData,args=(savePool,)).start()
                    savePool=[]

    def saveData(self,datas):
        self.saving = True
        if not os.path.exists(self.dataBase):
            os.mkdir(self.dataBase)
        for each in datas:
            path = os.path.join(self.dataBase,each[0]).replace("\\","/")
            if os.path.exists(path):
                f = open(path,"a")
            else:
                f = open(path,"w")
            f.write(json.dumps(each[1])+"\n")
        self.saving = False

    def downloadAllData(self):
        if self.conn==None:
            self.connect()
        self.conn.send(b"gethistorylist")
        r = self.conn.recv(102400)
        tickers = json.loads(r)["data"]
        self.conn.close()
        self.conn=None
        for each in tickers:
            print("download",each)
            self.transport(each)
            try:
                self.conn.close()
                self.conn = None
            except:
                pass

if __name__ == '__main__':
    t = CloudeDataTransport(ip="111.230.177.71")
    t.downloadAllData()