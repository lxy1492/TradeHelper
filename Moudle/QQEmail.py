
'''
以测试，可使用
'''

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import parseaddr,formataddr

#连接qq pop3/smtp的信息
SENDER = "415997348@qq.com"
SMTP_SERVER = "smtp.qq.com"
#此密码是qq邮箱SMTP登陆授权码
PASSWORD = "eqvipbrfowfsbgii"

class smtpQQEmail():

    def __init__(self,sender=SENDER,server=SMTP_SERVER,password=PASSWORD,title="Email",content="",receiver=""):
        self.sender = sender
        self.server = server
        self.password = password
        self.content = content
        self.receiver = receiver
        self.title = title
        self.fromWhom = ""
        self.toWhom = ""
        self.message_flag = False

    def setMessage(self):
        if(self.content==""):
            self.message_flag = False
            return 0
        else:
            #设置内容
            self.message = MIMEText(self.content,"plain","utf-8")
            #设置发件人
            self.message["From"] = Header(self.fromWhom,"utf-8")
            #设置收件人
            self.message["To"] =Header(self.toWhom,"utf-8")
            #设置title
            self.message["Subject"] = Header(self.title,"utf-8")
            self.message_flag = True
            return 1

    def setHTMLMessage(self):
        if (self.content == ""):
            self.message_flag = False
            return 0
        else:
            # 设置内容
            self.message = MIMEText(self.content, "html", "utf-8")
            # 设置发件人
            self.message["From"] = Header(self.fromWhom, "utf-8")
            # 设置收件人
            self.message["To"] = Header(self.toWhom, "utf-8")
            # 设置title
            self.message["Subject"] = Header(self.title, "utf-8")
            self.message_flag = True
            return 1

    def setFileMessage(self,type="plain",files=[]):
        if(len(files)==0):
            return 0
        self.message= MIMEMultipart()
        self.message["From"] = Header(self.fromWhom,'utf-8')
        self.message["To"] = Header(self.toWhom,'utf-8')
        self.message["Subject"] = Header(self.title,'utf-8')
        #设置正文内容
        self.message.attach(MIMEText(self.content,type,'utf-8'))
        #构造附件
        for each in files:
            name = each.split("/")[-1]
            f = MIMEText(open(each,'rb').read(),'base64','utf-8')
            f["Content-Type"] = "application/octet-stream"
            f["Content-Disposition"] = 'attachment;filename="{0}"'.format(name)
            self.message.attach(f)
        return 1

    def sendForText(self,receiver="",message="",title="",fromWhom="",toWhom=""):
        flag = False#判断是否需要重置message
        if(receiver!=""):
            self.receiver = receiver
            flag=True
        if(message!=""):
            self.content = message
            flag=True
        if(title!=""):
            self.title = title
            flag=True
        if(fromWhom!=""):
            self.fromWhom=fromWhom
            flag=True
        if(toWhom!=""):
            self.toWhom = toWhom
            flag = True
        if(flag):
            self.setMessage()
        if(self.message_flag):
            if(self.receiver==""):
                self.receiver = input("输入发送地址：")
            try:
                server = smtplib.SMTP(self.server,25)
                server.login(self.sender,self.password)
                server.sendmail(self.sender,self.receiver,self.message.as_string())
                server.quit()
                print("发送成功！")
                return 1
            except:
                print("Error：发送失败！")
                return 0
        else:
            if(self.content==""):
                print("内容为空")
                return 0
            else:
                self.setMessage()
                #print("###########")
                return self.sendForText()

    def sendHTMLEmail(self,reciver="",HTMLcontent="",fromWhom="",toWhom="",):
        print("send HTML message")
        flag = False
        if(reciver!=""):
            self.receiver = reciver
            flag = True
        if(fromWhom!=""):
            self.fromWhom = fromWhom
            flag = True
        if (toWhom!=""):
            self.toWhom = toWhom
            flag = True
        if(HTMLcontent!=""):
            self.content = HTMLcontent
            flag = True
        if(self.content==""):
            self.content = input("输入HTML脚本：")
        if(self.receiver == ""):
            self.receiver = input("输入接收者地址：")
        if(self.receiver==""):
            return 0
        if(self.content==""):
            return 0
        #print("@@@@@@@@@@@@@")
        self.setHTMLMessage()
        try:
            server = smtplib.SMTP(self.server,25)
            server.login(self.sender,self.password)
            server.sendmail(self.sender,self.receiver,self.message.as_string())
            server.quit()
            print("发送成功！")
            return 1
        except:
            print("Error：发送失败！")
            return 0

    def sendWithFiles(self,receive="",f=[],content="",toWhom="",fromWhom=""):
        flag = False
        if(content!=""):
            self.content = content
            flag = True
        if(toWhom!=""):
            self.toWhom = toWhom
            flag = True
        if(fromWhom!=""):
            self.fromWhom = fromWhom
            flag = True
        if(len(f)==0):
            return 0
        if(receive!=""):
            self.receiver = receive
        else:
            if(self.receiver==""):
                self.receiver = input("输入接收者地址：")
        if(self.receiver==""):
            return 0
        if(self.content == ""):
            self.content = input("输入正文内容：")
            type = input("输入正文类型(plain/html):")
        re = self.setFileMessage(files=f,type=type)
        if(re):
            try:
                server = smtplib.SMTP(self.server,25)
                server.login(self.sender,self.password)
                server.sendmail(self.sender,self.receiver,self.message.as_string())
                print("fas成功！")
                return 1
            except:
                print("Error:发送失败!")
                return 0
        else:
            return 0

    def sendImgMessage(self,imagefile,imageTitle="Imag"):

        msgRoot = MIMEMultipart('related')  # 邮件类型，如果要加图片等附件，就得是这个

        msgRoot['Subject'] = self.title# 邮件标题，以下设置项都很明了
        msgRoot['From'] = self.fromWhom
        # msgRoot['To'] = receiver # 发给单人
        msgRoot['To'] = ",".join([self.receiver])  # 发给多人
        # message['Cc'] = ";".join([SENDER])  # 抄送人

        # 以下为邮件正文内容，含有一个居中的标题和一张图片
        content = MIMEText(
            '<html><head><style>#string{text-align:center;font-size:25px;}</style><div id="string">'+imageTitle+'<div></head><body><img src="cid:image1" alt="image1"></body></html>',
            'html', 'utf-8')
        # 如果有编码格式问题导致乱码，可以进行格式转换：
        # content = content.decode('utf-8').encode('gbk')
        msgRoot.attach(content)

        # 上面加的图片src必须是cid:xxx的形式，xxx就是下面添加图片时设置的图片id
        # 添加图片附件
        fp = open(imagefile, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', 'image1')  # 这个id用于上面html获取图片
        msgRoot.attach(msgImage)
        try:
            server = smtplib.SMTP(self.server, 25)
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receiver, msgRoot.as_string())
            server.quit()
            print("发送图片邮件成功！")
        except:
            print("发送图片邮件失败！")


if __name__ == "__main__":
    # t = smtpQQEmail()
    # t.receiver = "415997348@qq.com"
    # t.content = '<a href="www.baidu.com">fffffffffffffffffffffffffff</a>'
    # t.sendHTMLEmail()
    import  os
    print(os.getcwd())
    os.chdir("../../")
    print(os.getcwd())
    t = smtpQQEmail()
    # t.receiver= "415997348@qq.com"
    # t.sendImgMessage("./Au9999/datasets/IMG/黄金9999_2019_7_11.jpg")
    t.receiver = "1650052434@qq.com"
    t.sendForText(receiver="1650052434@qq.com",message="test",title="test",fromWhom="stmpserver",toWhom="lxySpeed")