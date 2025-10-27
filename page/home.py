import streamlit as st
from components.viewer import show_stl_thumbnail_home
from components.chat import handle_user_input
from components.parameter_ui import show_parameter_sliders
from columns.left_col import left_column
from columns.right_col import right_column
from columns.nav_bar import navigation_bar
def render_home(data):
    st.markdown("""
    <div class='center'>
      <h1>✨ Lattice Genie</h1>
      <h5 class='center unbold'>Lattice Genie can generate lattice structures based on parameters</h5>
    </div>
                <style>
  .center { text-align: center; }
    .unbold { font-weight: normal !important; }
  .stDownloadButton button { display: block; margin-left: auto; margin-right: auto; }
  [data-testid='stHeaderActionElements'] {display: none;}

</style>

    """, unsafe_allow_html=True)
    display_thumbnails(data["crystal_images"])
    st.markdown("---")
    st.markdown("<div class='center' style='margin-bottom:5px;'><h2 >💬 Ask to configure lattice:</h2></div>", unsafe_allow_html=True)
   

    with st.container():
      handle_user_input(data)
      if st.session_state.get("confirmed_params"):
        show_parameter_sliders(data)

def render_home_dropdown_version(data):
    
    st.markdown("""
    <div class='center'>
      <h1>✨ Lattice Genie</h1>
      <h5 class='center unbold'>Lattice Genie can generate lattice structures based on parameters</h5>
    </div>
                <style>
  .center { text-align: center; }
    .unbold { font-weight: normal !important; }
  .stDownloadButton button { display: block; margin-left: auto; margin-right: auto; }
  [data-testid='stHeaderActionElements'] {display: none;}

</style>
    """, unsafe_allow_html=True)
    display_thumbnails(data["crystal_images"])
    st.markdown("---")
    left_col, right_col = st.columns([1,2])

# Use the functions inside the with blocks
    with left_col:
        left_column(data)
    with st.sidebar:
      navigation_bar(data)
    with right_col:
       right_column()
    
    
def display_thumbnails(images):
    cols = st.columns(len(images))
    for idx, (name, img_path) in enumerate(images.items()):
        with cols[idx]:
            try:
                show_stl_thumbnail_home(name, img_path)
            except:
                st.error(f"Couldn't load {name} image.")
            #st.markdown(f"<h4 style='text-align:center;font-weight: normal !important;'>{name}</h4>", unsafe_allow_html=True)
            if st.button(name,key=f'btn_{name}'):
              st.session_state[f'go_{name}'] = True
              st.rerun()
