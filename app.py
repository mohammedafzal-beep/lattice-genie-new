import streamlit as st
from utils.dataloader import load_data
from utils.session import init_state, reset_home_flag
from utils.utils import cleanup_stl_files
from page.home import render_home
from page.generic import render_generic_page
from page.nav_bar import nav_bar
import atexit
def run_app():
    init_state()
    nav_bar()
    data = load_data()
    reset_home_flag()
    page = st.sidebar.radio("Go to", data["pages"], key="current_page")
    
    atexit.register(cleanup_stl_files)
    if page == "Home":
        render_home(data)
    else:
        render_generic_page(page, data)
