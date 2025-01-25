import pandas as pd
import plotly.graph_objects as go
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
        self.original_df = df
        self.df = self.prepare_data_for_analysis()

    def prepare_data_for_analysis(self):
        """
        Preprocess and clean the DataFrame for Kaplan-Meier and other analyses.

        Returns:
            pd.DataFrame: Preprocessed DataFrame.
        """
        data = self.original_df.copy()
        data["UniqueTripID"] = data["ContainerID"].astype(str) + "_" + data["TripID"].astype(str)
        data = data[data["StartingDate"].notnull()]
        groupby_trip = data.groupby("UniqueTripID")
        aggregated = pd.DataFrame({
            "DayTrip": groupby_trip["DayTrip"].max(),
            "IsLost": groupby_trip["IsLost"].max()
        }).reset_index()
        aggregated.to_excel("./data/aggregated.xlsx", index=False)
        self._log_removed_rows(aggregated, ["DayTrip", "IsLost"])
        aggregated.dropna(subset=["DayTrip", "IsLost"]).reset_index(drop=True).to_excel("./data/aggregated_post_drop.xlsx", index=False)
        return aggregated.dropna(subset=["DayTrip", "IsLost"]).reset_index(drop=True)

    def _log_removed_rows(self, df, columns):
        """
        Log and print rows with NaN or infinite values in the specified columns.
        """
        problematic_rows = df[df[columns].isnull().any(axis=1)]
        if not problematic_rows.empty:
            print("The following rows have been removed due to NaN or infinite values:")
            print(problematic_rows)


    def kaplan_meier_curve(self):
        """
        Generate the Kaplan-Meier survival curve using Plotly.

        Returns:
            plotly.graph_objects.Figure: The Kaplan-Meier plot.
        """
        kmf = KaplanMeierFitter()
        kmf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=kmf.survival_function_.index,
            y=kmf.survival_function_['KM_estimate'],
            mode='lines',
            name='Survival Probability'
        ))

        fig.update_layout(
            title="Kaplan-Meier Survival Curve",
            xaxis_title="Trip Duration (Days)",
            yaxis_title="Survival Probability",
            template="plotly_white"
        )
        return fig

    def hazard_function(self):
        """
        Generate the Nelson-Aalen cumulative hazard curve using Plotly.

        Returns:
            plotly.graph_objects.Figure: The Nelson-Aalen plot.
        """
        naf = NelsonAalenFitter()
        naf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=naf.cumulative_hazard_.index,
            y=naf.cumulative_hazard_['NA_estimate'],
            mode='lines',
            name='Cumulative Hazard'
        ))

        fig.update_layout(
            title="Cumulative Hazard Function",
            xaxis_title="Trip Duration (Days)",
            yaxis_title="Cumulative Hazard",
            template="plotly_white"
        )
        return fig

    def shrinking_risk(self):
        """
        Compute and plot the shrinking risk over time using Plotly.

        Returns:
            plotly.graph_objects.Figure: The shrinking risk plot.
        """
        kmf = KaplanMeierFitter()
        kmf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])

        shrinking_risk = 1 - kmf.survival_function_['KM_estimate']

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=shrinking_risk.index,
            y=shrinking_risk.values,
            mode='lines',
            name='Shrinking Risk',
            line=dict(color='red')
        ))

        fig.update_layout(
            title="Shrinking Risk Over Time",
            xaxis_title="Trip Duration (Days)",
            yaxis_title="Shrinking Risk (1 - S(t))",
            template="plotly_white"
        )
        return fig

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
