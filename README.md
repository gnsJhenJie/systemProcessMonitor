# OS Thread Project - 系統監視工具
## Setup
### Server:  
* `pip install -r server/requirements.txt`  
* 在資料庫中以`server/records.sql`建立名為`records`的資料表
* 設定`server/configs_example.py`內的資料，並且重新命名為`server/configs.py`
### Client:  
* `pip install -r client/requirements.txt`  
* 設定`client/configs_example.py`內的資料，並且重新命名為`client/configs.py`
## Execute
### Server:
* `python3 server/app.py`
### Client:
* `python3 client/app.py`

## 簡介

這個工具分為Server與Client端，透過Socket作為通訊方法，在Server端可設置要監視哪些程式，Client端會依照設置檢查OS中是否正在執行上述的process，並回傳的資料給Server存進資料庫。

## 應用場景
- 電腦教室：統計每台電腦各應用程式的使用情形
- 公司：監視每個員工在電腦使用的程式及時間
## 程式功能&流程
### Server: 
環境:
- Python3.8以上
    - pymysql, json(資料傳輸格式為json), socket, threading
- Windows / UNIX 皆可
- MariaDB

功能:
- 依照監視組態```monitorProcesses.txt```以Socket發布要監視哪些process的資訊給Client
- 建立Socket伺服器接收Client端的資料
- 將Client端的資料寫入資料庫中

```server/app.py```為Server端的主程式，```server/configs.py```為設定相關參數的地方。

 在```server/app.py```中，`class Server`物件是最重要的一部分，當中包括以下methods:
 - `start_server()`: 連線到資料庫，並監聽指定的port，接著開啟一個Thread執行`accept_connecction()`（開一個Thread的用意是讓main thread可以繼續執行input()指令）
 - `accept_connection()`: 透過`while True`持續檢查是否有新的socket連線(從client端連入)，若有新連線則開一個thread執行`receive()`（因為與client的socket需保持連線狀態，所以需要一個client開一個thread來保持連線）
 - `send_configs()`: 當client第一次連線或是在terminal輸入update指令時，會透過這個method發布新的組態給client端
 - `close_server()`：關閉server

### Client:
環境:
- Python3.8以上
    - psutil(查詢OS中執行的process), json(資料傳輸格式為json), socket, threading
- Windows / UNIX 皆可

功能:
- 連線至`client/configs.py`所設定的Server，並持續檢查(每五秒檢查一次)是否有server要監視的process正在執行
- 傳送給Server哪些被監視的process正在執行

`client/app.py`為Client端的主程式，`client/configs.py`為設定相關參數的地方。

在`client/app.py`中，主要有以下兩個function:
- `send_msg()`: 檢查OS中是否有需監視的process正在執行，若有則透過socket連線以json格式回傳給Server
- `recv_msg()`: 以socket接收Server端傳來的監視組態

以上兩個function分別以兩個thread各自執行，因此可以同時接收新的組態與監視系統中的process，而組態以global variable的方式在兩個thread間共享。

## 實際畫面
Demo影片: https://youtu.be/qIIRTrGrUao

`server/app.py`:  
![](https://i.imgur.com/z3jRtlF.png)

資料表:  
![](https://i.imgur.com/wCFFYPE.png)

`client/app.py`:  
![](https://i.imgur.com/1Bw1WmY.png)



## 參考資料

- Python socket聊天室: https://www.twblogs.net/a/5ef78e5cdf18513b2737877a
- Python timestamp: https://timestamp.online/article/how-to-get-current-timestamp-in-python
- Python MySQL操作: https://www.learncodewithmike.com/2020/02/python-mysql.html
