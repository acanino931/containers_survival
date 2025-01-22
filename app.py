import streamlit as st
import pandas as pd
import logging

# Set up logging configuration
logging.basicConfig(
    filename='app.log',  # Log file name
    level=logging.DEBUG,  # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Example log messages
logging.info("Streamlit app started.")

# Title for the app
st.title("Streamlit Application")

# Upload file functionality
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Log file upload event
    logging.info(f"User uploaded a file: {uploaded_file.name}")
    
    # Read and display the file
    df = pd.read_csv(uploaded_file)
    st.write(df)
    
    # Log data shape
    logging.info(f"Data contains {df.shape[0]} rows and {df.shape[1]} columns.")