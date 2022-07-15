import streamlit as st
import SDC_DataPlatform as SDC
from SDC_DataPlatform import sidebar as SDC_sidebar
from SDC_DataPlatform import RealtimeData as SDC_RealTimeData
from SDC_DataPlatform import DataChart as SDC_DataChart
from SDC_DataPlatform import ControlPanel as SDC_ControlPanel

st.set_page_config(layout="wide")

SDC_sidebar.show()

if st.session_state["Page"] == SDC.Pages[0]:
    SDC_RealTimeData.show()
if st.session_state["Page"] == SDC.Pages[1]:
    SDC_DataChart.show()
if st.session_state["Page"] == SDC.Pages[2]:
    SDC_ControlPanel.show()
