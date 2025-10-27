import streamlit as st
from components.viewer import show_stl_thumbnail_page

def render_generic_page(page, data):
    st.markdown("""
<style>
.center { text-align: center; }
.unbold { font-weight: normal !important; }
[data-testid='stHeaderActionElements'] {display: none;}
</style>
""", unsafe_allow_html=True)
    st.markdown(f"<h2 class='center'>{page}</h2>", unsafe_allow_html=True)

    page_data = data["subtypes_info"].get(page)
    if page_data:
        st.markdown(f"<h4 class='center unbold'>{page_data['description']}</h4>", unsafe_allow_html=True)
    st.markdown("""
<style>
/* Style the button itself */
div.stButton > button {
    width: 150px !important;       /* button width */
    height: 40px !important;       /* button height */
    border-radius: 8px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Style the text inside the button (covers span/div children) */
div.stButton > button * {
    font-size: 17px !important;    /* 🔑 control text size */
    font-weight: bold !important;
    white-space: nowrap !important; /* keep it on one line */
}
</style>
""", unsafe_allow_html=True)



    col = st.columns([.84, .22, 1])[1]
    with col:
        if st.button("⬅ Back to Home"):
            st.session_state.go_home = True
            st.rerun()
    
    items = page_data.get("items", [])
    for row_start in range(0, len(items), 4):
        row_items = items[row_start:row_start+4]
        cols = st.columns(4)
        for i in range(4):
            with cols[i]:
                if i < len(row_items):
                    sub_name, img_path, desc = row_items[i]
                    try:
                        show_stl_thumbnail_page(sub_name, img_path, page=page)
                    except:
                        st.error(f"Couldn't load {sub_name} image.")
                    st.markdown(f"<h3 class='center'>{sub_name}</h3>", unsafe_allow_html=True)
              
                    st.markdown(f"<h5 class='center unbold'>{desc}</h5>", unsafe_allow_html=True)
                    
