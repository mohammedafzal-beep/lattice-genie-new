import streamlit as st
from utils.dataloader import load_data,log_event
from utils.session import init_state, reset_home_flag,init_state_dropdown_version
from utils.utils import cleanup_stl_files
from page.home import render_home, render_home_dropdown_version
from page.generic import render_generic_page
from page.nav_bar import nav_bar
import atexit


def run_app():
    init_state()
    nav_bar()
    data = load_data()
    reset_home_flag('Chat mode')
    page = st.sidebar.radio('', data["pages"], key="current_page")
    atexit.register(cleanup_stl_files)
    if page == "Home":
        render_home(data)
    else:
        render_generic_page(page, data)
        log_event('Home','Chat mode')

def run_app_dropdown_version():
    init_state_dropdown_version()
    nav_bar()
    data = load_data()
    reset_home_flag('Pro mode')
    page = st.sidebar.radio('', data["pages"], key="current_page")
    atexit.register(cleanup_stl_files)
    if page == "Home":
        log_event('Home','Pro mode')
        render_home_dropdown_version(data)
    else:
        render_generic_page(page, data)
