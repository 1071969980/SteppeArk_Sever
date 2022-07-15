import streamlit as st
import sqlite3
import os
import json


def InitState(key: str, value):
    if key not in st.session_state:
        st.session_state[key] = value


color = [
    '#002664', '#72BF44', '#EED308', '#5E6A71', '#7C9DBE', '#F47920', '#1C536E', '#2D580C',
]

Pages = ("Realtime Data", "Data Charts", "Control panel")

AdminKey = "982c7116-cef4-4d1c-b51e-8eda2c275741"


def GetRuntimeData():
    db_path = os.path.abspath(os.path.join(os.getcwd(), "..", "ModbusCOM/Runtime.db"))
    runtime_db = sqlite3.connect(db_path)
    runtime_cursor = runtime_db.cursor()

    runtime_cursor.execute("select * from InputParam")

    data = runtime_cursor.fetchall()

    runtime_db.close()

    return data


def GetData(time, name):
    db_path = os.path.abspath(os.path.join(os.getcwd(), "..", f"ModbusCOM/database/{time}.db"))
    if os.path.exists(db_path):
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        cursor.execute("select * from table01 where name = ?", (name,))
        data = cursor.fetchall()

        db.close()

        return data


def VerfyPassword(password: str):
    if password == AdminKey:
        st.session_state["admin"] = True


class Command:
    describe = ""
    type = ""


class ParamCommand(Command):
    globalParamName = ""
    value = 0

    def __init__(self, name: str, value: float, describe: str = "No Describe"):
        self.describe = describe
        self.type = "Param"
        self.globalParamName = name
        self.value = value

    def ToJson(self):
        dict = {"describe": self.describe,
                "type": self.type,
                "name": self.globalParamName,
                "value": self.value}
        return json.dumps(dict)

    @classmethod
    def FromJson(cls, jsonstr):
        d = json.loads(jsonstr)
        return cls(d["name"], d["value"], d["describe"])

class ModbusCommand(Command):

    def __init__(self,port,baudrate,bytesize,parity,stopbits,
                 slaveID,functionCode,address,outputValue,describe: str = "No Describe"):
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
    def FromJson(cls,jsonstr):
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
