import time,pickle,os,base64,config
from threading import Thread
from dataSource.DiYiGOLD import getUSDtoCNY,getLondonGold
from dataSource.GoldAndSliver import get_data as getGoldSliver
from dataSource.oil import get as getOil
from dataSource.SinaData import get_data,getUSD,getLondonAg,getLondonAU
from dataSource.USA_no_farm_payrolls import getNoFarmPayrolls_USA
from dataSource.AGTDfromSINA import getAGTD
from dataSource.AUTDfromSINA import getAUTD
from getData import get_data_from_server
from Moudle.dataType import DataType
from Moudle.systemTime import getWeekDay
from MySQLServer.mysql_server import mySQL_Server
import json

# 数据获取源函数
dataFunction = [getUSDtoCNY,getLondonGold,get_data,getOil,getUSD,getGoldSliver,getLondonAg,getLondonAU,getAGTD,getAUTD]

# 溢价计算对象
PremiumOBJs = ["Ag(T+D)","Au(T+D)","Au99.99","黄金延期","白银延期"]

class runFunction(Thread):

    def __init__(self, threadID):
        Thread.__init__(self)
        self.threadID = threadID

    def initFunction(self,f):
        self.r = None
        self.f = f

    def run(self) -> None:
        # print(self.f)
        try:
            r = self.f()
        except:
            print("执行程序失败：",self.f)
            r = None
        if r!=None:
            self.r = []
            if isinstance(r,list):
                self.r.extend(r)
            else:
                self.r.append(r)

