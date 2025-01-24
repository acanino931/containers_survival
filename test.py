import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import lognorm

# Parameters
threshold = 1  # Initial threshold (minimum duration)
sigma = 0.35   # Shape parameter (std deviation of the log-normal distribution)
mean = 3.5      # Mean of the underlying normal distribution

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


data_melted_pdf["Probability"] = data_melted_pdf["Probability"] * 10
# Create the Plotly Express figure
fig_pdf = px.line(
    data_melted_pdf,
    x="Duration",
    y="Probability",
    color="Type",
    title="Log-Normal Distribution (PDF and CDF)",
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
    title="Log-Normal Distribution (PDF and CDF)",
    labels={"Probability": "Probability", "Duration": "Duration"}
)

# Add a vertical line for the threshold
fig_cdf.add_vline(x=threshold, line_dash="dot", line_color="red", annotation_text="Threshold")

# Display the chart in Streamlit
fig_cdf.show()