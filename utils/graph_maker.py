import plotly.express as px
import plotly.graph_objects as go

def plot_histogram_with_thresholds(series, user_threshold, recommended_threshold):
    """
    Plots a histogram with two threshold lines using Plotly Express.

    Parameters:
        series (pd.Series): The data to be plotted as a histogram.
        user_threshold (float): The value for the user threshold line.
        recommended_threshold (float): The value for the recommended_threshold threshold line.

    Returns:
        plotly.graph_objects.Figure: The Plotly figure with the histogram and thresholds.
    """
    # Create the histogram using Plotly Express
    fig = px.histogram(series, x=series, nbins=30, title="Histogram Of the duration of trips")

    # Add vertical lines for the thresholds
    if user_threshold != recommended_threshold:
        fig.add_vline(x=user_threshold, line_dash="dash", line_color="red", annotation_text="User Threshold")
        fig.add_vline(x=recommended_threshold, line_dash="dash", line_color="blue", annotation_text="Recommended Threshold")
    else: 
        fig.add_vline(x=recommended_threshold, line_dash="dash", line_color="blue", annotation_text="Recommended Threshold")

    # Update layout for better visualization
    fig.update_layout(
        xaxis_title="Values",
        yaxis_title="Frequency",
        template="plotly_white"
    )

    return fig