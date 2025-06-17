import streamlit as st

def init_state():
    defaults = {
        'current_page': 'Home',
        'go_home': False,
        'messages': [],
        'confirmed_params': None,
        'stl_path': None,
        'last_assistant_msg': None,
        'last_params': {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def reset_home_flag():
    if st.session_state.go_home:
        st.session_state.current_page = "Home"
        st.session_state.go_home = False
        st.rerun()
