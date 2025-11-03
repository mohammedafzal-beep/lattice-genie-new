
import streamlit as st
from utils.utils import labeled_slider,generate_stl,surface_area_to_volume_ratio
from streamlit_stl import stl_from_file
from utils.dataloader import log_event,log_slider_changes
def show_parameter_sliders(data,mode):
  if mode == 'Chat mode' or (mode == 'Pro mode' and st.session_state.get("confirm")):
    with st.sidebar:
        st.markdown("---")
        
        with st.columns([1,6,1])[1]:
            st.markdown("<style><h4 style="margin:0;">Adjust Parameters</h4></style>",unsafe_html=True)
            st.session_state['struc_name'] = st.empty()
           


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
        
        with st.columns([2,6,1])[1]:
            button_placeholder = st.empty()
        st.session_state['S/V ratio'] = st.empty()
        schema = data["params_dict"].get(dict_key, 1)
        current_params = {}
        for param_key in schema:
            val = labeled_slider(param_key, schema[param_key], current_params)
            current_params[param_key] = val
        changed = log_slider_changes(current_params,mode)

        def S_V_ratio(stl_path):
           return 0

        if changed:
            st.session_state['spinner'] = st.empty()
            st.session_state['Scroll message'] = st.empty()
            st.session_state['spinner'].markdown(
    """
    <div style="display:flex; align-items:center; gap:12px;">
  <div class="loader" aria-hidden="true"></div>
  <div style="font-size:15px; font-weight:600; color:#3366ff;">Generating STL</div>
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

        with st.session_state['S/V ratio']:
            st.markdown(f"""<style>
            .slider-label {{
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 40px; /* separation between label and value */
  text-align: left;  /* LEFT align label as requested */
  padding-left: 6px; /* small padding so label lines up visually with slider start */
}}</style>
<div class="slider-container">
  <div class="slider-label">S/V Ratio: {surface_area_to_volume_ratio(st.session_state['stl_path'])}</div>""")
    
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
    position: absolute;
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
    with st.session_state['struc_name']:

        st.markdown(dot_html, unsafe_allow_html=True)
    if st.session_state.get('stl_generated'):
        st.session_state['spinner'].empty()  # Clear the message after displaying
        st.session_state['Scroll message'] = st.markdown("Scroll down below to view the structure and \
        ⬇️ Download using the button below it")
        
        stl_from_file(st.session_state['stl_path'],st.session_state.get('stl_color', '#336fff'), 
                auto_rotate=True, width=700, height=500,cam_distance=100*(current_params['resolution']/50),cam_h_angle=45,cam_v_angle=75)
        col = st.columns([1.2, .5, 1])[1]
        with col:
            with open(st.session_state['stl_path'], "rb") as f:
                st.download_button("⬇️ Download", data=f.read(), file_name=st.session_state['stl_path'], mime="model/stl")
                log_event("Download", mode)