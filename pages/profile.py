import streamlit as st

st.markdown(
    """
    <style>
        [data-testid="stSidebarNavItems"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.page_link("rag_app.py", label="Home")
    st.page_link("pages/profile.py", label="Profile")

st.write("hello")