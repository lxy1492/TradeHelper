from threading import Thread

class mutileThread(Thread):
    def __init__(self,name:str,f,*args,**kwargs):
        Thread.__init__(self)
        self.name =  name
        self.func = f
        self.result = None
        self.running = False
        self.error = False
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.running = True
        try:
            self.result = self.func(*self.args,**self.kwargs)
        except:
            self.error = True
        self.running = False
        

    def isRunning(self):
        return self.running


    def __str__(self):
        return str(self.name)+":"+str(self.func)
