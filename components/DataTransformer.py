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
            This operation is made to correct the misclassification of lost containers.
            """
            df = self.df.copy()
            print(df.columns)
            df["isLost"] = np.where((self.df["isLost"] == 1) & (self.df["IsFakeLost"] == 1), 0, self.df["isLost"])

            return df

    
    def create_summary_table(self):
        """
        Creates a summary table with the average percentage of days containers are in a trip,
        the percentage of incorrectly classified lost days, and additional metrics.

        Returns:
            pd.DataFrame: A summary DataFrame with KPIs.
            pd.series: The distribution of days in trip for all the trips
        """
        # Calculate the percentage of rows where StartingDate is not null
        total_rows = len(self.df)
        days_in_trip = self.df["StartingDate"].notnull().sum()
        perc_days_in_trip = days_in_trip / total_rows

        # Calculate the percentage of incorrectly classified lost days
        total_lost = self.df["isLost"].sum()
        fake_lost = self.df["IsFakeLost"].sum()
        percentage_fake_lost = fake_lost / total_lost if total_lost > 0 else 0

        # Group by ContainerID and TripID and calculate metrics
        groupby_trip_not_lost = self.df[self.df["RecollectingDate"].notnull()].groupby(["ContainerID", "TripID"])
        day_trip_max_not_lost = groupby_trip_not_lost["DayTrip"].max()


        groupby_trip_all = self.df.groupby(["ContainerID", "TripID"])
        day_trip_all = groupby_trip_all["DayTrip"].max()


        print (f"type day_trip_max:{type(day_trip_max_not_lost)}")
        print (f"type day_trip_max:{day_trip_max_not_lost}")
        #day_trip_all.to_excel("./data/day_trip_max.xlsx", index=False)
        threshold = math_functions.calculate_upper_bound(day_trip_all)

        # Calculate average and variance of DayTrip
        avg_days_trip_not_lost = day_trip_max_not_lost.mean()
        var_days_trip_not_lost = day_trip_max_not_lost.var()

        # Calculate the exponential threshold
        #threshold = math_functions.calculate_exponential_threshold(day_trip_max)

        # Create summary table with KPIs
        summary = pd.DataFrame({
            "Percentage Days in Trip": [perc_days_in_trip],
            "Percentage Fake Lost": [percentage_fake_lost],
            "Average Days in Trip (Not Lost)": [avg_days_trip_not_lost],
            "Variance of Days in Trip (Not Lost)": [var_days_trip_not_lost],
            "Recommended Threshold": [threshold]
        })

        return summary , day_trip_all
    
    def prepare_data_for_kaplan_meier(self):
        # reassign the missclassified lost values in order to have clean data for the training.
        data = self.reassign_lost_value()
        # creating a unique id that consider the event trip:
    
        data["UniqueTripID"] = data["ContainerID"].astype(str) + "_" + data["TripID"].astype(str)
        # eliminating all the row when the container is not exposed to risks
        data = data[data["StartingDate"].notnull()]

        groupby_trip_all = data.groupby(["UniqueTripID"])

        # Calculate the maximum DayTrip for each group
        day_trip_all = groupby_trip_all["DayTrip"].max()

        # Include the IsLost column by aggregating with max (1 = lost, 0 = not lost)
        is_lost_all = groupby_trip_all["IsLost"].max()

        # Combine into a single DataFrame
        result = pd.DataFrame({
            "DayTrip": day_trip_all,
            "IsLost": is_lost_all
        }).reset_index()

        #self.model_data = result
        result.to_excel("./data/model_data.xlsx", index=False)

        return result
    

    

# if __name__ == "__main__":
#     # Sample DataFrame
#     df = pd.read_excel("./data/survival_data.xlsx")

#     # Initialize the DataTransformer
#     transformer = DataTransformer(df)

#     # Reassign lost values
#     #transformer.reassign_lost_value()

#     # Create summary table
#     summary_table = transformer.create_summary_table()

#     # Display the transformed DataFrame
#     #print("Transformed DataFrame:")
#     #print(transformer.get_dataframe())

#     print("\nSummary Table:")
#     print(summary_table)