import socket
import threading
import config

class API_Server():
    def __init__(self, name="API_Server", ip=config.IP, port=config.PORT):
        self.ip = ip
        self.port = port
        self.s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name

    def setIP(self, ip):
        if isinstance(ip, str):
            self.ip = ip

    def setPort(self, port):
        if isinstance(port, int):
            self.port = port

    def Listen(self,num=10):
        if isinstance(num,int):
            self.s.bind((self.ip,self.port))
            self.s.listen(num)

    def getConnection(self):
        conn,addr = self.s.accept()
        t = threading.Thread(target=self.dealConnection,args=(conn,addr))
        t.start()

    def run(self):
        self.Listen()
        while(True):
            self.getConnection()


    def dealConnection(self,conn,addr):
        hello = "this is "+self.name
        conn.send(hello.encode())
        _ = conn.recv(1024)