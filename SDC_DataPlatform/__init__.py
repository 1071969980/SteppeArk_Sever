import streamlit as st
import sqlite3
import os

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
