import streamlit as st
from streamlit import session_state as ss
import SDC_DataPlatform as SDC
import time




def show():
    st.write(
    """
    # SteppeArk - Realtime Data
    """
    )


    mode = st.selectbox("mode",["Realtime Input Data","Golbal Parameter"])

    search = st.text_input("Search")

    if mode == "Realtime Input Data":

        data = SDC.QueryRuntimeData(search)
        cols = st.columns(4)
        foos = []

        for i in range(len(data)):
            with cols[i%4]:
                foos.append(st.empty())
        for i in range(len(data)):
            foos[i].metric(data[i][1],data[i][2])


        st.write(
        """
        ### press "R" to refresh
        """
        )

    elif mode == "Golbal Parameter":

        data = SDC.QueryRuntimeGlobalParams(search)
        cols = st.columns(4)
        foos = []

        for i in range(len(data)):
            with cols[i % 4]:
                foos.append(st.empty())
        for i in range(len(data)):
            foos[i].metric(data[i][1], data[i][2])

        st.write(
            """
            ### press "R" to refresh
            """
        )