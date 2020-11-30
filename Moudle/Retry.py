# 重写_warpper以保证被修饰函数的参数传递
# _wrapper函数执行被装饰函数
# 装饰器返回_wrapper而不是_wrapper执行结果

def retry(function,i=0,deepth=3):
    def _wrapper(*args,**kwargs):
        return function(*args,**kwargs)
    try:
        return _wrapper
    except:
        if(i>=deepth):
            print(str(function),"执行失败，返回None")
            return None
        else:
            print(str(function),"执行失败，尝试第",i,"次")
            return retry(function,i+1,)

@ retry
def example(*args):
    for each in args:
        print("args:",each)
    f = open("./Spider.py","r")
    data = f.read()
    return [data,"dsfsf"]

if __name__ == '__main__':
    print(example(23,454))