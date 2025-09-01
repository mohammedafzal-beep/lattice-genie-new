import streamlit as st
from components.viewer import show_stl_thumbnail_page

def render_generic_page(page, data):
    st.markdown("""
<style>
.center { text-align: center; }
.unbold { font-weight: normal !important; }
</style>
""", unsafe_allow_html=True)
    st.markdown(f"<h1 class='center'>{page}</h1>", unsafe_allow_html=True)

    page_data = data["subtypes_info"].get(page)
    if page_data:
        st.markdown(f"<h3 class='center unbold'>{page_data['description']}</h3>", unsafe_allow_html=True)
    col = st.columns([1, .18, 1])[1]
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
                    
