"""
Lattice Genie Utilities Module
------------------------------

This module provides utility functions and UI components for the Lattice Genie Streamlit app,
which dynamically generates STL files for various lattice structures based on user-defined parameters.

Includes:
- STL cleanup
- Parameter sliders with dynamic ranges
- Dynamic function importing
- STL generation wrapper
"""

import importlib
import os
import glob
import streamlit as st
from PIL import Image
from streamlit_stl import stl_from_file
import streamlit.components.v1 as components
import json
# --- Delete all STL files in the 'all_files/' directory to ensure a clean state before generation ---
def cleanup_stl_files():
    for f in glob.glob("all_files/*.stl"):
        try:
            os.remove(f)
        except Exception as e:
            print(f"Could not delete {f}: {e}")

# --- Display a fallback image if STL rendering fails ---
def backup(display, img_path):
    if not display:
        st.image(Image.open(img_path[1]).resize((256, 256)), use_container_width=True)

# --- Slider UI component that supports both static and C-dependent dynamic ranges ---
def labeled_slider(param_key, cfg, current_params,dict_key=None,font_size_label=22, font_size_value=20,color="#ffffff",
                 slider_width=600,label_value_gap=10,confirm_selection=False):
  # Define all supported dynamic range functions
  def t_range_func_C29(C): return (0.1, 1.0 + C, 0.1)
  def t_range_func_C30(C): return (0.1, 1.4 + C, 0.1)
  def t_range_func_C31(C): return (0.1, 1.0 + C, 0.1)
  def t_range_func_C32(C): return (0.2, 3.0 + C, 0.1)
  def t_range_func_C33(C): return (0.1, 0.8 + C, 0.1)
  def t_range_func_C34(C): return (0.1, 1.1 + C, 0.1)
  def t_range_func_C35(C): return (0.1, 0.7 + C, 0.1)




  RANGE_FUNC_MAP = {
      "t_range_func_C29": t_range_func_C29,
      "t_range_func_C30": t_range_func_C30,
      "t_range_func_C31": t_range_func_C31,
      "t_range_func_C32": t_range_func_C32,
      "t_range_func_C33": t_range_func_C33,
      "t_range_func_C34": t_range_func_C34,
      "t_range_func_C35": t_range_func_C35,
  }




  # Units for each param
  unit_map = {
      "a": "Å", "b": "Å", "c": "Å", "r": "Å", "C": "Å", "t": "Å", "d": "Å",
      "face_atom_radius": "Å", "center_atom_radius": "Å",
      "alpha": "°", "beta": "°", "gamma": "°", "resolution": ""
  }




  # Display names (Greek where applicable)
  greek_map = {
  "alpha":              "Rotation along a axis (α in degrees)",
  "beta":               "Rotation along b axis (β in degrees)",
  "gamma":              "Rotation along c axis (γ in degrees)",
  "face_atom_radius":   "Face atom radius",
  "a": "Edge length a",
  "b": "Edge length b",
  "c": "Edge length c",
  "C": "Level set constant C",
  "t": "Sheet thickness t",
  "d": "Distance between sheets d",
  "r": "Atomic radius r",
  "center_atom_radius": "Center atom radius",
    "resolution": "Mesh resolution"
}








  # Tooltip descriptions
  descriptions_dict = {
      'a': 'Lattice constant a',
      'b': 'Lattice constant b',
      'c': 'Lattice constant c',
      'C': 'It influences the volume fraction',
      't': 'Sheet thickness',
      'd': 'Strut diameter',
      'r': 'Radius of the spheres at the corners of the unit cell',
      'alpha': 'Angle between b and c',
      'beta': 'Angle between a and c',
      'gamma': 'Angle between a and b',
      'face_atom_radius': 'Radius of atoms at face centers in FCC',
      'centre_atom_radius': 'Radius of center atom in BCC',
      'resolution': 'Decrease resolution for faster generation'
  }




  # Render label with unit and tooltip
  unit = unit_map.get(param_key, "")
  display_key = greek_map.get(param_key, param_key)
  label = f"{display_key} ({unit})" if unit else f"{display_key}"
  help_text = descriptions_dict.get(param_key, "")




  # Handle dynamic range functions (e.g., t depends on C)
  if "range_func" in cfg:
      range_func = cfg["range_func"]
      if isinstance(range_func, str):
          range_func = RANGE_FUNC_MAP.get(range_func)
      if not callable(range_func):
          st.warning(f"Invalid range_func for {param_key}")
          return None
      C_val = current_params.get("C")
      if C_val is None:
          st.warning(f"Need C before {param_key}")
          return None
      min_val, max_val, step = range_func(C_val)
  else:
      # Static range
      min_val = cfg.get("min")
      max_val = cfg.get("max")
      step = cfg.get("step", 0.01)




  default_val = cfg.get("default", cfg.get("min", 0))
  prev_val = st.session_state.get(param_key, current_params.get(param_key, default_val))
  clamped_val = max(cfg.get("min", 0), min(prev_val, cfg.get("max", 1)))
  st.session_state[param_key] = clamped_val  # store current value
 # CHANGES START FROM HERE###
  html_code = """
<style>
.slider-container {{
  position: relative;
  width: 100%;
  max-width: {slider_width}px;   /* keep slider shorter than full width */
  margin: 0 auto;                /* center the slider container */
  height: 100px;
  font-family: sans-serif;
}}
.slider-label {{
  font-size: {label_size}px;
  font-weight: bold;
  color: {color};
  margin-bottom: 40px; /* separation between label and value */
  text-align: left;  /* LEFT align label as requested */
  padding-left: 6px; /* small padding so label lines up visually with slider start */
}}
.slider-inner-wrapper {{
  position: relative; /* ensures absolute child positions are with respect to this box */
  padding: 0 6px;     /* small horizontal padding so bubble doesn't clip at edges */
}}
input[type=range] {{
  -webkit-appearance: none;
  width: 100%;
  height: 12px;
  background: #555;
  border-radius: 6px;
  outline: none;
  margin: 0;
  position: relative;
}}
/* thumb size MUST match JS thumbWidth below (28) */
input[type=range]::-webkit-slider-thumb {{
  -webkit-appearance: none;
  width: 28px;
  height: 28px;
  background: {color};
  cursor: pointer;
  border-radius: 50%;
  border: none;
  margin-top: -8px;
  position: relative;
  z-index: 2;
}}
input[type=range]::-moz-range-thumb {{
  width: 28px;
  height: 28px;
  background: {color};
  cursor: pointer;
  border-radius: 50%;
  border: none;
}}
.slider-value {{
  position: absolute;
  font-size: {value_size}px;
  font-weight: bold;
  color: {color};
  top: -35px;      /* adjust vertical gap from handle; not overlapping blue track */
  /* do NOT use translateX here — left is set in pixels in JS */
  white-space: nowrap;
  pointer-events: none;
}}
.slider-minmax {{
  display: flex;
  justify-content: space-between;
  font-size: {label_size}px;
  font-weight: bold;
  color: {color};
  margin-top: 14px;
  padding: 0 6px; /* align min/max with slider edges */
}}
</style>




<div class="slider-container">
  <div class="slider-label">{label}</div>
  <div class="slider-inner-wrapper">
      <input type="range" min="{min_val}" max="{max_val}" step="{step}" value="{current_val}" id="slider-{param_key}">
      <div class="slider-value" id="value-{param_key}">{current_val}</div>
  </div>
  <div class="slider-minmax"><span>{min_val}</span><span>{max_val}</span></div>
</div>




<script>
(function() {{
  const slider = document.getElementById("slider-{param_key}");
  const valueDiv = document.getElementById("value-{param_key}");
  const inner = slider.parentElement; // .slider-inner-wrapper




  const thumbWidth = 28; // MUST match CSS thumb width above (px)




  function updateSlider() {{
      const val = slider.value;
      valueDiv.innerText = val;




      const min = Number({min_val});
      const max = Number({max_val});
      const percent = (val - min) / (max - min);




      // slider dimensions
      const sliderWidth = slider.clientWidth;
      const innerWidth = inner.clientWidth;




      // The handle center moves between thumbWidth/2 .. sliderWidth - thumbWidth/2
      const movableRange = sliderWidth - thumbWidth;
      const handleCenterOnSlider = (thumbWidth / 2) + (percent * movableRange);




      // slider's left inside inner (account for inner padding)
      const sliderRect = slider.getBoundingClientRect();
      const innerRect = inner.getBoundingClientRect();
      const sliderLeftRelativeToInner = sliderRect.left - innerRect.left;




      // left position (px) for the value DIV so it centers on the handle
      let leftPx = sliderLeftRelativeToInner + handleCenterOnSlider - (valueDiv.offsetWidth / 2);




      // clamp so the bubble doesn't overflow inner wrapper
      const minLeft = 0;
      const maxLeft = innerWidth - valueDiv.offsetWidth;
      if (leftPx < minLeft) leftPx = minLeft;
      if (leftPx > maxLeft) leftPx = maxLeft;




      valueDiv.style.left = leftPx + "px";




      // Update the track fill (dynamic) — percent*100
      const pct100 = percent * 100;
      slider.style.background = "linear-gradient(to right, {color} " + pct100 + "%, #555 " + pct100 + "%)";
    
  }}




  slider.addEventListener("input", updateSlider);
  slider.addEventListener("change", updateSlider);




  // small timeout to allow layout to settle so measurements are correct on init
  setTimeout(updateSlider, 0);




  // forward value to Streamlit (on change)
  slider.addEventListener("change", () => {{
      window.parent.postMessage({{paramKey: "{param_key}", value: parseFloat(slider.value)}}, "*");
  }});
}})();
</script>
""".format(
  label_size=font_size_label*.8,
  value_size=font_size_value*.8,
  label=label,
  min_val=min_val,
  max_val=max_val,
  current_val=clamped_val,
  step=step,
  param_key=param_key,
  color=color,
  slider_width=slider_width,
  label_value_gap=label_value_gap
)


  with st.sidebar:
       components.html(html_code, height=150)

  return st.session_state[param_key]


