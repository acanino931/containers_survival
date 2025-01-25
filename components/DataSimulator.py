import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils import math_functions

class DataSimulator:
    """
    Simulates the cyclical trips of containers, recording their starting and recollecting dates, 
    whether they are lost, and calculating the total stock of non-lost containers.
    """

    def __init__(self, num_containers, days, max_trip_days, scenario = 1, start_date="2023-01-01"):
        """
        Initializes the simulation parameters.

        Args:
            num_containers (int): Number of containers to simulate.
            days (int): Number of days to simulate from the start date.
            max_trip_days (int): Maximum days for a container to be considered not lost.
            start_date (str): Default start date value for simulated data.
        """
        self.num_containers = num_containers
        self.days = days
        self.max_trip_days = max_trip_days
        self.start_date = start_date
        self.scenario = scenario
        self.eval_metrics = None

    def update_fake_lost(self, df):
        """
        Updates the Is Fake Lost column to mark rows in the same trip as fake lost
        if a recollecting date appears after the expected time span and the trip was marked lost.

        Args:
            df (pd.DataFrame): The DataFrame containing simulated container data.

        Returns:
            pd.DataFrame: Updated DataFrame with Is Fake Lost values.
        """
        # Filter rows where recollecting date appears after max_trip_days
        fake_lost_trips = df[(df["RecollectingDate"].notnull()) & (df["IsLost"] == 1)][["ContainerID", "TripID"]].drop_duplicates()

        # Iterate through each misclassified trip
        for _, row in fake_lost_trips.iterrows():
            container_id = row["ContainerID"]
            trip_number = row["TripID"]

            # Update Is Fake Lost for all rows in the same trip but ensure only Lost rows are updated
            df.loc[(df["ContainerID"] == container_id) & (df["TripID"] == trip_number) & (df["IsLost"] == 1), "IsFakeLost"] = 1
        return df

    def reassign_lost_value(self, df):
        """
        Reassigns the value of the 'Lost' column to 0 if 'Lost' == 1 and 'Is Fake Lost' == 1.
        This operation is made to correct the misclassification of lost containers.
        """
        df["IsLost"] = np.where((df["IsLost"] == 1) & (df["IsFakeLost"] == 1), 0, df["IsLost"])

        return df
    
    def calculate_fake_lost_percentage(self,df):
        """
        Calculates the percentage of fake lost containers in the DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame containing simulated container data.

        Returns:
            float: The percentage of fake lost containers.
        """
        data = df.copy()
        #print(data.columns)
                # Calculate the percentage of incorrectly classified lost days
        data["UniqueTripID"] = data["ContainerID"].astype(str) + "_" + data["TripID"].astype(str)

        groupby_trip_lost_df = data[data["IsLost"] == 1][["UniqueTripID", "IsFakeLost"]]
        #precision_treshold = groupby_trip_lost_df["IsFakeLost"].mean()

        tp = len(groupby_trip_lost_df[groupby_trip_lost_df["IsFakeLost"] == 0])
        fp = len(groupby_trip_lost_df[groupby_trip_lost_df["IsFakeLost"] == 1])

        # we cannot directly observe the false negative cause we don't know the exact moment of losing the container we assume this value to be 0
        fn = 0

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0

        # Recall
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        # F1 Score
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        # Exporting just the Presicion and the F1 score, most important metrics for an unbalanced classification case as this.


        self.eval_metrics = {
            "precision_treshold": precision, 
            "F1_Score_threshold": f1_score
        }


    def simulate_container_data(self):
        """
        Simulates the container data and returns it as a DataFrame.

        Returns:
            pd.DataFrame: Simulated container data including container ID, actual date,
                          starting date, recollecting date, lost status, total stock, day trip, trip number, and fake lost flag.
        """
        # Define the starting date for the simulation
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        actual_dates = [start_date + timedelta(days=i) for i in range(self.days)]
        np.random.seed(42)
        # for the main scenario we are using the default parameters of the log normal
        # distribution in order to model the recollecting probability.
        if self.scenario == 1:
            log_norm_dist =    math_functions.get_lognorm_distribution()
        else:
            # TODO modify the lognorm distribution params fro scenario 2 
            pass
        


        # Initialize the dataframe
        data = []

        for container_id in range(1, self.num_containers + 1):
            starting_date = None
            recollecting_date = None
            is_lost = 0
            day_trip = None
            trip_number = None
            current_trip = 0

            for actual_date in actual_dates:
                if starting_date is None:  # Start a new trip
                    if np.random.rand() > 0.7:  # 1- [VALUE] is the probability of starting a new trip
                        starting_date = actual_date
                        day_trip = 1
                        current_trip += 1
                        trip_number = current_trip
                        is_lost = 0  # Reset lost status on a new trip
                    else:
                        day_trip = None
                        trip_number = None
                else:
                    if recollecting_date is None:  # Check for a recollecting date
                        #print(f"get_lognorm_PDF : {math_functions.get_lognorm_PDF(log_norm_dist, day_trip)}")
                        
                        if np.random.rand() < math_functions.get_lognorm_PDF(log_norm_dist, day_trip, scaling_factor = 5 ):
                            #print("recollection")
                            recollecting_date = actual_date

                        else:
                            
                            if actual_date > starting_date + timedelta(days=self.max_trip_days):
                                is_lost = 1  # Mark as lost after max_trip_days if not recollected

                        if day_trip is not None:
                            day_trip += 1  # Increment day_trip for each day in trip

                # Append current day's record
                data.append({
                    "ContainerID": container_id,
                    "ActualDate": actual_date,
                    "StartingDate": starting_date,
                    "RecollectingDate": recollecting_date,
                    "IsLost": is_lost,
                    "DayTrip": day_trip,
                    "TripID": trip_number,
                    "IsFakeLost": 0  # Default value, to be updated later
                })

                if recollecting_date:  # Reset for the next trip after recollection
                    starting_date = None
                    recollecting_date = None
                    is_lost = 0
                    day_trip = None
                    trip_number = None

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Update Is Fake Lost values to correctly calculate the field 
        df = self.update_fake_lost(df)

        # extraction of a KPI tod control the fake positive generated with the chosen threshold
        self.calculate_fake_lost_percentage(df)


        # cleaning the data in order to reassign the lost values of the misclassified days
        df = self.reassign_lost_value( df)

        # Add Total Stock column calculated over the cleaned data.
        df["TotalStock"] = df.groupby("ActualDate")["IsLost"].transform(lambda x: (x == 0).sum())

        return df
    


if __name__ == "__main__":
    simulator = DataSimulator(
        num_containers=1000,
        days=100,
        max_trip_days=40,
    )
    df = simulator.simulate_container_data()
    df.to_excel("./data/survival_data.xlsx", index=False)
    #df.to_csv("./data/survival_data.csv", index=False)


#

