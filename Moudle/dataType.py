import json

class DataType():
    def __init__(self,name,type_=None,value=None,unit=None,valueType=None,info=None,dataTime=None,dataDate=None,timeStamp=None,dataSource=None):
        self.name = name
        self.type = type_
        self.value = value
        self.valueType = valueType
        self.info=info
        self.dataTime = dataTime
        self.dataDate = dataDate
        self.timeStamp = timeStamp
        self.dataSource = dataSource
        self.unit=unit

    @ property
    def Dict(self):
        dic = {
            "name":self.name,
            # "type":self.type,
            "value":self.value,
            "valueType":self.valueType,
            "info":self.info,
            "dataTime":self.dataTime,
            "dataDate":self.dataDate,
            "timeStamp":self.timeStamp,
            "dataSource":self.dataSource,
            "unit":self.unit
        }
        return dic

    def setUnit(self,t):
        if isinstance(t,str):
            self.unit = t
            return 0
        return -1

    def setValueType(self,type_):
        if isinstance(type_,str):
            self.valueType = type_
            return 0
        return -1

    def setValue(self,value):
        if self.type==None:
            self.value = value
            return 0
        else:
            if isinstance(value,self.type):
                self.value = value
                return 0
        return -1

    def setType(self,type_):
        self.type = type_

    def setName(self,name):
        if isinstance(name,str):
            self.name = name
            return 0
        return -1

    def setInfo(self,info):
        if isinstance(info,dict):
            self.info = info
            return 0
        return -1

    def setTimeStamp(self,t):
        if isinstance(t,float):
            self.timeStamp = t
            return 0
        return -1

    def setDataTime(self,t):
        if isinstance(t,str):
            self.dataTime = t
            return 0
        return -1

    def setDataDate(self,t):
        if isinstance(t,str):
            self.dataDate = t
            return 0
        return -1

    def setDataSource(self,r):
        self.dataSource = r

    def __str__(self):
        string = "Name:"+self.name+";\n"
        if self.value == None:
            value_ = "None"
        else:
            value_ = str(self.value)
        if self.valueType == None:
            valueType_ = "None"
        else:
            try:
                valueType_ = str(self.valueType)
            except:
                valueType_ = ""
        if self.unit==None:
            unit_ = ""
        else:
            if isinstance(self.unit,str):
                unit_ = self.unit
            else:
                unit_ = "None"
        if unit_=="":
            string += "value:" + value_ + " type:" + valueType_ + ";\n"
        else:
            string += "value:" + value_ + "/" + unit_ + " type:" + valueType_ + ";\n"
        # string += "value:"+value_+"/"+unit_+" type:"+valueType_+";\n"
        string += "Date:"+str(self.dataDate)+" time:"+str(self.dataTime)+";\n"
        try:
            string += "info:"+json.dumps(self.info)+";\n"
        except:
            pass
        try:
            string += "source:"+str(self.dataSource)
        except:
            try:
                string += "source:"+json.dumps(self.dataSource)
            except:
                pass
        return string