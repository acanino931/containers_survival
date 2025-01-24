import streamlit as st
import pandas as pd
from DataSimulator import DataSimulator
st.title("Container Data Simulation")

st.markdown("""
This tool simulates the cyclical trips of containers, recording starting and recollecting dates, 
whether they are lost, and the total stock of non-lost containers.

### Parameters:
- **Number of Containers**: The total number of containers to simulate.
- **Days**: Number of days to simulate from the starting date (2023-01-01).
- **Min Recollect Offset**: Minimum days after the starting date to allow recollection.
- **Max Trip Days**: Maximum days for a container to be considered not lost.
""")

# Input fields for parameters
num_containers = st.number_input("Number of Containers", min_value=1, value=1000)
days = st.number_input("Days", min_value=1, value=100)
min_recollect_offset = st.number_input("Min Recollect Offset", min_value=1, value=15)
max_trip_days = st.number_input("Max Trip Days", min_value=1, value=40)

# Button to generate data
if st.button("Generate Data"):
    simulator = DataSimulator(
        num_containers=int(num_containers),
        days=int(days),
        min_recollect_offset=int(min_recollect_offset),
        max_trip_days=int(max_trip_days),
        recollecting_rate=0.1  # Fixed value
    )
    
    df = simulator.simulate_container_data()

    st.write("### Simulated Data")
    st.dataframe(df)

    # Option to download the data
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="simulated_container_data.csv",
        mime="text/csv"
    )