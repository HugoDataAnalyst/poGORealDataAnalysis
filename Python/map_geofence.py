import dash
from dash import dcc, html, Input, Output, ALL, State
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import base64
from dash.exceptions import PreventUpdate
import re
import tempfile
import os
app = dash.Dash(__name__)

# Load the DataFrame
geofence_df = pd.read_csv('../CSV/Geofences/Espinho.csv')
df_path = "../CSV/AreasLF/EspinhoLF.csv"  # Replace with your actual dataset path
#df = pd.read_csv(df_path, delimiter='\t')
df = pd.read_csv(df_path)
#print(df.columns)
#print(df.head())
# Function to construct image path
def construct_image_path(row):
    # Convert both pokemon_id and form to integers
    pokemon_id = int(row['pokemon_id'])
    form = int(row['form'])

    if form == 0:
        return f"{pokemon_id}.png"
    else:
        return f"{pokemon_id}_f{form}.png"

# Apply the function to construct image paths
df['pokemon_images'] = df.apply(construct_image_path, axis=1)



# Function to create Folium map
def generate_map_visual(df, geofence_df):
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


    # Use a temporary file for the map
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w+', encoding='utf-8') as temp_file:
        # Save the map to the temporary file
        m.save(temp_file.name)
        # Return the file path of the temporary file
        return temp_file.name

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

# Call generate_map_visual to generate the initial map
initial_map_html_path = generate_map_visual(df, geofence_df)

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
        height='600',
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
    checked_images = [item for sublist in checked_values if sublist for item in sublist]
    if not checked_images:
        raise PreventUpdate
    filtered_df = df[df['pokemon_images'].isin(checked_images)]

    temp_map_path = generate_map_visual(filtered_df, geofence_df)

    # Read the map's HTML content and delete the temporary file
    with open(temp_map_path, 'r') as file:
        map_content = file.read()
    os.remove(temp_map_path)  # Delete the temporary file after reading

    return map_content

if __name__ == '__main__':
    app.run_server(debug=True)

