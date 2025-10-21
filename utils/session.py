import streamlit as st

def init_state():
    defaults = {
        'current_page': 'Home',
        'go_home': False,
        'go_Bravais': False,
        'go_Inverse Bravais': False,
        'go_Sheet TPMS': False,
        'go_Skeletal TPMS': False,
        'go_Strut-based': False,
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
    if st.session_state.go_Bravais:
        st.session_state.current_page = "Bravais"
        st.session_state.go_Bravais = False
        st.rerun()
    if st.session_state['go_Inverse Bravais']:
        st.session_state.current_page = "Inverse Bravais"
        st.session_state['go_Inverse Bravais'] = False
        st.rerun()
    if st.session_state['go_Sheet TPMS']:
        st.session_state.current_page = "Sheet TPMS"
        st.session_state['go_Sheet TPMS'] = False
        st.rerun()
    if st.session_state['go_Skeletal TPMS']:
        st.session_state.current_page = "Skeletal TPMS"
        st.session_state['go_Skeletal TPMS'] = False
        st.rerun()
    if st.session_state['go_Strut-based']:
        st.session_state.current_page = "Strut-based"
        st.session_state['go_Strut-based'] = False
        st.rerun()



def init_state_dropdown_version():
   defaults = {
       'go_Bravais': False,
        'go_Inverse Bravais': False,
        'go_Sheet TPMS': False,
        'go_Skeletal TPMS': False,
        'go_Strut-based': False,
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
