import streamlit as st
from utils.utils import labeled_slider,generate_stl
def navigation_bar(data):
    dict_key = st.session_state.get('selected_dict_key', 1)
    if st.session_state.get("confirm"):
                   st.markdown(
       "<h2 style='text-align: center; color: #007BFF; font-size: 28px;'>Adjust parameters</h2>",
       unsafe_allow_html=True
   )


   # Reserve space for the button right under the heading
                   with st.columns([1,2.5,1])[1]:
                       button_placeholder = st.empty()


                   # --- Sliders ---
                   schema = data["params_dict"].get(dict_key, 1)
                   current_params = {}
                   for param_key in schema:
                       val = labeled_slider(param_key, schema[param_key], current_params)
                       current_params[param_key] = val


                   st.session_state["current_params"] = current_params


                   # --- Fill the button placeholder (after sliders computed) ---
                   with button_placeholder.container():
                       st.markdown(
                           "<div style='display:flex; justify-content:center; margin-top:8px;'>",
                           unsafe_allow_html=True,
                       )
                       if st.button("Generate STL", key="generate_stl"):
                           path = generate_stl(dict_key, current_params)
                           st.session_state['stl_path'] = path
                           st.session_state['stl_generated'] = True
                       st.markdown("</div>", unsafe_allow_html=True)
