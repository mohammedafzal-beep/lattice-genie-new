
import streamlit as st
from utils.utils import labeled_slider
from utils.utils import generate_stl
from streamlit_stl import stl_from_file
def show_parameter_sliders(data):
    
    with st.sidebar:
        with st.columns([1,6,1])[1]:
            st.markdown("---")
            st.markdown(
    "<h2 style=' color: #007BFF; font-size: 28px;'>Adjust parameters</h2>",
    unsafe_allow_html=True
    )


# Reserve space for the button right under the heading
        


        # --- Sliders ---
        confirmed = st.session_state['confirmed_params']
        dict_key = int(confirmed.get('dict_key', -1))
        
        struc_name = data['dict_key_map'].get(dict_key, 'Unknown Structure')
        # Track which structure is currently shown
        if "last_dict_key" not in st.session_state:
            st.session_state["last_dict_key"] = None
        if "button_pressed" not in st.session_state:
            st.session_state["button_pressed"] = False

        # If the structure changed, reset button_pressed
        if st.session_state["last_dict_key"] != dict_key:
            st.session_state["button_pressed"] = False
            st.session_state["last_dict_key"] = dict_key
        with st.columns([1,2,1])[1]:
            button_placeholder = st.empty()
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
                st.session_state["button_pressed"] = True
                #button_pressed = True
                st.session_state['spinner'] = st.empty()
                st.session_state['spinner'].markdown(
    """
    <div style="display:flex; align-items:center; gap:12px;">
  <div class="loader" aria-hidden="true"></div>
  <div style="font-size:15px; font-weight:600; color:#3366ff;">Generating STL... please wait</div>
</div>

<style>
:root{
  --spinner-size: 36px;        /* overall outer diameter */
  --spinner-thickness: 6px;    /* border width -> controls inner hole size */
  --spinner-color: #3366ff;
  --spinner-bg: rgba(0,0,0,0.08);
}

/* Spinner */
.loader {
  width: var(--spinner-size);
  height: var(--spinner-size);
  border-radius: 50%;
  box-sizing: border-box;                 /* include border in width/height */
  border: var(--spinner-thickness) solid var(--spinner-bg); /* ring background */
  border-top-color: var(--spinner-color); /* colored arc */
  flex-shrink: 0;                         /* prevent sidebar from squishing it */
  display: inline-block;
  line-height: 0;
  animation: spin 1s linear infinite;
  transform-origin: center center;
}

/* optional: slightly smoother anti-aliasing for some browsers */
.loader { -webkit-backface-visibility: hidden; backface-visibility: hidden; }

/* spin animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
    """,
    unsafe_allow_html=True
)

                path = generate_stl(dict_key, current_params)
                st.session_state['stl_path'] = path
                st.session_state['stl_generated'] = True
                current_params=st.session_state["current_params"]
        
                st.markdown("</div>", unsafe_allow_html=True)
        
        button_pressed = st.session_state.get("button_pressed", False)
    
        # HTML with red dot if button not pressed
        dot_html = f"""
<div style="position: relative; display: inline-block; margin-bottom: 8px;">
    <h4 style="margin:0;">{struc_name}</h4>
    {(
        "<span class='pulse-dot'></span>"
    ) if not button_pressed else ""}
</div>

<style>
.pulse-dot {{
    position: relative;
    top: 0;
    right: 0;
    height: 12px;
    width: 12px;
    background: radial-gradient(circle, red, darkred);
    border-radius: 50%;
    display: inline-block;
    animation: pulse 1s infinite;
}}

@keyframes pulse {{
    0% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(1.5); opacity: 0.6; }}
    100% {{ transform: scale(1); opacity: 1; }}
}}
</style>
"""
    with st.session_state['struc_name_placeholder']:

        st.markdown(dot_html, unsafe_allow_html=True)