import streamlit as st
from utils.dataloader import load_data
from utils.session import init_state, reset_home_flag
from utils.utils import cleanup_stl_files
from page.home import render_home
from page.generic import render_generic_page
from page.nav_bar import nav_bar
import atexit
import getpass 
import os
from openai import OpenAI
def openai_api_key_handling():
    secrets_file = ".streamlit/secrets.toml"


    if not os.path.exists(secrets_file):
    
        st.title("🔑 API Key Required")
        st.warning(
            "This is your first time running the app.\n\n"
            "👉 Please enter your **OpenAI API key** in the terminal prompt.\n"
            "After that, the key will be saved for future use."
        )
        api_key = getpass.getpass("🔑 Enter your OpenAI API key (first-time setup): ")
        client=OpenAI(api_key=api_key)
        # save it
        os.makedirs(".streamlit", exist_ok=True)
        with open(secrets_file, "w") as f:
            f.write(f'[default]\nOPENAI_API_KEY = "{api_key}"\n')
            st.success("API key saved! Please rerun the app.")

    
    return True


def run_app():
    init_state()
    nav_bar()
    data = load_data()
    reset_home_flag()
    page = st.sidebar.radio('', data["pages"], key="current_page")
    atexit.register(cleanup_stl_files)
    if page == "Home":
        render_home(data)
    else:
        render_generic_page(page, data)
