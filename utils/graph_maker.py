import plotly.express as px
import plotly.graph_objects as go

def plot_histogram_with_thresholds(series, user_threshold):
    """
    Plots a histogram with two threshold lines using Plotly Express.

    Parameters:
        series (pd.Series): The data to be plotted as a histogram.
        user_threshold (float): The value for the user threshold line.


    Returns:
        plotly.graph_objects.Figure: The Plotly figure with the histogram and thresholds.
    """
    # Create the histogram using Plotly Express
    fig = px.histogram(series, x=series, nbins=30, title="Histogram Of the duration of trips")

    # Add vertical lines for the thresholds

    fig.add_vline(x=user_threshold, line_dash="dash", line_color="red", annotation_text="User Threshold")


    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Values",
        yaxis_title="Frequency",
        template="plotly_white"
    )

    return fig



# new functions



def plot_kaplan_meier(survival_function):
    """
    Plot the Kaplan-Meier survival curve.

    Parameters:
        survival_function (pd.DataFrame): Survival probabilities over time.

    Returns:
        plotly.graph_objects.Figure: The Kaplan-Meier plot.
    """
    if survival_function.empty:
        raise ValueError("The survival function is empty. Cannot plot Kaplan-Meier curve.")
    #print(survival_function)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=survival_function.index,
        y=survival_function['KM_estimate'],
        mode='lines',
        name='Survival Probability'
    ))
    fig.update_layout(
        title="Kaplan-Meier Survival Curve",
        xaxis_title="Trip Duration (Days)",
        yaxis_title="Survival Probability",
        template="plotly_white"
    )
    return fig

def plot_hazard_function(cumulative_hazard):
    """
    Plot the Nelson-Aalen cumulative hazard curve.

    Parameters:
        cumulative_hazard (pd.Series): Cumulative hazard values over time.

    Returns:
        plotly.graph_objects.Figure: The Nelson-Aalen cumulative hazard plot.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cumulative_hazard.index,
        y=cumulative_hazard.values,
        mode='lines',
        name='Cumulative Hazard'
    ))
    fig.update_layout(
        title="Cumulative Hazard Function",
        xaxis_title="Trip Duration (Days)",
        yaxis_title="Cumulative Hazard",
        template="plotly_white"
    )
    return fig

def plot_shrinking_risk(shrinking_risk):
    """
    Plot the shrinking risk over time.

    Parameters:
        shrinking_risk (pd.Series): Shrinking risk values over time.

    Returns:
        plotly.graph_objects.Figure: The shrinking risk plot.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=shrinking_risk.index,
        y=shrinking_risk.values,
        mode='lines',
        name='Shrinking Risk',
        line=dict(color='red')
    ))
    fig.update_layout(
        title="Shrinking Risk Over Time",
        xaxis_title="Trip Duration (Days)",
        yaxis_title="Shrinking Risk (1 - S(t))",
        template="plotly_white"
    )
    return fig



def plot_mapped_survival(mapped_survival, threshold):
    """
    Plot the mapped survival curve with a vertical threshold line.

    Parameters:
        mapped_survival (pd.DataFrame): Adjusted survival probabilities in the new range.
        threshold (float): The threshold value to represent the median of trip duration.

    Returns:
        plotly.graph_objects.Figure: Plot of the mapped survival curve.
    """
    fig = go.Figure()
    
    # Add the survival curve
    fig.add_trace(go.Scatter(
        x=mapped_survival.index,
        y=mapped_survival['KM_estimate'],
        mode='lines',
        name='Mapped Survival Function',
        line=dict(color='blue')
    ))

    # Add a vertical line for the threshold
    fig.add_vline(
        x=threshold,
        line_dash="dash",
        line_color="red",
        annotation_text="Median of Trip Duration",
        annotation_position="top right"
    )

    # Update layout
    fig.update_layout(
        title="Survival Curve, probability for the container not to be lost",
        xaxis_title="Trip Duration (Days)",
        yaxis_title="Survival Probability",
        template="plotly_white"
    )
    
    return fig

def plot_available_containers(df, threshold):
    """
    Plot the remaining number of containers over time with a user-defined vertical threshold.

    Parameters:
        df (pd.DataFrame): DataFrame with two columns:
            - 'Duration': Duration of each trip (time).
            - 'Containers': Number of containers at each time point.
        threshold (float): User-defined time threshold for the vertical line.
    
    Returns:
        plotly.graph_objects.Figure: Plot of remaining containers over time.
    """
    # Plot the remaining containers
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Containers'],
        mode='lines',
        name='Remaining Containers'
    ))

    # Add a vertical line for the threshold
    fig.add_vline(
        x=threshold,
        line_dash="dash",
        line_color="red",
        annotation_text="Threshold",
        annotation_position="top right"
    )

    # Update layout
    fig.update_layout(
        title="Remaining Number of Containers Over Time",
        xaxis_title="Time (Days)",
        yaxis_title="Remaining Containers",
        template="plotly_white"
    )
    return fig