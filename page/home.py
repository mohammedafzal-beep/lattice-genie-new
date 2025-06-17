import streamlit as st
from components.viewer import show_stl_thumbnail_home
from components.chat import handle_user_input
from components.parameter_ui import show_parameter_sliders

def render_home(data):
    
    st.markdown("""
    <div class='center'>
      <h1>Lattice Genie</h1>
      <p>Generate lattice structures via simple chat interface and preview STL.</p>
    </div>
                <style>
  .center { text-align: center; }
  .stDownloadButton button { display: block; margin-left: auto; margin-right: auto; }
</style>
    """, unsafe_allow_html=True)
    display_thumbnails(data["crystal_images"])
    st.markdown("---")
    st.markdown("<div class='center'><h3>💬 Ask to configure lattice:</h3></div>", unsafe_allow_html=True)
    handle_user_input(data)
    if st.session_state.get("confirmed_params"):
        show_parameter_sliders(data)

def display_thumbnails(images):
    cols = st.columns(len(images))
    for idx, (name, img_path) in enumerate(images.items()):
        with cols[idx]:
            try:
                show_stl_thumbnail_home(name, img_path)
            except:
                st.error(f"Couldn't load {name} image.")
            st.markdown(f"<p style='text-align:center;font-weight:bold'>{name}</p>", unsafe_allow_html=True)
