import time
def getWeekDay():
     t  =time.localtime()
     return t.tm_wday+1

if __name__ == '__main__':
    d = getWeekDay()
    print(d)