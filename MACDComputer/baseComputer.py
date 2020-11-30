from Moudle.printError import *
from Moudle.dataType import DataType
from threading import Thread

class BaseComputer():
    def __init__(self, name="Computer", poolLength=None):
        self.lastResult = None
        self.data_pool = []
        self.data_pool_length = poolLength
        self.dataDriver = None
        self.threadDataDriver = False
        self.name = name
        self.setup_ready = False
        self.savePath = "./BaseModule.pkl"
        self.saveDataPath = None
        self.setUp()

    def setSaveDataPath(self, path):
        if isinstance(path, str):
            self.saveDataPath = path.replace("\\", "/")
            return 0
        else:
            return -1

    def setSavePath(self, path):
        if isinstance(path, str):
            self.savePath = path
            return 0
        else:
            return -1

    def setUp(self):
        self.setup_ready = True

    def setDataDriver(self, f, asy=False):
        self.dataDriver = f
        if asy:
            self.threadDataDriver = True

    def PushData(self, data):
        if not self.setup_ready:
            print_warnning("该对象未初始化,请运行setUp()")
        if isinstance(data, DataType):
            self.data_pool.append(data)
            i = 0
            if self.data_pool_length > 0:
                while (len(self.data_pool) > self.data_pool_length):
                    i += 1
                    self.data_pool.remove(self.data_pool[0])
            else:
                print_warnning("没有设置数据池上限！！！")
            # 当注册了数据驱动函数后执行，分多线程触发和序列执行两种
            if self.dataDriver != None:
                if self.threadDataDriver:
                    t = Thread(target=self.dataDriver)
                    t.start()
                else:
                    self.dataDriver()
            # 返回i的大小代表移除了多少数据
            return i
        else:
            print_error("数据类型错误，请输入正确的数据类型-BaseData")
            return -1

    def PopData(self):
        if len(self.data_pool) > 0:
            data = self.data_pool[0]
            self.data_pool.remove(self.data_pool[0])
            return data
        else:
            print_error("当前数据池为空")
            return None

    def Clear(self):
        self.data_pool = []

    def setPoolLength(self, length):
        if isinstance(length, int):
            self.data_pool_length = length
        else:
            print_error("输入数据类型错误")

    def setPool(self, dataPool):
        if isinstance(dataPool, list):
            i = 0
            for each in dataPool:
                if not isinstance(each, DataType):
                    print_error("检测到数据类型错误，dataPool必须只包含BaseData类型")
                    return -1
            self.data_pool = dataPool
            return i
        else:
            print_error("dataPool必须为数组类型")

    def getMA(self, MA, data=None, dataLength=None):
        if data == None:
            data = self.data_pool
        if dataLength == None:
            dataLength = self.data_pool_length
        if MA > dataLength:
            print_warnning("MA", MA, "大于规定数据池长度", self.data_pool_length, "，重置MA为数据池长度")
            MA = dataLength
        return self.getMean(end=-1, length=MA, dataPool=data)

    def getDataLength(self):
        return len(self.data_pool)

    def getMean(self, start=0, end=None, length=None, dataPool=None):
        if dataPool == None:
            dataPool = self.data_pool
        if length != None:
            dateLength = len(dataPool)
            if length > dateLength:
                length = dateLength
                print_warnning("length out of data_pool,设置长度超长！")
            if end == None:
                end = start + length
            else:
                if end > 0:
                    if end >= length:
                        start = end - length
                    else:
                        start = 0
                        print_warnning("设置长度超出结束位置")
                else:
                    if end < 0:
                        end = dateLength + end
                        if end > length:
                            start = end - length
                        end = end + 1
        if end == None:
            data = dataPool[start:]
        else:
            data = dataPool[start:end]
        # for each in data:
        #     print("看看能不能输出value",str(each))
        mean_ = sum([each.value for each in data]) / (end - start)
        # return data
        r = DataType(name="均值", value=mean_)
        return r

    # 保存自身缓存
    def save(self):
        d = pickle.dumps(self)
        with open(self.savePath, "wb") as f:
            f.write(d)

    # 保存计算结果的方法
    def saveData(self):
        pass

    def getSaveDataFileName(self):
        pass

    @property
    def lastData(self):
        if isinstance(self.data_pool, list):
            if len(self.data_pool) > 0:
                return self.data_pool[-1]
        return None


def testDataLengthConputer():
    d = []
    for i in range(10):
        data = DataType(name="testData" + str(i), value=i)
        d.append(data)
    c = BaseComputer()
    c.setPool(d)
    c.setPoolLength(10)
    r = c.getMean(length=10, end=-1)
    for each in r:
        print(each.value, end="  |")


def testMACompute(MA):
    d = []
    for i in range(10):
        data = DataType(name="testData" + str(i), value=i)
        d.append(data)
    c = BaseComputer()
    c.setPool(d)
    r = c.getMA(MA)
    print_warnning(r)

if __name__ == '__main__':
    testDataLengthConputer()
    testMACompute()
