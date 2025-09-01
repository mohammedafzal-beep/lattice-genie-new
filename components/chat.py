import streamlit as st
import json
from openai import OpenAI
from components.parameter_ui import show_parameter_sliders

client = OpenAI(api_key='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')
def handle_user_input(data):
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    
    st.markdown("""
<style>
/* Target all spans inside chat messages */
div[data-testid="stChatMessage"] * {
    font-size: 22px !important;   /* adjust as needed */
    line-height: 1.4 !important;
}

/* Optional: force nowrap for single-line messages if needed */
div[data-testid="stChatMessage"] span {
    white-space: normal !important;
}
</style>
""", unsafe_allow_html=True)
    cols = st.columns([1, 1, 1])
    with cols[1]:
        messages_container = st.container()
        # Display existing messages
        with messages_container:
            for msg in st.session_state['messages']:
                st.chat_message(msg['role']).write(msg['content'])

        # Chat input
        user_input = st.chat_input('Ask Lattice Genie to generate a lattice structure.')

        if user_input:
            # Reset if generating new STL
            if st.session_state.get('stl_path'):
                st.session_state['messages'] = []
                st.session_state['confirmed_params'] = None
                st.session_state['stl_path'] = None
                st.session_state['last_assistant_msg'] = None
                st.rerun()

            # Append and show user input immediately
            st.session_state['messages'].append({'role': 'user', 'content': user_input})
            with messages_container:
                st.chat_message('user').write(user_input)

                # Typing dots directly below user message using CSS class
                typing_placeholder = st.empty()
                typing_placeholder.markdown("""
                <style>
                .typing-dots {
                    display: flex;
                    justify-content: center;
                    margin-top: 70px;
                    margin-bottom: 60px;
                }
                .typing-dots .dot {
                    height: 14px;
                    width: 14px;
                    margin: 0 4px;
                    background-color: blue;
                    border-radius: 50%;
                    display: inline-block;
                    animation: blink 1.4s infinite both;
                }
                .typing-dots .dot:nth-child(2) { animation-delay: 0.2s; }
                .typing-dots .dot:nth-child(3) { animation-delay: 0.4s; }
                @keyframes blink { 0% {opacity:.2;} 20% {opacity:1;} 100% {opacity:.2;} }
                </style>
                <div class="typing-dots">
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
                """, unsafe_allow_html=True)

            # Call OpenAI
            messages = [{'role': 'system', 'content': data['system_prompt']}] + st.session_state['messages']
            try:
                resp = client.chat.completions.create(model='gpt-4.1-nano-2025-04-14', messages=messages, temperature=0)
                assistant_msg = resp.choices[0].message.content
            except Exception as e:
                assistant_msg = f"OpenAI API Error: {e}"

            # Replace typing dots with assistant message
            typing_placeholder.empty()
            msg_to_display = process_assistant_response(assistant_msg, data["params_dict"])

            # Now actually show the assistant’s clean message
            with messages_container:
                st.chat_message("assistant").write(msg_to_display)


def process_assistant_response(assistant_msg, params_dict):
    start = assistant_msg.find('{')
    end = assistant_msg.rfind('}')
    confirmed = False

    if start != -1 and end != -1 and end > start:
        try:
            parsed = json.loads(assistant_msg[start:end + 1])
            dict_key = parsed.get('dict_key')
            if dict_key is not None:
                schema = params_dict.get(int(dict_key), {})
                base = {'dict_key': dict_key}
                for k, cfg in schema.items():
                    base[k] = cfg['default']
                st.session_state['confirmed_params'] = base
                confirmed = True
        except json.JSONDecodeError:
            pass

    if confirmed:
        msg_to_display = "⬇️ Make sure to download the STL before proceeding to newer generation. " \
        "To generate a new structure, type anything in the chat and hit 'Enter'."
    else:
        msg_to_display = assistant_msg

    st.session_state["messages"].append({"role": "assistant", "content": msg_to_display})
    st.session_state["last_assistant_msg"] = msg_to_display
    return msg_to_display
