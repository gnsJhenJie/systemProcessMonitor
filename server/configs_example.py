# 請記得將檔名改為configs.py
# 伺服器監聽port
port = 8805
# 資料庫配置
db_host = "127.0.0.1"
db_port = 3306
db_username = "root"
db_password = "PASSWORD"
db_dbname = "computerMonitor"
db_charset = "utf8"

# 以下勿更改
monitorProcesses = []


def updateMonitorProcesses():
    global monitorProcesses
    with open('monitorProcesses.txt', 'r') as file:
        monitorProcesses = file.read().splitlines()


updateMonitorProcesses()
