import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import lognorm

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

adjusted_mu ,adjusted_sigma =  calculate_adjusted_params(mu = 3, sigma = 0.3, perc_trips_observed = 0.5) # , k_mu = 1, k_sigma = 0.2

print(adjusted_mu,adjusted_sigma)
# Parameters
threshold = 1  # Initial threshold (minimum duration)
mean = adjusted_mu #4      # Mean of the underlying normal distribution
sigma = adjusted_sigma #0.35   # Shape parameter (std deviation of the log-normal distribution) 


# Calculate scale (scale = exp(mean) for a log-normal distribution)
scale = np.exp(mean)

# Define the log-normal distribution
log_normal_dist = lognorm(s=sigma, scale=scale)

# List of duration values greater than the threshold
x = np.linspace(1, 80, 80) 

pdf_values = log_normal_dist.pdf(x)
cdf_values = log_normal_dist.cdf(x)

# Create a DataFrame for Plotly Express
data = pd.DataFrame({
    "Duration": x,
    "PDF": pdf_values,
    "CDF": cdf_values
})

# Melt the data for easier plotting with Plotly Express
data_melted = data.melt(id_vars="Duration", var_name="Type", value_name="Probability")
#print (data_melted)

data_melted_pdf = data_melted[data_melted["Type"] == "PDF"]

data_melted_cdf = data_melted[data_melted["Type"] == "CDF"]


data_melted_pdf["Probability"] = data_melted_pdf["Probability"] * 5
# Create the Plotly Express figure
fig_pdf = px.line(
    data_melted_pdf,
    x="Duration",
    y="Probability",
    color="Type",
    title="Log-Normal Distribution PDF (Probability Density Function )",
    labels={"Probability": "Probability", "Duration": "Duration"}
)

# Add a vertical line for the threshold
fig_pdf.add_vline(x=threshold, line_dash="dot", line_color="red", annotation_text="Threshold")

# Display the chart in Streamlit
fig_pdf.show()


# Create the Plotly Express figure
fig_cdf = px.line(
    data_melted_cdf,
    x="Duration",
    y="Probability",
    color="Type",
    title=f"Log-Normal Distribution PDF ",
    labels={"Probability": "Probability", "Duration": "Duration"}
)

# Add a vertical line for the threshold
fig_cdf.add_vline(x=threshold, line_dash="dot", line_color="red", annotation_text="Threshold")

# Display the chart in Streamlit
fig_cdf.show()