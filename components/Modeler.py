import pandas as pd
from lifelines import KaplanMeierFitter


class Modeler:
    def __init__(self, df, prob_in_trip):
        """
        Initialize the Modeler class with a DataFrame.

        Parameters:
            df (pd.DataFrame): The input DataFrame, which must contain:
                - 'DayTrip': Duration of each trip.
                - 'IsLost': 1 if the container was lost, 0 otherwise.
                - 'UniqueTripID': A unique identifier for each trip.
            prob_in_trip (float): The probability of a container being in a trip.
        """
        self.original_df = df
        self.df = self.prepare_data_for_analysis()
        self.prob_in_trip = prob_in_trip
        self.pecentage_not_lost_t_max =  1 - self.df['IsLost'].mean()
        self.median_trip_time = self.df['DayTrip'].median()
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
        return aggregated.dropna(subset=["DayTrip", "IsLost"]).reset_index(drop=True)

    def kaplan_meier_fitter(self):
        """
        Fit the Kaplan-Meier model and return the fitter object.

        Returns:
            KaplanMeierFitter: Fitted Kaplan-Meier model.
        """
        kmf = KaplanMeierFitter()
        kmf.fit(self.df['DayTrip'], event_observed=self.df['IsLost'])
        return kmf
    
    def get_km_estimate_at_timeline(self, survival_function):
        """
        Get the KM estimate at a specific timeline.

        Parameters:
            survival_function (pd.DataFrame): The survival function DataFrame from Kaplan-Meier fitting.
            self.median_trip_time (float): The specific time point to extract the KM estimate.

        Returns:
            float: The survival probability (KM estimate) at the given timeline.
        """
        print(self.median_trip_time)
        print(survival_function)
        if self.median_trip_time in survival_function.index:
            return survival_function.loc[self.median_trip_time , 'KM_estimate']
        else:
            raise ValueError(f"Timeline {self.median_trip_time } not found in the survival function index.")
        

    def get_km_estimate_at_specific_timeline(self, timeline, survival_function):
        """
        Get the KM estimate at a specific timeline.

        Parameters:
            survival_function (pd.DataFrame): The survival function DataFrame from Kaplan-Meier fitting.
            self.median_trip_time (float): The specific time point to extract the KM estimate.

        Returns:
            float: The survival probability (KM estimate) at the given timeline.
        """

        if timeline in survival_function.index:
            return survival_function.loc[timeline , 'KM_estimate']
        else:
            raise ValueError(f"Timeline {timeline} not found in the survival function index.")
        
    

    def mapped_survival_function(self):
        """
        Map the Kaplan-Meier survival probabilities to a range [1, desired_survival].

        Parameters:
            self.pecentage_lost_t_max represent the desired_survival (float): Desired survival probability at the end of the interval.

        Returns:
            pd.DataFrame: Adjusted survival function in the new range.
        """
        kmf = self.kaplan_meier_fitter()
        survival_function = kmf.survival_function_

        min_value = survival_function.min()
        max_value = survival_function.max()

        mapped_survival = (survival_function - min_value) / (max_value - min_value)
        #print( self.pecentage_not_lost_t_max )
        mapped_survival = self.pecentage_not_lost_t_max + mapped_survival * (1 - self.pecentage_not_lost_t_max)

        print ( mapped_survival )

        return mapped_survival

    def calculate_available_containers(self, initial_containers):
        """
        Calculate the number of available containers over time.

        Parameters:
            initial_containers (int): The initial number of containers.

        Returns:
            pd.Series: Number of available containers over time.
        """
        kmf = self.kaplan_meier_fitter()
        survival_prob = kmf.survival_function_['KM_estimate']
        return initial_containers * self.prob_in_trip * survival_prob

    def shrinking_rate_at_median(self):
        """
        Calculate the shrinking risk (probability of being lost) at the median trip duration.

        Returns:
            float: Shrinking risk at the median trip duration.
        """
        kmf = self.kaplan_meier_fitter()

        # Median trip duration
        median_duration = self.df['DayTrip'].median()

        # Risk of loss at the median duration
        shrinking_risk = 1 - kmf.survival_function_.loc[median_duration, 'KM_estimate']
        return shrinking_risk
