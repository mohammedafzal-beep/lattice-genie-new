import streamlit as st
import json
from openai import OpenAI
from streamlit_stl import stl_from_file
from html import escape
import tempfile
import os
import uuid, time
from components.parameter_ui import show_parameter_sliders

client=OpenAI(api_key='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')

# ---------- Helper: append generated STL (write to persistent temp file) ----------
def append_generated_stl_from_filename(filename: str, role: str = "assistant"):
   
    while st.session_state['stl_path'] is None:
      pass
    else:
        # Normalize/resolve to absolute path for clarity
        source_path = os.path.abspath(filename)

        # Append the STL message referencing the existing file path
        st.session_state["messages"].append({
            "id": str(uuid.uuid4()),
            "role": role,
            "type": "stl",
            "file_path": source_path,
            "filename": filename
        })

        # Keep track of paths (optional, matches existing tmp_stl_paths usage)
        st.session_state.setdefault("tmp_stl_paths", []).append(source_path)

        # Rerun to render the new STL inline immediately
        st.rerun()
    

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
/* Target the chat input placeholder */
div[data-testid="stChatInput"] textarea::placeholder {
    font-size: 22px !important;   /* bigger font */
    color: #666 !important;       /* optional: change color */
     align-self: center !important; /* center vertically */
                
}
/* Optional: force nowrap for single-line messages if needed */
div[data-testid="stChatMessage"] span {
    white-space: normal !important;
}
div[data-testid="stChatInput"] textarea {
    font-size: 22px !important;
    line-height: 1.6 !important;
    padding: 6px 10px !important;  
}
/* Enlarge the send (triangle) button */
div[data-testid="stChatInput"] button {
    transform: scale(1.3);      /* adjust multiplier as needed */
    margin-left: 10px;          /* optional: add spacing */
     align-self: center !important; /* center vertically */
}</style>
<script>
(function() {
  // Documents to try (current, parent, top)
  const docs = [document, (window.parent && window.parent.document), (window.top && window.top.document)].filter(Boolean);

  const selectors = [
    'div[data-testid="stChatMessageList"]',
    'div[data-testid="stChatMessages"]',
    'div[data-testid="stChatContainer"]',
    'div[data-testid="stChatVirtualizedList"]',
    'section.main',
    'div.block-container',
    'div[role="main"]',
    'main'
  ];

  function findContainer() {
    // Try common selectors
    for (const d of docs) {
      for (const sel of selectors) {
        try {
          const el = d.querySelector(sel);
          if (el) return el;
        } catch (e) {}
      }
    }
    // Fallback: find a chat message then find first scrollable ancestor
    for (const d of docs) {
      try {
        const anyMsg = d.querySelector('div[data-testid="stChatMessage"], div[data-testid="stChatBubble"], div[class*="stChat"]');
        if (anyMsg) {
          let p = anyMsg.parentElement;
          while (p) {
            try {
              const cs = window.getComputedStyle(p);
              if (cs.overflowY === 'auto' || cs.overflowY === 'scroll' || p.scrollHeight > p.clientHeight) return p;
            } catch (e) {}
            p = p.parentElement;
          }
        }
      } catch (e) {}
    }
    return null;
  }

  function scrollToBottom(el) {
    if (!el) return;
    try {
      el.scrollTop = el.scrollHeight;
    } catch (e) {}
  }

  function setupObserver(el) {
    if (!el || el.__chatObserverAttached) return;
    el.__chatObserverAttached = true;

    const observer = new MutationObserver((mutations) => {
      // Quick micro-delay so Streamlit DOM finishes painting
      setTimeout(() => scrollToBottom(el), 10);

      // If our special message appears, do stronger, delayed scrolls
      for (const m of mutations) {
        for (const n of m.addedNodes || []) {
          try {
            if (n && n.innerText && n.innerText.includes('Generation may take a few seconds')) {
              setTimeout(() => scrollToBottom(el), 50);
              setTimeout(() => scrollToBottom(el), 300);
              setTimeout(() => scrollToBottom(el), 700);
            }
          } catch (e) {}
        }
      }
    });

    observer.observe(el, { childList: true, subtree: true });

    // A short aggressive retry burst to catch slow renders (50ms x 40 = 2s)
    let tries = 0;
    const t = setInterval(() => {
      scrollToBottom(el);
      tries += 1;
      if (tries > 40) clearInterval(t);
    }, 50);
  }

  function attachOnce() {
    const el = findContainer();
    if (el) {
      setupObserver(el);
      scrollToBottom(el);
      return true;
    }
    return false;
  }

  // Try immediate attach; if not found, poll until found (5s max)
  if (!attachOnce()) {
    let attempts = 0;
    const poll = setInterval(() => {
      if (attachOnce() || ++attempts > 100) clearInterval(poll);
    }, 50);
  }
})();
    </script>
""", unsafe_allow_html=True)
    st.session_state['message_container'] = st.container()
    # Display existing messages
    with st.session_state['message_container']:
        for msg in st.session_state['messages']:
            st.chat_message(msg['role']).write(msg['content'])


    # Chat input
    user_input = st.chat_input('Ask Lattice Genie to generate a lattice structure.')

    if user_input:

        # Append and show user input immediately
        st.session_state['messages'].append({'role': 'user', 'content': user_input})
        with st.session_state['message_container']:
            st.chat_message('user').write(user_input)
            


            # Typing dots directly below user message using CSS class
            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <style>
            .typing-dots {
                display: flex;
                justify-content: center;
                margin-top: 65px;
                margin-bottom: 65px;
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
            resp = client.chat.completions.create(model='gpt-4o', messages=messages, temperature=0)
            assistant_msg = resp.choices[0].message.content
        except Exception as e:
            assistant_msg = f"OpenAI API Error: {e}"

        # Replace typing dots with assistant message
        typing_placeholder.empty()
        process_status = process_assistant_response(assistant_msg, data)
        if process_status == 'processed':
            pass
        else:
          with st.session_state['message_container']:
              st.session_state["messages"].append({"role": "assistant", "content": assistant_msg})
              st.chat_message("assistant").write(assistant_msg)
    


def process_assistant_response(assistant_msg, data):
    start = assistant_msg.find('{')
    end = assistant_msg.rfind('}')
    confirmed = False
    params_dict = data["params_dict"]
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
                return 'processed'
        except json.JSONDecodeError:
            pass
      

