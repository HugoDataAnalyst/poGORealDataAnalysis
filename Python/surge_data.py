#Import necessary libraries
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import ipywidgets as widgets
from ipywidgets import interactive, Layout, Output
from IPython.display import display, clear_output
from datetime import datetime

#Load the dataset
#surge_df = pd.read_csv('../CSV/Surge/SurgeGlobaliv100LF.csv')

# Create a function to display Surge-IV100
def display_surge_iv100(surge_df):
    
    # Calculate the width and height in pixels based on the desired figsize in inches and DPI
    figsize_inches = (8.27, 5.87)
    dpi = 96
    width_pixels = int(figsize_inches[0] * dpi)
    height_pixels = int(figsize_inches[1] * dpi)

    fig = go.Figure()
    
    # Define the unique requests values
    hours = surge_df['hourly_date']
    iv100 =  surge_df['iv100']

    fig.add_trace(go.Bar(
        x=hours, # X-axis: Hours
        y=iv100, # Y-axis: Number of Requests
        hoverinfo='x+y', # Mouse Hover information combined between x and y
        text=iv100, # Text labels for each bar
        textposition='auto', # Auto position the text
        marker=dict(color='blue') # Set the bar color to blue
    ))

    # Insert labels for the title, x-axis, y-axis and define sizing of the image.
    fig.update_layout(
        title='IV100',
        xaxis_title='Hour',
        yaxis_title='IV 100',
        xaxis=dict(dtick=1),
        showlegend=False,
        width=width_pixels,
        height=height_pixels
    )

    # Transform the interactive Plotly chart into an Html and save it.
    #fig.write_html('../CSV/interactive_surge_iv100.html')
    
    # Display the figure
    return fig


# Create a function to display Surge-IV0
def display_surge_iv0(surge_df):
    
    # Calculate the width and height in pixels based on the desired figsize in inches and DPI
    figsize_inches = (8.27, 5.87)
    dpi = 96
    width_pixels = int(figsize_inches[0] * dpi)
    height_pixels = int(figsize_inches[1] * dpi)

    fig = go.Figure()
    
    # Define the unique requests values
    hours = surge_df['hourly_date']
    iv0 =  surge_df['iv0']

    fig.add_trace(go.Bar(
        x=hours, # X-axis: Hours
        y=iv0, # Y-axis: Number of Requests
        hoverinfo='x+y', # Mouse Hover information combined between x and y
        text=iv0, # Text labels for each bar
        textposition='auto', # Auto position the text
        marker=dict(color='blue') # Set the bar color to blue
    ))

    # Insert labels for the title, x-axis, y-axis and define sizing of the image.
    fig.update_layout(
        title='IV0',
        xaxis_title='Hour',
        yaxis_title='IV 0',
        xaxis=dict(dtick=1),
        showlegend=False,
        width=width_pixels,
        height=height_pixels
    )

    # Transform the interactive Plotly chart into an Html and save it.
    #fig.write_html('../CSV/interactive_surge_iv0.html')
    
    # Display the figure
    return fig

# Create a function to display Surge-Little League
def display_surge_little_league(surge_df):
    
    # Calculate the width and height in pixels based on the desired figsize in inches and DPI
    figsize_inches = (8.27, 5.87)
    dpi = 96
    width_pixels = int(figsize_inches[0] * dpi)
    height_pixels = int(figsize_inches[1] * dpi)

    fig = go.Figure()
    
    # Define the unique requests values
    hours = surge_df['hourly_date']
    little_rank_1 =  surge_df['little_top_1']

    fig.add_trace(go.Bar(
        x=hours, # X-axis: Hours
        y=little_rank_1, # Y-axis: Number of Requests
        hoverinfo='x+y', # Mouse Hover information combined between x and y
        text=little_rank_1, # Text labels for each bar
        textposition='auto', # Auto position the text
        marker=dict(color='blue') # Set the bar color to blue
    ))

    # Insert labels for the title, x-axis, y-axis and define sizing of the image.
    fig.update_layout(
        title='Little League',
        xaxis_title='Hour',
        yaxis_title='Little Rank 1',
        xaxis=dict(dtick=1),
        showlegend=False,
        width=width_pixels,
        height=height_pixels
    )

    # Transform the interactive Plotly chart into an Html and save it.
    #fig.write_html('../CSV/interactive_surge_little_rank_1.html')
    
    # Display the figure
    return fig

# Create a function to display Surge-Great League
def display_surge_great_league(surge_df):
    
    # Calculate the width and height in pixels based on the desired figsize in inches and DPI
    figsize_inches = (8.27, 5.87)
    dpi = 96
    width_pixels = int(figsize_inches[0] * dpi)
    height_pixels = int(figsize_inches[1] * dpi)

    fig = go.Figure()
    
    # Define the unique requests values
    hours = surge_df['hourly_date']
    great_rank_1 =  surge_df['great_top_1']

    fig.add_trace(go.Bar(
        x=hours, # X-axis: Hours
        y=great_rank_1, # Y-axis: Number of Requests
        hoverinfo='x+y', # Mouse Hover information combined between x and y
        text=great_rank_1, # Text labels for each bar
        textposition='auto', # Auto position the text
        marker=dict(color='blue') # Set the bar color to blue
    ))

    # Insert labels for the title, x-axis, y-axis and define sizing of the image.
    fig.update_layout(
        title='Great League',
        xaxis_title='Hour',
        yaxis_title='Great Rank 1',
        xaxis=dict(dtick=1),
        showlegend=False,
        width=width_pixels,
        height=height_pixels
    )

    # Transform the interactive Plotly chart into an Html and save it.
    #fig.write_html('../CSV/interactive_surge_little_rank_1.html')
    
    # Display the figure
    return fig

# Create a function to display Surge-Ultra League
def display_surge_ultra_league(surge_df):
    
    # Calculate the width and height in pixels based on the desired figsize in inches and DPI
    figsize_inches = (8.27, 5.87)
    dpi = 96
    width_pixels = int(figsize_inches[0] * dpi)
    height_pixels = int(figsize_inches[1] * dpi)

    fig = go.Figure()
    
    # Define the unique requests values
    hours = surge_df['hourly_date']
    ultra_rank_1 =  surge_df['ultra_top_1']

    fig.add_trace(go.Bar(
        x=hours, # X-axis: Hours
        y=ultra_rank_1, # Y-axis: Number of Requests
        hoverinfo='x+y', # Mouse Hover information combined between x and y
        text=ultra_rank_1, # Text labels for each bar
        textposition='auto', # Auto position the text
        marker=dict(color='blue') # Set the bar color to blue
    ))

    # Insert labels for the title, x-axis, y-axis and define sizing of the image.
    fig.update_layout(
        title='UltraLeague',
        xaxis_title='Hour',
        yaxis_title='Ultra Rank 1',
        xaxis=dict(dtick=1),
        showlegend=False,
        width=width_pixels,
        height=height_pixels
    )

    # Transform the interactive Plotly chart into an Html and save it.
    #fig.write_html('../CSV/interactive_surge_little_rank_1.html')
    
    # Display the figure
    return fig

#display_surge_iv100LF(surge_df)