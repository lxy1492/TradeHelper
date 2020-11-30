import config
import json
import pickle
import os
import time
import base64
from threading import Thread
from Moudle.dataType import DataType

class DB_manager():
    def __init__(self,DataBaseDIR=config.DataBase):
        self.DataBaseDIR = DataBaseDIR
        self.fileList = None
        self.OriginalPath = os.path.join(self.DataBaseDIR,"Original").replace("\\","/")

        # historyInfo
        self.historyInfoResult = {}
        # eachDayInfo
        self.eachDayInfoResult = {}

    def getFileList(self,path=None):
        if path==None:
            path = self.OriginalPath
        if isinstance(path,str):
            r = {}
            """
            {
                name:[
                        filename,
                        filedate[year,mon,day]
                ]
            }
            """
            for each in os.listdir(self.OriginalPath):
                name = each.split(" ")[0]
                date = each.split(" ")[1].split(".")[0]
                if not name in r:
                    r.update({name:[]})
                splitdate = self.getDate(date)
                if not splitdate==None:
                    date = splitdate
                r[name].append([each,date])
            self.fileList = r
            return r
        else:
            return None

    def getDate(self,date):
        for each in ["-",":","_","|",",",";","/","\\"]:
            if each in date:
                date = date.split(each)
                return date
        return None

    def getDateANDStamps(self,path=None,name=None,date=None):
        if path==None:
            if name==None or date==None:
                return -1
            else:
                if isinstance(date,list):
                    if len(date)==3:
                        text = ""
                        for i in range(len(date)):
                            text = text+date[i]
                            if i<2:
                                text += "_"
                        date = text
                    else:
                        return -1
                elif isinstance(date,str):
                    for each in ["-",":","|",",",";","/","\\"]:
                        if each in date:
                            date = date.replace(each,"_")
                            break
                fileName = name+" "+date+".tbs"
                # print(fileName)
                path = os.path.join(self.OriginalPath,fileName).replace("\\","/")
                if os.path.exists(path):
                    return self.getDateANDStamps(path=path)
                else:
                    return -1
        if os.path.exists(path):
            stamps= []
            with open(path,"r") as f:
                for each in f.read().split("\n"):
                    if each!="":
                        data = json.loads(each)
                        stamp = data["stamp"]
                        date = data["date"]
                        time_ = data["time"]
                        stamps.append([stamp,date,time_])
            if len(stamps)>0:
                return stamps
            else:
                return None
        else:
            return -1

    def getDataByTIME(self,name,TIME,dataType="original"):
        if isinstance(TIME,float):
            t = time.localtime(TIME)
            year = t.tm_year
            mon = t.tm_mon
            day = t.tm_mday
            stamp = TIME
            if mon<10:
                mon = "0"+str(mon)
            else:
                mon = str(mon)
            if day<10:
                day = "0"+str(day)
            else:
                day = str(day)
            date = str(year)+"_"+mon+"_"+day
        elif isinstance(TIME,str):
            if " " in TIME:
                date = TIME.split(" ")[0]
                stamp = TIME.split(" ")[1]
            else:
                return -1
        elif isinstance(TIME,list):
            if len(TIME)==2:
                if isinstance(TIME[0],str) and isinstance(TIME[1],str):
                    date = TIME[0]
                    stamp = TIME[1]
                    for each in ["-",";",",","|","\\","/",":"]:
                        if each in date:
                            date = date.replace(each,"_")
                            break
                else:
                    return -1
            else:
                return -1
        fileName = name+" "+date+".tbs"
        fileName = os.path.join(self.OriginalPath,fileName).replace("\\","/")
        # print(fileName)
        if os.path.exists(fileName):
            return self.getData(fileName,stamp,dataType)
        else:
            return -1

    def getData(self,path,stamp,dataType="original"):
        r = None
        if os.path.exists(path):
            with open(path,"r") as f:
                for each in f.read().split("\n"):
                    if each!="":
                        data = json.loads(each)
                        if isinstance(stamp,float):
                            if stamp==data["stamp"]:
                                r = data
                                break
                        elif isinstance(stamp,str):
                            if stamp == data["time"]:
                                # print(data["time"])
                                r = data
                                break
        # print(r)
        if r!=None:
            if dataType=="datatype":
                return r["data"]
            elif dataType == "dict":
                r = pickle.loads(base64.b64decode(r["data"]))
                if isinstance(r,DataType):
                    return r.Dict
                else:
                    # print()
                    return r
            else:
                return r
        return None

    def getAllDict(self,name,date=None):
        if date==None:
            path = ""
            # print(name)
            if os.path.exists(name):
                path = name
            elif os.path.exists(os.path.join(self.OriginalPath,name).replace("\\","/")):
                path = os.path.join(self.OriginalPath,name).replace("\\","/")
            else:
                return -1
            # print(path)
            with open(path,"r") as f:
                datas = []
                lastTime=None
                for each in f.read().split("\n"):
                    if each!="":
                        data = json.loads(each)
                        data = base64.b64decode(data["data"])
                        data = pickle.loads(data)
                        if isinstance(data,DataType):
                            if lastTime==None:
                                datas.append(data.Dict)
                                if data.info!=None:
                                    if "date" in data.info:
                                        lastTime = data.info["date"]
                                    else:
                                        lastTime = data.dataDate+data.dataTime
                                else:
                                    lastTime = data.dataDate+data.dataTime
                            else:
                                if data.info!=None:
                                    if "date" in data.info:
                                        if data.info["date"]==lastTime:
                                            pass
                                        else:
                                            datas.append(data.Dict)
                                            lastTime = data.info["date"]
                                    else:
                                        datas.append(data.Dict)
                                else:
                                    if data.dataDate+data.dataTime!=lastTime:
                                        datas.append(data.Dict)
                                        lastTime = data.dataDate+data.dataTime
            return datas
        else:
            for each in ["-",";",",",".","|","/","\\"]:
                if each in date:
                    date = date.replace(each,"_")
                    break
            name = name+" "+date+".tbs"
            path = os.path.join(self.OriginalPath,name).replace("\\","/")
            return self.getAllDict(path)

    def getFilesdata(self,fileNameOrPath):
        if isinstance(fileNameOrPath,str):
            if not os.path.exists(fileNameOrPath):
                fileNameOrPath = os.path.join(self.DataBaseDIR,"Original",fileNameOrPath).replace("\\","/")

            if os.path.exists(fileNameOrPath):
                # print(fileNameOrPath)
                with open(fileNameOrPath,"r") as f:
                    data = []
                    for each in f.read().split("\n"):
                        if each !="":
                            try:
                                # print(json.loads(each))
                                base64data = base64.b64decode(json.loads(each)["data"])
                                original = pickle.loads(base64data)
                                # print(original)
                                data.append(original)
                            except:
                                pass
                return data
        elif isinstance(fileNameOrPath,list):
            data = []
            for each in fileNameOrPath:
                r = self.getFilesdata(each)
                # print(each,r)
                if r!=None:
                    data.extend(r)
            return data
        return None

    def historyInfo(self,data):
        # print(data)
        max_ = None
        min_ = None
        values = []
        if data==None:
            return None
        if not isinstance(data,list):
            return None
        for each in data:
            if isinstance(each,DataType):
                if isinstance(each.value, float) or isinstance(each.value, int):
                    # print(each)
                    if max_==None:
                        max_ = each
                    else:
                        if each.value>max_.value:
                            max_ = each
                    if min_==None:
                        min_ = each
                    else:
                        if each.value<min_.value:
                            min_ = each
                    values.append(each.value)
        if len(values)>0:
            mean_ = sum(values)/len(values)
        else:
            mean_ = None
        if isinstance(max_,DataType):
            maxInfo = max_.Dict
        else:
            maxInfo = None
        if isinstance(min_,DataType):
            minInfo = min_.Dict
        else:
            minInfo = None
        return {"max":maxInfo,"min":minInfo,"mean":mean_}

    def getOneHistoryInfo(self,name,files,eachDay=False):
        data = self.getFilesdata(files)
        r = self.historyInfo(data)
        if eachDay:
            if name in self.eachDayInfoResult:
                self.eachDayInfoResult[name].append(r)
            else:
                self.eachDayInfoResult.update({name:[r]})
        else:
            if name in self.historyInfoResult:
                self.historyInfoResult[name].append(r)
            else:
                self.historyInfoResult.update({name:[r]})

    def getHistoryInfo(self,name=None,date=None,length=None):
        l = self.getFileList()
        files = {}
        if isinstance(name,str):
            name = [name]
            date = [date]
            files.update({name[0]:[]})
        elif name==None:
            # l = self.getFileList()
            name = []
            # date = [date]
            newDate = []
            for each in l:
                name.append(each)
                newDate.append(date)
                files.update({each:[]})
            date = newDate
        for i in range(len(date)):
            if date[i]!=None:
                splited = False
                for each in ["-", "_", " ","\\", "/", ".", ":", ";"]:
                    d = date[i].split(each)
                    if len(d)==3:
                        year = d[0]
                        mon = d[1]
                        day = d[2]
                        if len(mon)<=1:
                            mon = "0"+mon
                        if len(day)<=1:
                            day = "0"+day
                        date[i] = [year,mon,day]
                        splited = True
                        break
                if splited==False:
                    if len(date[i])==8:
                        year = date[i][:4]
                        mon = date[i][4:6]
                        day = date[i][6:]
                        # print(date[:4],date[4:6],date[6:])
                        # print(year,mon,day)
                        date[i] = [year,mon,day]

        if length!=None:
            if isinstance(length,int):
                if length<0:
                    length=None
            elif isinstance(length,str):
                try:
                    length = int(length)
                except:
                    pass
        for i in range(len(name)):
            fileNum = len(l[name[i]])
            for j in range(fileNum):
                if length!=None:
                    if fileNum>length:
                        if date[i]==None:
                            d = fileNum-length
                            if j>=d:
                                files[name[i]].append(l[name[i]][j][0])
                        else:
                            files[name[i]].append(l[name[i]][j][0])
                            if len(files[name[i]])>length:
                                files[name[i]].remove(files[name[i]][0])
                    else:
                        files[name[i]].append(l[name[i]][j][0])
                else:
                    files[name[i]].append(l[name[i]][j][0])
                # print(date[i])
                if date[i]!=None:
                    if l[name[i]][j][1] == date[i]:
                        break
        th = []
        for each in files:
            t = Thread(target=self.getOneHistoryInfo,args=(each,files[each]))
            th.append(t)
            t.start()
        for each in th:
            each.join()
        return self.historyInfoResult
        # for each in files:
        #     data = self.getFilesdata(files[each])
        #     result.update({each:self.historyInfo(data)})
        # return result

    def getDayInfo(self,name=None,date=None):
        l = self.getFileList()
        files = {}
        if isinstance(name,str):
            if name in l:
                name = [name]
        else:
            name = []
            for each in l:
                name.append(each)
        th = []
        for eachName in name:
            file = None
            if isinstance(date,str):
                for eachPoint in ["-", "_", " ", "\\", "/", ".", ":", ";"]:
                    if eachPoint in date:
                        newDate = date.replace(eachPoint,"")
                        if len(newDate)==8:
                            year = newDate[:4]
                            mon = newDate[4:6]
                            day = newDate[6:]
                            newDate = [year,mon,day]
                            date = newDate
                            break
            if isinstance(date,list):
                for eachFileName in l[eachName]:
                    if eachFileName[-1]==date:
                        file = eachFileName[0]
                        break
            else:
                file = l[eachName][-1][0]
            if file == None:
                file = l[eachName][-1][0]
            t = Thread(target=self.getOneHistoryInfo,args=(eachName,file,True))
            th.append(t)
            t.start()
        for each in th:
            each.join()
        return self.eachDayInfoResult






if __name__ == '__main__':
    import sys
    os.chdir("../")
    DB = DB_manager()
    print(DB.getFileList())
    print(DB.getDateANDStamps(name="Ag(T+D)",date="2020-05-06"))
    print(DB.getDataByTIME(name="Ag(T+D)",TIME=["2020-05-06","00:05:41"]))
    print(DB.getDataByTIME(name="Ag(T+D)", TIME=1588694741.7027016))
    dicts = DB.getAllDict("Ag(T+D)","2020-04-28")
    print(sys.getsizeof(dicts))
    print(DB.getHistoryInfo("Ag(T+D)","20200503",4))
    print(DB.getDayInfo())
