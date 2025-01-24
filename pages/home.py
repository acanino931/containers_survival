import streamlit as st
import pandas as pd
from components.DataSimulator import DataSimulator
from components.DataTransformer import DataTransformer
from utils import graph_maker

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
max_trip_days = st.number_input("Max Trip Days", min_value=1, value=40)

# Button to generate data
if st.button("Generate Data"):
    # Generate and store the simulated data in session_state
    simulator = DataSimulator(
        num_containers=int(num_containers),
        days=int(days),
        max_trip_days=int(max_trip_days)
    )
    
    st.session_state.df = simulator.simulate_container_data()

    # Transform and store the summary table in session_state
    st.session_state.transformer = DataTransformer(st.session_state.df)
    summary_table, day_trip_all = st.session_state.transformer.create_summary_table()
    st.session_state.summary_table = summary_table
    st.session_state.day_trip_all = day_trip_all
    st.session_state.recommended_threshold = summary_table.loc[0, "Recommended Threshold"]

# Check if data has been generated
if "df" in st.session_state:
    st.write("### Simulated Data")
    st.dataframe(st.session_state.df)

    # Option to download the data
    csv = st.session_state.df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="simulated_container_data.csv",
        mime="text/csv"
    )

    # Display the summary table
    st.write("### Summary Table")
    st.table(st.session_state.summary_table)

    # Place the first button in the first column
    if st.button("Generate Threshold Histogram"):
        fig = graph_maker.plot_histogram_with_thresholds(
            st.session_state.day_trip_all,
            user_threshold=max_trip_days,
            recommended_threshold=st.session_state.recommended_threshold
        )
        st.plotly_chart(fig, use_container_width=True)

    # Use the transformer for the second button
    if st.button("Launch the Kaplan Meier model"):
        if "transformer" in st.session_state:
            a = st.session_state.transformer.prepare_data_for_kaplan_meier()
        else:
            st.warning("Please generate data first.")