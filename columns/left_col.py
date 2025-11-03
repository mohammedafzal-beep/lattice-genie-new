import streamlit as st
import sys
import os
from utils.utils import subtype_selection_to_dict_key
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Mode switch area (top)
def left_column(data):
    
    st.markdown(
    """
    <div style='text-align:center;'>
    <h3 style='margin-top:-20px;'>✨ Generation Mode </h3>
    </div>
    """,
    unsafe_allow_html=True,
    )
    # Structure selection block
    # Build dropdowns from data. We expect params_dict schemas have meta.type and meta.subtype.
    # Collect unique types and subtypes
    subtype_selection_to_dict_key(data)


    st.write('')
    selection_pane=st.columns([.7,5.3,1,4.5,1])
    with selection_pane[1]:
        if st.button('✅ Confirm'):
            st.session_state["confirm"] = True
            
    with selection_pane[3]:
            if st.button('❌ Reset '):
                st.session_state["confirm"] = False
                st.session_state['stl_path'] = None
                st.session_state['stl_generated'] = False
                st.session_state['current_params'] = None
                st.session_state['selected_type'] = None
                st.session_state['selected_subtype'] = None
                st.session_state['selected_dict_key'] = None
                st.rerun()