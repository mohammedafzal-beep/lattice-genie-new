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


def init_state_dropdown_version():
   defaults = {
       
       'api_key_configured': False,
       'current_page': 'Home',
        'go_home': False,
       'mode': 'pro',  # 'pro' or 'chat'
       'messages': [],
       'current_params': None,
       'stl_path': None,
       'stl_generated': False,
       'last_assistant_msg': None,
       'last_params': {},
       'selected_type': None,
       'selected_subtype': None,
       'selected_dict_key': None,
       'thumbnail_nav_target': None,
       'confirm_selection': False,
   }
   for k, v in defaults.items():
       if k not in st.session_state:
           st.session_state[k] = v
