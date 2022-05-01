import socket
import threading
import os
import configs
import psutil
import time
import datetime
import json


def get_ip():
    """Get ip"""
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip


def get_time():
    """Get current time"""
    now = datetime.datetime.now()
    send_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return send_time


communicateDict = {
    "user": os.getlogin(),
    "computerName": socket.gethostname(),
    "processes": [],
}

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = (configs.server_addr, configs.server_port)
print("正在連線到", end="")
print(addr)
s.connect(addr)

monitor_apps = []


def recv_msg():  #
    global monitor_apps
    print("連接成功！")
    while True:
        try:  # 測試發現，當服務器率先關閉時，這邊也會報ConnectionResetError
            response = s.recv(1024)
            print("Received new configs from server")
            monitor_apps = json.loads(response.decode("gbk"))[
                "monitorProcesses"]
        except ConnectionResetError:
            print("伺服器已關閉，連線結束！")
            s.close()
            break
    os._exit(0)


def send_msg():
    global monitor_apps
    global communicateDict
    print("連線成功！")
    while True:
        # Get Generator object containing all running processes
        process_iterator = psutil.process_iter()
        # Iterate over Generator object to get
        # each process object contained by it
        communicateDict['processes'] = []
        for proc in process_iterator:
            try:
                # Get process name & pid from process object
                processName = proc.name()
                # print(type(processName))
                if processName in monitor_apps and processName not in communicateDict['processes']:
                    communicateDict['processes'].append(processName)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        msg = json.dumps(communicateDict)
        if communicateDict['processes']:
            print(msg)
            s.send(msg.encode("gbk"))
        time.sleep(5)
    os._exit(0)


# 兩個thread
# 一個用於接收來自伺服器的資料(如：新的監視process組態)
# 一個用於發送資料(如：每五秒傳送一次client端有哪些被監視的process正在執行)
threads = [threading.Thread(target=recv_msg),
           threading.Thread(target=send_msg)]
for t in threads:
    t.start()