class DataServer():
    def __init__(self,name="dataServer"):
        """
        self.lastResult结构如下:
        [eachData for DataType or None]
        self.dataPool结构如下：
        [[self.lastResult],[],[],...]
        :param name:
        """
        self.name = name
        self.getDataFunction = []
        self.lastGetDataTimeStamp = None
        self.interval = 60
        self.sleep = 1
        self.getDataMaxTime = 40
        self.lastResult = None
        self.dataPool = []
        self.saveLength = 10
        self.running = True
        self.showDetail = True
        self.dealLastResultFunction = []
        self.dealLastResultByThread = True
        self.mySQL_Server = mySQL_Server()
        self.stop = False
        self.getDataFromDataServer = False
        self.dataServerIP = get_data_from_server.IP
        self.dataServerPort = get_data_from_server.PORT
        self.USDtoCNY = 7.0859
        self.premiumObjs = PremiumOBJs
        self.oz_g = 28.3495231
        self.removeNoneValue = True
        self.emailAndLineObj = None

    def setUSDtoCNY(self,data=None):
        if isinstance(data,float) or isinstance(data,int):
            if isinstance(data,int):
                data = float(data)
            if data>0:
                self.USDtoCNY = data
                return 0
        elif isinstance(data,DataType):
            if isinstance(data.value,float):
                if data.value>0:
                    self.USDtoCNY = data
                    return 0
        elif isinstance(data,list):
            for each in data:
                if isinstance(each,DataType):
                    if each.name == "USDtoCNY":
                        if isinstance(each.value,float):
                            if each.value>0:
                                self.USDtoCNY = each.value
                                return 0
        elif data==None:
            self.setUSDtoCNY(self.lastResult)
        return -1

    def addPremiunOBJs(self,name):
        if isinstance(name,str):
            self.premiumObjs.append(name)
        elif isinstance(name,list):
            for each in name:
                self.addPremiunOBJs(each)

    def compute_premium(self,lastResultData=None,re_set_USDtoCNY = True):
        if re_set_USDtoCNY:
            self.setUSDtoCNY()
            # print("重置USDtoCNY")
        if lastResultData==None:
            lastResultData=self.lastResult
        for each in lastResultData:
            if isinstance(each,DataType):
                if each.name in self.premiumObjs:
                    if isinstance(each.value,float) or isinstance(each.value,int):
                        oz_price = each.value*self.oz_g
                        oz_price = oz_price/self.USDtoCNY
                        if each.unit!=None:
                            if isinstance(each.unit,str):
                                if each.unit.lower()=="kg":
                                    oz_price = oz_price/1000
                        else:
                            if each.name=="Ag(T+D)" or each.name=="白银延期":
                                oz_price = oz_price/1000
                        # print(each.name,"ozprice",oz_price,each.unit)
                        if each.info==None:
                            each.info = {"ozprice":oz_price}
                        else:
                            if isinstance(each.info,dict):
                                if "ozprice" in each.info:
                                    each.info["ozprice"] = oz_price
                                else:
                                    each.info.update({"ozprice":oz_price})
                            else:
                                each.info = {"ozprice":oz_price}
                        if each.name=="Ag(T+D)" or each.name=="白银延期":
                            for eachLast in self.lastResult:
                                if isinstance(eachLast,DataType):
                                    if eachLast.name == "伦敦银":
                                        try:
                                            premium = oz_price - eachLast.value
                                            if "premium" in each.info:
                                                each.info["premium"] = premium
                                            else:
                                                each.info.update({"premium":premium})
                                        except:
                                            print("计算AGTD premium失败")
                                        if "premiumLine" in each.info:
                                            each.info["premiumLine"] = eachLast.value
                                        else:
                                            each.info.update({"premiumLine":eachLast.value})

                        elif each.name == "Au(T+D)" or each.name=="黄金延期":
                            for eachLast in self.lastResult:
                                if isinstance(eachLast,DataType):
                                    if eachLast.name == "伦敦金":
                                        try:
                                            premium = oz_price - eachLast.value
                                            if "premium" in each.info:
                                                each.info["premium"] = premium
                                            else:
                                                each.info.update({"premium":premium})
                                        except:
                                            print("计算AGTD premium失败")
                                        if "premiumLine" in each.info:
                                            each.info["premiumLine"] = eachLast.value
                                        else:
                                            each.info.update({"premiumLine":eachLast.value})

                        elif each.name == "Au99.99":
                            for eachLast in self.lastResult:
                                if isinstance(eachLast,DataType):
                                    if eachLast.name == "伦敦金":
                                        try:
                                            premium = oz_price - eachLast.value
                                            if "premium" in each.info:
                                                each.info["premium"] = premium
                                            else:
                                                each.info.update({"premium":premium})
                                        except:
                                            print("计算AU99.99 premium失败")
                                        if "premiumLine" in each.info:
                                            each.info["premiumLine"] = eachLast.value
                                        else:
                                            each.info.update({"premiumLine":eachLast.value})
        return lastResultData

    def registerDataFunction(self,f):
        if isinstance(f,list):
            self.getDataFunction.extend(f)
        else:
            self.getDataFunction.append(f)

    def getNoFarmPayRolls(self):
        return getNoFarmPayrolls_USA()

    # 去除未更新的数据，通过获取数据的时间判断
    def clearRepetition(self,result):
        c = []
        for each in result:
            if isinstance(each,DataType):
                # 增加对空值的去除
                if self.removeNoneValue:
                    if each.value == None:
                        c.append(each.name)
                # 第一次启动的时候lastResult为None
                if self.lastResult==None:
                    return result
                for eachLast in self.lastResult:
                    if isinstance(eachLast,DataType):
                        if each.name == eachLast.name:
                            if each.dataTime == eachLast.dataTime:
                                c.append(each.name)
        if len(c)>0:
            r = []
            for eahc in result:
                if isinstance(eahc,DataType):
                    if eahc.name in c:
                        print("重复数据》》》",eahc.name,eahc.dataDate,eahc.dataTime)
                        pass
                    else:
                        r.append(eahc)
            # print(r)
            return r
        return result

    def ComputeGoldToSliver(self,lastResult=None):
        AuTD = None
        AgTD = None
        LondonGold = None
        LondonSliver = None
        if lastResult==None:
            lastResult = self.lastResult
        for each in lastResult:
            if isinstance(each,DataType):
                if each.name == "Au(T+D)":
                    AuTD = each
                if each.name == "Ag(T+D)":
                    AgTD = each
                if each.name == "伦敦金":
                    LondonGold = each
                if each.name == "伦敦银":
                    LondonSliver = each
        if LondonGold==None:
            for each in lastResult:
                if isinstance(each,DataType):
                    if each.name == "LondonGold":
                        LondonGold = each
        if AuTD == None or AgTD == None:
            pass
        else:
            if isinstance(AuTD.value, float) or isinstance(AuTD.value, int):
                if isinstance(AgTD.value, float) or isinstance(AgTD.value, int):
                    rate = AuTD.value * 1000 / AgTD.value
                    GoldSliverRate = DataType(name="上海金银比", valueType="延期金银比", value=rate,dataDate=AuTD.dataDate,dataTime=AuTD.dataTime,timeStamp=AuTD.timeStamp)
                    lastResult.append(GoldSliverRate)
        if LondonGold !=None and LondonSliver!=None:
            if isinstance(LondonGold.value,float) or isinstance(LondonGold.value,int):
                if isinstance(LondonSliver.value,float) or isinstance(LondonSliver.value,int):
                    rate = LondonGold.value/LondonSliver.value
                    GoldSliverRate = DataType(name="伦敦金银比",valueType="伦敦现货金银比",value=rate,dataDate=LondonGold.dataDate,dataTime=LondonGold.dataTime,timeStamp=LondonGold.timeStamp)
                    lastResult.append(GoldSliverRate)
        return lastResult



    def getData(self):
        wday = getWeekDay()
        if self.lastResult!=None and wday>=6:
            # print(wday)
            return 0
        t = time.time()
        if self.lastGetDataTimeStamp == None:
            self.lastGetDataTimeStamp = 0
        if t-self.lastGetDataTimeStamp<self.interval:
            return -1
        threadList = []
        id = 0
        for each in self.getDataFunction:
            # print(each)
            t = runFunction(id)
            t.initFunction(each)
            threadList.append(t)
            id += 1
        for each in threadList:
            each.start()
        self.lastGetDataTimeStamp = time.time()
        result = []
        for each in threadList:
            each.join(timeout=self.getDataMaxTime)
        for each in threadList:
            if each.r!=None:
                result.extend(each.r)
        # 先对所有结果计算溢价
        try:
            result = self.compute_premium(result)
        except:
            pass
        # 计算金银比
        try:
            result = self.ComputeGoldToSliver(result)
        except:
            pass
        # 注意这里要对result进行copy之后传入clearRepetition，否则remov函数会修改result，即便result只是在这里被引用
        # 保存的数据会清除重复，但是显示的数据不会
        self.dataPool.append(self.clearRepetition(result.copy()))
        self.lastResult = result
        if self.showDetail:
            print("获取数据:")
            for each in result:
                print(each.name,":",each.value,"  ",each.dataTime)
        # self.lastResult = self.clearRepetition(result)

        # 保存新的
        Thread(target=self.saveToDataBase).start()
        Thread(target=self.dealLastResult).start()

    def getEmailFromSercer(self,obj=None):
        try:
            obj = self.emailAndLineObj
            email = get_data_from_server.getEmail_From_Server()
            # print(email)
            if obj!=None:
                try:
                    obj.emailAddress = email
                except:
                    pass
        except:
            print("error:","获取服务器email数据失败")
        # return email
        # try:
        #     print(obj.emailAddress)
        # except:
        #     pass

    def getLineFromServer(self,obj=None):
        try:
            obj = self.emailAndLineObj
            line = get_data_from_server.getLine_From_Server()
            # print(line)
            if obj!=None:
                try:
                    obj.object_ = line
                except:
                    pass
        except:
            print("error:","获取服务器提醒线数据失败！")
        # return line
        # try:
        #     print(obj.object_)
        # except:
        #     pass

    def getDataFromServer(self):
        lastResut=None
        try:
            # r = get_data_from_server.getData(self.dataServerIP,self.dataServerPort)
            r = get_data_from_server.getDataOneByOne(self.dataServerIP,self.dataServerPort)
            if r==None:
                return
            lastResut = []
            if self.lastResult == None:
                self.lastResult = []
                for each in r["data"]:
                    trdata = get_data_from_server.transformToDataType(each)
                    # print(trdata)
                    if trdata!=None:
                        lastResut.append(trdata)
                        # self.lastResult.append(trdata)
            else:
                for each in r["data"]:
                    exists = False
                    for eachLast in self.lastResult:
                        # print(eachLast)
                        if eachLast.name == each["name"]:
                            exists = True
                            # if each["timeStamp"]==None:
                            #     print(each)
                            if eachLast.timeStamp<each["timeStamp"]:
                                trdata = get_data_from_server.transformToDataType(each)
                                if not trdata==None:
                                    lastResut.append(trdata)
                                # lastResut.append(get_data_from_server.transformToDataType(each))
                    if not exists:
                        trdata = get_data_from_server.transformToDataType(each)
                        if trdata!=None:
                            lastResut.append(trdata)
                        # lastResut.append(get_data_from_server.transformToDataType(each))
            # print(len(lastResut))
        except:
            print("eeror:","获取服务器last数据失败！")
        if self.getDataFromDataServer:
            Thread(target=self.getEmailFromSercer).start()
            Thread(target=self.getLineFromServer).start()
        if lastResut!=None:
            if len(lastResut)>0:
                self.lastResult = lastResut
                self.dataPool.append(self.lastResult)
                Thread(target=self.saveToDataBase).start()
                Thread(target=self.dealLastResult).start()

    def saveToDataBase(self,force=False):
        if len(self.dataPool)>=self.saveLength or force:
            for each in self.dataPool:
                for eachData in each:
                    fileName = self.getFileName(eachData)
                    dirPath = config.DataBase+"Original/"
                    # dirPath = os.path.join(config.DataBase,"Original/").replace("\\","/")
                    if os.path.exists(dirPath):
                        pass
                    else:
                        os.makedirs(dirPath)
                    filePath = os.path.join(dirPath,fileName).replace("\\","/")
                    saveData = pickle.dumps(eachData)
                    saveData = base64.b64encode(saveData)
                    saveData = saveData.decode()
                    # print(saveData)
                    if not os.path.exists(filePath):
                        f = open(filePath,"w")
                    else:
                        f = open(filePath,"a")
                    f.write(json.dumps({
                        "stamp":eachData.timeStamp,
                        "date":eachData.dataDate,
                        "time":eachData.dataTime,
                        "value":eachData.value,
                        "name":eachData.name,
                        "data":saveData,
                    }))
                    f.write("\n")
                    f.close()
                    if self.showDetail:
                        print("saveToDataBase:",eachData.name)
            self.dataPool = []

    def saveToMysql(self):
        pass

    def saveDataToTable(self,data):
        dataBase = data.name
        r = self.mySQL_Server.judgeDtataBaseExist(dataBase)
        if not r:
            self.mySQL_Server.createDataBase(dataBase)
        self.mySQL_Server.useDataBase(dataBase)
        table = data.dataDate
        if isinstance(table,str):
            table = table.replace("-","_")
        else:
            t = time.localtime()
            t = time.strftime("%Y_%m_%d", t)
            table = t
        r = self.mySQL_Server.judgeTableExist(table)
        if not r:
            sql = """CREATE TABLE IF NOT EXISTS {0}(
                        Name CHAR [20],
                        Value FLOAT ,
                        Date CHAR [10],
                        Time CHAR [10],
                        Info LONGTEXT,
                        Stamp FLOAT ,
                        );""".format(table)
            self.mySQL_Server.excute(sql)
            self.mySQL_Server.commit()
        sql = """
        
        """

    def getFileName(self,dataType):
        if isinstance(dataType,DataType):
            t = dataType.dataDate
            if isinstance(t,str):
                t = t.replace("-","_")
            else:
                t = time.localtime()
                t = time.strftime("%Y_%m_%d",t)
            fileName = dataType.name+" "+t
            return fileName+".tbs"
        else:
            raise ValueError("数据类型错误，不是DataType类型无法获取数据名称生成文件名")

    def run(self):
        self.start()

    def start(self):
        while(self.running):
            if self.getDataFromDataServer:
                self.getDataFromServer()
                # try:
                #     self.getDataFromServer()
                # except:
                #     print("error:获取服务器数据失败")
                time.sleep(10)
            else:
                self.getData()
            if isinstance(self.sleep,float) or isinstance(self.sleep,int):
                if self.sleep>0:
                    time.sleep(self.sleep)
            while(self.stop):
                time.sleep(1)
            # print(self.lastResult)

    def dealLastResult(self):
        for eachFunction in self.dealLastResultFunction:
            if self.dealLastResultByThread:
                Thread(target=eachFunction,args=(self.lastResult,)).start()
            else:
                eachFunction(self.lastResult)

    def getLastDataList(self):
        l = []
        for each in self.lastResult:
            if each!=None:
                l.append([each.name,each.value,each.dataTime,each.dataDate])
        return l

    def getDataFromLastResult(self,name=None):
        r = []
        for each in self.lastResult:
            if each!=None:
                if each.name == name:
                    r.append(each.Dict)
                elif name==None:
                    r.append(each.Dict)
        return r
    def getLastResult(self):
        r = []
        for each in self.lastResult:
            if each!=None:
                r.append(each.Dict)
        return r

    def addDealLastResulFunction(self,f):
        if isinstance(f,list):
            self.dealLastResultFunction.extend(f)
        else:
            self.dealLastResultFunction.append(f)

    def getLastResultDataByName(self,name):
        r = []
        if isinstance(name,str):
            for each in self.lastResult:
                if isinstance(each,DataType):
                    if each.name == name:
                        r.append(each)
        if len(r)>0:
            return r
        else:
            return None

if __name__ == '__main__':
    os.chdir("../")
    # r = getLondonGold()
    # print(r)
    # data = pickle.dumps(r)
    # strdata = base64.b64encode(data)
    # print(strdata)
    # r = base64.b64decode(strdata)
    # print(pickle.loads(r))
    data = DataServer()
    data.registerDataFunction(dataFunction)
    data.start()