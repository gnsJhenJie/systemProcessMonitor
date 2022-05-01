import os
import threading
import socket
import datetime
import configs
import json
import pymysql


def get_ip():
    """Get host ip"""
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip


def get_time():
    """Get current time"""
    now = datetime.datetime.now()
    send_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return send_time


class Server:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = ('0.0.0.0', configs.port)
        self.users = {}
        self.configDict = {
            "monitorProcesses": configs.monitorProcesses,
        }
        self.db_settings = {
            "host": configs.db_host,
            "port": configs.db_port,
            "user": configs.db_username,
            "password": configs.db_password,
            "db": configs.db_dbname,
            "charset": configs.db_charset,
        }

    def start_server(self):
        try:
            self.conn = pymysql.connect(**self.db_settings)
            print("資料庫連線成功")
        except Exception as e:
            print("資料庫連線失敗")
            print(e)
            os.exit(0)
        try:
            self.sock.bind(self.addr)
        except Exception:
            print(Exception)
        self.sock.listen(5)
        print("伺服器已開啓，等待連接...")

        # 建立用於接收新連線的thread
        threading.Thread(target=self.accept_connection).start()
        # self.accept_connection()

    def accept_connection(self):
        while True:
            s, addr = self.sock.accept()
            self.users[addr] = s
            number = len(self.users)
            print("用戶端{}連接成功！現在共有{}個連線".format(addr, number))

            # 每個socket連線都需要一個thread來receive訊息
            threading.Thread(target=self.receive, args=(s, addr)).start()

    def receive(self, sock, addr):
        self.send_configs(target=sock)
        last_record_timestamp = {}
        while True:
            try:  # 測試後發現，當用戶率先選擇退出時，這邊就會報ConnectionResetError
                response = sock.recv(4096).decode("gbk")
                response_dict = json.loads(response)
                msg = "{} 用戶端{}：{}".format(get_time(), addr, response)
                if response != "":
                    print(msg)
                else:
                    break
                with self.conn.cursor() as cursor:

                    for process in response_dict["processes"]:
                        if (process in last_record_timestamp and (datetime.datetime.now() - last_record_timestamp[process]).seconds < 30):
                            command = "UPDATE records SET endTime = %s WHERE process = %s AND user = %s AND computerName = %s ORDER BY endTime DESC LIMIT 1"
                            last_record_timestamp[process] = datetime.datetime.now(
                            )
                            cursor.execute(command, (get_time(
                            ), process, response_dict["user"], response_dict["computerName"]))
                        else:
                            command = "INSERT INTO records(client_ip, user, computerName, process, startTime, endTime) VALUES(%s, %s, %s, %s, %s, %s)"
                            last_record_timestamp[process] = datetime.datetime.now(
                            )
                            cursor.execute(
                                command, (addr[0], response_dict["user"], response_dict["computerName"], process, get_time(), get_time()))
                    self.conn.commit()
                # for client in self.users.values():
                #     client.send(msg.encode("gbk"))
            except ConnectionResetError:
                print("用戶{}已經斷線！".format(addr))
                self.users.pop(addr)
                break

    def send_configs(self, target=None):
        """發布組態檔(哪些process需要被監視)"""
        msg = json.dumps(self.configDict)
        if target:
            print("send", msg)
            target.send(msg.encode("gbk"))
        else:
            for client in self.users.values():
                client.send(msg.encode("gbk"))

    def close_server(self):
        for client in self.users.values():
            client.close()
        self.sock.close()
        os._exit(0)


if __name__ == "__main__":
    server = Server()
    server.start_server()
    while True:
        print("輸入stop並按下enter，來關閉伺服器")
        print("輸入update並按下enter，來發佈新的process監聽組態")
        cmd = input()
        if cmd == "stop":
            server.close_server()
        elif cmd == "update":
            configs.updateMonitorProcesses()
            server.configDict["monitorProcesses"] = configs.monitorProcesses
            server.send_configs()
            print("已發佈新的process監聽組態")
        else:
            print("輸入指令無效，請重新輸入！")
