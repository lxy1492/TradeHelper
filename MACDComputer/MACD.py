import os
import json
import time
import config
from Moudle.printError import *
from Moudle.strTime import get_local_str_date_time
from Moudle.dataType import DataType
from MACDComputer.baseComputer import BaseComputer

EMA1_Config = config.ema1
EMA2_Config = config.ema2
DEA_Config = config.dea
SaveName = config.saveName
DataBaseDir_Config = config.DataBase
MACD_DATA_PATH_Config = os.path.join(DataBaseDir_Config,config.macdPath).replace("\\","/")
TEMP_Length_Config = config.templength

class MACD_Computer(BaseComputer):

    def dataPushDriver(self):
        self.ComputeBAR(computeDEA=True, computeDIF=True)
        self.PushSaveData()

    def setDataDriver(self,f=None,asy = False):
        # 获取数据后计算数据
        if f==None:
            f = self.dataPushDriver
        self.dataDriver = f

    def setUp(self,name="MACD_computer",dataLength=None,EMA1=None,EMA2=None,DEA=None):
        if isinstance(name,str):
            self.name = name
        if dataLength!=None:
            self.setPoolLength(dataLength)
        if isinstance(EMA1,int):
            self.ema1_MA = EMA1
        else:
            self.ema1_MA = EMA1_Config
        if isinstance(EMA2,int):
            self.ema2_MA = EMA2
        else:
            self.ema2_MA = EMA2_Config
        if isinstance(DEA,int):
            self.dea_MA = DEA
        else:
            self.dea_MA = DEA_Config
        self.EMA1 = []
        # 控制数据缓存长度
        self.ema1_length = TEMP_Length_Config
        self.EMA2 = []
        # 控制数据缓存长度
        self.ema2_length = TEMP_Length_Config
        self.DIF = []
        self.DEA = []
        # 控制数据缓存长度
        self.dea_length = TEMP_Length_Config
        self.BAR = []
        # 控制数据缓存长度
        self.bar_length = TEMP_Length_Config
        self.saveTemp = []
        self.savePath = os.path.join(DataBaseDir_Config,SaveName).replace("\\","/")
        if not os.path.exists(path=MACD_DATA_PATH_Config):
            os.makedirs(MACD_DATA_PATH_Config)
        self.saveDataPath = MACD_DATA_PATH_Config.replace("\\","/")
        self.saveTempLength = TEMP_Length_Config
        self.data_pool_length = self.ema2_MA
        self.setDataDriver()
        self.setup_ready = True

    def Compute_EMA(self):
        r1 = self.Compute_EMA1()
        r2 = self.Compute_EMA2()
        return r1,r2

    def Compute_EMA1(self):
        mean_ = self.getMA(MA=self.ema1_MA)
        ema1 = BaseData(name="ema1",value=mean_.value)
        l = self.lastData
        if l!=None:
            ema1.setStamp(l.stamp)
        length = self.PushEMA1(ema1)
        return ema1,length

    def Compute_EMA2(self):
        mean_ = self.getMA(MA=self.ema2_MA)
        ema2 = BaseData(name="ema2",value=mean_.value)
        l = self.lastData
        if l!=None:
            ema2.setStamp(l.stamp)
        length = self.PushEMA2(ema2)
        return ema2,length

    def PushEMA(self,data,MA):
        if isinstance(MA,int):
            if MA==1:
                return self.PushEMA1(data)
            elif MA == 2:
                return self.PushEMA2(data)
        elif isinstance(MA,str):
            if MA=="1":
                return self.PushEMA1(data)
            elif MA=="2":
                return self.PushEMA2(data)
        else:
            print_error("设置MA类型错误")


    def PushEMA1(self,data):
        if isinstance(data,BaseData):
            self.EMA1.append(data)
            length = len(self.EMA1)
            if length>self.ema1_length:
                self.EMA1 = self.EMA1[-1:]
            return length
        else:
            print_error("Push数据类型错误")
            return -1

    def PushEMA2(self,data):
        if isinstance(data,BaseData):
            self.EMA2.append(data)
            length = len(self.EMA2)
            if length>self.ema2_length:
                self.EMA2 = self.EMA2[-1:]
            return len(self.EMA2)
        else:
            print_error("Push数据类型错误")
            return -1

    def Compute_DIF(self):
        r = self.Compute_EMA()
        eam1 = r[0][0]
        eam2 = r[1][0]
        dif_value = eam1.value - eam2.value
        dif = BaseData(name="DIF",value=dif_value)
        dif.setStamp(eam1.stamp)
        length = self.PushDIF(dif)
        return dif,length

    def PushDIF(self,data):
        if isinstance(data,BaseData):
            self.DIF.append(data)
            length = len(self.DIF)
            while(length>self.dea_MA):
                self.DIF.remove(self.DIF[0])
                length = len(self.DIF)
            return length
        else:
            print_error("PUSH DIF数据类型错误")
            return -1

    def ComputeDEA(self,computeDIF=False):
        if computeDIF:
            self.Compute_DIF()
        if len(self.DIF)<=0:
            print_error("没有DIF数据,无法完成计算")
            return -1
        mean_ = self.getMA(MA=self.dea_MA,data=self.DIF,dataLength=self.dea_MA)
        dea = BaseData(name="DEA",value=mean_.value)
        stamp = self.DIF[-1].stamp
        dea.setStamp(stamp)
        length = self.PushDEA(data=dea)
        return dea,length

    def PushDEA(self,data):
        if isinstance(data,BaseData):
            self.DEA.append(data)
            length = len(self.DEA)
            if self.dea_length<length:
                self.DEA = self.DEA[-1:]
            return length
        else:
            print_error("PUSH DEA数据类型错误" )
            return -1

    def ComputeBAR(self,computeDEA=False,computeDIF = False):
        if computeDEA:
            self.ComputeDEA(computeDIF=computeDIF)
        if len(self.DEA)>0 and len(self.DIF)>0:
            bar_value = (self.DIF[-1].value - self.DEA[-1].value)*2
            bar = BaseData(name="BAR",value=bar_value)
            stamp = self.DEA[-1].stamp
            bar.setStamp(stamp)
            length = self.PushBAR(bar)
            return bar,length

    def PushBAR(self,data):
        if isinstance(data,BaseData):
            self.BAR.append(data)
            length = len(self.BAR)
            if length>self.bar_length:
                self.BAR = self.BAR[-1:]
            return length
        else:
            print_error("PUSH BAR数据类型错误")
            return -1

    def getSaveDataFileName(self):
        t = get_local_str_date_time()
        name = self.name+" "+t+".pkl"
        return name

    def getLastResult(self):
        ema1 = self.EMA1[-1]
        ema2 = self.EMA2[-1]
        dif = self.DIF[-1]
        dea = self.DEA[-1]
        bar = self.BAR[-1]
        stamp = ema1.stamp
        date = time.localtime(stamp)
        date_str = str(date.tm_year)+"年"+str(date.tm_mon)+"月"+str(date.tm_mday)+"日"+str(date.tm_hour)+"时"+str(date.tm_mon)+"分"+str(date.tm_sec)+"秒"
        self.lastResult = {
            "PRICE":self.data_pool[-1].value,
            "EMA1":ema1.value,
            "EMA2":ema2.value,
            "DIF":dif.value,
            "DEA":dea.value,
            "BAR":bar.value,
            "stamp":stamp,
            "date":date_str,
        }
        return self.lastResult

    def PushSaveData(self,data=None):
        if data==None:
            data = self.getLastResult()
        self.saveTemp.append(data)
        length = len(self.saveTemp)
        # 设定自动保存数据长度
        if length>=self.saveTempLength:
            self.saveData()
        return length

    # 退出前运行此方法，保存结果和缓存
    def saveData(self,path=None):
        if path==None:
            path = self.getSaveDataFileName()
            if self.saveDataPath!=None:
                path = os.path.join(self.saveDataPath,path)
        if os.path.exists(path):
            f = open(path,"a")
        else:
            f = open(path,"w")
        data = self.saveTemp
        self.saveTemp = []
        for each in data:
            # print(each)
            json_str = json.dumps(each)
            f.write(json_str+"\n")
        f.close()
        self.save()