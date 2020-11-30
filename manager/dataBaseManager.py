import json,pickle,time,os,base64
from Moudle.mutile_thread import mutileThread

dataBaseDIR = "../FileWebDIR/TradeHelperDataBase/"
originalDIR = os.path.join(dataBaseDIR,"Original").replace("\\","/")

def getDate(fileName):
    data = fileName.split(" ")[1].split(".")[0]
    data = int(data)
    # print(data)
    return data

def sortFile(l):
    if isinstance(l,list):
        ll = []
        for i in range(len(l)):
            s = None
            early = None
            for each in l:
                if early==None:
                    early = getDate(each)
                    s = each
                else:
                    date = getDate(each)
                    if early>date:
                        early = date
                        s = each
            ll.append(s)

            l.remove(s)
        return ll
    elif isinstance(l,dict):
        for each in l:
            l[each] = sortFile(l[each])
        return l
    return None


def getALLOrigianlList(DIR=originalDIR,sortFileList=False,objs=None):
    l = {}
    for each in os.listdir(DIR):
        if ".tbs" in each and " " in each:
            if each.split(".")[-1]=="tbs":
                if isinstance(objs,str):
                    objs = [objs]
                if isinstance(objs,list) and len(objs)>=1:
                    name = each.split(" ")[0]
                    if name in objs:
                        if name in l:
                            l[name].append(each)
                        else:
                            l.update({name: [each]})
                else:
                    name = each.split(" ")[0]
                    if name in l:
                        l[name].append(each)
                    else:
                        l.update({name:[each]})
    if sortFileList:
        l = sortFile(l)
    return l

def readData(*args):
    datas = []
    path = None
    if len(args)==1:
        path = args[0]
    elif len(args)>=2:
        DIR = None
        Name = None
        for each in args:
            if isinstance(each,str):
                if each.split(".")[-1] == "tbs" and " " in each:
                    Name = each
                elif os.path.exists(each):
                    DIR = each
        if DIR!=None and Name!=None:
            path = os.path.join(DIR,Name).replace("\\","/")
    if path!=None:
        with open(path,"r") as f:
            for eachLine in f.read().split("\n"):
                if eachLine!="":
                    # datas.append(json.loads(eachLine))
                    # print(eachLine)
                    datas.append(pickle.loads(base64.b64decode(json.loads(eachLine)["data"])))
    return datas

def getOriginalData(l):
    if isinstance(l,str):
        l = [l]
    if isinstance(l,list):
        data = []
        for each in l:
            data.extend(readData(originalDIR,each))
        return data
    elif isinstance(l,dict):
        data = {}
        ths = []
        for eachKey in l:
            t = mutileThread(eachKey,getOriginalData,l[eachKey])
            ths.append(t)
            t.run()
        for each in ths:
            while(each.running):
                pass
            data.update({each.name:each.result})
            # each.stop()
            del each
        return data
    return None


def loadOBJData(obj="Ag(T+D)",date=None):
    if date!=None:
        if isinstance(date,str):
            for each in ["-"," ","_",":",";",".",",","|","\\","/"]:
                if each in date:
                    date.replace(each,"")
                    break
            l = getALLOrigianlList()
            for each in l[obj]:
                if getDate(each)==date:
                    return getOriginalData(each)
            return None
        elif isinstance(date,list):
            data = []
            for each in date:
                r = loadOBJData(obj,each)
                if r!=None:
                    if isinstance(r,list):
                        data.extend(r)
                    else:
                        data.append(r)
            return data
    else:
        l = getALLOrigianlList()
        # print(obj)
        l = l[obj]
        dates = []
        for each in l:
            dates.append(getDate(each))
        return loadOBJData(obj,dates)
    return None



if __name__ == '__main__':
    os.chdir("../")
    # print(int("2020_04_15"))
    l = getALLOrigianlList()
    data = getOriginalData(l)
    for each in data:
        print(each,"  :  ",len(data[each]))