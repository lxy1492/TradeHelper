import socket,json,time
from Moudle.QQEmail import smtpQQEmail
from Moudle.strTime import getChineseStrTime
from getData.get_data_from_server import IP,PORT
class priceNotition():
    def __init__(self,name="priceNotition",ip=IP,port=PORT,recvSize=102400):
        self.name = name
        self.emailService = smtpQQEmail()
        self.emial = None
        self.line = None
        self.ip = ip
        self.port = port
        self.recvSize = recvSize
        self.shutdown = False
        self.interval = 30

    def setIP(self,ip):
        if not isinstance(ip,str):
            return -3
        if "." in ip and len(ip.split("."))==4:
            try:
                _ = int(ip.replace(".",""))
                self.ip = ip
                return 0
            except:
                return -1
        return -2

    def setPort(self,port):
        if isinstance(port,str):
            try:
                port = int(port)
            except:
                return -1
        if isinstance(port,int):
            self.port = port
            return 0
        else:
            return -2

    def decodeRecv(self,r,loadJson=False):
        try:
            if loadJson:
                return json.loads(r.decode())
            else:
                return r.decode()
        except:
            try:
                if loadJson:
                    return json.loads(r.decode("gbk"))
                else:
                    return r.decode("gbk")
            except:
                try:
                    if loadJson:
                        return json.loads(r.decode("gb2312"))
                    else:
                        return r.decode("gb2312")
                except:
                    return None

    def getData(self,order):
        client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.connect((self.ip,self.port))
        _ = client.recv(1024)
        # print(self.decodeRecv(r))
        if isinstance(order,str):
            order = order.encode()
        if isinstance(order,bytes):
            client.send(order)
            r = client.recv(self.recvSize)
            r = self.decodeRecv(r,loadJson=True)
            if r!=None:
                return r
        return None

    def getEmail(self,order="getEmail"):
        r  =self.getData(order)
        try:
            if r["result"]=="success":
                self.emial = r['email']
        except:
            pass

    def getLine(self,order="getLine"):
        r = self.getData(order)
        if isinstance(r,dict):
            return r
        return None

    def checkLine(self,l):
        """

        :param l: 输入提醒线数据，字典类型{监视对象名称：{提醒线数值：[是否跨越True or False，差距]}}
        :return: 【【监视对象名称，提醒线数值】，。。。。】
        """
        obj = []
        if isinstance(l,dict):
            if self.line==None:
                for eachObj in l:
                    for eachLine in l[eachObj]:
                        if l[eachObj][eachLine][0]==True:
                            # obj=[[eachObj,eachLine]]
                            obj.append([eachObj,eachLine])
            else:
                for eachObj in l:
                    for eachLine in l[eachObj]:
                        if l[eachObj][eachLine][0]==True:
                            if eachObj in self.line:
                                if eachLine in self.line[eachObj]:
                                    if self.line[eachObj][eachLine][0]==False:
                                        obj.append([eachObj,eachLine])
                                else:
                                    obj.append([eachObj,eachLine])
                            else:
                                obj.append([eachObj,eachLine])
        t = getChineseStrTime()
        print("             ",t)
        if isinstance(l,dict):
            for each in l:
                print("get line ",each,":",l[each])
        else:
            print("get line:",l)
        # print("\n")
        if isinstance(self.line,dict):
            for each in self.line:
                print("line ",each,":",self.line[each])
        else:
            print("line:",self.line)
        print("============ 检测到的对象 ================")
        if len(obj)>0:
            print(obj)
        else:
            print("        没有信号被检测到")
        print("========================================\n\n")
        return obj

    def synchronize(self,l):
        if isinstance(l,dict):
            self.line = l

    def sendNotice(self,obj):
        """

        :param obj: 【【对象，提醒线数值】，。。。。】
        :return:
        """
        if len(obj)<=0:
            return 0
        data = []
        # data:[【获取到的数据字典，提醒线】，。。。。。]
        if isinstance(obj,list):
            for each in obj:
                r = self.getData("last "+each[0])
                # print(r)
                if r==None:
                    r = {
                        "name":each,
                        "value":"无法获取",
                        "valueType":"无法获取",
                        "dataTime":"无法获取",
                        "dataDate":"无法获取",
                        "timeStamp":"无法获取",
                        "dataSource":"无法获取",
                        "unit":"无法获取",
                        "info":{}
                    }
                if "result" in r:
                    if r["result"] == "success":

                        # print(r["data"])
                        if r["data"] == None:
                            r = {
                                "name": each,
                                "value": "无法获取",
                                "valueType": "无法获取",
                                "dataTime": "无法获取",
                                "dataDate": "无法获取",
                                "timeStamp": "无法获取",
                                "dataSource": "无法获取",
                                "unit": "无法获取",
                                "info": {}
                            }
                            data.append([r, each[1]])
                        else:
                            data.append([r["data"],each[1]])
                else:
                    if "data" in r:
                        if r["data"]==None:
                            r = {
                                "name": each,
                                "value": "无法获取",
                                "valueType": "无法获取",
                                "dataTime": "无法获取",
                                "dataDate": "无法获取",
                                "timeStamp": "无法获取",
                                "dataSource": "无法获取",
                                "unit": "无法获取",
                                "info": {}
                            }
                            data.append([r, each[1]])
                        else:
                            data.append([r["data"],each[1]])
                    else:
                        if "name" in r and "value" in r and "valueType" in r:
                            try:
                                data.append([r, each[1]])
                            except:
                                print("error:无法处理数据",r)
                        else:
                            print("error:获取到位置数据结构",r)
        text = ""
        for i in range(len(data)):
            each = data[i][0]
            name = each["name"]
            value = str(each['value'])
            valuetype = each["valueType"]
            dataTime = each["dataTime"]
            date = each["dataDate"]
            stamp = str(each["timeStamp"])
            source = each["dataSource"]
            unit = str(each["unit"])
            info = ""
            for eachInfo in each["info"]:
                info+=eachInfo+":"+str(each["info"][eachInfo])+";"
            text += name+"价格穿透提醒线："+str(data[i][1])+"<br>\n"
            text += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br>\n"
            text += "当前价格:"+value+"/"+unit+"  "+valuetype+"<br>\n"
            text += "详情："+info+"<br>\n"
            text += "数据来源:"+str(source)+"<br>"
            text += date+"  "+dataTime+"<br>\n"
            text += stamp
            text += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br><br>\n\n"
        try:
            self.getEmail()
        except:
            print("error:获取邮箱失败")
        if self.emial==None:
            print("error:没有设置邮箱")
        for each in self.emial:
            recever = each[0]
            address = each[1]
            self.emailService.sendForText(receiver=address,message=text,title="TradeHelperMonitor",fromWhom="TradeHelper",toWhom=recever)
        return 0

    def run(self):
        while(not self.shutdown):
            l = self.getLine()
            monitor_obj = self.checkLine(l)
            self.synchronize(l)
            self.sendNotice(monitor_obj)
            time.sleep(self.interval)


if __name__ == '__main__':
    app = priceNotition()
    app.run()