import streamlit as st
from streamlit import session_state as ss

import SDC_DataPlatform as SDC


def SendParamCommand(name, value, describe):
    c = SDC.ParamCommand(name, value, describe)
    json_str = c.ToJson()
    sender = SDC.ComSocket()
    sender.send(json_str.encode("utf-8"))
    return


def SendModbusCommand(port, baudrate, bytesize, parity, stopbits,
                      slaveID, functionCode, address, outputValue, describe):
    c = SDC.ModbusCommand(port, baudrate, bytesize, parity, stopbits,
                          slaveID, functionCode, address, outputValue, describe)
    json_str = c.ToJson()
    sender = SDC.ComSocket()
    sender.send(json_str.encode("utf-8"))
    return


def show():
    if not ss.admin:
        st.write("## Sorry, Plz input password in sidebar")
    else:
        CommandType = st.selectbox("Command Type", ["Global Param Command", "Modbus Command"])

        with st.form("CommandForm", True):
            if CommandType == "Global Param Command":

                colsM = st.columns([1, 7, 1], gap="large")
                with colsM[1]:
                    datas = SDC.QueryRuntimeGlobalParams()
                    dataNames = []
                    for data in datas:
                        dataNames.append(data[1])

                    st.write("----Change global parameter of system")
                    name = st.selectbox("Global Param", dataNames)
                    value = st.number_input("Value")
                    describe = st.text_input("Command Describe", "No Describe")

                    st.title("")

                colsB = st.columns([1, 5, 2], gap="large")
                with colsB[-1]:
                    sb = st.form_submit_button("Send Command",
                                               "Command will be executed later, due to ModbusCOM's read_interval config")
                with colsB[1]:
                    if sb:
                        SendParamCommand(name, value, describe)
                        st.info(f"""Command will be executed later, due to ModbusCOM's read_interval config""")

            elif CommandType == "Modbus Command":
                st.write("----Send modbus command to slave device")
                cols = st.columns([1, 3, 1, 3, 1], gap="large")
                with cols[1]:
                    st.write("### Serial Port Define")
                    port = st.selectbox("Port", [0, 1])
                    baudrate = st.selectbox("Baudrate", [300, 1200, 2400, 9600, 19200, 38400, 115200], index=3)
                    bytesize = st.selectbox("Byte Size", [7, 8], index=1)
                    parity = st.selectbox("Data Parity", ["N", "E", "O"], help="N:无校验位，E:偶数校验，O:奇数校验")
                    stopbits = st.selectbox("Stop bits", [1, 1.5, 2])

                with cols[-2]:
                    st.write("### Modbus Command define")
                    slaveID = st.number_input("Slave Device Modbus ID", step=1)
                    functionCode = st.selectbox("Modbus Function Code", [3, 4, 1, 2, 6, 5], help="""
                    3：读保持寄存器
                    4：读输入寄存器
                    1：读线圈寄存器
                    6：写单个保持寄存器
                    5：写单个线圈寄存器
                    """)
                    address = st.number_input("Modbus Register Address", step=1)
                    outputValue = st.number_input("Modbus Command Output Value", step=1,
                                                  help="Only valid if Function is 6 or 5")

                st.title("")

                colsM = st.columns([1, 7, 1], gap="large")
                with colsM[1]:
                    describe = st.text_input("Command Describe", "No Describe")

                st.title("")

                colsB = st.columns([1, 5, 2], gap="large")
                with colsB[-1]:
                    sb = st.form_submit_button("Send Command",
                                               "Command will be executed later, due to ModbusCOM's read_interval config")
                with colsB[1]:
                    if sb:
                        SendModbusCommand(port, baudrate, bytesize, parity, stopbits,
                                          slaveID, functionCode, address, outputValue, describe)
                        st.info(f"""Command will be executed later, due to ModbusCOM's read_interval config""")

        st.write("## Command History")
        commandH = SDC.QueryCommandHistory()
        st.dataframe(commandH, height=300)
