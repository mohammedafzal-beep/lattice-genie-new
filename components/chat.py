import streamlit as st
import json
from openai import OpenAI
client=OpenAI(api_key='***') # Replace with your OpenAI API key
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
            resp = client.chat.completions.create(model='gpt-4o', messages=messages, temperature=0)
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
        msg_to_display = "Generation may take a few seconds. \n" \
        "⬇️ Make sure to download the STL before proceeding to newer generation. \n" \
        "To generate a new structure, type anything in the chat and hit 'Enter'."
        st.markdown("""<script>setTimeout(() => {
      var chat = window.parent.document.querySelector('section.main');
      if (chat) chat.scrollTop = chat.scrollHeight;
    }, 300);</script>""", unsafe_allow_html=True)
    else:
        msg_to_display = assistant_msg

    st.session_state["messages"].append({"role": "assistant", "content": msg_to_display})
    st.session_state["last_assistant_msg"] = msg_to_display
    return msg_to_display
