import streamlit as st
import SDC_DataPlatform as SDC
from streamlit import session_state as ss


def show():
    if not ss.admin:
       st.write( "## Sorry, Plz input password in sidebar")
    else:
       st.write("# Welcome")
       with st.form("CommandForm"):
           CommandType = st.selectbox("Command Type",["Globe Param Command","Modbus Command"])



