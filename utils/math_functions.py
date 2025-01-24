from scipy.stats import expon
from scipy.stats import lognorm
import numpy as np
import pandas as pd

# Example: Calculate the threshold to isolate the top 5% (95th percentile)
def calculate_exponential_threshold( data, confidence=0.95):
        """
        Calculates the threshold for isolating the top (1 - confidence) cases
        assuming an exponential distribution.

        Args:
            data (pd.Series): The data (e.g., DayTrip values) to analyze.
            confidence (float): The desired confidence level (default is 0.95).

        Returns:
            float: The calculated threshold.
        """
        mean_value = data.mean()  # Calculate the mean of the data
        threshold = expon.ppf(confidence, scale=mean_value)  # Compute the threshold
        return threshold



def get_lognorm_distribution(mean= 3.5 , sigma = 0.35 ):

    """
    Function that return the lognorm distrinution parameters
    used to model the recollecting probability
    """

    # Calculate scale (scale = exp(mean) for a log-normal distribution)
    scale = np.exp(mean)

    # Define the log-normal distribution
    log_normal_dist = lognorm(s=sigma, scale=scale)

    # List of duration values greater than the threshold
    x = np.linspace(1, 300, 300) 
    print (x)

    pdf_values = log_normal_dist.pdf(x)
    cdf_values = log_normal_dist.cdf(x)

    # Create a DataFrame for Plotly Express
    data = pd.DataFrame({
        "Duration": x,
        "PDF": pdf_values,
        "CDF": cdf_values
    })
    return data

def get_lognorm_PDF(df, duration, scaling_factor = 10):
    """
    Returns the Probability Density Function (PDF) value for a given duration by looking up a DataFrame.
    If the duration does not exist in the DataFrame, it finds the closest duration value.

    Parameters:
        df (pd.DataFrame): DataFrame containing "Duration" and "PDF" columns.
        duration (float): The duration value for which the PDF is required.

    Returns:
        float: The PDF value for the given duration.
    """
    # Ensure "Duration" and "PDF" columns exist
    if "Duration" not in df.columns or "PDF" not in df.columns:
        raise ValueError("The DataFrame must contain 'Duration' and 'PDF' columns.")
    
    # Find the row with the closest Duration value
    closest_row = df.iloc[(df["Duration"] - duration).abs().idxmin()]
    
    # Return the PDF value from the closest row
    return closest_row["PDF"] * scaling_factor
    

#dist = get_lognorm_distribution()
#res = get_lognorm_PDF(dist,0)
#print (res)