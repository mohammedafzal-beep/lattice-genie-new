import streamlit as st
from components.viewer import show_stl_thumbnail_page

def render_generic_page(page, data):
    st.markdown(f"<h1 class='center'>{page}</h1>", unsafe_allow_html=True)

    page_data = data["subtypes_info"].get(page)
    if page_data:
        st.markdown(f"<p class='center'>{page_data['description']}</p>", unsafe_allow_html=True)

    if st.button("⬅ Back to Home"):
        st.session_state.go_home = True
        st.rerun()
    st.markdown(
    """
    <style>
    div[data-testid="stButton"] { display: flex; justify-content: center; }
    </style>
    """,
    unsafe_allow_html=True
)
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
                    st.markdown(f"**{sub_name}**")
                    st.markdown(f"{desc}")
