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

    data = SDC.GetRuntimeData()
    cols = st.columns(4)
    foos = []

    for i in range(len(data)):
        with cols[i%4]:
            foos.append(st.empty())
    for i in range(len(data)):
        foos[i].metric(data[i][1],data[i][2])


    while True:
        if ss.Page != SDC.Pages[0]:
            break

        data = SDC.GetRuntimeData()

        for i in range(len(data)):
            foos[i].metric(data[i][1], data[i][2])

        time.sleep(3)
