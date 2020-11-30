import os,json,pickle,base64
from Moudle.dataType import DataType

DataBaseDIR = "../FileWebDIR/TradeHelperDataBase/Original/"

class Compute_Premium():
    def __init__(self,dataBaseDir=DataBaseDIR,obj="Ag(T+D)",InternationalOBJ = "伦敦银",savePath="./"):
        self.dataBaseDir = dataBaseDir
        self.obj = obj
        self.internationalObj = InternationalOBJ
        self.fileList=None
        self.oz_g = 28.3495231
        self.USDtoCNYrate = None
        self.date = None
        self.savePath = savePath

    def getAllFileList(self):
        files = {}
        for each in os.listdir(self.dataBaseDir):
            if each.split(".")[-1] == "tbs":
                name = each.split(" ")[0]
                if name in files:
                    files[name].append(each)
                else:
                    files.update({name:[each]})
        return files

    def getFileList(self):
        files = self.getAllFileList()
        if self.obj in files:
            self.fileList = files
            return self.fileList
        else:
            return None

    def readOriginalDataFromFile(self,path,date=None,loads=False):
        if date!=None:
            path = path+" "+date+".tbs"
        if os.path.exists(path):
            pass
        else:
            path = os.path.join(self.dataBaseDir,path).replace("\\","/")
        if not os.path.exists(path):
            return -1
        else:
            data = []
            with open(path,"r") as f:
                for each in f.read().split("\n"):
                    if each!="":
                        if loads:
                            data.append(pickle.loads(base64.b64decode(json.loads(each)["data"])))
                        else:
                            data.append(json.loads(each))
            return data

    def getData(self):
        if self.fileList==None:
            self.getFileList()
        obj_files = self.fileList[self.obj]
        usdTocny_files = self.fileList["USDtoCNY"]

    def getDate(self,files):
        if isinstance(files,str):
            return files.split(" ")[1].split(".")[0]
        elif isinstance(files,list):
            dates = []
            for each in files:
                date = self.getDate(each)
                if date!=None:
                    dates.append(date)
            return dates
        elif isinstance(files,dict):
            dates = {}
            for each in files:
                date = self.getDate(files[each])
                if date!=None:
                    dates.update({each:date})
        return None

    def getStamp(self,data):
        if isinstance(data,dict):
            if "stamp" in data:
                return data["stamp"]
            else:
                stamps = {}
                for each in data:
                    stamp = self.getStamp(data[each])
                    stamps.update({each:stamp})
                return stamps
        elif isinstance(data,DataType):
            return data.timeStamp
        elif isinstance(data,list):
            stamps = []
            for each in data:
                stamp = self.getStamp(each)
                if stamp!=None:
                    stamps.append(stamp)
        return None

    def getUSDtoCNYbyStamp(self,USDtoCNY_Datas,stamp):
        # 二分法查找
        start = 0
        # end = len(USDtoCNY_Datas)
        try:
            end = len(USDtoCNY_Datas)
        except:
            return -1
        index = (end-start)//2+start
        while(True):
            # print(USDtoCNY_Datas[index])
            if USDtoCNY_Datas[index]["stamp"]>stamp:
                end = index
            elif USDtoCNY_Datas[index]["stamp"]==stamp:
                # print("search stamp:", USDtoCNY_Datas[index]["stamp"])
                return USDtoCNY_Datas[index]["value"]
            else:
                start = index
            index = (end-start)//2+start
            # print(start,end)
            if end<=start or end-start==1:
                # print("search stamp:", USDtoCNY_Datas[index]["stamp"])
                return USDtoCNY_Datas[index]["value"]
                # print("search stamp:",USDtoCNY_Datas[index]["stamp"])

    def PackResult(self,data):
        if isinstance(data,DataType):
            data = pickle.dumps(data)
            data = base64.b64encode(data).decode()
            # data = [data]
            return data
        elif isinstance(data,list):
            datas = []
            for each in data:
                r = self.PackResult(each)
                if r!=None:
                    datas.append(r)
            return datas
        elif isinstance(data,dict):
            data = json.dumps(data)
            return data
        return None


    def saveResult(self,data,splitBydate=False,path=None,date=None):
        data  = self.PackResult(data)
        if path==None:
            path = self.savePath
        if splitBydate and date!=None:
            if isinstance(date,str):
                name = self.obj+" "+date+".tbs"
                path = os.path.join(path,name).replace("\\","/")
                if os.path.exists(path):
                    f = open(path,"a")
                else:
                    f = open(path,"w")
            else:
                raise TypeError("date must be str")
        else:
            name = self.obj+".tbs"
            path = os.path.join(path,name).replace("\\","/")
            if not os.path.exists(path):
                f = open(path,"w")
            else:
                f = open(path,"a")
        # print(data)
        for each in data:
            f.write(each+"\n")
        f.close()


    def compute(self):
        if self.fileList==None:
            self.getFileList()
        if self.date==None:
            self.date = self.getDate(files=self.fileList[self.obj])
        for each in self.date:
            result = []
            obj_datas = self.readOriginalDataFromFile(self.obj,date=each,loads=True)
            USDtoCNY_datas = self.readOriginalDataFromFile("USDtoCNY",date=each,loads=False)
            InternationalDatas = self.readOriginalDataFromFile(self.internationalObj,date=each,loads=False)
            # print(InternationalDatas)
            for eachData in obj_datas:
                if isinstance(eachData,DataType):
                    stamp = eachData.timeStamp
                    # print("obj stamp:",stamp)
                    usd_to_cny_rate = self.getUSDtoCNYbyStamp(USDtoCNY_datas,stamp)
                    self.USDtoCNYrate = usd_to_cny_rate
                    if isinstance(eachData.value,float) or isinstance(eachData.value,int):
                        oz = eachData.value*self.oz_g/self.USDtoCNYrate
                        if self.obj=="Ag(T+D)":
                            oz = oz/1000
                        eachData.info.update({"oz":oz})
                        internationalValue = self.getUSDtoCNYbyStamp(InternationalDatas,stamp)
                        if isinstance(internationalValue,float) or isinstance(internationalValue,int):
                            if internationalValue<0:
                                d = None
                            else:
                                d = oz-internationalValue
                            eachData.info.update({"premium":d})
                        else:
                            eachData.info.update({"premium":None})
                    result.append(eachData)
            self.saveResult(result)


if __name__ == '__main__':
    os.chdir("../")
    t = Compute_Premium()
    t.compute()