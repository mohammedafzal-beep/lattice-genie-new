import streamlit as st
from streamlit_stl import stl_from_file
from utils.dataloader import log_event
import time
def right_column():
    st.markdown('<h3 style="display: flex; align-items: center; justify-content: center; margin-top: -20px; text-align:center;">📸 Preview </h3>', unsafe_allow_html=True)

        # If there's an STL path, preview; otherwise show sample for selected_dict_key
    stl_path = st.session_state.get('stl_path')
        # Try previewing last params or a quick generated preview
    
    if stl_path:
        try:
            stl_from_file(stl_path, st.session_state.get('stl_color', '#336fff'), shininess=50, auto_rotate=True, width=500, height=300, 
                          cam_distance=100*(st.session_state["current_params"]['resolution']/50), cam_h_angle=45, cam_v_angle=75)
            
        except Exception:
            st.error('Failed to render STL preview. You may still download it using the button below if generated.')

        # Download button
        try:
            with open(stl_path, 'rb') as f:
                with st.columns([1, 1, 1])[1]:
                    st.download_button('⬇️ Download STL', data=f.read(), file_name=stl_path, mime='model/stl')
                    log_event(data,'Pro mode')
        except Exception:
            st.warning('STL file not available for download. Generate again.')
    else:
        placeholder = st.empty()
        placeholder.markdown(
"""
<div style="
    width: 525px;
    height:350px;
    border: 2px dashed #ccc;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;  /* center horizontally */
    text-align: center;
">
    Your STL will appear here
</div>
""",
unsafe_allow_html=True
)
