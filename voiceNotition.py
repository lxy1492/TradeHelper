import time
try:
    import pythoncom
except:
    pythoncom = None
try:
    import win32com.client as win
except:
    win = None
from getData.getData import DataServer


def check():
    if pythoncom==None or win==None:
        return False
    return True

def voiceBroad(text):
    if not check():
        return -1
    if isinstance(text, str):
        speak = win.Dispatch("SAPI.SpVoice")
        speak.Speak(text)
    elif isinstance(text, list):
        speak = win.Dispatch("SAPI.SpVoice")
        if len(text) > 0:
            for each in text:
                if each != "":
                    speak.Speak(each)
    return 0

class voice_notition():
    def __init__(self,name="voice notition",data=None):
        self.name = name
        try:
            pythoncom.CoInitialize()
        except:
            pass
        self.data = data
        self.notition=[self.voiceTime]
        self.text = []
        self.textNew = False
        self.lock = False

        self.attentionForData = ["Ag(T+D)","Au(T+D)","LondonGold","伦敦银","GoldSliver"]

        # voiceTime的变量
        self.lastTimeStamp = None
        self.timeVoiceInterval = 1800 # 秒

    def setText(self,mess):
        if isinstance(mess,str):
            self.text.append(mess)
            self.textNew = True

    def clearText(self):
        self.text = []
        self.textNew = False


    def __str__(self):
        return self.name

    def voiceTime(self):
        stamp = time.time()
        if self.lastTimeStamp!=None:
            if isinstance(self.lastTimeStamp,float) or isinstance(self.lastTimeStamp,int):
                d = stamp-self.lastTimeStamp
                if d<self.timeVoiceInterval:
                    return -1
        t = time.localtime()
        year = t.tm_year
        mon = t.tm_mon
        day = t.tm_mday
        h = t.tm_hour
        m = t.tm_min
        s = t.tm_sec
        text = ""
        if h in [7,0,24]:
            text += "现在是北京时间:"+str(year)+"年"+str(mon)+"月"+str(day)+"日"+","+str(h)+"点"+str(m)+"分。"
        elif h in [8,18,22,12]:
            text += "现在是北京时间:" + str(h) + "点" + str(m) + "分。"
        else:
            text += "现在是:" + str(h) + "点" + str(m) + "分。"
        self.setText(text)

        if m-self.timeVoiceInterval/60>1 or m-self.timeVoiceInterval/60<-1:
            if m<30:
                dt = str(year)+"-"+str(mon)+"-"+str(day)+" "+str(h)+":0:0"
            else:
                dt = str(year) + "-" + str(mon) + "-"
                str(day) + " " + str(h) + ":30:0"
            timeArray = time.strftime(dt,"%Y-%m-%d %H:%M:%S")
            timeStamp = time.mktime(timeArray)
            self.lastTimeStamp = timeStamp
        else:
            self.lastTimeStamp = time.time()
        return 0

    def sendVoice(self):
        if not check():
            return -1
        self.lock = True
        for each in self.text:
            voiceBroad(each)
        self.clearText()
        return 0

    def run(self,*args,**kwargs):
        if self.lock:
            return -1
        for each in self.notition:
            try:
                each()
            except:
                pass
        if self.textNew:
            # self.textNew = False
            self.sendVoice()
        return 0