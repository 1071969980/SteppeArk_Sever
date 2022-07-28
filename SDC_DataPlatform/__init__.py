import pandas
import streamlit as st
import sqlite3
import os
import json
import zmq


def InitState(key: str, value):
    if key not in st.session_state:
        st.session_state[key] = value


color = [
    '#002664', '#72BF44', '#EED308', '#5E6A71', '#7C9DBE', '#F47920', '#1C536E', '#2D580C',
]

Pages = ("Realtime Data", "Data Charts", "Control panel")

AdminKey = "982c7116-cef4-4d1c-b51e-8eda2c275741"


@st.experimental_singleton
def ComSocket():
    context = zmq.Context()

    ventilator_send = context.socket(zmq.PUSH)
    ventilator_send.bind("tcp://127.0.0.1:5557")

    return ventilator_send


@st.experimental_singleton
def ComPoller():
    poller = zmq.Poller()
    poller.register(ComSocket(), zmq.POLLIN)

    return poller


def QueryRuntimeGlobalParams():
    db_path = os.path.abspath(os.path.join(os.getcwd(), "Runtime.db"))
    runtime_db = sqlite3.connect(db_path)
    runtime_cursor = runtime_db.cursor()

    runtime_cursor.execute("select * from GlobalParam")

    data = runtime_cursor.fetchall()
    runtime_db.close()
    return data


def QueryRuntimeData(name: str=""):
    db_path = os.path.abspath(os.path.join(os.getcwd(), "Runtime.db"))
    runtime_db = sqlite3.connect(db_path)
    runtime_cursor = runtime_db.cursor()

    if not name:
        runtime_cursor.execute("select * from InputParam")
    else:
        splitname = name.split()
        if len(splitname)>1:
            sqlconditions = []
            for re in splitname:
                sqlconditions.append(f"name like '%{re}%'")
            sqlcondition = " and ".join(sqlconditions)
            runtime_cursor.execute(f"select * from InputParam where {sqlcondition}")

        else:
            runtime_cursor.execute(f"select * from InputParam where name like '%{name}%'")


    data = runtime_cursor.fetchall()

    runtime_db.close()

    return data


def QueryData(time, name):
    db_path = os.path.abspath(os.path.join(os.getcwd(), f"database/{time}.db"))
    if os.path.exists(db_path):
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        cursor.execute("select * from table01 where name = ?", (name,))
        data = cursor.fetchall()

        db.close()

        return data
    else:
        return []


def QueryDataLabel(time):
    db_path = os.path.abspath(os.path.join(os.getcwd(), f"database/{time}.db"))
    if os.path.exists(db_path):
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT name FROM table01")
        data = cursor.fetchall()

        db.close()

        dataL = []
        for row in data:
            dataL.append(row[0])

        return dataL

    else:
        return []


def QueryCommandHistory():
    db_path = os.path.abspath(os.path.join(os.getcwd(), "Runtime.db"))
    runtime_db = sqlite3.connect(db_path)
    runtime_cursor = runtime_db.cursor()

    runtime_cursor.execute("select * from CommandHistory")

    data = runtime_cursor.fetchall()

    runtime_db.close()

    dataL = []
    for row in data:
        dataL.append(list(row))
    dataL.reverse()

    return pandas.DataFrame(dataL,columns=["ID","Time","Command","Result"])


def VerifyPassword(password: str):
    if password == AdminKey:
        st.session_state["admin"] = True


class ParamCommand:

    def __init__(self, name: str, value: float, describe: str = "No Describe"):
        self.describe = describe
        self.type = "Param"
        self.paramName = name
        self.value = value

    def ToJson(self):
        return json.dumps(self.__dict__)

    @classmethod
    def FromJson(cls, jsonstr):
        d = json.loads(jsonstr)
        return cls(d["paramName"], d["value"], d["describe"])


class ModbusCommand:

    def __init__(self, port, baudrate, bytesize, parity, stopbits,
                 slaveID, functionCode, address, outputValue, describe: str = "No Describe"):
        self.describe = describe
        self.type = "Modbus"
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.slaveID = slaveID
        self.functionCode = functionCode
        self.address = address
        self.outputValue = outputValue

    @classmethod
    def FromJson(cls, jsonstr):
        d = json.loads(jsonstr)
        return cls(
            d["port"],
            d["baudrate"],
            d["bytesize"],
            d["parity"],
            d["stopbits"],
            d["slaveID"],
            d["functionCode"],
            d["address"],
            d["outputValue"],
            d["describe"]
        )

    def ToJson(self):
        return json.dumps(self.__dict__)
