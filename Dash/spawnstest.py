import dash
from dash import dcc, html, Input, Output, ALL, State
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import base64
from dash.exceptions import PreventUpdate
import re
import os

app = dash.Dash(__name__)

# Load the DataFrame
surge_df = pd.read_csv('../CSV/Surge/SurgeGlobaliv100LF.csv')
geofence_df = pd.read_csv('../CSV/Geofences/Espinho.csv')
df_path = "../CSV/AreasLF/EspinhoLF.csv"  # Replace with your actual dataset path
df = pd.read_csv(df_path, delimiter='\t')

# Function to construct image path
def construct_image_path(row):
    if row['form'] == 0:
        return f"{row['pokemon_id']}.png"
    else:
        return f"{row['pokemon_id']}_f{row['form']}.png"

df['pokemon_images'] = df.apply(construct_image_path, axis=1)

# Create a function to display Surge
def display_surge(surge_df):
    # Calculate the width and height in pixels based on the desired figsize in inches and DPI
    figsize_inches = (8.27, 5.87)
    dpi = 96
    width_pixels = int(figsize_inches[0] * dpi)
    height_pixels = int(figsize_inches[1] * dpi)

    fig = go.Figure()
    
    # Define the unique requests values
    hours = df['request_hour']
    num_requests = df['num_requests']

    fig.add_trace(go.Bar(
        x=hours, # X-axis: Hours
        y=num_requests, # Y-axis: Number of Requests
        hoverinfo='x+y', # Mouse Hover information combined between x and y
        text=num_requests, # Text labels for each bar
        textposition='auto', # Auto position the text
        marker=dict(color='blue') # Set the bar color to blue
    ))

    # Insert labels for the title, x-axis, y-axis and define sizing of the image.
    fig.update_layout(
        title='Surge-Pricing',
        xaxis_title='Hour',
        yaxis_title='Ride Requests',
        xaxis=dict(dtick=1),
        showlegend=False,
        width=width_pixels,
        height=height_pixels
    )

    # Transform the interactive Plotly chart into an Html and save it.
    #fig.write_html('../InteractiveGraphics/interactive_surge_pricing.html')
    
    # Display the figure
    fig.show()


# Function to create Folium map
def quicktestmapv2(df, geofence_df):
    map_center = [df["avg_lat"].mean(), df["avg_lon"].mean()]
    m = folium.Map(location=map_center, zoom_start=10)
    #marker_cluster = MarkerCluster().add_to(m)
    marker_cluster = MarkerCluster(
        sticky=False,
        maxClusterRadius=30
    ).add_to(m)
    for _, row in df.iterrows():
        icon_image = f"../Dash/UICONS/pokemon/{row['pokemon_images']}"
        icon = folium.CustomIcon(icon_image, icon_size=(40, 40))
        hover_text = (
            f"Pokemon ID: {row['pokemon_id']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/pokemon.png' alt='Icon 2' height='20' width='20'>" f": {row['count_poke']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/100iv.png' alt='Icon 2' height='20' width='20'>" f": {row['iv_100']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/0iv.png' alt='Icon 2' height='20' width='20'>" f": {row['iv_0']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/sparkles.png' alt='Icon 2' height='20' width='20'>" f": {row['shinies']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/500.png' alt='Icon 2' height='20' width='20'>" f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/first.png' alt='Icon 2' height='20' width='20'>" f": {row['little_top_1']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/1500.png' alt='Icon 2' height='20' width='20'>" f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/first.png' alt='Icon 2' height='20' width='20'>" f": {row['great_top_1']}<br>"
            f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/2500.png' alt='Icon 2' height='20' width='20'>" f"<img src='https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/first.png' alt='Icon 2' height='20' width='20'>" f": {row['ultra_top_1']}<br>"
        )
        folium.Marker(
            location=[row["avg_lat"], row["avg_lon"]],
            icon=icon,
            popup=folium.Popup(html=hover_text, max_width=300)  # Attach the hover text as a popup
        ).add_to(marker_cluster)        

    # Loop through each geofence
    for _, geofence in geofence_df.iterrows():
        area_name = geofence['AreaName']
        # Extract coordinates for the geofence
        coords = []
        i = 1
        while f'Lat{i}' in geofence and f'Lon{i}' in geofence:
            lat = geofence[f'Lat{i}']
            lon = geofence[f'Lon{i}']
            if not pd.isna(lat) and not pd.isna(lon):
                coords.append((lat, lon))
            i += 1

        if coords:
            # Create a polygon on the map
            folium.Polygon(
                locations=coords,
                color='blue',
                fill=False,
                popup=folium.Popup(area_name)
            ).add_to(m)


    map_html_path = "folium_map.html"
    m.save(map_html_path)
    return map_html_path

# Function to extract numbers from the filename and use them for sorting
def sort_key_func(filename):
    # Extract all numbers, but return them as a list of integers
    numbers = map(int, re.findall(r'\d+', filename))
    return list(numbers)

# Sort unique images using the custom sort key
unique_images = df['pokemon_images'].unique()
unique_images_sorted = sorted(unique_images, key=sort_key_func)

# Convert images to base64 encoding
base64_images = {}
for image_path in unique_images_sorted:
    image_full_path = f"../Dash/UICONS/pokemon/{image_path}"
    try:
        with open(image_full_path, "rb") as image_file:
            base64_images[image_path] = base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"File not found: {image_full_path}")
        base64_images[image_path] = None

# Call quicktestmapv2 to generate the initial map
initial_map_html_path = quicktestmapv2(df, geofence_df)

# Dash layout
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.Iframe(
        id='map-iframe',
        srcDoc=open(initial_map_html_path, 'r').read(),
        width='100%',
        height='600px',
        style={'border': 'none'}
    ),    
    html.Div(
        children=[
            html.Div(
                id='filter-images',
                children=[
                    html.Div([
                        html.Img(
                            src="data:image/png;base64," + base64_images[image] if base64_images[image] else "",
                            id={'type': 'display-image', 'index': image},
                            style={'width': '50px', 'height': '50px', 'cursor': 'pointer'},
                        ),
                        dcc.Checklist(
                            options=[{'label': '', 'value': image}],
                            value=[image],
                            id={'type': 'filter-checklist', 'index': image},
                            inline=True,
                            style={'display': 'inline-block', 'width': '50px', 'height': '50px', 'cursor': 'pointer'},
                        )
                    ]) for image in unique_images_sorted
                ],
                style={'display': 'grid', 'gridTemplateColumns': 'repeat(6, 1fr)', 'gap': '10px', 'overflowY': 'scroll', 'maxHeight': '400px', 'width': '50%'},
            ),
        ],
        style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '10px'}
    ),
    html.Div(id='hidden-div', style={'display': 'none'}),
])

# Callback to update the map based on the state of the checklists
@app.callback(
    Output('map-iframe', 'srcDoc'),
    [Input({'type': 'filter-checklist', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def update_map(checked_values):
    checked_images = [item for sublist in checked_values if sublist is not None for item in sublist]
    if not checked_images:
        raise PreventUpdate
    filtered_df = df[df['pokemon_images'].isin(checked_images)]
    filtered_map_html_path = quicktestmapv2(filtered_df)
    return open(filtered_map_html_path, 'r').read()


if __name__ == '__main__':
    app.run_server(debug=True)
