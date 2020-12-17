from tkinter import *
import tkinter.font as tkFont
import IPy
import os
import platform
import sys
import socket
import threading
import queue
import base64
from icon import img

class BoxScan:
    def __init__(self, BoxScanUI):
        self.BoxScanUI = BoxScanUI

    # 初始化GUI
    def BoxScanGui(self):
        self.BoxScanUI.title("盒子端口扫描器")
        tmp = open("tmp.ico", "wb+")
        tmp.write(base64.b64decode(img))
        tmp.close()
        self.BoxScanUI.iconbitmap("tmp.ico")
        os.remove("tmp.ico")
        self.center(400, 680)
        # 固定GUI
        self.BoxScanUI.resizable(0, 0)

        # 启用网格布局
        self.fontExample = tkFont.Font(family="微软雅黑", size=9, weight="bold")
        self.fontStyle = tkFont.Font(family="微软雅黑", size=11)
        self.frame_t = Frame(self.BoxScanUI)
        self.frame_c = Frame(self.BoxScanUI)
        self.frame_f = Frame(self.BoxScanUI)
        self.frame_t.grid(row=0, column=0)
        self.frame_c.grid(row=1, column=0)
        self.frame_f.grid(row=2, column=0)

        self.ipTip = Label(self.frame_t, text="请输入IP地址：", font=self.fontStyle)
        self.portTip = Label(self.frame_t, text="请输入端口范围：", font=self.fontStyle)
        self.threadTip = Label(self.frame_t, text="请输入线程数：", font=self.fontStyle)
        self.ipInput = StringVar()
        self.portInput = StringVar()
        self.threadInput = StringVar()
        self.ipInput.set("127.0.0.1")
        self.portInput.set("1-1000")
        self.threadInput.set("20")
        self.ipEntry = Entry(self.frame_t, textvariable=self.ipInput, font=self.fontStyle)
        self.portEntry = Entry(self.frame_t, textvariable=self.portInput, font=self.fontStyle)
        self.threadEntry = Entry(self.frame_t, textvariable=self.threadInput, font=self.fontStyle)
        self.ipTip.grid(row=0, column=0, padx=10, pady=5)
        self.ipEntry.grid(row=0, column=1, padx=10, pady=5)
        self.portTip.grid(row=1, column=0, padx=10, pady=5)
        self.portEntry.grid(row=1, column=1, padx=10, pady=5)
        self.threadTip.grid(row=2, column=0, padx=10, pady=5)
        self.threadEntry.grid(row=2, column=1, padx=10, pady=5)

        self.informationText = Text(self.frame_c, width=54, height=27)
        self.scroll = Scrollbar(self.frame_c)
        self.scroll.pack(side=RIGHT, fill=Y, pady=30)
        self.informationText.pack(side=RIGHT, fill=Y, pady=30)
        self.scroll.config(command=self.informationText.yview)
        self.informationText.config(yscrollcommand=self.scroll.set, font=self.fontExample, fg="#3EAE3E", bg="black")
        self.informationText.insert(END, "-------------------------------BoxScanner------------------------------\n")

        self.btn = Button(self.frame_f, text="开始扫描", command=self.run, font=self.fontStyle)
        self.btn.pack(pady=5)

    # 启动GUI时居屏幕中间
    def center(self, width, height):
        screenwidth = self.BoxScanUI.winfo_screenwidth()
        screenheight = self.BoxScanUI.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.BoxScanUI.geometry(size)

    # 校验IP地址格式
    def checkIP(self):
        try:
            IPy.IP(self.ipEntry.get())
            return True
        except Exception:
            return False

    # 校验端口格式
    def checkPort(self):
        if re.match("^(?:[0-9]{1,5}-){1}[0-9]{1,5}$", self.portInput.get()):
            return True
        return False

    # 校验线程数格式
    def checkThread(self):
        numStr1 = self.threadEntry.get()
        numStr2 = str(numStr1).strip().lstrip('-').lstrip('+')
        if str(numStr2).isdigit():
            return True
        return False

    # 获取目的主机的操作系统
    def getOS(self):
        os = platform.system()
        if os == "Windows":
            return "-n"
        elif os == "Linux":
            return "-c"
        else:
            self.informationText.insert(END, "[+] 暂不支持此系统!")
            sys.exit()

    # 使用Ping命令检测目标地址是否存活
    def pingIP(self, ip):
        output = os.popen("ping %s 1 %s" % (self.getOS(), ip)).readlines()
        for n in output:
            if str(n).upper().find("TTL") >= 0:
                self.informationText.insert(END, "-------------------------------BoxScanner------------------------------\n")
                self.informationText.insert(END, "[+] TargetIP：%s\n" % ip)
                self.informationText.insert(END, "[+] %s online\n" % ip)
                return True

    # 使用线程防止在Tk窗口下将socket放入mainloop时导致tk窗口的假死
    def setThreads(self, func, *args):
        t = threading.Thread(target=func, args=args)
        t.setDaemon(True)
        t.start()

    # 开启端口扫描
    def portSetting(self, port, thread):
        ports = port.split('-')
        startPort = ports[0]
        endPort = ports[1]
        portsList = list(range(int(startPort), int(endPort) + 1))
        portQueue = queue.Queue()
        for num1 in portsList:
            portQueue.put(num1)
        for num2 in range(0, int(thread)):
            self.setThreads(self.portScan, portQueue)

    def portScan(self, portQueue):
        while True:
            if portQueue.empty():
                break
            ip = self.rightIP
            port = portQueue.get()
            s = socket.socket()
            s.settimeout(0.4)
            try:
                if s.connect_ex((ip, port)) == 0:
                    self.informationText.insert(END, "[+] PORT %s OPEN \n" % port)
            except Exception:
                pass
            finally:
                s.close()


    def run(self):
        global rightThread
        self.informationText.delete(0.0, END)
        if self.checkIP():
            self.rightIP = self.ipEntry.get()
        else:
            self.informationText.insert(END, "-------------------------------BoxScanner------------------------------\n")
            self.informationText.insert(END, "[+] ip格式错误,请输入正确格式!")
            return
        if self.checkPort():
            rightPort = self.portEntry.get()
        else:
            self.informationText.insert(END, "-------------------------------BoxScanner------------------------------\n")
            self.informationText.insert(END, "[+] 端口格式错误,请输入正确格式(1-65535)!")
            return
        if self.checkThread():
            rightThread = self.threadEntry.get()
        else:
            self.informationText.insert(END, "-------------------------------BoxScanner------------------------------\n")
            self.informationText.insert(END, "[+] 请输入正确的线程数!")
            return
        if self.pingIP(self.rightIP):
            self.portSetting(rightPort, rightThread)
        else:
            self.informationText.insert(END, "-------------------------------BoxScanner------------------------------\n")
            self.informationText.insert(END, "[+] %s offline 请重新输入IP地址\n" % self.rightIP)
            return


if __name__ == "__main__":
    root = Tk()
    UI = BoxScan(root)
    UI.BoxScanGui()
    root.mainloop()
