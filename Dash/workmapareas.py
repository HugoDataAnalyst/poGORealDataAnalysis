import dash
from dash import dcc, html, callback, Input, Output, ALL, State
import dash_bootstrap_components as dbc
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import base64
from dash.exceptions import PreventUpdate
import re
import sys
sys.path.insert(0, '../Python/')
sys.path.insert(0, '../Dash/')
from verynicefoliummap import quicktestmapv2
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


# Function to construct image path
def construct_image_path(row):
    if row['form'] == 0:
        return f"{row['pokemon_id']}.png"
    else:
        return f"{row['pokemon_id']}_f{row['form']}.png"

# Function to extract numbers from the filename for sorting
def sort_key_func(filename):
    numbers = map(int, re.findall(r'\d+', filename))
    return list(numbers)

# Function to create map layout
def create_map_layout():
    return html.Div([
        dcc.Dropdown(
            id='event-dropdown',
            options=[
                {'label': 'Lights Festival Event', 'value': 'LF'},
                {'label': 'No Event', 'value': 'NE'}
            ],
            value='LF',
            style={'font-weight': 'bold'}
        ),
        dcc.Dropdown(
            id='section-dropdown',
            options=[
                {'label': 'North Portugal', 'value': 'NorthPortugal'},
                {'label': 'Center Portugal', 'value': 'CenterPortugal'},
                {'label': 'South Portugal', 'value': 'SouthPortugal'},
                {'label': 'Germany', 'value': 'Germany'},
                {'label': 'Switzerland', 'value': 'Switzerland'},
                {'label': 'Italy', 'value': 'Italy'},
            ],
            value='CenterPortugal',
        ),
        dcc.Dropdown(
            id='specific-areas-dropdown',
            options=[], # Options will be set by callback
            value=None
        ),
        html.Div(id='map-area-content'),
        dcc.Store(id='checklist-state', data=[])
    ])

# Callback to update areas dropdown based on section selection
@app.callback(
    Output('specific-areas-dropdown', 'options'),
    [Input('section-dropdown', 'value')]
)
def set_specific_areas_options(selected_section):
    if selected_section == 'NorthPortugal':
        return [{'label': 'Porto', 'value': 'Porto'}]
    elif selected_section == 'CenterPortugal':
        return [
            {'label': 'Aveiro', 'value': 'Aveiro_Esgueira_SantaJoana'},
            {'label': 'Espinho', 'value': 'Espinho'},
            {'label': 'Grijó', 'value': 'Grijo'},
        ]
    return []


# Callback for loading data and updating map based on selection
@app.callback(
    Output('map-area-content', 'children'),
    [Input('event-dropdown', 'value'),
     Input('specific-areas-dropdown', 'value'),
     Input('checklist-state', 'data')]
)
def update_map_content(event_type, selected_area, checklist_state):
    if not selected_area:
        return "Please select an area."

    try:
        df_path = f"../CSV/Areas{event_type}/{selected_area}{event_type}.csv"
        df = pd.read_csv(df_path, delimiter='\t')
    
        df['pokemon_images'] = df.apply(construct_image_path, axis=1)
        unique_images = df['pokemon_images'].unique()
        unique_images_sorted = sorted(unique_images, key=sort_key_func)

        base64_images = {}
        for image_path in unique_images_sorted:
            image_full_path = f"../Dash/UICONS/pokemon/{image_path}"
            try:
                with open(image_full_path, "rb") as image_file:
                    base64_images[image_path] = base64.b64encode(image_file.read()).decode("utf-8")
            except FileNotFoundError:
                print(f"File not found: {image_full_path}")
                base64_images[image_path] = None

        filtered_df = df[df['pokemon_images'].isin(checklist_state)] if checklist_state else df
        folium_map_path = quicktestmapv2(filtered_df)

        return html.Div([
            html.Iframe(
                srcDoc=open(folium_map_path, 'r').read(),
                width='100%',
                height='600'
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
                                    value=[image] if image in checklist_state else [],
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
            )
        ])
    except Exception as e:
        return html.Div(f"Error loading data: {e}")


# Placeholder for create_table_layout function from tablefixing.py
def create_table_layout():
    # Your table layout code here
    pass

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Button('Areas-Table', id='to-table'),
    html.Button('Areas-Map', id='to-map'),
    html.Div(id='page-content')
])

# Callback for navigation buttons
@app.callback(Output('url', 'pathname'),
              [Input('to-table', 'n_clicks'),
               Input('to-map', 'n_clicks')],
              prevent_initial_call=True)
def navigate_to_page(n_clicks_table, n_clicks_map):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'to-table' in changed_id:
        return '/table-areas'
    elif 'to-map' in changed_id:
        return '/map-areas'

# Callback for updating the page content based on URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/table-areas':
        return create_table_layout()
    elif pathname == '/map-areas':
        return create_map_layout()
    else:
        return 'Welcome Page'

# Callback to update the map based on the state of the checklists
@app.callback(
    Output('checklist-state', 'data'),
    [Input({'type': 'filter-checklist', 'index': ALL}, 'value')],
    prevent_initial_call=True
)
def update_checklist_state(checklist_values):
    # Flatten the list of lists to a single list of checked values
    checked_images = [item for sublist in checklist_values if sublist for item in sublist]
    return checked_images

if __name__ == '__main__':
    app.run_server(debug=True)
