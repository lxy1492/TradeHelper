import time
from Moudle.dataType import DataType
from monitor.MonitorOBJDealFunction import DealFunction,OBJDealFunction

class MonitorOBJ():
    def __init__(self,name,obj=None,data=None,stamp=None):
        self.name = name
        self.obj = obj
        self.data = data
        self.triggled = False
        self.stamp = stamp
        self.DealFunction = None

    def __str__(self):
        return str(self.name)+"-"+str(self.obj)+"-"+str(self.stamp)

    def SetFunction(self,f):
        if self.DealFunction == None:
            self.DealFunction = [f]
            return 0
        else:
            self.DealFunction = [f]
            return 0

    def AddDealFunction(self,f):
        if self.DealFunction == None:
            return self.SetFunction(f)
        elif isinstance(self.DealFunction,list):
            self.DealFunction.append(f)
            return 0
        elif isinstance(self.DealFunction,f):
            self.DealFunction = [self.DealFunction,f]
            return 0
        return -1

    def AutoSetDealFunction(self):
        if self.name in DealFunction:
            fs = DealFunction[self.name]
            for each in fs:
                if each not in self.DealFunction:
                    self.AddDealFunction(each)
        if self.obj in OBJDealFunction:
            objfs = OBJDealFunction[self.obj]
            for each in objfs:
                if each not in self.DealFunction:
                    self.AddDealFunction(each)


    def setStamp(self,s=None):
        if s==None:
            self.stamp = time.localtime()
            return 0
        if isinstance(s,float):
            if s>0:
                self.stamp = s
                return 0
        elif isinstance(s,int):
            if s>0:
                try:
                    self.stamp=float(s)
                    return 0
                except:
                    pass
        elif isinstance(s,str):
            try:
                self.stamp = float(s)
                return 0
            except:
                pass
        elif isinstance(s,DataType):
            if isinstance(s.timeStamp,float):
                self.stamp = s.timeStamp
                return 0
        elif isinstance(s,dict):
            for each in ["stamp","Stamp","DataStamp","dataStamp","datastamp","data_stamp","timestamp","timeStamp"]:
                if each in dict:
                    return self.setStamp(dict[each])
        return -1

class Triggler():
    def __init__(self):
        self.dataPool = []
    def addData(self,data,Name=None):
        if isinstance(data,dict):
            if "name" in dict:
                Newdata = MonitorOBJ(name=Name,obj=dict["name"],data=data)
                if "stamp" in data:
                    if isinstance(data["stamp"],float):
                        Newdata.stamp = data["stamp"]
                    else:
                        Newdata.stamp = time.localtime()
                Newdata.AutoSetDealFunction()
                # Newdata.AutoSetDealFunction()
                self.dataPool.append(Newdata)
                return 0
        elif isinstance(data,DataType):
            Newdata = MonitorOBJ(name=Name,obj=data.name,data=data)
            Newdata.setStamp(data)
            Newdata.AutoSetDealFunction()
            self.dataPool.append(Newdata)
            return 0
        elif isinstance(data,float) or isinstance(data,str) or isinstance(data,int):
            Newdata = MonitorOBJ(name=Name,obj="常量",data=data,stamp=time.localtime())
            Newdata.AutoSetDealFunction()
            self.dataPool.append(Newdata)
            return 0
        return -1

if __name__ == '__main__':
    pass