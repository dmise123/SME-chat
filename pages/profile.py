import streamlit as st

# Hide sidebar navigation items
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
    st.page_link("rag_app.py", label="Home")  # This assumes rag_app.py is your main app
    st.page_link("pages/information.py", label="Bakery Information")  # Adjusted to include pages/
    st.page_link("pages/profile.py", label="Profile")

st.write("Hello, welcome to the main application!")
