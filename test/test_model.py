import pandas as pd
import plotly.graph_objects as go
from lifelines import WeibullFitter
import numpy as np

# Load the data
df = pd.read_csv("./data/data_model.csv")

#df['IsLost'] = df['IsLost'] -1
#df['IsLost'] = df['IsLost'] * -1

print (df['IsLost'].mean())
print(df.head(5))



def fit_weibull_model(df):
    """
    Fit a Weibull survival model and return the fitted object.
    """
    wf = WeibullFitter()
    wf.fit(df['DayTrip'], event_observed=df['IsLost'])
    return wf

def adjust_weibull_scale(wf, desired_survival, max_duration):
    """
    Adjust the scale parameter of the Weibull model to match a desired survival probability at the maximum duration.

    Parameters:
        wf (WeibullFitter): Fitted Weibull model.
        desired_survival (float): Desired survival probability at the end of the observation period.
        max_duration (float): Maximum duration in the dataset.

    Returns:
        WeibullFitter: Adjusted Weibull model.
    """
    # Adjust the scale parameter using the Weibull survival formula
    adjusted_scale = (-max_duration / (np.log(desired_survival))) ** (1 / wf.rho_)
    wf.lambda_ = adjusted_scale
    return wf

def plot_weibull_survival(wf, adjusted=False):
    """
    Plot the Weibull survival function.

    Parameters:
        wf (WeibullFitter): Fitted Weibull model.
        adjusted (bool): Whether the plot is for the adjusted Weibull model.

    Returns:
        plotly.graph_objects.Figure: Plotly figure of the Weibull survival function.
    """
    survival_function = wf.survival_function_
    survival_function['Weibull_estimate'] = 1- survival_function['Weibull_estimate']
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=survival_function.index,
        y=survival_function['Weibull_estimate'],
        mode='lines',
        name='Adjusted Weibull Survival Function' if adjusted else 'Weibull Survival Function'
    ))
    fig.update_layout(
        title="Adjusted Weibull Survival Curve" if adjusted else "Weibull Survival Curve",
        xaxis_title="Trip Duration (Days)",
        yaxis_title="Survival Probability",
        template="plotly_white"
    )
    return fig

# Fit the Weibull model
model = fit_weibull_model(df)

# Adjust the Weibull scale parameter for the desired survival probability
desired_survival = 0.97
max_duration = df['DayTrip'].max()
adjusted_model = adjust_weibull_scale(model, desired_survival, max_duration)

# Plot the original and adjusted Weibull survival functions
original_fig = plot_weibull_survival(model)
adjusted_fig = plot_weibull_survival(adjusted_model, adjusted=True)

# Show the plots
print("Original Weibull Survival Curve:")
original_fig.show()

print("Adjusted Weibull Survival Curve:")
adjusted_fig.show()


# from lifelines import WeibullFitter

# from lifelines.datasets import load_waltons
# waltons = load_waltons()
# wbf = WeibullFitter()
# wbf.fit(waltons['T'], waltons['E'])
# wbf.plot()
# print(wbf.lambda_)

# print(waltons['T'])
# print(waltons['E'])