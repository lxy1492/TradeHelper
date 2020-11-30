import json,sys,os,pickle,base64,time,config
from threading import Thread
from getData.getData import DataServer,dataFunction
from API.APIServer import API_Server
from Moudle.dataType import DataType
from monitor.monitor_price import PriceMonitor
from getData.getHistory import getHistoryData
from manager.viewDataBase import DB_manager
from manager import transPortData
from voiceNotition import voice_notition

class DataHelper(API_Server):
    def __init__(self,name="datahelper"):
        API_Server.__init__(self,name=name)
        self.data = DataServer("getData")
        self.name = name
        self.dataThreadID = None
        self.priceMonitor = PriceMonitor()
        self.data.addDealLastResulFunction(self.priceMonitor.judge)
        # self.data.addDealLastResulFunction(self.data.compute_premium)
        self.priceMonitor.dealLineFunction.extend([self.priceMonitor.sendEmailMessage])
        self.data.getDataFromDataServer = False
        self.data.emailAndLineObj = self.priceMonitor
        self.voiceNotition = voice_notition(data=self.data)
        # self.data.addDealLastResulFunction(self.voiceNotition.run)

    def startGetData(self):
        self.data.registerDataFunction(dataFunction)
        self.data.start()

    def exit(self):
        print("保存数据并关闭")
        self.data.saveToDataBase(force=True)
        self.data.running = False
        try:
            sys.exit(0)
        except:
            os._exit(0)

    def run(self):
        self.dataThreadID = Thread(target=self.startGetData)
        self.dataThreadID.start()
        self.Listen()
        while (True):
            self.getConnection()

    def dealConnection(self,conn,addr):
        hello = "this is " + self.name
        conn.send(hello.encode())
        r = conn.recv(10240)
        # print(r)
        try:
            r = r.decode()
        except:
            try:
                r = r.decode("gbk")
            except:
                try:
                    r = r.decode("gb2312")
                except:
                    r = None
        if r!=None:
            r_lower = r.lower()
        print("deal connection:", addr," for order:",r)
        if r_lower=="last":
            # 这里返回的是data的Dict
            data = self.data.getLastResult()
            # print(type(data))
            # for each in data:
            #     print(each)
            data = json.dumps({
                "result":"success",
                "data":data,
            })
            data = data.encode()
            conn.send(data)
        elif "last " in r_lower:
            args = r.split(" ")
            while("" in args):
                args.remove("")
            name = args[1]
            data = None
            for each in self.data.lastResult:
                if isinstance(each,DataType):
                    if each.name==name:
                        data = {"result":"success","info":name,"data":each.Dict}
                        break
            if data==None:
                data = {"resut":"failed","info":"no "+name+" data in last result","data":None}
            conn.send(json.dumps(data).encode())
            return 0
        elif r_lower=="listlast":
            data = self.data.getLastDataList()
            data = json.dumps({
                "result":"success",
                "data":data,
            })
            data = data.encode()
            conn.send(data)
        elif "getlast" in r_lower:
            if " " in r:
                name = r.split(" ")[-1]
                data = self.data.getDataFromLastResult(name)
                data = json.dumps({
                    "result":"success",
                    "data":data
                })
                data = data.encode()
                conn.send(data)
            else:
                conn.send(json.dumps({"result":"确少参数"}).encode())
        elif "shutdown"==r_lower:
            conn.send(json.dumps({"result":"accept"}).encode())
            self.exit()
        elif "save"==r_lower:
            self.data.saveToDataBase(force=True)
            conn.send(json.dumps({"result": "accept"}).encode())
        elif "savelength " in r_lower:
            try:
                l = int(r.split(" ")[-1])
                self.data.saveLength = l
                conn.send(json.dumps({"result": "accept"}).encode())
            except:
                print("处理savelength错误:",r)
                conn.send(json.dumps({"result": "error"}).encode())
        elif "originallist" == r_lower:
            # path = "./DataBase/Original/"
            path = config.DataBase+"/Original/"
            list_ = []
            for each in os.listdir(path):
                if os.path.isfile(os.path.join(path,each)):
                    if each.split(".")[-1].lower()=="tbs":
                        name = each.split(" ")[0]
                        if not name in list_:
                            list_.append(name)
            conn.send(json.dumps({"result":"success","list":list_}).encode())
        elif "getoriginalbystamp " in r_lower:
            name = r.split(" ")[1]
            stamp = r.split(" ")[2]
            try:
                stamp = float(stamp)
            except:
                conn.send(json.dumps({"result": "failed", "info": "无法解析stamp"}).encode())
                return -1
            history = getHistoryData()
            data = history.getOriginalByStamp(name,stamp)
            conn.send(json.dumps({"result": "success", "info": "", "data": data}).encode())
        elif "gethistorybystamp " in r_lower:
            name = r.split(" ")[1]
            stamp = r.split(" ")[2]
            try:
                stamp = float(stamp)
            except:
                conn.send(json.dumps({"result":"failed","info":"无法解析stamp"}).encode())
                return -1
            history = getHistoryData()
            data = history.getDataByStamp(name,stamp)
            r = []
            for each in data:
                r.append(each.Dict)
            conn.send(json.dumps({"result":"success","info":"","data":r}).encode())
        elif "gethistorylist" == r_lower:
            history = getHistoryData()
            history.getDataFileList()
            conn.send(json.dumps({"result":'success',"data":history.fileList}).encode())
        elif "gethistorylist " in r_lower:
            name = r.split(" ")[1]
            history = getHistoryData()
            r = history.getDataFileList()
            if name in r:
                conn.send(json.dumps({"result":"success","data":r[name],"info":""}).encode())
            else:
                conn.send(json.dumps({"result":"failed","info":"no such file:"+name}).encode())
        elif "gethistorydatabydate " in r_lower:
            obj = r.split(" ")
            name = obj[1]
            date = obj[2]
            if len(obj)==4:
                time_ = obj[3]
            else:
                time_ = None
            history = getHistoryData()
            # print(date,time_)
            r,info = history.getHistoryDataByDate(name,date,time_)
            if r==None:
                return_data = {
                    "result":"failed",
                    "info":info,
                }
            else:
                return_data = {
                    "result":"success",
                    "info":info,
                    "data":r,
                }
            conn.send(json.dumps(return_data).encode())
        elif "gethistorybydate " in r_lower:
            name = r.split(" ")[1]
            date = r.split(" ")[2].replace("-","_")
            time_ = r.split(" ")[3]
            if ":" in time_:
                pass
            else:
                try:
                    time_ = float(time_)
                except:
                    pass
            fileName = os.path.join(config.DataBase+"Original/",name+" "+date+".tbs")
            # print(fileName)
            if os.path.exists(fileName):
                with open(fileName,"r") as f:
                    r = []
                    for each in f.read().split("\n"):
                        select = True
                        if each!="":
                            try:
                                data = json.loads(each)
                                if isinstance(time_,str):
                                    time_ = time_.split(":")
                                    datatime = data["time"].split(":")
                                    # print(datatime)
                                    for i in range(len(time_)):
                                        if int(datatime[i])!=int(time_[i]):
                                            select = False
                                    if select:
                                        r.append(data)
                                elif isinstance(time_,float):
                                    if (data["stamp"]-time_)**2<360:
                                        r.append(data)
                            except:
                                pass
                    re = []
                    for each in r:
                        try:
                            re.append(pickle.loads(base64.b64decode(each["data"])).Dict)
                        except:
                            re.append(each)
                    if len(re)>0:
                        conn.send(json.dumps({"result":'success',"data":re}).encode())
                    else:
                        t = time.localtime()
                        date = date.split("_")
                        r = []
                        if t.tm_year == int(date[0]) and t.tm_mon == int(date[1]) and t.tm_mday == int(date[2]):
                            if isinstance(time_, str):
                                time_ = time_.split(":")
                                if len(time_) >= 2:
                                    if t.tm_hour == int(time_[0]):
                                        for each in self.data.lastResult:
                                            if each.name == name:
                                                if each.dataTime.split(":")[1] == time_[1]:
                                                    r.append(each.Dict)
                            elif isinstance(time_, float):
                                for each in self.data.lastResult:
                                    if each.name == name:
                                        if (each.timeStamp - time_) ** 2 < 360:
                                            r.append(each.Dict)
                        if len(r) > 0:
                            conn.send(json.dumps({"result": "success", "data": r}).encode())
                        else:
                            # print(date,time_)
                            conn.send(json.dumps({"result": "failed","info":"没有获取到符合条件的数据"}).encode())
            else:
                t = time.localtime()
                date = date.split("_")
                r = []
                if t.tm_year == int(date[0]) and t.tm_mon == int(date[1]) and t.tm_mday == int(date[2]):
                    if isinstance(time_,str):
                        time_ = time_.split(":")
                        if len(time_)>=2:
                            if t.tm_hour == int(time_[0]):
                                for each in self.data.lastResult:
                                    if each.name == name:
                                        if each.dataTime.split(":")[1] == time_[1]:
                                            r.append(each.Dict)
                    elif isinstance(time_,float):
                        for each in self.data.lastResult:
                            if each.name == name:
                                if (each.timeStamp-time_)**2<360:
                                    r.append(each.Dict)
                if len(r)>0:
                    conn.send(json.dumps({"result":"success","data":r}).encode())
                else:
                    conn.send(json.dumps({"result":"failed"}).encode())
        elif "setline " in r_lower:
            name = r.split(" ")[1]
            line = r.split(" ")[2]
            try:
                line = float(line)
            except:
                pass
            if isinstance(line,float):
                priceNow = None
                for each in self.data.lastResult:
                    if each.name == name:
                        priceNow = each.value
                        break
                self.priceMonitor.setLine(name,line,priceNow)
            conn.send(json.dumps({"result":"accept"}).encode())
        elif "getline" == r_lower:
            conn.send(json.dumps(self.priceMonitor.object_).encode())
        elif "getline " in r_lower:
            name = r.split(" ")[-1]
            if name in self.priceMonitor.object_:
                conn.send(json.dumps(self.priceMonitor.object_[name]).encode())
            else:
                conn.send(json.dumps({"result":"no such object"}).encode())
        elif "addemail " in r_lower:
            name = r.split(" ")[1]
            add = r.split(" ")[2]
            if self.priceMonitor.addEmailAddr(name,add)>=0:
                conn.send(json.dumps({"result":"accept"}).encode())
            else:
                conn.send(json.dumps({"result":"failed"}).encode())
        elif "getemail" == r_lower:
            conn.send(json.dumps({"result":"success","email":self.priceMonitor.emailAddress}).encode())
        elif "emailnotice " in r_lower:
            notice = r_lower.split(" ")[-1]
            if notice in ["off","shutdown","exit","end"]:
                self.priceMonitor.emailNotice = False
                conn.send(json.dumps({"result":"email notice set off"}).encode())
            elif notice in ["on","start"]:
                self.priceMonitor.emailNotice = True
                conn.send(json.dumps({"result": "email notice set on"}).encode())
            else:
                conn.send(json.dumps({"result": "no operation for "+r}).encode())
        elif "getdatapool" == r_lower:
            dataPool = {}
            for eachlastresult in self.data.dataPool:
                for each in eachlastresult:
                    # print (each)
                    if isinstance(each, DataType):
                        if each.name in dataPool:
                            thedata = {"name":each.name,"value":each.value,"valuetype":each.valueType,"date":each.dataDate,"time":each.dataTime,"stamp":each.timeStamp,"source":each.dataSource}
                            dataPool[each.name].append(thedata)
                        else:
                            thedata = {"name":each.name,"value":each.value,"valuetype":each.valueType,"date":each.dataDate,"time":each.dataTime,"stamp":each.timeStamp,"source":each.dataSource}
                            dataPool.update({each.name:[thedata]})
            conn.send(json.dumps({"result":"success","data":dataPool}).encode())
        elif "cleanallline" == r_lower:
            self.priceMonitor.cleanAllLine()
            conn.send(json.dumps({"result":"success","info":"清除所有提醒线"}).encode())
        elif "cleanline " in r_lower:
            obj = r.split(" ")
            if len(obj)==3:
                try:
                    self.priceMonitor.cleanLine(obj[1],float(obj[2]))
                    conn.send(json.dumps({"result": "success", "info": "清除提醒线" + r}).encode())
                except:
                    conn.send(json.dumps({"result": "failed", "info": "指令格式错误" + r}).encode())
            elif len(obj)==2:
                self.priceMonitor.cleanLine(obj[1])
                conn.send(json.dumps({"result": "success", "info": "清除提醒线" + r}).encode())
            else:
                conn.send(json.dumps({"result": "failed", "info": "指令错误" + r}).encode())
        elif "cleanallline " in r_lower:
            try:
                line = float(r.split(" ")[1])
                self.priceMonitor.cleanAllLine(line)
                conn.send(json.dumps({"result": "success", "info": "清除所有提醒线" + r}).encode())
            except:
                conn.send(json.dumps({"result": "failed", "info": "解析cleanallline参数失败"}).encode())
        elif "cleanfalseline" == r_lower:
            self.priceMonitor.cleanFalseLine()
            conn.send(json.dumps({"result": "success", "info": "清除所有已触及的提醒线"}).encode())
        elif "removeemail" == r_lower:
            self.priceMonitor.cleanEmail()
            conn.send(json.dumps({"result": "success", "info": "清除所有提醒邮箱地址"}).encode())
        elif "removeemail " in r_lower:
            obj = r.split(" ")[" "]
            if "@" in obj:
                self.priceMonitor.cleanEmail(obj)
                conn.send(json.dumps({"result": "success", "info": "清除"+obj}).encode())
            else:
                conn.send(json.dumps({"result": "failed", "info": obj+"不是正确的邮箱格式"}).encode())
        elif "deallinefunction" == r_lower:
            f = []
            for each in self.priceMonitor.dealLineFunction:
                f.append(str(each))
            conn.send(json.dumps({"result":f}).encode())
        elif "emailnoticestate" == r_lower:
            if self.priceMonitor.emailNotice:
                conn.send(json.dumps({"result": "on"}).encode())
            else:
                conn.send(json.dumps({"result": "off"}).encode())
        elif "nofarmpayrolls" == r_lower:
            r = self.data.getNoFarmPayRolls()
            conn.send(json.dumps({"result":"success","data":r}).encode())
        elif "usedataserver" == r_lower:
            self.data.getDataFromDataServer = True
            conn.send(json.dumps({"result":"success","IP":self.data.dataServerIP,"port":self.data.dataServerPort}).encode)
        elif "dataserverhost" == r_lower:
            conn.send(json.dumps({"result":"success","IP":self.data.dataServerIP,"port":self.data.dataServerPort}).encode)
        elif "setdataserverhost " in r_lower:
            host = r.split(" ")
            if len(host)>3:
                ip = host[1]
                port = host[2]
                if len(ip.split("."))==4:
                    try:
                        port = int(port)
                    except:
                        pass
                    if isinstance(port,int):
                        self.data.dataServerIP = ip
                        self.data.dataServerPort = port
                        conn.send(json.dumps({"result": "success", "IP": self.data.dataServerIP,
                                              "port": self.data.dataServerPort}).encode())
                    else:
                        conn.send(json.dumps({"result": "failed", "info":"端口参数解析错误","port":port,"ip":ip}).encode())
                else:
                    conn.send(json.dumps({"result": "failed", "info": "IP参数解析错误", "port": port, "ip": ip}).encode())
            else:
                conn.send(json.dumps({"result": "failed", "info": "参数解析错误","order":r}).encode())
        elif "transporthistory" == r_lower:
            transPortData.transportAllHistory(conn)
        elif "transport " in r_lower:
            obj  = r.split(" ")
            if len(obj)==2:
                transPortData.transportData(conn,obj[1])
            elif len(obj)==3:
                transPortData.transportForDate(conn,obj[1],obj[2])
        elif "gethistoryinfo" in r_lower:
            s = r.split(" ")
            while("") in s:
                s.remove("")
            name = None
            date = None
            length = None
            # print(s)
            if len(s)==1:
                name = None
                date = None
                length = None
            elif len(s)==2:
                name = s[1]
                date = None
                length = None
            elif len(s)==3:
                name = s[1]
                date = None
                length = None
                for each in ["-","_","\\","/",".",":",";"]:
                    if each in s[2]:
                        date = s[2]
                        break
                if date==None:
                    try:
                        _ = int(s[2])
                        if len(s[2])==8:
                            date = s[2]
                    except:
                        date = None
                if date==None:
                    try:
                        length = int(s[2])
                    except:
                        pass
            elif len(s)==4:
                name = s[1]
                date = None
                length = None
                for each in ["-","_","\\","/",".",":",";"]:
                    if each in s[2]:
                        date = s[2]
                        break
                if date!=None:
                    try:
                        length = int(s[3])
                    except:
                        length = None
                else:
                    if len(s[2])==8:
                        try:
                            _ = int(s[2])
                            date = s[2]
                            try:
                                length = int(s[3])
                            except:
                                pass
                        except:
                            date = None
                    else:
                        try:
                            _ = int(s[2])
                            length = int(s[2])
                        except:
                            pass
                        for each in ["-", "_", "\\", "/", ".", ":", ";"]:
                            if each in s[3]:
                                date = s[3]
                                break
            DB = DB_manager()
            # print(name,date,length)
            data = DB.getHistoryInfo(name,date,length)
            # print(data)
            conn.send(json.dumps({"result": "success", "info": "","data":data}).encode())

        elif "getdayinfo" in r_lower:
            s = r.split(" ")
            if len(s)==1:
                name = None
                date = None
            elif len(s)==2:
                name = s[1]
                date = None
            elif len(s)>2:
                name = s[1]
                date = s[2]
            else:
                name = None
                date = None
            DB = DB_manager()
            r = DB.getDayInfo(name,date)
            conn.send(json.dumps({"result": "success", "info": "","data":r}).encode())

        elif "getstamp " in r_lower:
            obj = r.split(" ")[1]
            history = getHistoryData()
            history.getDataFileList()
            if not obj in history.fileList:
                conn.send(json.dumps({"result":"failed","info":"没有"+obj}).encode())
                return -1
            files = history.fileList[obj]
            stamps= []
            for each in files:
                with open(os.path.join(history.originaldatabase,each).replace("\\","/")) as f:
                    for eachLine in f.read().split("\n"):
                        if eachLine!="":
                            stamps.append(json.loads(eachLine)["stamp"])
            conn.send(json.dumps({"result":"success","stamp":stamps,"info":""}).encode())
        elif "getdictfromoriginal " in r_lower:
            original = r.split(" ")[1]
            try:
                try:
                    original = base64.b64decode(original)
                except:
                    conn.send(json.dumps({"result": "failed", "info": "转换base64编码失败", "data": ""}).encode())
                    return -1
                try:
                    data = pickle.loads(original)
                except:
                    conn.send(json.dumps({"result": "failed", "info": "加载数据对象失败", "data": ""}).encode())
                    return -1
                try:
                    dic = data.Dict
                except:
                    conn.send(json.dumps({"result": "failed", "info": "获取字典数据失败", "data": ""}).encode())
                    return -1
                conn.send(json.dumps({"result":"success","info":"转换成功","data":dic}).encode())
            except:
                conn.send(json.dumps({"result":"failed","info":"转换失败","data":""}).encode())
        elif "databaselist" == r_lower:
            db = DB_manager()
            l = db.getFileList()
            if l!=-1:
                if l!=None:
                    if isinstance(l,dict):
                        conn.send(json.dumps(l).encode())
                    else:
                        conn.send(json.dumps({"error": l}).encode())
                else:
                    conn.send(json.dumps({"error": l}).encode())
            else:
                conn.send(json.dumps({"error":l}).encode())
        elif "databasestamp " in r_lower:
            args = r.split(" ")
            name = args[1]
            date = args[2]
            db = DB_manager()
            r = db.getDateANDStamps(name=name,date=date)
            if r!=-1:
                if r!=None:
                    conn.send(json.dumps({"stamp":r,"result":"success"}).encode())
            conn.send(json.dumps({"result":"failed","error":r}).encode())
        elif "databasedata " in r_lower:
            args = r.split(" ")
            name = args[0]
            if len(args)==4:
                date = args[1]
                time_ = args[2]
                db = DB_manager()
                r = db.getDataByTIME(name=name,TIME=[date,time_],dataType="dict")
                conn.send(json.dumps({"result":r}).encode())
            elif len(args)==3:
                stamp = args[1]
                db = DB_manager()
                try:
                    stamp = float(stamp)
                except:
                    conn.send(json.dumps({"error":"解析时间戳参数错误:"+r}).encode())
                    return -1
                r = db.getDataByTIME(name=name,TIME=stamp,dataType="dict")
                conn.send(json.dumps({"result": r}).encode())
            else:
                conn.send(json.dumps({"error": "参数错误:"+r}).encode())
                return -1
        elif "datafrombaseindate " in r_lower:
            name = r.split(" ")[1]
            date = r.split(" ")[2]
            db = DB_manager()
            r = db.getAllDict(name=name,date=date)
            if r==-1:
                conn.send(json.dumps({"result":"failed","error": "无法获取"+name+" "+date+"的数据"}).encode())
                return -1
            elif r==None:
                conn.send(json.dumps({"result":"failed","error": "没有关于"+name+" "+date+"的数据"}).encode())
                return -1
            else:
                l = len(r)
                i = 0
                while(i<l):
                    end = i+10
                    if end>l-1:
                        end = l
                    return_data = r[i:end]
                    i = end
                    if i<l:
                        conn.send(json.dumps({"result":str(i)+"/"+str(l),"data":return_data}).encode())
                        _ = conn.recv(1024)
                    else:
                        conn.send(json.dumps({"result": "success", "data": return_data}).encode())
                return 0
        elif "setremovenone " in r_lower:
            set = r_lower.split(" ")[1]
            if set=="on":
                self.data.removeNoneValue = True
                conn.send(json.dumps({"result": "success", "info": "set on"}))
            elif set=="off":
                self.data.removeNoneValue = False
                conn.send(json.dumps({"result": "success", "info": "set off"}))
            else:
                conn.send(json.dumps({"result":"failed","info":"no such option:"+set}))
        elif "downloaddata " in r_lower:
            transPortData.downloadData(conn,r)
        elif "getagtdfromlondonsliver" in r_lower:
            londonprice = None
            if "getagtdfromlondonsliver " in r_lower:
                data = r.split(" ")[1]
                while("" in data):
                    data.remove("")
                if len(data)>1:
                    try:
                        data = float(data)
                        londonprice = data
                    except:
                        conn.send(json.dumps({"result":"failed","info":"cannot get london sliver price from order:"+r,"data":None}).encode())
                        return -1
            if londonprice==None:
                for each in self.data.lastResult:
                    if isinstance(each,DataType):
                        if each.name=="伦敦银" or each.name=="LondonSLiver":
                            if isinstance(each.value,float) or isinstance(each.value,int):
                                londonprice = each.value
            if londonprice==None:
                conn.send(json.dumps({"result":"failed","info":"cannot get london price from last result","data":None}).encode())
                return -1
            AgTD_price = londonprice*self.data.USDtoCNY*1000/self.data.oz_g
            info = "london sliver price:"+str(londonprice)+";"+"USDtoCNY:"+str(self.data.USDtoCNY)+";"+"oz_g:"+str(self.data.oz_g)
            conn.send(json.dumps({"result":"success","info":info,"data":AgTD_price}).encode())

        elif "computelondonslivertoagtd " in r_lower:
            data = r.split(" ")
            while("" in data):
                data.remove("")
            premium = None
            londonprice = None
            if len(data)<0:
                conn.send(json.dumps(
                    {"result": "failed", "info": "cannot deal the order by split:"+r, "data": None}).encode())
                return -1
            if len(data)==1:
                londonprice=None
                for each in self.data.lastResult:
                    if isinstance(each,DataType):
                        if each.name=="伦敦银" or each.name=="LondonSLiver":
                            if isinstance(each.value,float) or isinstance(each.value,int):
                                londonprice = each.value
                if londonprice==None:
                    conn.send(json.dumps({"result": "failed", "info": "no london sliver price", "data": None}).encode())
                    return -1
                AgTD_price = londonprice * self.data.USDtoCNY * 1000 / self.data.oz_g
                info = "London sliver price:"+str(londonprice)+";USDtoCNY:" + str(self.data.USDtoCNY) + ";" + "oz_g:" + str(self.data.oz_g)
                conn.send(json.dumps({"result": "success", "info": info, "data": AgTD_price}).encode())
                return 0
            elif len(data)==2:
                try:
                    if float(data[1])<8:
                        premium = float(data[1])
                        londonprice = None
                    else:
                        premium = None
                        londonprice = float(data[1])
                    if londonprice==None:
                        for each in self.data.lastResult:
                            if isinstance(each,DataType):
                                if each.name=="伦敦银" or each.name=="LondonSliver":
                                    if isinstance(each.value,float) or isinstance(each.value,int):
                                        londonprice = each.value
                                        break
                    if premium==None:
                        premium=-0.41
                    if londonprice==None:
                        conn.send(json.dumps(
                            {"result": "failed", "info": "cannot get london sliver price from last result", "data": None}).encode())
                        return -1
                    # londonprice = londonprice+premium
                    print(londonprice+premium)
                    ag_price = (londonprice+premium)*1000*self.data.USDtoCNY/self.data.oz_g
                    conn.send(json.dumps({"result":"success","info":"USDtoCNY:"+str(self.data.USDtoCNY)+"; premium:"+str(premium)+"; london sliver price:"+str(londonprice)+";","data":ag_price}).encode())
                    return 0
                except:
                    conn.send(json.dumps({"result": "failed", "info": "cannot get args from "+r, "data": None}).encode())
                    return -1
            elif len(data)>2:
                try:
                    londonprice = float(data[1])
                except:
                    conn.send(
                        json.dumps({"result": "failed", "info": "cannot get london sliver price argument from " + r, "data": None}).encode())
                    return -1
                try:
                    premium = float(data[2])
                except:
                    conn.send(
                        json.dumps({"result": "failed", "info": "cannot get premium argument from " + r, "data": None}).encode())
                    return -1
                # londonprice = londonprice+premium
                ag_price = (londonprice+premium)*self.data.USDtoCNY*1000/self.data.oz_g
                info = "USDtoCNY:"+str(self.data.USDtoCNY)+"; premium:"+str(premium)+"; london sliver price:"+str(londonprice)+";"
                conn.send(json.dumps({"result":'success',"info":info,"data":ag_price}).encode())
                return 0

        elif "londonslivertoagtd" == r_lower:
            LondonSliver = None
            AgTD = None
            for each in self.data.lastResult:
                if isinstance(each,DataType):
                    if each.name == "Ag(T+D)":
                        AgTD = each
                    elif each.name == "伦敦银" or each.name == "LondonSliver":
                        LondonSliver = each
            if LondonSliver==None:
                conn.send(json.dumps({"result":"failed","info":"没有获取到London Sliver","data":None}).encode())
                return -1
            if not isinstance(LondonSliver.value,float) or isinstance(LondonSliver.value,int):
                conn.send(json.dumps({"result": "failed", "info": "无法获取London Sliver实时价格", "data": None}).encode())
                return -1
            premium = None
            if AgTD!=None:
                if "premium" in AgTD.info:
                    try:
                        premium = float(AgTD.info["premium"])
                    except:
                        pass
            # print(AgTD)
            # print(LondonSliver)
            if premium!=None:
                AgTDPrice = (LondonSliver.value+premium)*1000*self.data.USDtoCNY/self.data.oz_g
                info = "LondonSLiver:"+str(LondonSliver.value)+";"+"AgPrice:"+str(AgTD.value)+";"
                info += "USDtoCNY:"+str(self.data.USDtoCNY)+";"
                info += "premium:"+str(premium)+";"+"London date:"+LondonSliver.dataDate+" "+LondonSliver.dataTime+";"
                info += "AgTD date:"+AgTD.dataDate+" "+AgTD.dataTime+";"
                conn.send(json.dumps({"result":"success","info":info,"data":AgTDPrice}).encode())
            else:
                AgTDPrice = LondonSliver.value*1000*self.data.USDtoCNY/self.data.oz_g
                info = "LondonSliver:"+str(LondonSliver.value)+"; USDtoCNY:"+str(self.data.USDtoCNY)+";"
                info += "LondonSliver date:"+LondonSliver.dataDate+" "+LondonSliver.dataTime+";"
                conn.send(json.dumps({"result":"success","info":info,"data":AgTDPrice}).encode())

        elif "getagtdfromlondongold " in r_lower:
            data = r.split(" ")
            while("" in data):
                data.remove("")
            LondonGoldPrice = None
            Rate = None
            if len(data)>1:
                if len(data)==2:
                    try:
                        price = float(data[1])
                        if price<1000:
                            Rate = price
                        else:
                            LondonGoldPrice = price
                    except:
                        pass
                else:
                    for each in data:
                        try:
                            price = float(each)
                            if price<1000:
                                Rate = price
                            else:
                                LondonGoldPrice = price
                        except:
                            pass
            if LondonGoldPrice==None:
                for each in self.data.lastResult:
                    if isinstance(each,DataType):
                        if each.name == "伦敦金" or each.name=="LondonGold":
                            LondonGoldPrice = each.value
                            break
            if Rate==None:
                for each in self.data.lastResult:
                    if isinstance(each,DataType):
                        if each.name == "伦敦金银比":
                            Rate=each.value
            if isinstance(LondonGoldPrice,float) and isinstance(Rate,float):
                LondonSliverPrice  = LondonGoldPrice/Rate
                premium = None
                for each in self.data.lastResult:
                    if isinstance(each,DataType):
                        if each.name=="Ag(T+D)":
                            if "premium" in each.info:
                                premium = each.info["premium"]
                if isinstance(premium,float):
                    # print(premium,LondonSliverPrice)
                    AGTDPrice = ((LondonSliverPrice+premium)*self.data.USDtoCNY*1000)/self.data.oz_g
                    info = "LondonGold:"+str(LondonGoldPrice)+"; LondonSliver:"+str(LondonSliverPrice)+"; Rate:"+str(Rate)+";"
                    info += "premium:"+str(premium)+";USDtoCNY:"+str(self.data.USDtoCNY)
                    conn.send(json.dumps({"result":"success","info":info,"data":AGTDPrice}).encode())
                    return 0
                else:
                    AGTDPrice = (LondonSliverPrice*self.data.USDtoCNY*1000)/self.data.oz_g
                    info = "LondonGold:" + str(LondonGoldPrice) + "; LondonSliver:" + str(
                        LondonSliverPrice) + "; Rate:" + str(Rate) + ";"
                    info += "premium:" + str(premium) + ";USDtoCNY:" + str(self.data.USDtoCNY)
                    conn.send(json.dumps({"result": "success", "info": info, "data": AGTDPrice}).encode())
                    return 0
            else:
                conn.send(json.dumps({"result": "success", "info": "没有获取到LondonGold和Rate", "data": None}).encode())

        else:
            # print(">>>>>>>>>>>>",r_lower)
            conn.send(json.dumps({"result":"no such order!"}).encode())
            return -1
        return 0