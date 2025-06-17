import streamlit as st
from utils.utils import labeled_slider
from utils.utils import generate_stl
from streamlit_stl import stl_from_file
def show_parameter_sliders(data):
    with st.sidebar:
        st.markdown("### Adjust Parameters")

        confirmed = st.session_state['confirmed_params']
        dict_key = int(confirmed.get('dict_key', -1))
        schema = data["params_dict"].get(dict_key, {})

        if not schema:
            st.warning("No parameter schema for this structure.")
            st.stop()

        current_params = {}
        for param_key in schema:
            val = labeled_slider(param_key, schema[param_key], current_params)
            current_params[param_key] = val


        st.session_state['last_params'] = current_params.copy()
        st.session_state['stl_path'] = generate_stl(dict_key, current_params)
    file_name=f"{st.session_state['stl_path']}"
    file_name=file_name[9:]
    # Show STL if generated
    if st.session_state.get('stl_path'):
        st.markdown("<div class='center'><h3>🧱 Generated STL Structure</h3></div>", unsafe_allow_html=True)
        stl_from_file(st.session_state['stl_path'],st.session_state.get('stl_color', '#336fff'), 
                      auto_rotate=True, width=700, height=500,cam_distance=0)
        with open(st.session_state['stl_path'], 'rb') as f:
            st.download_button(
                "Download STL", data=f.read(),
                file_name=f"{st.session_state['stl_path']}", mime="model/stl"
            )
        st.markdown("</div>", unsafe_allow_html=True)