import streamlit as st

def nav_bar():
    st.sidebar.markdown(
        """
       <div class='center'>
            <p style='font-size:1.65rem; line-height:1.2; '>Navigation Bar</p>
        </div>
        <style>
            .stAlert { display: none; }
            .center { text-align: center; }
            section[data-testid="stSidebar"] * {
                font-size: 1.4rem;
            }
            /* Reduce gap above and below the horizontal rule */
            section[data-testid="stSidebar"] hr {
                margin-top: 0.2em;
                margin-bottom: 0.2em;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")
    
