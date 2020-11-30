import time

def get_local_str_date_time():
    t = time.localtime()
    strTime = str(t.tm_year)+"_"+str(t.tm_mon)+"_"+str(t.tm_mday)
    # print(t)
    return strTime

def getChineseStrTime():
    # t = time.time()
    t = time.localtime()
    year = t.tm_year
    mon = t.tm_mon
    day = t.tm_mday
    h = t.tm_hour
    m = t.tm_min
    s = t.tm_sec
    string = str(year)+"年"+str(mon)+"月"+str(day)+"日  "+str(h)+"时"+str(m)+"分"+str(s)+"秒"
    return string