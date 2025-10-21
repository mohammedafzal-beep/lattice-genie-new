import streamlit as st
import json
from openai import OpenAI
from streamlit_stl import stl_from_file
from html import escape
import tempfile
import os
import uuid, time
from components.parameter_ui import show_parameter_sliders

client=OpenAI(api_key='***')

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

  # --- Session init (unchanged features) ---
  if "messages" not in st.session_state:
      st.session_state["messages"] = []
  if "initialized" not in st.session_state:
      st.session_state["initialized"] = False
  if "pending_llm" not in st.session_state:
      st.session_state["pending_llm"] = None
  if "processing_input" not in st.session_state:
      st.session_state["processing_input"] = False
  if "tmp_stl_paths" not in st.session_state:
      st.session_state["tmp_stl_paths"] = []

  # Add an opening assistant message exactly once
  if not st.session_state["initialized"]:
      if not st.session_state["messages"]:
          st.session_state["messages"].append({
              "id": str(uuid.uuid4()),
              "role": "assistant",
              "type": "text",
              "content": "Hello! I am Lattice Genie. Ask me to recommend a lattice structure."
          })
      st.session_state["initialized"] = True

  # ---------- CSS (no avatars; user messages flush-right) ----------
  # Added animated typing-dots CSS — these dots will be injected as HTML inside the assistant placeholder message.
  st.markdown("""
  <style>
  .chat-wrapper { width:100%; max-width:900px; margin:8px auto; display:flex; flex-direction:column; }
  .chat-box {
      border:1px solid #444;
      border-radius:12px;
      background:#2e2e2e;
      padding:12px;
      height:420px;
      overflow-y:auto;
      display:flex;
      flex-direction:column;
      gap:8px;
      box-sizing:border-box;
  }
  .message {
      max-width:75%;
      padding:10px 14px;
      border-radius:12px;
      font-size:17px;
      line-height:1.4;
      word-wrap:break-word;
      color:#ffffff;
      display:inline-block;
  }
  .user { margin-left:auto; background-color:#7324B9; text-align:right; }
  .assistant { margin-right:auto; background-color:#3f51b5; text-align:left; }
  .stl-wrapper { margin-top:6px; margin-bottom:6px; }
  .stChatInputWrapper { margin-top: -6px; } /* visually attach native chat_input */

  /* animated typing dots (these are in-message HTML) */
  .typing-dots { display:flex; gap:6px; align-items:center; justify-content:flex-end; margin-top:6px; }
  .typing-dots .dot { width:10px; height:10px; border-radius:50%; background:#cfe9ff; opacity:0.25; animation:typing-blink 1s infinite ease-in-out; transform-origin:center; }
  .typing-dots .dot:nth-child(1){ animation-delay:0s; }
  .typing-dots .dot:nth-child(2){ animation-delay:0.15s; }
  .typing-dots .dot:nth-child(3){ animation-delay:0.3s; }
  @keyframes typing-blink {
    0% { transform: translateY(0); opacity:0.25; }
    30% { transform: translateY(-6px); opacity:1; }
    60% { transform: translateY(0); opacity:0.6; }
    100% { transform: translateY(0); opacity:0.25; }
  }
  </style>
  """, unsafe_allow_html=True)

  # --- Render chat wrapper and messages (all inside chat-box) ---
  st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

  messages_html = '<div class="chat-box" id="chat-box">'
  # Build simple HTML for text messages only; STL handled via stl_from_file below in order
  for msg in st.session_state["messages"]:
      role = msg.get("role", "assistant")
      css_class = "user" if role == "user" else "assistant"

      # If this is a typing placeholder message (msg['typing'] == True), render its raw HTML content (not escaped).
      if msg.get("type", "text") == "text":
          if msg.get("typing", False):
              # content contains HTML for dots; insert raw
              content_html = msg.get("content", "")
              messages_html += f'<div class="message {css_class}">{content_html}</div>'
          else:
              content = escape(msg.get("content", ""))
              messages_html += f'<div class="message {css_class}">{content}</div>'
      else:
          # Insert a placeholder div for STL; actual stl_from_file will render immediately afterwards.
          filename = escape(msg.get("filename", os.path.basename(msg.get("file_path", "")) if msg.get("file_path") else "model.stl"))
          messages_html += f'<div class="message {css_class}"><div style="font-size:13px;color:#e6eef8">File: {filename}</div><div class="stl-wrapper"></div></div>'
  messages_html += '</div>'

  # Auto-scroll to bottom after render
  messages_html += """
  <script>
  const box = document.getElementById('chat-box');
  if (box) { box.scrollTop = box.scrollHeight; }
  </script>
  """
  st.markdown(messages_html, unsafe_allow_html=True)

  # --- Native Streamlit chat_input (do NOT change this key elsewhere) ---
  user_input = st.chat_input("Ask Lattice Genie to recommend a structure", key="user_chat_input")

  # Now render STL widgets in-place in the same order: we iterate messages and when type=='stl' we call stl_from_file
  for msg in st.session_state["messages"]:
      if msg.get("type") == "stl":
          file_path = msg.get("file_path")
          with st.container():
            st.markdown('<div class="stl-wrapper" style="margin-left:10px;margin-right:10px;">', unsafe_allow_html=True)

          # call stl_from_file directly with the saved file path; key by message id
            try:
                stl_from_file(
                    file_path=file_path,
                    color='#FF9900',
                    material='material',
                    auto_rotate=False,
                    opacity=1.0,
                    shininess=100,
                    cam_v_angle=60,
                    cam_h_angle=-90,
                    cam_distance=None,
                    height=360,
                    max_view_distance=1000,
                    key=f"stl_{msg.get('id')}"
                )
                # Download button directly under the STL viewer (same flow)
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    st.download_button(label="Download STL", data=data, file_name=msg.get("filename", "model.stl"), mime='application/sla', key=f"dl_{msg.get('id')}")
                except Exception as e:
                    st.markdown(f'<div style="color:#ff9999">Download unavailable: {escape(str(e))}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to render STL '{msg.get('filename','model.stl')}': {e}")

  st.markdown('</div>', unsafe_allow_html=True)  # close wrapper

  # -------------------------
  # Input handling logic (two-pass): immediate user message, LLM processed on next run
  # -------------------------

  # Step 1: If the user submitted text, append it immediately and mark pending LLM for follow-up processing.
  if user_input and st.session_state["pending_llm"] is None:
      # Prevent accidental duplicate if last message already equals this user_input
      is_dup = False
      if st.session_state["messages"]:
          last = st.session_state["messages"][-1]
          if last.get("role") == "user" and last.get("content") == user_input:
              is_dup = True

      if not is_dup:
          # Immediately show the user's message
          st.session_state["messages"].append({
              "id": str(uuid.uuid4()),
              "role": "user",
              "type": "text",
              "content": user_input
          })

      # Register pending LLM processing (we'll do it on the next run)
      st.session_state["pending_llm"] = {"input": user_input}

      # Rerun so the UI updates immediately with the user's message visible
      st.rerun()

  # Step 2: If there is pending work and we're not already processing it, do the LLM call now.
  # We append a typing placeholder message (with HTML dots) and rerun so the dots appear inside chat-box.
  if st.session_state["pending_llm"] is not None and not st.session_state["processing_input"]:
      st.session_state["processing_input"] = True
      pending = st.session_state["pending_llm"]
      user_text = pending.get("input", "")

      # Append an assistant placeholder message that contains the animated dots HTML and mark typing=True
      typing_html = '<div class="typing-dots" style="justify-content:flex-end;"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>'
      st.session_state["messages"].append({
          "id": str(uuid.uuid4()),
          "role": "assistant",
          "type": "text",
          "content": typing_html,
          "typing": True
      })

      # Rerun so the typing dots appear immediately inside the chat box
      st.rerun()

  # Next run: detect the typing placeholder and perform the LLM call, then replace the placeholder with the assistant reply
  if st.session_state["processing_input"] and st.session_state["messages"]:
      last_msg = st.session_state["messages"][-1]
      if last_msg.get("role") == "assistant" and last_msg.get("typing", False):
          pending = st.session_state.get("pending_llm") or {}
          user_text = pending.get("input", "")

          # Call the LLM (blocking)
          assistant_reply = call_openai_chat(st.session_state["messages"], data)
            
          process_status = process_assistant_response(assistant_reply, data)
          if process_status == 'processed':
            append_generated_stl_from_filename(st.session_state['stl_path'])
          else:
          # Replace the typing placeholder with the real assistant reply (plain text)
            st.session_state["messages"][-1] = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "type": "text",
                "content": assistant_reply
            }

          # Clear pending and processing flags
          st.session_state["pending_llm"] = None
          st.session_state["processing_input"] = False

          # Rerun to render the assistant reply (the typing HTML is gone now)
          st.rerun()



