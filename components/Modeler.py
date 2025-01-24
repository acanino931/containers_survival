import pandas as pd
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, NelsonAalenFitter

class Modeler:
    def __init__(self, df):
        """
        Initialize the Modeler class with a DataFrame.

        Parameters:
            df (pd.DataFrame): The input DataFrame, which must contain:
                - 'DayTrip': Duration of each trip.
                - 'IsLost': 1 if the container was lost, 0 otherwise.
                - 'UniqueTripID': A unique identifier for each trip.
        """
        self.df = df

    def kaplan_meier_curve(self):
        """
        Generate the Kaplan-Meier survival curve.

        Returns:
            Kaplan-Meier plot
        """
        kmf = KaplanMeierFitter()
        kmf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        plt.figure(figsize=(8, 5))
        kmf.plot_survival_function()
        plt.title("Kaplan-Meier Survival Curve")
        plt.xlabel("Trip Duration (Days)")
        plt.ylabel("Survival Probability")
        plt.grid()
        plt.show()

    def hazard_function(self):
        """
        Generate the Nelson-Aalen cumulative hazard curve.

        Returns:
            Nelson-Aalen plot
        """
        naf = NelsonAalenFitter()
        naf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        plt.figure(figsize=(8, 5))
        naf.plot_cumulative_hazard()
        plt.title("Cumulative Hazard Function")
        plt.xlabel("Trip Duration (Days)")
        plt.ylabel("Cumulative Hazard")
        plt.grid()
        plt.show()

    def shrinking_risk(self):
        """
        Compute and plot the shrinking risk over time.

        Returns:
            Shrinking risk plot
        """
        kmf = KaplanMeierFitter()
        kmf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        shrinking_risk = 1 - kmf.survival_function_

        plt.figure(figsize=(8, 5))
        plt.plot(shrinking_risk.index, shrinking_risk.values, label="Shrinking Risk", color="red")
        plt.title("Shrinking Risk Over Time")
        plt.xlabel("Trip Duration (Days)")
        plt.ylabel("Shrinking Risk (1 - S(t))")
        plt.grid()
        plt.legend()
        plt.show()

    def main_kpis(self):
        """
        Compute main KPIs for survival analysis.

        Returns:
            dict: A dictionary containing:
                - 'Median Survival Time': Time at which survival probability is 50%.
                - 'Cumulative Shrinking Risk': Probability of loss at the end of the observed period.
                - 'Max Hazard': Maximum cumulative hazard observed.
        """
        kmf = KaplanMeierFitter()
        kmf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        naf = NelsonAalenFitter()
        naf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        median_survival_time = kmf.median_survival_time_
        cumulative_shrinking_risk = 1 - kmf.survival_function_.iloc[-1].values[0]
        max_hazard = naf.cumulative_hazard_.iloc[-1].values[0]

        return {
            "Median Survival Time": median_survival_time,
            "Cumulative Shrinking Risk": cumulative_shrinking_risk,
            "Max Hazard": max_hazard
        }
