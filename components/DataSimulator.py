import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataSimulator:
    """
    Simulates the cyclical trips of containers, recording their starting and recollecting dates, 
    whether they are lost, and calculating the total stock of non-lost containers.
    """

    def __init__(self, num_containers, days, min_recollect_offset, max_trip_days, recollecting_rate=0.1, start_date="2023-01-01"):
        """
        Initializes the simulation parameters.

        Args:
            num_containers (int): Number of containers to simulate.
            days (int): Number of days to simulate from the start date.
            min_recollect_offset (int): Minimum days after starting date to allow recollection.
            max_trip_days (int): Maximum days for a container to be considered not lost.
            recollecting_rate (float): Probability of recovering a container in each day within the allowed time span (from the start_date + min_recollect_offset to start_date + max_trip_days).
            start_date (str): Default start date value for simulated data.
        """
        self.num_containers = num_containers
        self.days = days
        self.min_recollect_offset = min_recollect_offset
        self.max_trip_days = max_trip_days
        self.recollecting_rate = recollecting_rate
        self.start_date = start_date

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
        fake_lost_trips = df[(df["RecollectingDate"].notnull()) & (df["isLost"] == 1)][["ContainerID", "TripID"]].drop_duplicates()

        # Iterate through each misclassified trip
        for _, row in fake_lost_trips.iterrows():
            container_id = row["ContainerID"]
            trip_number = row["TripID"]

            # Update Is Fake Lost for all rows in the same trip but ensure only Lost rows are updated
            df.loc[(df["ContainerID"] == container_id) & (df["TripID"] == trip_number) & (df["isLost"] == 1), "IsFakeLost"] = 1

        return df

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
                        if actual_date >= starting_date + timedelta(days=self.min_recollect_offset):
                            if actual_date <= starting_date + timedelta(days=self.max_trip_days):
                                if np.random.rand() < self.recollecting_rate:
                                    recollecting_date = actual_date
                                    is_lost = 0
                                    # Ensure the final values are written on the row with the recollecting date
                                    data.append({
                                        "ContainerID": container_id,
                                        "ActualDate": actual_date,
                                        "StartingDate": starting_date,
                                        "RecollectingDate": recollecting_date,
                                        "isLost": is_lost,
                                        "DayTrip": day_trip,
                                        "TripID": trip_number,
                                        "IsFakeLost": 0  # Will be updated later if needed
                                    })
                                    starting_date = None
                                    recollecting_date = None
                                    is_lost = 0
                                    day_trip = None
                                    trip_number = None
                                    continue
                            else:  # After max_trip_days, allow recollecting but keep is_lost = 1
                                if np.random.rand() < self.recollecting_rate/10:
                                    recollecting_date = actual_date
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
                    "isLost": is_lost,
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

        # Add Total Stock column
        df["TotalStock"] = df.groupby("ActualDate")["isLost"].transform(lambda x: (x == 0).sum())

        # Update Is Fake Lost values
        df = self.update_fake_lost(df)

        return df
    


if __name__ == "__main__":
    simulator = DataSimulator(
        num_containers=1000,
        days=100,
        min_recollect_offset=15,
        max_trip_days=40,
        recollecting_rate= 0.1
    )
    df = simulator.simulate_container_data()
    df.to_excel("./data/survival_data.xlsx", index=False)
    #df.to_csv("./data/survival_data.csv", index=False)


#

