import streamlit as st

# Configure the page layout to remove the sidebar
st.set_page_config(
    page_title="IFCO Data science Challenge App",
    page_icon="📦",
    layout="centered",  # Center all content on the main page
    initial_sidebar_state="collapsed",
    menu_items=None
)
# disable sidebar
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# App Title
st.title("Welcome to the IFCO Data science challenge App")

st.markdown("""
### Select a Page
Choose the action you'd like to perform below:
""")

# Centered Navigation
page = st.selectbox(
    "Navigate to:",
    options=["Data Generation Scenario1", "Data Generation Scenario2", "Launch the Model"],
    index=0
)

# Page Navigation Logic
if page == "Data Generation Scenario1":
    from pages.data_gen import run_data_generation
    run_data_generation(scenario=1)

elif page == "Data Generation Scenario2":
    from pages.data_gen import run_data_generation
    run_data_generation(scenario=2)

elif page == "Launch the Model":
    from pages.launch_the_model import launch_the_model
    launch_the_model()