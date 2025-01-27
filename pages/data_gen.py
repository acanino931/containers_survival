import streamlit as st
import pandas as pd
from components.DataSimulator import DataSimulator
from components.DataTransformer import DataTransformer
from utils import graph_maker

def run_data_generation(scenario=1):
    """
    Run the Data Generation Page for the selected scenario.

    Args:
        scenario (int): The scenario to run (1 or 2).
    """
    st.title(f"Data generation for - Scenario {scenario}")

    # Shared explanation for both scenarios
    st.markdown("""
    In this tool, the **probability of recollecting a container** is modeled using a **log-normal distribution**. 
    This distribution allows us to simulate realistic trip durations by assuming that the time before recollection is 
    skewed, with a longer tail representing containers that take more time to return.
    """)

    # Additional explanation for Scenario 2
    if scenario == 2:
        st.subheader("Scenario 2: Observability of Trips")
        st.markdown("""
        In **Scenario 2**, the **percentage of observable trips** is taken into account. This percentage dynamically 
        modifies the parameters of the log-normal distribution to make the simulation more realistic.

        - A **smaller percentage** of observable trips results in an **increased average time** before a container is recollected. 
        - The **variability** of trip durations also increases as fewer trips are observed, leading to a wider spread in the distribution.

        A good way to compare the behavior of both scenarios is by looking at the **duration histograms** that you can generate 
        at the end of this page. It is also important to **set a new threshold** in Scenario 2 to avoid misclassifying containers 
        that are likely still in the cycle as lost.
        """)

    # Parameter input fields
    st.markdown("""
    **Adjust the parameters below to simulate data:**
    """)
    num_containers = st.number_input("Number of Containers", min_value=1, value=1000, step=1)
    st.session_state.num_containers = num_containers
    days = st.number_input("Number of Days", min_value=1, value=100, step=1)
    st.session_state.days = days
    min_trip_days = st.number_input("Minimum Days for a Trip", min_value=1, value=20, step=1)
    perc_trips_observed = 1.0  # Default for Scenario 1

    if scenario == 2:
        perc_trips_observed = st.slider("Insert the Percentage of Observable Trips", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

    st.markdown("""
    Setting a threshold of a reasonable minimum trip duration is important to avoid misclassifying containers that recently have started a trip when the period
    of observation ends.\n Those containers will not be considered as lost even if the recollection date will be null.\n
    If the threshold value is too high the model would underestimate the probability of a container being lost.
    """)

    

    # Button to generate data
    if st.button("Generate Data"):
        st.write(f"Generating data for Scenario {scenario}...")
        
        try:
            # Initialize the DataSimulator with scenario-specific parameters
            simulator = DataSimulator(
                num_containers=int(num_containers),
                days=int(days),
                min_trip_days=int(min_trip_days),
                scenario = scenario,
                perc_trips_observed =perc_trips_observed
            )

            # Generate data and store it in session_state
            st.session_state.df = simulator.simulate_container_data()

            # Transform the data and store summary results in session_state
            st.session_state.transformer = DataTransformer(st.session_state.df)

            summary_table, day_trip_all = st.session_state.transformer.create_summary_table(simulator.eval_metrics)

            st.session_state.summary_table = summary_table
            st.session_state.day_trip_all = day_trip_all
            #st.session_state.recommended_threshold = summary_table.loc[0, "Recommended Threshold"]
            st.session_state.perc_days_in_trip = summary_table.loc[0, "Percentage Days in Trip"]

            # Success message
            st.success("Data generation complete!")
            st.markdown("""
                ### Explanation of the Generated Data

                The generated data has a **panel structure**, where the \( n \) containers are repeated for each day. Below is a detailed description of the fields:

                - **`StartingDate`**:  
                Represents the date when a container started a new trip. It can either have a value (indicating the start of a trip) or be null if the container is in stock.

                - **`RecollectingDate`**:  
                Indicates the date when a container has been recollected, marking the end of the trip. After this date, the container can either start another trip or remain idle.

                - **`isLost`**:  
                A dummy variable representing containers classified as lost according if both this 2 conditions are met:
                1. The container has not been recollected in the observed time span.
                2. The trip duration exceeds the user-defined threshold.

                - **`DayTrip`**:  
                Represents the duration of the trip for each container.

                - **`IsFakeLost`**:  
                Indicates containers initially misclassified as lost according to the user-defined threshold.

                - **`TotalStock`**:  
                Represents the total number of containers that are **not lost** at any given moment.

                ### Important Notes:
                - The values of `isLost` and `TotalStock` are corrected to exclude the false-positive bias introduced by the user-defined threshold.
                """)

        except Exception as e:
            st.error(f"An error occurred during data generation: {e}")
            return

    # Display generated data and options if data exists
    if "df" in st.session_state:
        st.write("### Simulated Data")
        st.dataframe(st.session_state.df)

        # Option to download the data as a CSV file
        csv = st.session_state.df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"simulated_container_data_scenario_{scenario}.csv",
            mime="text/csv"
        )

        # Display the summary table
        st.write("### Summary Table")
        st.table(st.session_state.summary_table)
        st.markdown("""
            - **`Percentage Days in Trip`**:  
            The percentage of days containers are actively in a trip compared to the total days considered in the simulation.

            - **`Trip Precision user threshold`**:  
            Precision value initially calculated at the **user-defined threshold** for classifying containers as "lost".  
            This field is meant to give more information to the user over the possible rate of false negative according to the threshold chosen.
            The formula for precision is:
        """)
        st.latex(r"Precision = \frac{True\ Positives}{True\ Positives + False\ Positives}")
        st.markdown("""
            - **`Median trip duration`**:  
            Median value of the trip duration distribution in days.

            - **`Average trip duration`**:  
            Average of the trip duration distribution in days.

            - **`Variance trip duration `**:  
            Varianceof the trip duration distribution in days.
        """)
        st.subheader("To change the current threshold, input the new threshold value in the generate data section and click the generation button.")

        # Generate the threshold histogram
        if st.button("Generate Threshold Histogram"):
            fig = graph_maker.plot_histogram_with_thresholds(
                st.session_state.day_trip_all,
                user_threshold=min_trip_days,
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
                        The previous metrics about the False positve determined by the user threshold will not impact the performance of the model.
                        The values used for training the model are corrected for having a better performance.
                        In other words the value of all the False posivives FP (Containers that are incorrectly classified as lost) are updated and considered as not-lost in the training set.
                        """)
            st.subheader("To continue access the launch the model page, from the navigator on the top of this page.")

    # # Use the transformer for the second button
    # if st.button("Launch the Kaplan Meier model"):
    #     if "transformer" in st.session_state:
    #         a = st.session_state.transformer.prepare_data_for_kaplan_meier()
    #     else:
    #         st.warning("Please generate data first.")