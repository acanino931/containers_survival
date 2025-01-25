import streamlit as st
from lifelines import KaplanMeierFitter, NelsonAalenFitter
import matplotlib.pyplot as plt
from components.Modeler import Modeler
def launch_the_model():
    st.title("Launch the Model")

    st.markdown("""
    Use this page to analyze the generated data with survival analysis techniques, 
    including Kaplan-Meier survival curves, hazard functions, and shrinking risk.
    """)

    if "df" not in st.session_state:
        st.warning("No data found. Please generate data in the Scenario 1 Data Gen page first.")
        return

    df = st.session_state.df
    #df.to_excel("./data/input_modeler.xlsx", index=False)
    modeler = Modeler(df)

    st.write("### Preprocessed Data for Analysis")
    st.dataframe(modeler.df)

    if modeler.df.shape[0] < modeler.original_df.shape[0]:
        st.warning(f"{modeler.original_df.shape[0] - modeler.df.shape[0]} rows with invalid values were removed.")
        st.write("Removed rows:")
        st.dataframe(modeler.original_df[modeler.original_df[['DayTrip', 'IsLost']].isnull().any(axis=1)])

    if st.button("Kaplan-Meier Survival Curve"):
        st.write("### Kaplan-Meier Survival Curve")
        st.plotly_chart(modeler.kaplan_meier_curve(), use_container_width=True)

    if st.button("Hazard Function"):
        st.write("### Hazard Function")
        st.plotly_chart(modeler.hazard_function(), use_container_width=True)

    if st.button("Shrinking Risk Over Time"):
        st.write("### Shrinking Risk Over Time")
        st.plotly_chart(modeler.shrinking_risk(), use_container_width=True)

    if st.button("Compute Main KPIs"):
        st.write("### Main KPIs")
        kpis = modeler.main_kpis()
        st.json(kpis)