# --- Compute a clamped max to ensure range endpoints align with slider steps ---
def get_adjusted_max(min_val, max_val, step):
    k = int((max_val - min_val) // step)
    return min_val + k * step

# --- Dynamically import a function (e.g., structure generator) from a module in a folder ---
def dynamic_import(folder_name: str, module_name: str, variable_name: str):
    module_path = f"{folder_name}.{module_name}"
    module = importlib.import_module(module_path)
    return getattr(module, variable_name)
"""
# --- Initialize session state for the app ---
def init_state():
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'confirmed_params' not in st.session_state:
        st.session_state['confirmed_params'] = None
    if 'stl_path' not in st.session_state:
        st.session_state['stl_path'] = None
    if 'last_assistant_msg' not in st.session_state:
        st.session_state['last_assistant_msg'] = None"""

# --- Generate STL file using structure-specific generation function ---
def generate_stl(dict_key, params):
    # Maps structure key to its function name (used to dynamically import and call)
    func_dict = {
        1: "Cubic", 2: "Cubic_FCC", 3: "Cubic_BCC", 4: "Cubic_Ortho",
        5: "Ortho_BaseCent", 6: "Ortho_FCC", 7: "Ortho_BCC", 8: "Tetra",
        9: "Tetra_BCC", 10: "Mono", 11: "Mono_BaseCent", 12: "Triclinic",
        13: "Rhombo", 14: "Hexa", 15: "Inverse", 16: "Inverse_FCC",
        17: "Inverse_BCC", 18: "Inverse_Cubic_Ortho", 19: "Inverse_Ortho_BaseCent", 20: "Inverse_Ortho_FCC",
        21: "Inverse_Ortho_BCC", 22: "Inverse_Tetra", 23: "Inverse_Tetra_BCC", 24: "Inverse_Mono",
        25: "Inverse_Mono_BaseCent", 26: "Inverse_Rhombo", 27: "Inverse_Triclinic", 28: "Inverse_Hexa",
        29: "Sheet_Primitive", 30: "Sheet_Gyroid", 31: "Sheet_Diamond", 32: "Sheet_IWP",
        33: "Sheet_FKS", 34: "Sheet_FRD", 35: "Sheet_Neovius", 36: "Skeletal_Primitive",
        37: "Skeletal_Gyroid", 38: "Skeletal_Diamond", 39: "Skeletal_IWP", 40: "Skeletal_FKS",
        41: "Skeletal_FRD", 42: "Skeletal_Neovius", 43: "Inverted_Diamond", 44: "Inverted_FRD",
        45: "Inverted_Gyroid", 46: "Inverted_IWP", 47: "Inverted_Neovius", 48: "Inverted_Primitive",
        49: "Inverted_FKS", 50: "Truss_Cubic", 51: "Truss_BCC", 52: "Truss_BFCC",
        53: "Truss_Octet", 54: "Truss_AFCC", 55: "Truss_Iso", 56: "Truss_BCCZ",
        57: "Truss_Tetra", 58: "Truss_FCC", 59: "Truss_FCCZ", 60: "Truss_G7",
        61: "Truss_Octa", 62: "Truss_FBCCZ", 63: "Truss_FBCCXYZ",
    }

    #try:
    func_name = func_dict.get(int(dict_key))
    """if not func_name:
        st.error("Invalid structure key.")
        return None"""
    # Import the structure function dynamically from its module
    func = dynamic_import('all_func', f'{dict_key}_' + func_name.lower(), func_name)
    filepath = func(**params)
    return filepath

    """if not filepath or not os.path.isfile(filepath):
            st.error(f"STL generation failed or file not found: {filepath}")
            return None"""

        

    #except Exception as e:
        #st.error(f"Error in generate_stl(): {e}")
        #return None



