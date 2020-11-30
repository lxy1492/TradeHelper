from Moudle.dataType import DataType
from Moudle.QQEmail import smtpQQEmail
from monitor.monitorObject import Triggler
from Tools.broadAudio import voiceBroad

class PriceMonitor():
    def __init__(self):
        # object_结构示例：{'Ag(T+D)': {'3800.01': [False, 4.989999999999782]}}
        self.object_ = {}
        self.dealLineFunction = []
        self.emailServer = smtpQQEmail()
        # [[接收者，地址]]
        self.emailAddress = []
        self.emailNotice = True
        self.trigger = Triggler()


    def addObject(self,name):
        if isinstance(name,str):
            d = {}
            self.object_.update({"name":d})

    # 当前价格减设置线，第一个是判断此线是否被越过，第二个是判断方向
    def setLine(self,name,line,priceNow=None):
        if isinstance(line,float) or isinstance(line,int):
            if isinstance(name,str):
                if priceNow==None:
                    d = None
                else:
                    if isinstance(priceNow,int) or isinstance(priceNow,float):
                        d = priceNow-line
                    else:
                        d = None
                if name in self.object_:
                    self.object_[name].update({line:[False,d]})
                else:
                    d = {line:[False,d]}
                    self.object_.update({name:d})

    def getAllLine(self):
        return self.object_

    def cleanAllLine(self,line=None):
        if line==None:
            self.object_ = {}
        else:
            for each in self.object_:
                self.cleanLine(each,line)

    def cleanLine(self,obj,line=None):
        if isinstance(obj,str):
            if obj in self.object_:
                if line==None:
                    self.object_[obj]={}
                else:
                    for each in self.object_[obj]:
                        if each==line:
                            self.object_[obj].pop(line)

    def cleanFalseLine(self,obj=None,line=None):
        for each in self.object_:
            if each==obj or obj==None:
                for eachLine in self.object_[each]:
                    if line==eachLine or line==None:
                        if self.object_[each][eachLine][0]==False:
                            # self.cleanLine(eachLine,eachLine)
                            try:
                                self.object_[each].remove(eachLine)
                            except:
                                print("error:无法移除已触及的提醒线,",eachLine)

    @ property
    def allLine(self):
        return self.getAllLine()

    def judge(self,datas):
        # r的格式是{目标名字：【设置提醒线，当前价格】}
        # print("panduan")
        r = {}
        if isinstance(datas,DataType):
            datas = [datas]
        if isinstance(datas,list):
            for each in datas:
                if isinstance(each,DataType):
                    if each.name in self.object_:
                        if isinstance(each.value,int) or isinstance(each.value,float):
                            for eachLine in self.object_[each.name]:
                                if self.object_[each.name][eachLine][0]==False:
                                    # print(each.value,eachLine)
                                    try:
                                        d = float(each.value)-float(eachLine)
                                        if self.object_[each.name][eachLine][1]!=None:
                                            if isinstance(self.object_[each.name][eachLine][1],int) or isinstance(self.object_[each.name][eachLine][1],float):
                                                if d*self.object_[each.name][eachLine][1]<=0:
                                                    self.object_[each.name][eachLine][0]=True
                                                    r.update({each.name:[eachLine,each.value]})
                                            else:
                                                self.object_[each.name][eachLine][1]=d
                                    except:
                                        pass
        # print(r)
        for each in self.dealLineFunction:
            # print(each,r)
            each(r)

    def addEmailAddr(self,name,add):
        if "@" in add:
            if isinstance(name,str) and isinstance(add,str):
                for each in self.emailAddress:
                    if each[1] == add:
                        return -1
                self.emailAddress.append([name,add])
                return 0
        return -1

    def sendVoice(self,lines):
        text = "price monitor提醒"
        for each in lines:
            name = each
            line = lines[each][0]
            priceNow = lines[each][1]
            if each=="Ag(T+D)":
                name = "白银延期"
            elif each=="Au(T+D)":
                name = "黄金延期"
            elif each=="Au99.99":
                name = "上海黄金现货"
            elif name=="LondonGold":
                name = "来自第一黄金网数据，伦敦黄金"
            elif name=="GoldSliver":
                name = "金银比"
            if name=="金银比":
                text += ":"+str(priceNow)+"已触及提醒线"+str(line)
            else:
                text += ":"+name+",当前价格"+str(priceNow)+"已触及涉及提醒线,"+str(line)+"。"
        voiceBroad(text)

    def sendEmailMessage(self,lines):
        if not self.emailNotice:
            return -1
        if lines=={} or len(lines)<=0:
            return -1
        # print(lines)
        message = ""
        for each in lines:
            line = lines[each][0]
            priceNow = lines[each][1]
            text = "PriceMonitor For "+each+" cross the line "+str(line)+" at "+str(priceNow)+"\n"
            message+=text
        if len(self.emailAddress)<=0:
            return -1
        for eachAccept in self.emailAddress:
            toWhom = eachAccept[0]
            add = eachAccept[1]
            # print(">>>>>>>>>>>>>>",message)
            self.emailServer.sendForText(receiver=add,message=message,toWhom=toWhom,fromWhom="TraderHelper PriceMonitor")
            print("发送邮件至：",toWhom,message)
        return 0

    def cleanEmail(self,obj=None):
        if obj==None:
            self.emailAddress = []
        else:
            if isinstance(obj,str):
                if "@" in obj:
                    for each in self.emailAddress:
                        if each[1] == obj:
                            self.emailAddress.remove(each)

if __name__ == '__main__':
    server = PriceMonitor()
    server.dealLineFunction.append(server.sendEmailMessage)
    server.addEmailAddr("lxy","415997348@qq.com")
    server.emailNotice = True
    server.setLine("Ag(T+D)",3702,3721)
    data1 = DataType(name="Ag(T+D)",value=3702,dataTime="11:11",dataDate="2020-04-16")
    server.judge([data1])