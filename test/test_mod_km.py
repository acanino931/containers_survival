import pandas as pd
import plotly.graph_objects as go
from lifelines import KaplanMeierFitter

def fit_kaplan_meier(df):
    """
    Fit a Kaplan-Meier survival model and return the survival probabilities.
    """
    kmf = KaplanMeierFitter()
    kmf.fit(df['DayTrip'], event_observed=df['IsLost'])
    return kmf.survival_function_

def map_survival_to_custom_range(survival_function, desired_survival):
    """
    Map the survival probabilities to a custom range [1, desired_survival].

    Parameters:
        survival_function (pd.Series): Original survival probabilities.
        desired_survival (float): Desired survival probability at the end of the interval.

    Returns:
        pd.Series: Adjusted survival probabilities in the new range.
    """
    min_value = survival_function.min()  # Smallest survival probability in the original range
    max_value = survival_function.max()  # Largest survival probability in the original range (usually 1)

    # Scale and shift the survival function to fit the range [1, desired_survival]
    mapped_survival = (survival_function - min_value) / (max_value - min_value)  # Normalize to [0, 1]
    mapped_survival = desired_survival + mapped_survival * (1 - desired_survival)  # Map to [1, desired_survival]

    return mapped_survival

def plot_mapped_survival(mapped_survival):
    """
    Plot the mapped survival curve.

    Parameters:
        mapped_survival (pd.Series): Mapped survival probabilities.

    Returns:
        plotly.graph_objects.Figure: Plot of the mapped survival curve.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mapped_survival.index,
        y=mapped_survival['KM_estimate'],
        mode='lines',
        name='Survival Curve function',
        line=dict(color='blue')
    ))
    fig.update_layout(
        title="Survival Curve ",
        xaxis_title="Trip Duration (Days)",
        yaxis_title="Survival Probability",
        template="plotly_white"
    )
    return fig

# Load the data
df = pd.read_csv("./data/data_model.csv")

# Fit the Kaplan-Meier survival function
original_survival = fit_kaplan_meier(df)

# Map the survival probabilities to a custom range
desired_survival = 0.97  # Desired survival probability at the end of the interval
mapped_survival = map_survival_to_custom_range(original_survival, desired_survival)

# Plot only the mapped survival curve
fig = plot_mapped_survival(mapped_survival)
fig.show()
