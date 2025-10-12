import streamlit as st
from utils.utils import subtype_selection_to_dict_key
def pro_mode(data):

    st.markdown(
    """
    <div style='text-align:center;'>
    <h3 style='margin-top:-20px;'>✨ Generation Mode </h3>
    <h6 style='margin-top:0; font-weight:250;'>Not sure which structure to pick? Click on button below to enable chat mode</h6>
    </div>
    """,
    unsafe_allow_html=True,
    )
    # Structure selection block
    # Build dropdowns from data. We expect params_dict schemas have meta.type and meta.subtype.
    # Collect unique types and subtypes
    subtype_selection_to_dict_key(data)


    st.write('')
    selection_pane=st.columns([1,3,1,3,1])
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
    with st.columns([.93,1,1])[1]:
        if st.button("💬 Chat Mode"):
            st.session_state['mode'] = 'chat'
            st.rerun()