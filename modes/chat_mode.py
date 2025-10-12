import streamlit as st
from components.chat import call_openai_chat, render_chat
from utils.utils import labeled_slider,generate_stl
def chat_mode(data):
    st.markdown(
        """
        <div style='text-align:center;'>
            <h3 style='margin-top:-20px;'>💬 Chat Mode</h3>
            <h6 style='margin-top:0; font-weight:250;'>If you know which structure to generate, click button below to enable generation mode.</h6>
        </div>
        """,
        unsafe_allow_html=True,
        )
            
            # Initialize messages
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []


            # --- Chat CSS ---
    st.markdown("""
    <style>
    .chat-box {
        border: 1px solid #ccc;
        border-radius: 12px;
        background-color: #f9f9f9;
        padding: 12px;
        height: 400px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    .message {
        max-width: 70%;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 12px;
        font-size: 18px;
        line-height: 1.4;
        word-wrap: break-word;
        color: #000000ff;
    }
    .user {
        align-self: flex-end;
        background-color: #DCF8C6;
        text-align: right;
    }
    .assistant {
        align-self: flex-start;
        background-color: #E6F0FF;
        text-align: left;
    }
    .avatar {
        width: 24px;
        height: 24px;
        display: inline-block;
        vertical-align: middle;
    }
    </style>
    """, unsafe_allow_html=True)


            # --- Chat input + Generation Mode button ---
    user_input = st.chat_input("Ask Lattice Genie to recommend a structure")
    with st.columns([1.15,1.5,1])[1]:
        if st.button("✨ Generation Mode"):
            st.session_state['mode'] = 'pro'
            st.rerun()


    # --- Handle user input ---
    if user_input:
        st.session_state['messages'].append({'role':'user','content':user_input})

        assistant_msg = call_openai_chat("system prompt", [{'role':'user','content':user_input}]) 

        st.session_state['messages'].append({'role':'assistant','content':assistant_msg})

        render_chat()


    if st.session_state.get("confirm"):
            dict_key = st.session_state.get('selected_dict_key', 1)
            with st.sidebar:
            
                st.markdown(
    "<h2 style='text-align: center; color: #007BFF; font-size: 28px;'>Adjust parameters</h2>",
    unsafe_allow_html=True
    )

    # Reserve space for the button right under the heading
                with st.columns([1,1.5,1])[1]:
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