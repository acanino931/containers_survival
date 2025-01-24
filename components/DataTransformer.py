import pandas as pd
import numpy as np
from utils import math_functions

class DataTransformer:
    """
    A class to perform data transformation tasks on a given DataFrame.
    """

    def __init__(self, dataframe):
        """
        Initializes the DataTransformer with a DataFrame.

        Args:
            dataframe (pd.DataFrame): The input DataFrame to perform transformations on.
        """
        self.df = dataframe
        self.model_data = None  # Property to store prepared data for Kaplan-Meier estimation


    def get_dataframe(self):
        """
        Returns the transformed DataFrame.

        Returns:
            pd.DataFrame: The transformed DataFrame.
        """
        return self.df

    def reassign_lost_value(self):
            """
            Reassigns the value of the 'Lost' column to 0 if 'Lost' == 1 and 'Is Fake Lost' == 1.
            Uses numpy's where function for efficient row-wise operation.
            """
            df = self.df.copy()
            df["isLost"] = np.where((self.df["isLost"] == 1) & (self.df["IsFakeLost"] == 1), 0, self.df["isLost"])

            return df

    
    def create_summary_table(self):
        """
        Creates a summary table with the average percentage of days containers are in a trip,
        the percentage of incorrectly classified lost days, and additional metrics.

        Returns:
            pd.DataFrame: A summary DataFrame with KPIs.
        """
        # Calculate the percentage of rows where StartingDate is not null
        total_rows = len(self.df)
        days_in_trip = self.df["StartingDate"].notnull().sum()
        average_days_in_SC = days_in_trip / total_rows

        # Calculate the percentage of incorrectly classified lost days
        total_lost = self.df["isLost"].sum()
        fake_lost = self.df["IsFakeLost"].sum()
        percentage_fake_lost = fake_lost / total_lost if total_lost > 0 else 0

        # Group by ContainerID and TripID and calculate metrics
        groupby_trip = self.df[self.df["RecollectingDate"].notnull()].groupby(["ContainerID", "TripID"])
        day_trip_max = groupby_trip["DayTrip"].max()
        print (f"type day_trip_max:{type(day_trip_max)}")
        print (f"type day_trip_max:{day_trip_max}")

        # Calculate average and variance of DayTrip
        avg_days_trip_not_lost = day_trip_max.mean()
        var_days_trip_not_lost = day_trip_max.var()

        # Calculate the exponential threshold
        threshold = math_functions.calculate_exponential_threshold(day_trip_max)

        # Create summary table with KPIs
        summary = pd.DataFrame({
            "Average Days in SC": [average_days_in_SC],
            "Percentage Fake Lost": [percentage_fake_lost],
            "Average Days in Trip (Not Lost)": [avg_days_trip_not_lost],
            "Variance of Days in Trip (Not Lost)": [var_days_trip_not_lost],
            "Exponential Threshold": [threshold]
        })

        return summary
    
    def prepare_data_for_kaplan_meier(self):
        model_df =  self.reassign_lost_value()
        # selecting just the rows where the containers are in a trip
        model_df = model_df[model_df["StartingDate"].notnull()].copy()
        # selecting just the column needed
        model_df = model_df[["ContainerID", "ActualDate", "isLost","TripID"]].copy()

        self.model_data = model_df

    

if __name__ == "__main__":
    # Sample DataFrame
    df = pd.read_excel("./data/survival_data.xlsx")

    # Initialize the DataTransformer
    transformer = DataTransformer(df)

    # Reassign lost values
    #transformer.reassign_lost_value()

    # Create summary table
    summary_table = transformer.create_summary_table()

    # Display the transformed DataFrame
    #print("Transformed DataFrame:")
    #print(transformer.get_dataframe())

    print("\nSummary Table:")
    print(summary_table)