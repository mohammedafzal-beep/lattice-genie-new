import streamlit as st
from modes.chat_mode import chat_mode
import sys
import os
from modes.pro_mode import pro_mode
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Mode switch area (top)
def left_col(data):
    if st.session_state.mode == 'pro':
        pro_mode(data)
        

    else:
        chat_mode(data)