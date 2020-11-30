from manager.dataManager import DataHelper
import os,json
from multiprocessing import Process
from threading import Thread
import tkinter as tk


class TradeHelper(DataHelper):
    def __init__(self,name="TradeHelper"):
        DataHelper.__init__(self,name)

class winAPP():
    def __init__(self,title="TradeHelper",size="400x300",getDataFromServer=False):
        self.window = tk.Tk()
        self.window.title(title)
        self.window.geometry(size)
        self.var = tk.StringVar()
        self.var.set("点击开始运行"+title)
        label = tk.Label(self.window,textvariable=self.var,font=("Arial",12),width=30,height=2)
        label.pack()
        self.start = tk.Button(self.window,text="开始",font=("Arial",12),width=10,height=1,command=self.click_start)
        self.TradeHelper = TradeHelper()
        self.TradeHelper.data.getDataFromDataServer=getDataFromServer
        self.start.pack()
        self.getDataFromServer = tk.Button(self.window,text="服务器数据",font=("Arial",12),width=10,height=1,command=self.setServerData)
        self.getDataFromServer.pack()
        # self.runTradeHelper()

    def runTradeHelper(self):
        t = Process(target=self.TradeHelper.run)
        t.start()

    def click_start(self):
        self.var.set("正在运行")
        # self.runTradeHelper()
    def setServerData(self):
        self.TradeHelper.data.getDataFromDataServer=True

    def run(self):
        # self.runTradeHelper()
        self.window.mainloop()

def runOnTheOthreProcess():
    app = TradeHelper()
    t = Process(target=app.run)
    t.start()


def runTradeHelper():
    app = TradeHelper()
    if os.path.exists("./config.json"):
        with open("./config.json","r") as f:
            rewrite = False
            try:
                config = json.loads(f.read())
                app.data.getDataFromDataServer = config["getDataFromDataServer"]
            except:
                rewrite = True
        if rewrite:
            with open("./config.json", "w") as f:
                app.data.getDataFromDataServer = False
                f.write(json.dumps({"getDataFromDataServer": False}))
    else:
        with open("./config.json","w") as f:
            app.data.getDataFromDataServer = False
            f.write(json.dumps({"getDataFromDataServer":False}))
    app.run()

def writegetdatafromserverconfig(a=True):
    with open("./config.json", "w") as f:
        # app.data.getDataFromDataServer = True
        f.write(json.dumps({"getDataFromDataServer": a}))

if __name__ == '__main__':
    writegetdatafromserverconfig(True)
    runTradeHelper()
