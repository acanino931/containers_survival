import streamlit as st
from components.Modeler import Modeler
from utils.graph_maker import plot_mapped_survival, plot_available_containers
from utils.math_functions import calculate_available_containers

def launch_the_model():
    st.title("Launch the Model")

    st.markdown("""
    This page answers two key questions:

    1. **What is the probability of a container being lost when starting a trip?**
    2. **How many containers are available at any given time during the observed period?**
    """)

    if "df" not in st.session_state or "num_containers" not in st.session_state or "perc_days_in_trip" not in st.session_state:
        st.warning("Required data is missing. Please generate data in the Scenario Data Gen page first.")
        return
    if "mapped_survival" not in st.session_state:
        st.session_state.mapped_survival = None  # Initialize to None

    if "shrinking_rate" not in st.session_state:
        st.session_state.shrinking_rate = None  # Initialize to None

    if "median_trip_time" not in st.session_state:
        st.session_state.median_trip_time = None

    # Load session data
    df = st.session_state.df
    num_containers = st.session_state.num_containers
    days = st.session_state.days
    perc_days_in_trip = st.session_state.perc_days_in_trip

    # Initialize the Modeler class
    modeler = Modeler(df, prob_in_trip=perc_days_in_trip)
    st.session_state.median_trip_time = modeler.median_trip_time

    # Display preprocessed data
    st.subheader("Preprocessed Data")
    st.dataframe(modeler.df)

    # Question 1: Shrinking Rate
    st.subheader("Question 1: What is the probability of a container being lost when starting a trip (Shrinking Rate)?")
    st.markdown("""
        To answer this question, we use the Kaplan-Meier survival curve to estimate the survival probabilities of containers over time.  
        The shrinking rate at any given moment is calculated as:
    """)
    st.latex(r"Shrinking\ Ratio = 1 - S(t_{\text{median}})")

    st.markdown("""
        where \(S(t)\) is the survival probability at a given time \(t\).  
        For this analysis, we consider the **median trip duration** to estimate the **Shrinking Rate**.

        The survival probabilities are mapped to a range from 1 to the observed probability of not being lost in the interval.  
        For example, if 3% of the containers have been lost, the survival probability at the last moment of the observed period will be 0.97.  
    """)

    if st.button("Generate Kaplan-Meier Curve"):
        st.markdown("""
        ### Kaplan-Meier Estimation

        Kaplan-Meier is based purely on observed data. It calculates the survival probabilities at each observed time point directly from the data without fitting it to a theoretical distribution.

        The survival probability is estimated as the product of conditional probabilities at each event time:
        """)
        st.latex(r"S(t) = \prod_{t_i \leq t} \left(1 - \frac{d_i}{n_i}\right)")

        st.markdown("""
        Where:

        - \(d_i\): Number of events (e.g., losses) at time \(t_i\).
        - \(n_i\): Number of individuals at risk just before \(t_i\).
        """)

        mapped_survival = modeler.mapped_survival_function()
        median_hazard = modeler.get_km_estimate_at_timeline(mapped_survival)
        shrinking_rate = 1 - median_hazard
        st.session_state.shrinking_rate = shrinking_rate
        st.session_state.mapped_survival = mapped_survival
        

        fig = plot_mapped_survival(mapped_survival , modeler.median_trip_time)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Answer: The shrinking rate is: {shrinking_rate:.4f}")

    # Question 2: Available Containers
    st.subheader("Question 2: How many containers are available at any given time?")
    st.markdown("""
    To estimate the number of available containers at any given time, we calculate:

    - Let \(H\) represent the **constant shrinking hazard** derived from survival analysis, averaged over the requested time interval \(t_{min}\) to \(t_{max}\).
    - Let \(P_{trip}\) represent the **probability of being in a trip**, assumed to be constant across the interval.
    - Let \(N_{initial}\) be the **total number of initial containers**.

     we instead assume the shrinking rate, \(H\), to be **constant over the interval**. This simplifies the calculation while accounting for overlapping trips.

    """)

    st.latex(r"""
        N_{available}(t) = N_{available}(t) - N_{available}(t) \cdot H \cdot P_{trip}
    """)

    st.markdown("""
    To calculate \( H \), the **shrinking hazard**, we divide the total shrinking rate S over the time interval \( [t_{min}, t_{max}] \) by the length of the interval.

    ### Definition of \( H \)
    - Let \( S \) be the mean shrinking rate derived from survival analysis in the previous point.
    - Let \( t_{min} \) and \( t_{max} \) represent the start and end of the time interval.

    The shrinking risk per unit time, \( H \), is calculated as:
    """)

    st.latex(r"""
        H = \frac{S}{t_{max} - t_{min}}
    """)

    st.markdown("""
    Since multiple trips can happen within the same time span, we are using assuming that the risk it's a constant value for each day in the time span,
                this formula assumes that the shrinking rate is distributed evenly across the interval, as it accounts for the fact that multiple trips can occur within the same time span. By normalizing \( S \) over the interval length, we obtain a constant \( H \) for use in our calculations.
    """)


    final_containers = st.number_input("Initial Number of Containers", min_value=1, value=int(num_containers), step=1)
    final_days = st.number_input("Observation Time", min_value=1, value=int(days), step=1)

    

    if st.button("Estimate Available Containers"):


        if st.session_state.shrinking_rate is None:
            st.warning("Please generate Kaplan-Meier Curve first. Shrinking_rate missing")
            return

        shrinking_rate = st.session_state.shrinking_rate


        # we are assuming that the risk it's equally distributed for all the period.
        adjusted_shrinking_rate =  shrinking_rate/ days * perc_days_in_trip


        df_remaining_containers = calculate_available_containers(final_containers, days , adjusted_shrinking_rate  )



        st.markdown("""
        The following graph represent the estimated number of available containers over time:
        """)
        fig = plot_available_containers(df_remaining_containers, final_days)
        st.plotly_chart(fig, use_container_width=True)


        filtered_row = df_remaining_containers[df_remaining_containers['Day'] == final_days]


        if not filtered_row.empty:
            final_estimate = filtered_row['Containers'].iloc[0]
        else:
            st.error(f"Day {final_days} is not in the DataFrame.")
            final_estimate = None
        

        st.subheader(f"The estimated number of containers for the given time is: {round(final_estimate)}")

        st.markdown("""
        NOTE: In case you want to generate a new prediction after modifying the initial data generation parameters or the scenario,
                     please click once again the Generate Kaplan-Meier Curve to be sure of the updated results.
        """)

        
