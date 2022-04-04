import streamlit as st
from streamlit import session_state as ss
import SDC_DataPlatform as SDC


def show():
    SDC.InitState("admin", False)

    if ss.admin:
        st.sidebar.write(
        """
        # Welcome! Admin
        """
        )

    add_selectbox = st.sidebar.selectbox(
        label="Page",
        options=SDC.Pages,
        key="Page",
        index=1
    )

    if not ss.admin:
        adminKey = st.sidebar.text_input(label="AdminKey", placeholder="Key to access advanced features")
        st.sidebar.button("Login",on_click=SDC.VerfyPassword,args=(adminKey,))