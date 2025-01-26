import streamlit as st
from components.Modeler import Modeler
from utils.graph_maker import plot_mapped_survival, plot_available_containers

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

    # Load session data
    df = st.session_state.df
    num_containers = st.session_state.num_containers
    days = st.session_state.days
    perc_days_in_trip = st.session_state.perc_days_in_trip

    # Initialize the Modeler class
    modeler = Modeler(df, prob_in_trip=perc_days_in_trip)

    # Display preprocessed data
    st.subheader("Preprocessed Data")
    st.dataframe(modeler.df)

    # Question 1: Shrinking Rate
    st.subheader("Question 1: What is the probability of a container being lost when starting a trip (Shrinking Rate)?")
    st.markdown("""
        To answer this question, we use the Kaplan-Meier survival curve to estimate the survival probabilities of containers over time.  
        The shrinking rate at any given moment is calculated as:
    """)
    st.latex(r"Shrinking\ Rate = 1 - S(t)")

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
        st.session_state.mapped_survival = mapped_survival

        fig = plot_mapped_survival(mapped_survival , modeler.median_trip_time)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Answer: The shrinking rate is: {shrinking_rate:.4f}")

    # Question 2: Available Containers
    st.subheader("Question 2: How many containers are available at any given time?")
    st.markdown("""
    To estimate the number of available containers at any given time, we calculate:

    - Let \(P_{trip}(t)\) be the probability of being in a trip over time.
    - Let \(1 - S(t)\) represent the shrinking rate derived from survival analysis, where \(S(t)\) is the survival probability.
    - Let \(N_{initial}\) be the total number of initial containers.

    Combining these, the number of available containers over time, \(N_{available}(t)\), is calculated as:
    """)
    st.latex(r"""
    N_{available}(t) = N_{initial} \cdot P_{trip}(t) \cdot  (1 - S(t)))
    """)
    final_containers = st.number_input("Initial Number of Containers", min_value=1, value=int(num_containers), step=1)
    final_days = st.number_input("Observation Time", min_value=1, value=int(days), step=1)

    

    if st.button("Estimate Available Containers"):

        if st.session_state.mapped_survival is None:
            st.warning("Please generate Kaplan-Meier Curve first.")
            return
        mapped_survival_adjusted = st.session_state.mapped_survival.copy()
        #  calculating the risk of losing a containerfor each moment # KM_estimate 
        mapped_survival_adjusted['Hazard'] =  1 - mapped_survival_adjusted['KM_estimate'] * perc_days_in_trip

        mapped_survival_adjusted['Containers'] = final_containers - final_containers * mapped_survival_adjusted['Hazard']

        mapped_survival_adjusted= mapped_survival_adjusted[['Containers']]

        st.markdown("""
        The following graph represent the estimated number of available containers over time:
        """)
        fig = plot_available_containers(mapped_survival_adjusted, final_days)
        st.plotly_chart(fig, use_container_width=True)

        final_estimate = mapped_survival_adjusted.loc[final_days, 'Containers']
        print ( final_estimate)

        st.subheader(f"The estimated number of containers for the given time is: {round(final_estimate)}")

        
