import json
import logging
import time
import sys
import os
import sqlite3
import configparser
from enum import Enum
import serial
import modbus_tk
from modbus_tk import modbus_rtu
import zmq
import SDC_DataPlatform


class Runtime(Enum):
    Input = 1
    Output = 2
    Global = 3


def DebugLog(mesg):
    print(f"DEBUG: {mesg}")
    logging.debug(mesg)


def ErrorLog(mesg):
    print(f"ERROR: {mesg}")
    logging.error(mesg)


def CriticalToExit(mesg):
    print(f"CRITICAL: {mesg}")
    logging.critical(mesg)
    input("press entry to exit")
    sys.exit(0)


def SaveDataToPersistenceSQL(cursor: sqlite3.Cursor, time, name, data):
    cursor.execute("INSERT INTO table01 VALUES (null,?,?,?)", (time, name, data))


def InitDataToRuntimeSQL(cursor: sqlite3.Cursor, table: int, name: str):
    '''
    初始化数据到运行时数据库

    :param cursor: 数据库的指针
    :param table: 表名，int类型，定义在类 Runtime（Enum）之中
    :param name: 数据的名称
    :return:
    '''
    if table == Runtime.Input:
        cursor.execute("INSERT INTO InputParam VALUES (null,?,?)", (name, 0))
        return
    if table == Runtime.Output:
        cursor.execute("INSERT INTO OutputParam VALUES (null,?,?)", (name, 0))
        return
    if table == Runtime.Global:
        cursor.execute("INSERT INTO GlobalParam VALUES (null,?,?)", (name, 0))
        return


def UpdateDataToRuntimeSQL(cursor: sqlite3.Cursor, table, name, data):
    if table == Runtime.Input:
        if cursor.execute("select * from InputParam where name = ?", (name,)).fetchall():
            cursor.execute("UPDATE InputParam SET data = ? WHERE name = ?", (data, name))
        else:
            ErrorLog(f"could not find {name} in InputParam table")
        return
    if table == Runtime.Output:
        if cursor.execute("select * from OutputParam where name = ?", name).fetchall():
            cursor.execute("UPDATE InputParam SET data = ? WHERE name = ?", (data, name))
        else:
            ErrorLog(f"could not find {name} in OutputParam table")
        return
    if table == Runtime.Global:
        if cursor.execute("select * from GlobalParam where name = ?", name).fetchall():
            cursor.execute("UPDATE InputParam SET data = ? WHERE name = ?", (data, name))
        else:
            ErrorLog(f"could not find {name} in GlobalParam table")
        return


def ExecuteSeverCommand(command: str):
    d = json.loads(command)
    # if d["type"] == "Parma":
    #
    # elif d["type"] == "Modbus":