# End of script


'''
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
}
.scrollable-container {
    max-height: 500px;      /* or 100vh if you want full height */
    overflow-y: auto;
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
    #cols = st.columns([1, 1, 1])
    #with cols[1]:
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
            st.markdown("""
<script>
(function() {
  // try docs
  const docs = [document, (window.parent && window.parent.document), (window.top && window.top.document)].filter(Boolean);

  function isVisible(el) {
    if (!el || !(el instanceof Element)) return false;
    const rect = el.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }

  function findLastMessageElement() {
    const candidateSelectors = [
      '[data-testid*="stChatMessage"]',
      '[data-testid*="stChatBubble"]',
      '[data-testid*="stChatMessages"] > *',
      'div[class*="stChat"]',
      'div[role="listitem"]',
      'div[role="article"]',
      'article',
      'main .stMarkdown',
      'section.main div:has(span)'
    ];
    for (const d of docs) {
      try {
        // try selectors first
        for (const sel of candidateSelectors) {
          const nodes = d.querySelectorAll(sel);
          if (nodes && nodes.length) {
            // find last visible from end
            for (let i = nodes.length - 1; i >= 0; --i) {
              if (isVisible(nodes[i])) return {el: nodes[i], doc: d};
            }
          }
        }

        // fallback: any element that looks like a message text (non-empty innerText)
        const all = d.querySelectorAll('div, p, span, article');
        for (let i = all.length - 1; i >= 0; --i) {
          const n = all[i];
          try {
            if (n.innerText && n.innerText.trim().length > 5 && isVisible(n)) {
              // heuristic: likely a chat message
              return {el: n, doc: d};
            }
          } catch (e) {}
        }
      } catch (e) {}
    }
    return null;
  }

  function getScrollableAncestor(el) {
    if (!el) return null;
    let p = el.parentElement;
    while (p) {
      try {
        const cs = (p.ownerDocument || document).defaultView.getComputedStyle(p);
        const overflowY = cs && cs.overflowY;
        if (overflowY === 'auto' || overflowY === 'scroll' || p.scrollHeight > p.clientHeight) return p;
      } catch (e) {}
      p = p.parentElement;
    }
    // fallback to body of same doc
    return (el.ownerDocument && el.ownerDocument.scrollingElement) || document.scrollingElement || document.body;
  }

  function forceScrollToElement(el) {
    if (!el) return;
    try {
      // scroll the element into view (best effort)
      el.scrollIntoView({block: 'end', behavior: 'auto', inline: 'nearest'});
    } catch (e) {}
    // also force its nearest scrollable ancestor
    const anc = getScrollableAncestor(el);
    if (anc) {
      try {
        anc.scrollTop = anc.scrollHeight + 200; // push a bit further
      } catch (e) {}
    }
    // also try global document scrolling elements
    try { (el.ownerDocument && el.ownerDocument.scrollingElement).scrollTop = (el.ownerDocument && el.ownerDocument.scrollingElement).scrollHeight; } catch (e) {}
    try { document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight; } catch (e) {}
  }

  function doScrollCycle() {
    const found = findLastMessageElement();
    if (found && found.el) {
      forceScrollToElement(found.el);
      return true;
    }
    return false;
  }

  function attachObserverToRoot(rootDoc) {
    try {
      const root = rootDoc.querySelector('body') || rootDoc;
      if (!root) return;
      const observer = new MutationObserver(() => {
        // micro task to let streamlit finish painting
        setTimeout(() => {
          const ok = doScrollCycle();
          // if special message present, do stronger delayed scrolls
          const found = findLastMessageElement();
          if (found && found.el && found.el.innerText && found.el.innerText.includes('Generation may take a few seconds')) {
            setTimeout(() => forceScrollToElement(found.el), 60);
            setTimeout(() => forceScrollToElement(found.el), 250);
            setTimeout(() => forceScrollToElement(found.el), 800);
          }
        }, 12);
      });
      observer.observe(root, { childList: true, subtree: true });
    } catch (e) {}
  }

  function attachFocusHandler(rootDoc) {
    try {
      const textarea = rootDoc.querySelector('div[data-testid="stChatInput"] textarea, textarea[placeholder], input[type="text"]');
      if (textarea) {
        textarea.addEventListener('focus', () => setTimeout(doScrollCycle, 30));
        textarea.addEventListener('input', () => setTimeout(doScrollCycle, 10));
      }
    } catch (e) {}
  }

  // Try immediate attach + aggressive retry/poll for up to ~8s
  let attached = false;
  for (const d of docs) {
    try {
      attachObserverToRoot(d);
      attachFocusHandler(d);
      attached = true;
    } catch (e) {}
  }

  // Also run repeated attempts for a few seconds
  let attempts = 0;
  const poll = setInterval(() => {
    const ok = doScrollCycle();
    // attempt to attach handlers if not already
    for (const d of docs) {
      attachFocusHandler(d);
    }
    attempts++;
    if (ok || attempts > 160) { // 160 * 50ms = 8s
      clearInterval(poll);
    }
  }, 50);

})();
</script>
""", unsafe_allow_html=True)


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
        msg_to_display = process_assistant_response(assistant_msg, data["params_dict"])
        if msg_to_display == 1:
            pass
        else:
          with st.session_state['message_container']:
              st.session_state["messages"].append({"role": "assistant", "content": msg_to_display})
              st.chat_message("assistant").write(msg_to_display)
        '''    


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
                show_parameter_sliders(data)
                return 'processed'
        except json.JSONDecodeError:
            pass


### dropdown version ##########
def append_user_message(text):
   st.session_state.messages.append({'role': 'user', 'content': text})


def append_assistant_message(text):
   st.session_state.messages.append({'role': 'assistant', 'content': text})
   st.session_state.last_assistant_msg = text


 # --- Render chat ---
def render_chat():
    html = '<div class="chat-box">'
    for msg in st.session_state['messages']:
        if msg['role'] == 'user':
            html += f'<div class="message user">{msg["content"]} <span class="avatar">🧑</span></div>'
        else:
            html += f'<div class="message assistant"><span class="avatar">🤖</span> {msg["content"]}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# for both versions ##
def call_openai_chat(messages, data, model='gpt-4o'):
  
  try:
      messages = [{'role': 'system', 'content': data['system_prompt']}] + messages
      resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
      return resp.choices[0].message.content
  except Exception as e:
      return f"OpenAI API Error: {e}"

