import os,json,config,pickle,time,base64
from Moudle.dataType import DataType

class getHistoryData():
    def __init__(self,dataPath=config.DataBase):
        self.database = dataPath
        if os.path.exists(self.database):
            pass
        else:
            os.makedirs(self.database)
        self.originaldatabase = os.path.join(self.database,"Original").replace("\\","/")
        if not os.path.exists(self.originaldatabase):
            os.makedirs(self.originaldatabase)
        self.fileList = None

    def getDataFileList(self):
        filelist = os.listdir(self.originaldatabase)
        file_list = []
        for each in filelist:
            path = os.path.join(self.originaldatabase,each).replace("\\","/")
            # print(path)
            # print(os.path.isfile(path))
            if os.path.isfile(path):
                if each.split(".")[-1] == "tbs":
                    # print(each)
                    file_list.append(each)
        files = {}
        for each in file_list:
            if each.split(" ")[0] in files:
                files[each.split(" ")[0]].append(each)
            else:
                files.update({each.split(" ")[0]:[each]})
        files = self.sortFiles(files)
        self.fileList = files
        return files

    def getData(self,name,date=None,d=60):
        if date==None:
            if not ".tbs" in name:
                name = name+".tbs"
            if not os.path.exists(name):
                if not os.path.exists(os.path.join(self.originaldatabase,name).replace("\\","/")):
                    return None
                else:
                    name = os.path.join(self.originaldatabase,name).replace("\\","/")
            data = []
            with open(name,"r") as f:
                for each in f.read().split("\n"):
                    data.append(pickle.loads(each["data"]))
            return data
        else:
            if isinstance(date,str):
                if "-" in date or "_" in date:
                    fileName = name+" "+date+".tbs"
                    return self.getData(fileName)
            elif isinstance(date,float) or isinstance(date,int):
                t = time.localtime(date)
                year = t.tm_year
                mon = t.tm_mon
                day = t.tm_mday
                if mon<10:
                    mon = "0"+str(mon)
                else:
                    mon = str(mon)
                fileName = name+" "+str(year)+"_"+mon+"_"+str(day)+".tbs"
                fileName = os.path.join(self.originaldatabase,fileName).replace("\\","/")
                # print(fileName)
                if not os.path.exists(fileName):
                    # fileName = os.path.join(self.originaldatabase,"Ag(T+D) 2020_04_24.tbs").replace("\\","/")
                    # print(fileName)
                    return None
                r = []
                with open(fileName,"r") as f:
                    for each in f.read().split("\n"):
                        if each!="":
                            data  = json.loads(each)
                            if (date - data["stamp"])**2<=d**2:
                                r.append(pickle.loads(base64.b64decode(data["data"])))
                return r
        return None

    def getDataByStamp(self,name,stamp,d=60):
        t = time.localtime(stamp)
        year = t.tm_year
        mon = t.tm_mon
        day = t.tm_mday
        if mon < 10:
            mon = "0" + str(mon)
        else:
            mon = str(mon)
        fileName = name + " " + str(year) + "_" + mon + "_" + str(day) + ".tbs"
        fileName = os.path.join(self.originaldatabase, fileName).replace("\\", "/")
        # print(fileName)
        if not os.path.exists(fileName):
            # fileName = os.path.join(self.originaldatabase,"Ag(T+D) 2020_04_24.tbs").replace("\\","/")
            # print(fileName)
            return None
        r = []
        with open(fileName, "r") as f:
            for each in f.read().split("\n"):
                if each != "":
                    data = json.loads(each)
                    # print(d**2)
                    # print(data["stamp"])
                    if (stamp - data["stamp"])**2 <= d**2:
                        r.append(pickle.loads(base64.b64decode(data["data"])))
        return r

    def getOriginalByStamp(self,name,stamp,d=60):
        t = time.localtime(stamp)
        year = t.tm_year
        mon = t.tm_mon
        day = t.tm_mday
        if mon < 10:
            mon = "0" + str(mon)
        else:
            mon = str(mon)
        if day<10:
            day = "0"+str(day)
        else:
            day = str(day)
        fileName = name + " " + str(year) + "_" + mon + "_" + day + ".tbs"
        fileName = os.path.join(self.originaldatabase, fileName).replace("\\", "/")
        # print(fileName)
        if not os.path.exists(fileName):
            # fileName = os.path.join(self.originaldatabase,"Ag(T+D) 2020_04_24.tbs").replace("\\","/")
            # print(fileName)
            return None
        r = []
        with open(fileName, "r") as f:
            for each in f.read().split("\n"):
                if each != "":
                    data = json.loads(each)
                    # print(d**2)
                    # print(data["stamp"])
                    if (stamp - data["stamp"]) ** 2 <= d ** 2:
                        r.append(data)
        return r

    @ staticmethod
    def getDateFromStamp(stamp):
        if isinstance(stamp,int) or isinstance(stamp,float):
            t = time.localtime(stamp)
            year = t.tm_year
            mon = t.tm_mon
            day = t.tm_mday
            h = t.tm_hour
            m = t.tm_min
            s = t.tm_sec
            if mon<10:
                mon = "0"+str(mon)
            else:
                mon=str(mon)
            if day<10:
                day = "0"+str(day)
            else:
                day = str(day)
            date = str(year)+mon+day
            date = int(date)
            if m<10:
                m = "0"+str(m)
            else:
                m = str(m)
            if s<10:
                s = "0"+str(s)
            else:
                s = str(s)
            h = str(h)+m+s
            h = int(h)
            return date,h


    def sortFiles(self,Files):
        fileList = Files
        if isinstance(fileList,list):
            r = []
            for i in range(len(fileList)):
                select = None
                min_ = None
                for each in fileList:
                    date = self.getDateStamp(each)
                    if min_==None:
                        min_ = date
                        select = each
                    else:
                        if date<min_:
                            min_ = date
                            select = each
                if select!=None:
                    r.append(select)
                    fileList.remove(select)
            return r
        elif isinstance(fileList,dict):
            r = {}
            for each in fileList:
                r.update({each:self.sortFiles(fileList[each])})
            return r

    @ staticmethod
    def getDateStamp(fileName):
        if " " in fileName:
            fileName = fileName.split(" ")[-1]
        if "." in fileName:
            fileName = fileName.split(".")[0]
        fileName = fileName.replace("-","_")
        dates = fileName.split("_")
        year = dates[0]
        mon = dates[1]
        day = dates[2]
        mon = int(mon)
        day = int(day)
        if day<10:
            day = "0"+str(day)
        else:
            day = str(day)
        if mon < 10:
            mon = "0"+str(mon)
        else:
            mon = str(mon)
        date = year+mon+day
        date = int(date)
        return date

    def readHistoryData(self,name,date=None,loads=False):
        if date!=None:
            filePath = os.path.join(self.originaldatabase,name+" "+date.replace("-","_")+".tbs").replace("\\","/")
        else:
            filePath = name.replace("-","_")
            if ".tbs" not in name:
                filePath = filePath+".tbs"
            if os.path.exists(filePath):
                pass
            else:
                filePath = os.path.join(self.originaldatabase,filePath).replace("\\","/")
        # print(filePath)
        if os.path.exists(filePath):
            with open(filePath,"r") as f:
                data = []
                for each in f.read().split("\n"):
                    if each!="":
                        if loads:
                            data.append(json.loads(each))
                        else:
                            data.append(each)
            return data
        return None

    def getHistoryDataByDate(self,name,date,time_=None):
        if time_ == None:
            pass
        else:
            for each in [":","_","-"," ","/","|","\\"]:
                if each in time_:
                    time_ = time_.split(each)
                    break
        for each in [":","_","-"," ","/","|","\\"]:
            if each in date:
                date = date.split(each)
        # print(time_)
        if time_!=None:
            try:
                try:
                    H = int(time_[0])
                except:
                    H = 0
                try:
                    M = int(time_[1])
                except:
                    M = 0
                try:
                    S = int(time_[2])
                except:
                    S = 0
            except:
                return None,"无法解析时间"
        else:
            H = None
            M = None
            S = None
        try:
            year = int(date[0])
            mon = int(date[1])
            day = int(date[2])
        except:
            return None,"无法解析日期"
        if time_==None:
            fileName = name+" "+str(year)+"_"
            if mon<10:
                fileName += "0"+str(mon)+"_"
            else:
                fileName += str(mon)+"_"
            if day<10:
                fileName += "0"+str(day)
            else:
                fileName += str(day)
            fileName += ".tbs"
            filePath = os.path.join(self.originaldatabase,fileName).replace("\\","/")
            # print(filePath)
            if not os.path.exists(filePath):
                return None,"不存在此日期的数据记录:"+fileName
            with open(filePath,"r") as f:
                datas = []
                for each in f.read().split("\n"):
                    if each!="":
                        try:
                            datas.append(json.loads(each))
                        except:
                            pass
                if len(datas)>0:
                    return datas,"获取数据成功"
                else:
                    return datas,"没有获取到数据"
        else:
            t = str(year)+"-"+str(mon)+"-"+str(day)+" "+str(H)+":"+str(M)+":"+str(S)
            # print(t)
            timeArray = time.strptime(t,"%Y-%m-%d %H:%M:%S")
            # timeStamp = int(time.mktime(timeArray))
            stamp = int(time.mktime(timeArray))
            # stamp = time.localtime(timeArray)
            # print(stamp)
            datas = self.getOriginalByStamp(name,stamp)
            return datas,"获取数据成功"
        return None,"未找到符合条件的数据"

if __name__ == '__main__':
    os.chdir("../")
    d = getHistoryData()
    print(d.originaldatabase)
    r = d.getDataFileList()
    for each in r:
        for eachFile in r[each]:
            print(eachFile)
    r = d.getData("Ag(T+D)",1587658014.4206567)
    for each in r:
        print(each.timeStamp)
    # r = d.getDataByStamp("Ag(T+D)",1587741055.0396316,d=60)
    # print(r)
    r = d.readHistoryData("Ag(T+D) 2020-04-28")
    print(r)