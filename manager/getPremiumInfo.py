from Moudle.dataType import DataType
from manager.dataBaseManager import loadOBJData

def AGTD_Premium(obj="Ag(T+D)",date=None):
    data = loadOBJData(obj,date)
    print(len(data))

if __name__ == '__main__':
    import os
    os.chdir("../")
    data = AGTD_Premium()