if __name__ == "__main__":

    # region ——————配置log格式——————
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s; %(levelname)s; %(message)s",
                        datefmt='%Y-%m-%d  %H:%M:%S',
                        filename='rootLog.log',
                        )
    logging.debug("app start")
    modbus_tk.LOGGER.disabled = True
    # endregion

    # region ——————环境校验——————

    # 判断是否存在RTUMasterDefine目录
    if getattr(sys, 'frozen', False):
        RootDir = os.path.dirname(sys.executable)
    elif __file__:
        RootDir = os.path.dirname(__file__)
    masterDefDir = os.path.join(RootDir, "modbusRTU_MasterDefine")

    if not os.path.exists(masterDefDir):
        CriticalToExit("'./modbusRTU_MasterDefine' is not found")
    masterDefs = os.listdir(masterDefDir)
    if len(masterDefs) == 0:
        CriticalToExit("no defines been found in './modbusRTU_MasterDefine'")

    # 检查数据库文件夹
    databaseDir = os.path.join(RootDir, "database")
    if not os.path.exists(databaseDir):
        os.makedirs(databaseDir)
        logging.debug("create './database' folder")

    # 检查配置文件
    configPath = os.path.join(RootDir, "./config.ini")
    if not os.path.exists(configPath):
        CriticalToExit(f"Could not find config.ini in root dir")

    # endregion

    # region ——————读取ModbusMaster定义————————
    jsonD = []
    for p in masterDefs:
        p = os.path.join(masterDefDir, p)
        try:
            with open(p, "r", encoding="utf-8") as f:
                jsonD.append(json.load(f))
            DebugLog(f"load {p} successfully")

        except:
            CriticalToExit(f"load {p} fail")
    # endregion

    # region ——————读取配置文件——————
    try:
        cf = configparser.ConfigParser()
        cf.read(configPath)
        readInterval = int(cf.get("Port Define", "read_interval"))
        switchPortInterval = int(cf.get("Port Define", "switch_port_interval"))
    except Exception as e:
        CriticalToExit(f"Critical error raise. Error is {e.__str__()}")
    # endregion

    # region ——————创建数据库——————
    date = "2020-01-01"
    if time.strftime("%Y-%m-%d", time.localtime()) != date:
        date = time.strftime("%Y-%m-%d", time.localtime())
    databasePath = os.path.join(databaseDir, f"{date}.db")
    if not os.path.exists(databasePath):
        db = sqlite3.connect(databasePath)
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS table01(
        id INTEGER PRIMARY KEY,
        time TEXT NOT NULL
        ,name TEXT NOT NULL,
        data NUMERIC NOT NULL)""")
        DebugLog(f"Create new database at: {databasePath}")
    else:
        db = sqlite3.connect(databasePath)
        cursor = db.cursor()
    # endregion

    # region ——————检查Runtime数据库————————
    RuntimeDatabasePath = os.path.join(RootDir, "Runtime.db")
    if not os.path.exists(RuntimeDatabasePath):
        CriticalToExit("Could not find Runtime.db in root dir")
    else:
        runtime_db = sqlite3.connect(RuntimeDatabasePath)
        runtime_cursor = runtime_db.cursor()
        runtime_cursor.execute("delete from InputParam")
        for D in jsonD:
            # 查找Action的字典键值
            for key, value in D.items():
                if key.find("Action") != -1:
                    actionKey = key
            # 初始化InputParam
            for action in D[actionKey]:
                paramName = action[0]
                InitDataToRuntimeSQL(runtime_cursor, Runtime.Input, paramName)
        runtime_db.commit()
        DebugLog("InputParam init")

    # endregion

    #region 设置通讯端口
    context = zmq.Context()

    comSocket = context.socket(zmq.PULL)
    comSocket.connect("tcp://127.0.0.1:5557")

    poller = zmq.Poller()
    poller.register(comSocket, zmq.POLLIN)
    #endregion

    print("Start modbus COM after 5s...")
    for i in range(5):
        time.sleep(1)
        print(f"{5 - i}...")

    # 开始读取数据的循环
    while True:
        # region ——————检测是否新建数据库——————
        if time.strftime("%Y-%m-%d", time.localtime()) != date:
            date = time.strftime("%Y-%m-%d", time.localtime())
        databasePath = os.path.join(databaseDir, f"{date}.db")
        if not os.path.exists(databasePath):
            cursor.close()
            db.close()
            db = sqlite3.connect(databasePath)
            cursor = db.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS table01(
                    id INTEGER PRIMARY KEY,
                    time TEXT NOT NULL
                    ,name TEXT NOT NULL,
                    data NUMERIC NOT NULL)""")
            DebugLog(f"Create new database at: {databasePath}")
        # endregion

        # region ——————主站读取数据——————
        # 循环读取每一个主站定义
        for D in jsonD:
            port = D["Port"]
            baud = D["Baud"]
            byteSize = D["ByteSize"]
            parity = D["Parity"]
            stopBits = D["Stop"]
            functionCode = D["FuncCode"]
            try:
                if port == 0:
                    port = cf.get("Port Define", "port01")
                else:
                    port = cf.get("Port Define", "port02")
                master = modbus_rtu.RtuMaster(serial.Serial(
                    port=port, baudrate=baud, bytesize=byteSize, parity=parity, stopbits=stopBits))
                master.set_timeout(1.0)
                # 查找Action的字典键值
                for key, value in D.items():
                    if key.find("Action") != -1:
                        actionKey = key
                # 循环执行定义中的动作
                for action in D[actionKey]:
                    paramName = action[0]
                    slaveID = action[1]
                    address = action[2]
                    factor = action[3]
                    res = master.execute(slaveID, functionCode, address, 1)
                    if factor != 1:
                        res = round((res[0]) * factor, 2)
                    else:
                        res = res[0]
                    print(f"{paramName} = {res} (read from slave {slaveID})")
                    SaveDataToPersistenceSQL(cursor,
                                             time.strftime("%H:%M:%S", time.localtime()),
                                             paramName,
                                             res)

                    UpdateDataToRuntimeSQL(runtime_cursor, Runtime.Input, paramName, res)

                master.close()
                print("wait for serial port ready")
                time.sleep(switchPortInterval)

            except Exception as e:
                index = jsonD.index(D)
                ErrorLog(f"Error raised when execute {masterDefs[index]}. Error is {e.__str__()}")
                if 'master' in dir():
                    master.close()
            finally:
                db.commit()
                runtime_db.commit()

        # endregion

        # region ——————网站指令行为——————
        socks = dict(poller.poll(1000))

        if socks:
            if socks.get(comSocket) == zmq.POLLIN:
                recv = comSocket.recv(zmq.NOBLOCK).decode("utf-8")

        # endregion

        # region ——————主站业务逻辑——————

        # endregion

        print(f"sleep for next COM  ({int(readInterval)}s)")
        time.sleep(readInterval)
