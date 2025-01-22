import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataSimulator:
    """
    Simulates the cyclical trips of containers, recording their starting and recollecting dates, 
    whether they are lost, and calculating the total stock of non-lost containers.
    """

    def __init__(self, num_containers, days, min_recollect_offset, max_trip_days, recollecting_rate =0.1,start_date = "2023-01-01"):
        """
        Initializes the simulation parameters.

        Args:
            num_containers (int): Number of containers to simulate.
            days (int): Number of days to simulate from the start date.
            min_recollect_offset (int): Minimum days after starting date to allow recollection.
            max_trip_days (int): Maximum days for a container to be considered not lost.
            recollecting_rate (float): Probability of recovering a container in each day within the allowed time span ( from the start_date + min_recollect_offset to start_date + max_trip_days)
            start_date (str): Default start date value for simulated data.
        """
        self.num_containers = num_containers
        self.days = days
        self.min_recollect_offset = min_recollect_offset
        self.max_trip_days = max_trip_days
        self.recollecting_rate = recollecting_rate 
        self.start_date = start_date

    def simulate_container_data(self):
        """
        Simulates the container data and returns it as a DataFrame.

        Returns:
            pd.DataFrame: Simulated container data including container ID, actual date,
                          starting date, recollecting date, lost status, and total stock.
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

            for actual_date in actual_dates:
                if starting_date is None:  # Start a new trip
                    if np.random.rand() > 0.7:  # 1- [VALUE] is the probability of starting a new trip
                        starting_date = actual_date
                else:
                    if recollecting_date is None:  # Check for a recollecting date within the allowed window
                        if actual_date >= starting_date + timedelta(days=self.min_recollect_offset):
                            if actual_date <= starting_date + timedelta(days=self.max_trip_days):
                                if np.random.rand() < self.recollecting_rate:
                                    recollecting_date = actual_date
                                    is_lost = 0
                            else:  # If max_trip_days passed without recollection, mark as lost
                                is_lost = 1

                # Append current day's record
                data.append({
                    "Container ID": container_id,
                    "Actual Date": actual_date,
                    "Starting Date": starting_date,
                    "Recollecting Date": recollecting_date,
                    "Lost": is_lost
                })

                if recollecting_date:  # Reset for the next trip after recollection
                    starting_date = None
                    recollecting_date = None
                    is_lost = 0

        # Create a DataFrame
        df = pd.DataFrame(data)

        # Add Total Stock column
        df["Total Stock"] = df.groupby("Actual Date")["Lost"].transform(lambda x: (x == 0).sum())

        return df

# Example usage:
# if __name__ == "__main__":
#     simulator = DataSimulator(
#         num_containers=1000,
#         days=100,
#         min_recollect_offset=15,
#         max_trip_days=40,
#         recollecting_rate= 0.1
#     )
#     df = simulator.simulate_container_data()
#     df.to_excel("./data/survival_data.xlsx", index=False)
    #df.to_csv("./data/survival_data.csv", index=False)


#

