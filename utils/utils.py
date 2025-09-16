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
def labeled_slider(param_key, cfg, current_params):
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
    'alpha': 'Angle between b and c',
    'beta': 'Angle between a and c',
    'gamma': 'Angle between a and b',
    "face_atom_radius":   "face atom radius",
    'a': 'Lattice constant a',
    'b': 'Lattice constant b',
    'c': 'Lattice constant c',
    'C': 'Level set constant',
    't': 'Sheet thickness',
    'd': 'Distance between two sheets',
    'r': 'Atomic radius',
    'alpha': 'Angle between b and c',
    'beta': 'Angle between a and c',
    'gamma': 'Angle between a and b',
    "center_atom_radius": "center atom radius",
    "resolution": "Resolution"
}


    # Tooltip descriptions
    descriptions_dict = {
        'a': 'Lattice constant a',
        'b': 'Lattice constant b',
        'c': 'Lattice constant c',
        'C': 'Level set constant',
        't': 'Sheet thickness',
        'd': 'Distance between two sheets',
        'r': 'Atomic radius',
        'alpha': 'Angle between b and c',
        'beta': 'Angle between a and c',
        'gamma': 'Angle between a and b',
        'face_atom_radius': 'Radius of atoms at face centers in FCC',
        'centre_atom_radius': 'Radius of center atom in BCC',
        'resolution': 'Decrease res for faster gen'
    }

    # Render label with unit and tooltip
    unit = unit_map.get(param_key, "")
    display_key = greek_map.get(param_key, param_key)
    label = f"**{display_key} ({unit})**" if unit else f"**{display_key}**"
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

    default_val = cfg.get("default", min_val)
    prev_val = st.session_state.get(param_key, current_params.get(param_key, default_val))
    clamped_val = max(min_val, min(prev_val, max_val))
    if param_key not in st.session_state:
        st.session_state[param_key] = clamped_val


    return st.sidebar.slider(
        label=label,
        min_value=min_val,
        max_value=max_val,
        value=clamped_val,
        step=step,
        key=param_key,
        help=help_text,
        label_visibility="visible"
    )

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



