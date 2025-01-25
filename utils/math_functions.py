from scipy.stats import expon
from scipy.stats import lognorm
import numpy as np
import pandas as pd



def get_lognorm_distribution(mean= 3.5 , sigma = 0.3 ):

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
    #print (x)

    pdf_values = log_normal_dist.pdf(x)
    cdf_values = log_normal_dist.cdf(x)

    # Create a DataFrame for Plotly Express
    data = pd.DataFrame({
        "Duration": x,
        "PDF": pdf_values,
        "CDF": cdf_values
    })
    return data

def get_lognorm_PDF(df, duration, scaling_factor = 5):
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


def calculate_upper_bound(series , k = 3):
    """
    Calculates the upper bound for detecting outliers using the Interquartile Range (IQR).
    Used because it is a robust measure.
    the k parameter it's setted to 3 instead of the default Tukey value 1,5 beacuse of the skewness of the log normal distribution

    Parameters:
        data (pd.DataFrame): The input DataFrame.
        column (str): The column name to calculate the upper bound.

    Returns:
        float: The upper bound for detecting outliers.
    """
    # Calculate Q1 and Q3
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)

    # Calculate IQR
    IQR = Q3 - Q1

    # Calculate the upper bound
    upper_bound = Q3 + k * IQR

    return round(upper_bound)


def calculate_adjusted_params(perc_trips_observed, mu, sigma):
    """
    Calculate the adjusted mean (mu') and standard deviation (sigma')
    for a log-normal distribution based on the percentage of observed trips,
    ensuring the mean of the distribution adjusts dynamically.

    Parameters:
        perc_trips_observed (float): Percentage of observed trips (0 < perc_trips_observed <= 1).
        mu (float): Original mean of the natural logarithm of the distribution.
        sigma (float): Original standard deviation of the natural logarithm of the distribution.

    Returns:
        tuple: Adjusted mean (mu'), adjusted standard deviation (sigma').
    """
    if perc_trips_observed <= 0 or perc_trips_observed > 1:
        raise ValueError("perc_trips_observed must be in the range (0, 1].")

    # Calculate the current mean of the log-normal distribution
    current_mean = np.exp(mu + (sigma**2) / 2)

    # Target mean: If perc_trips_observed < 1, the mean should scale accordingly
    target_mean = current_mean / perc_trips_observed

    # Adjust the mean (mu') to achieve the target mean
    adjusted_mu = np.log(target_mean) - (sigma**2) / 2

    # Adjust the standard deviation (sigma') to slightly increase variability
    if perc_trips_observed < 1:
        adjustment_factor = np.log(1 / perc_trips_observed)  # Scales with reduced observation
        adjusted_sigma = sigma + 0.1 * adjustment_factor  # Increase dispersion slightly
    else:
        adjusted_sigma = sigma

    return adjusted_mu, adjusted_sigma


