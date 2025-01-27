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
            df["IsLost"] = np.where((self.df["IsLost"] == 1) & (self.df["IsFakeLost"] == 1), 0, self.df["IsLost"])

            return df

    
    def create_summary_table(self, dictionary_metrics):
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


        # Group by ContainerID and TripID and calculate metrics
        #groupby_trip_not_lost = self.df[self.df["RecollectingDate"].notnull()].groupby(["ContainerID", "TripID"])
        #day_trip_max_not_lost = groupby_trip_not_lost["DayTrip"].max()



        groupby_trip_all = self.df.groupby(["ContainerID", "TripID"])
        day_trip_all = groupby_trip_all["DayTrip"].max()


        #median_trip = groupby_trip_all["DayTrip"].median().reset_index(name="Median")
        median_trip = day_trip_all.median()
        
        #percentile_25 = groupby_trip_all["DayTrip"].quantile(0.25).reset_index(name="Percentile_25")
        #percentile_75 = groupby_trip_all["DayTrip"].quantile(0.75).reset_index(name="Percentile_75")


        # Calculate average and variance of DayTrip
        avg_days_trip = day_trip_all.mean()
        var_days_trip = day_trip_all.var()

        # Calculate the exponential threshold
        #threshold = math_functions.calculate_exponential_threshold(day_trip_max)


        summary = pd.DataFrame({
            "Percentage Days in Trip": [perc_days_in_trip],
            "Trip Precision user treshold":dictionary_metrics.get("precision_treshold"),
            "Median trip duration":median_trip,
            "Average trip duration": [avg_days_trip],
            "Variance trip duration": [var_days_trip],
        })

        return summary , day_trip_all
    

        #self.model_data = result
        #result.to_excel("./data/model_data.xlsx", index=False)

        #return result
    

    

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