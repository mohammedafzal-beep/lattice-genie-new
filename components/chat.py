import streamlit as st
import json
from openai import OpenAI

client = OpenAI(api_key='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')

def handle_user_input(data):
    user_input = st.chat_input('Ask Lattice Genie to generate a lattice structure.')

    if user_input and st.session_state.get('stl_path'):
        st.session_state['messages'] = []
        st.session_state['confirmed_params'] = None
        st.session_state['stl_path'] = None
        st.session_state['last_assistant_msg'] = None
        st.rerun()

    for msg in st.session_state['messages']:
        st.chat_message(msg['role']).write(msg['content'])

    if user_input:
        st.chat_message('user').write(user_input)
        st.session_state['messages'].append({'role': 'user', 'content': user_input})

        messages = [{'role': 'system', 'content': data['system_prompt']}] + st.session_state['messages']
        with st.empty().container():
            st.markdown("""
            <div class='typing-wrapper'><div class='typing'>
            <div class='dot'></div><div class='dot'></div><div class='dot'></div>
            </div></div>
            """, unsafe_allow_html=True)

        try:
            resp = client.chat.completions.create(model='gpt-4o', messages=messages, temperature=0)
            assistant_msg = resp.choices[0].message.content
        except Exception as e:
            st.error(f"OpenAI API Error: {e}")
            assistant_msg = None

        if assistant_msg and assistant_msg != st.session_state['last_assistant_msg']:
            st.session_state['last_assistant_msg'] = assistant_msg
            process_assistant_response(assistant_msg, data['params_dict'])

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
        msg_to_display = "✅ Got the lattice type. Adjust sliders to generate the STL."
    else:
        msg_to_display = assistant_msg

    st.session_state['messages'].append({'role': 'assistant', 'content': msg_to_display})
    st.chat_message('assistant').write(msg_to_display)
