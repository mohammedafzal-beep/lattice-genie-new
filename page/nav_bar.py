import streamlit as st

def nav_bar():
    st.sidebar.markdown(
        """
        <div class='center'>
            <h1>Navigation Bar</h1>
        </div>
        <style>
            .stAlert {
                display: none;
            }
            .center {
                text-align: center;
            }
        </style>
        
        """,
        unsafe_allow_html=True
    )
    st.sidebar.markdown("---")
    
