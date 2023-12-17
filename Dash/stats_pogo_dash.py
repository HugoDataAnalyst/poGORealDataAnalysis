import dash
from dash import dcc, html, callback, Input, Output, ALL, State, MATCH
import dash_bootstrap_components as dbc
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import base64
from dash.exceptions import PreventUpdate
import re
import sys
import os
import tempfile
import json
from math import ceil
from urllib.parse import parse_qs, urlparse
sys.path.insert(0, '../Python/')
sys.path.insert(0, '../Dash/')
from map_geofence import generate_map_visual
from dash.dependencies import ClientsideFunction

import plotly.graph_objects as go
from datetime import datetime
from surge_data import display_surge_iv100, display_surge_iv0, display_surge_little_league, display_surge_great_league, display_surge_ultra_league

app = dash.Dash(__name__, title='Go Analysis', update_title='Loading...', external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

ROWS_PER_PAGE = 10

# Ensure the mapping is applied only once
mapping_applied = False
# Load the mapping
def load_id_to_name_mapping(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return {int(k): v for k, v in data.items()}
# Function to apply the mapping
def apply_name_mapping(df, mapping):
    global mapping_applied
    if not mapping_applied:
         df['name'] = df['pokemon_id'].map(mapping).fillna("Unknown")
         mapping_applied = True
    return df

# Function to construct image path based on pokemon_id and form
def construct_table_image_path(row):
    if row['form'] == 0:
        return f"https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/pokemon/{row['pokemon_id']}.png"
    else:
        return f"https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/pokemon/{row['pokemon_id']}_f{row['form']}.png"


def get_column_display_names(df):
# Map of original column names to display names
    column_display_names = {
        'count_poke': 'Count Pokes',
        'percentage': 'Pokemon %',
        'avg_level': 'Avg Level',
        'iv_100': 'IV 100',
        'shinies': 'Shinies',
        'little_top_1': 'Little Top 1',
        'great_top_1': 'Great Top 1',
        'ultra_top_1': 'Ultra Top 1',
        'avg_iv': 'Avg IV',
        'iv100_percentage': 'IV 100%',
        'iv_0': 'IV 0',
        'iv0_percentage': 'IV 0%',
        'shiny_odds': 'Shiny %',
        'little_top1_percentage': 'Little Top %',
        'great_top1_percentage': 'Great Top %',
        'ultra_top1_percentage': 'Ultra Top %',
        'name': 'Name',
        # Add more mappings as needed
    }
    return {col: column_display_names.get(col, col) for col in df.columns}

def round_columns(df):
# Columns to round to 3 decimals
    columns_to_round = [
        'Pokemon %',
        'Avg Level',
        'Avg IV',
        'IV 100%',
        'IV 0%',
        'Shiny %',
        'Little Top %',
        'Great Top %',
        'Ultra Top %',
    ]
    # Round specified columns to 3 decimals
    df[columns_to_round] = df[columns_to_round].apply(pd.to_numeric, errors='coerce').round(3)


# Function to construct image path for map
def construct_image_path(row):
    # Convert both pokemon_id and form to integers
    pokemon_id = int(row['pokemon_id'])
    form = int(row['form'])

    if form == 0:
        return f"{pokemon_id}.png"
    else:
        return f"{pokemon_id}_f{form}.png"


# Function to extract numbers from the filename for sorting
def sort_key_func(filename):
    numbers = map(int, re.findall(r'\d+', filename))
    return list(numbers)

# Function to create surge layout
def create_surge_layout():
    # Styling the dropdown menus
    dropdown_style = {
        'color': '#007BFF',
        'backgroundColor': 'white',
        'borderBottom': '2px solid #007BFF',  # Only the bottom border is blue and slightly thicker
        'borderRadius': '0px',
        'padding': '5px',
        'marginBottom': '10px',
        'fontWeight': 'bold',
        'cursor': 'pointer'
    }   
    return html.Div([
        dcc.Dropdown(
            id='surge-event-dropdown',
            options=[
                {'label': 'Lights Festival Event', 'value': 'LF'},
                {'label': 'No Event', 'value': 'NE'}
            ],
            value='LF',
            style=dropdown_style
        ),
        dcc.Dropdown(
            id='surge-section-dropdown',
            options=[
                {'label': 'Global', 'value': 'Global'},
            ],
            value='Global',
            style=dropdown_style
        ),        
        dcc.Dropdown(
            id='surge-specific-dropdown',
            options=[], # Options will be set by callback
            value=None,
            placeholder='Please Select a Metric',            
            style=dropdown_style
        ),
    ], style={'margin': '10%'})

# Callback to update surge dropdown based on section selection
@app.callback(
    Output('surge-specific-dropdown', 'options'),
    [Input('surge-section-dropdown', 'value')]
)
def set_specific_surge_options(selected_surge_section):
    if selected_surge_section == 'Global':
        return [
            {'label': 'IV 100', 'value': 'SurgeGlobaliv100'},
            {'label': 'IV 0', 'value': 'SurgeGlobaliv0'},
            {'label': 'Little League Rank 1', 'value': 'SurgeGlobalLittleTop1'},
            {'label': 'Great League Rank 1', 'value': 'SurgeGlobalGreatTop1'},
            {'label': 'Ultra League Rank 1', 'value': 'SurgeGlobalUltraTop1'}
        ]
    return []

# Callback to handle changes in both dropdowns
@app.callback(
    Output('surge-graph-container', 'children'),
    [Input('surge-event-dropdown', 'value'),   # Event type (LF or NE)
     Input('surge-specific-dropdown', 'value')] # Specific surge category (e.g., 'IV 100')
)
def update_surge_graph(surge_event_type, selected_surge_section):
    if not surge_event_type or not selected_surge_section:
        return html.Div('')

    # Construct the file path dynamically
    file_path = f"../CSV/Surge/{selected_surge_section}{surge_event_type}.csv"

    # Load the DataFrame
    try:
        surge_df = pd.read_csv(file_path)
    except FileNotFoundError:
        return html.Div(f"Data file not found: {file_path}")

    # Call the appropriate function based on the selected_surge_section
    if selected_surge_section == 'SurgeGlobaliv100':
        fig = display_surge_iv100(surge_df)
    elif selected_surge_section == 'SurgeGlobaliv0':
        fig = display_surge_iv0(surge_df)
    elif selected_surge_section == 'SurgeGlobalLittleTop1':
        fig = display_surge_little_league(surge_df)
    elif selected_surge_section == 'SurgeGlobalGreatTop1':
        fig = display_surge_great_league(surge_df)
    elif selected_surge_section == 'SurgeGlobalUltraTop1':
        fig = display_surge_ultra_league(surge_df)        
    # Return a Graph component to display the figure
    #return dcc.Graph(figure=fig)
    # Wrap the Graph component in a Div and apply margin styling
    return html.Div(dcc.Graph(figure=fig), style={'margin': '10%', 'marginLeft': 'auto', 'marginRight': 'auto', 'width': 'fit-content'})

# Function to create map layout
def create_map_layout():
    # Styling the dropdown menus    
    dropdown_style = {
        'color': '#007BFF',
        'backgroundColor': 'white',
        'borderBottom': '2px solid #007BFF',  # Only the bottom border is blue and slightly thicker
        'borderRadius': '0px',
        'padding': '5px',
        'marginBottom': '10px',
        'fontWeight': 'bold',
        'cursor': 'pointer'
    }      
    return html.Div([
        dcc.Dropdown(
            id='event-dropdown',
            options=[
                {'label': 'Lights Festival Event', 'value': 'LF'},
                {'label': 'No Event', 'value': 'NE'}
            ],
            value='LF',
            style=dropdown_style
        ),
        dcc.Dropdown(
            id='section-dropdown',
            options=[
                {'label': 'North Portugal', 'value': 'NorthPortugal'},
                {'label': 'Center Portugal', 'value': 'CenterPortugal'},
                {'label': 'Lisbon Portugal', 'value': 'LisbonPortugal'},
                {'label': 'Alentejo Portugal', 'value': 'AlentejoPortugal'},
                {'label': 'Algarve Portugal', 'value': 'AlgarvePortugal'},
                {'label': 'Germany', 'value': 'Germany'},
                {'label': 'Switzerland', 'value': 'Switzerland'},
                {'label': 'Italy', 'value': 'Italy'},
            ],
            value='CenterPortugal',
            style=dropdown_style            
        ),
        dcc.Dropdown(
            id='specific-areas-dropdown',
            options=[], # Options will be set by callback
            value=None,
            placeholder='Please Select an Area',            
            style=dropdown_style            
        ),
        html.Div(id='map-area-content'),
        dcc.Store(id='checklist-state', data=[])
    ], style={'margin': '10%'})

# Callback to update areas dropdown based on section selection
@app.callback(
    Output('specific-areas-dropdown', 'options'),
    [Input('section-dropdown', 'value')]
)
def set_specific_areas_options(selected_section):
    if selected_section == 'NorthPortugal':
        return [
            {'label': 'Canidelo & Madalena', 'value': 'CanideloMadalena'},
            {'label': 'Espinho', 'value': 'Espinho'},
            {'label': 'Grijó', 'value': 'Grijo'},
            {'label': 'Maia & Gueifães & Castelo da Maia', 'value': 'MaiaGueifaesCasteloMaia'},
            {'label': 'Matosinhos & Foz do Douro', 'value': 'MatosinhosFozDouro'},
            {'label': 'Porto', 'value': 'Porto'},
            {'label': 'Rio Tinto & Pedrouços & Baguim', 'value': 'RioTintoPedroucosBaguim'},
            {'label': 'São Mamede & Senhora da Hora', 'value': 'SaoMamedeSenhoraHora'},
            {'label': 'Vila do Conde & Póvoa de Varzim', 'value': 'VilaCondePovoaVarzim'},
            {'label': 'Vila Nova Gaia', 'value': 'VilaNovaGaia'},
            {'label': 'Vila Real', 'value': 'VilaReal'}
        ]
    elif selected_section == 'CenterPortugal':
        return [
            {'label': 'Agueda', 'value': 'Agueda'},
            {'label': 'Anadia', 'value': 'Anadia'},
            {'label': 'Antuzede & Pedrulha & Lordemão', 'value': 'AntuzedePedrulhaLordemao'},
            {'label': 'Aveiro', 'value': 'AveiroEsgueiraSantaJoana'},
            {'label': 'Barra', 'value': 'Barra'},
            {'label': 'Coimbra & Olivais & Portela', 'value': 'CoimbraOlivaisPortela'},
            {'label': 'Ílhavo', 'value': 'Ilhavo'},
            {'label': 'Oliveirinha & Eixo & São Bernardo', 'value': 'OliveirinhaEixoSaoBernardo'},
            {'label': 'São Martinho Bispo & Santa Clara', 'value': 'SaoMartinhoBispoSantaClara'},            
            {'label': 'Vila Nova de Poiares', 'value': 'Poiares'},
        ]
    elif selected_section == 'LisbonPortugal':
        return [
            {'label': 'Agualva-Cácem', 'value': 'AgualvaCacem'}, 
            {'label': 'Almada', 'value': 'Almada'}, 
            {'label': 'Amadora', 'value': 'Amadora'}, 
            {'label': 'Carcavelos & Parede', 'value': 'CarcavelosParede'}, 
            {'label': 'Carnaxide & Algés', 'value': 'CarnaxideAlges'},
            {'label': 'Cascais', 'value': 'Cascais'}, 
            {'label': 'Lisboa & Surroundings', 'value': 'LisboaCampoGrande'}, 
            {'label': 'Montijo', 'value': 'Montijo'}, 
            {'label': 'Odivelas & Parque das Nações', 'value': 'OdivelasParqueDasNacoes'}, 
            {'label': 'Póvoa de Santa Iria', 'value': 'PovoaSantaIria'}, 
            {'label': 'Porto Salvo & Oeiras', 'value': 'PortoSalvoOeiras'}, 
            {'label': 'Seixal', 'value': 'Seixal'}, 
            {'label': 'Setúbal & Pinhal Novo & Palmela', 'value': 'Setubal'}, 
            {'label': 'Sintra & Algueirão-Mem Martins', 'value': 'SintraAlgueirao'}, 
        ]
    elif selected_section == 'AlentejoPortugal':
        return [
            {'label': 'Almeirim', 'value': 'Almeirim'}, 
            {'label': 'Évora', 'value': 'Evora'}, 
        ] 
    elif selected_section == 'AlgarvePortugal':
        return [
            {'label': 'Quarteira & Vilamoura', 'value': 'QuarteiraVilamoura'}, 
        ]
    elif selected_section == 'Germany':
        return [
            {'label': 'Hermeskeil', 'value': 'Hermeskeil'}, 
            {'label': 'Lebach', 'value': 'Lebach'},  
            {'label': 'Losheim am See', 'value': 'Losheim'}, 
            {'label': 'Saarlouis', 'value': 'Saarlouis'}, 
            {'label': 'Sankt Wendel', 'value': 'Wendel'},                         
        ] 
    elif selected_section == 'Switzerland':
        return [
            {'label': 'Yverdon-les-Bains', 'value': 'Yverdon'},                        
        ]
    elif selected_section == 'Italy':
        return [
            {'label': 'Stezzano & Dalmine & Osio Sotto & Boccaleone', 'value': 'Stezzano'}, 
        ]                                        
    return []


# Callback for loading data and updating map based on selection
@app.callback(
    Output('map-area-content', 'children'),
    [Input('url', 'pathname'),
     Input('event-dropdown', 'value'),
     Input('specific-areas-dropdown', 'value'),
     Input('checklist-state', 'data')],
     #prevent_initial_call=True # Prevent the callback from running upon initilization
)
def update_map_content(pathname, event_type, selected_area, checklist_state):
    # Only update map content when the pathname indicates map areas
    if not pathname.startswith('/map-areas') or not selected_area:
        return html.Div("")

    try:
        df_path = f"../CSV/Areas{event_type}/{selected_area}{event_type}.csv"
        #df = pd.read_csv(df_path, delimiter='\t')
        df = pd.read_csv(df_path)
        geofence_path = f"../CSV/Geofences/{selected_area}.csv"
        geofence_df = pd.read_csv(geofence_path)

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
        folium_map_path = generate_map_visual(filtered_df, geofence_df)

        # Initialize map_html_content
        map_html_content = ""

        # Read HTML content from the temporary file
        with open(folium_map_path, 'r') as file:
            map_html_content = file.read()

        # Delete the temporary file
        os.remove(folium_map_path)

        return html.Div([
            html.Iframe(
                srcDoc=map_html_content,
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
                        style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(50px, 1fr))', 'gap': '10px', 'overflowY': 'scroll', 'maxHeight': '400px', 'width': '50%', 'margin': '10%'},
                    ),
                ],
                style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'marginTop': '10px'}
            )
        ], style={'margin': '10% 10%', 'marginLeft': 'auto', 'marginRight': 'auto'})
    except Exception as e:
        return html.Div(f"Error loading data: {e}")

# Placeholder for create_table_layout function from tablefixing.py
def create_table_layout():
    # Styling the dropdown menus    
    dropdown_style = {
        'color': '#007BFF',
        'backgroundColor': 'white',
        'borderBottom': '2px solid #007BFF',  # Only the bottom border is blue and slightly thicker
        'borderRadius': '0px',
        'padding': '5px',
        'marginBottom': '10px',
        'fontWeight': 'bold',
        'cursor': 'pointer'
    }
    search_input_style = {
        'display': 'block',  # Change this as needed to show/hide
        'width': '20%',  # Full width
        'padding': '10px',  # Padding inside the input for spacing
        'margin': '10px 0',  # Margin around the input for spacing from other elements
        'fontSize': '16px',  # Larger font size for better readability
        'borderRadius': '5px',  # Rounded borders
        'border': '1px solid #007BFF',  # Light grey border
        'boxShadow': 'inset 0 1px 3px rgba(0, 0, 0, 0.1)',  # Inner shadow for depth
        'outline': 'none',  # Removes the default focus outline
        'transition': 'border-color 0.3s ease-in-out',  # Smooth transition for border color
    }
    return html.Div([
        dcc.Dropdown(
            id='table-event-dropdown',
            options=[
                {'label': 'Lights Festival Event', 'value': 'LF'},
                {'label': 'No Event', 'value': 'NE'}
            ],
            value='LF',
            style=dropdown_style
        ),
        dcc.Dropdown(
            id='table-section-dropdown',
            options=[
                {'label': 'Global', 'value': 'Global'},
                {'label': 'North Portugal', 'value': 'NorthPortugal'},
                {'label': 'Center Portugal', 'value': 'CenterPortugal'},
                {'label': 'Lisbon Portugal', 'value': 'LisbonPortugal'},
                {'label': 'Alentejo Portugal', 'value': 'AlentejoPortugal'},
                {'label': 'Algarve Portugal', 'value': 'AlgarvePortugal'},
                {'label': 'Germany', 'value': 'Germany'},
                {'label': 'Switzerland', 'value': 'Switzerland'},
                {'label': 'Italy', 'value': 'Italy'},
            ],
            value='CenterPortugal',
            style=dropdown_style            
        ),
        dcc.Dropdown(
            id='specific-table-areas-dropdown',
            options=[], # Options will be set by callback
            value=None,
            placeholder='Please Select an Area',
            style=dropdown_style            
        ),
        html.Div(style={'height': '20px'}),
        html.Div(
            dcc.Input(
                id='table-search-input', 
                type='text', placeholder='Search by Name', 
                debounce=True,
                style=search_input_style
            ),
            id='search-query-container',
            style={'display': 'none'}  # Initially hidden
        ),        
        html.Div(id='table-area-content'),
        html.Div(id='pagination-placeholder'),
        dcc.Store(id='table-sort-state', data={'column': None, 'direction': 'asc'})
    ], style={'margin': '10%'})

# Callback to update areas dropdown (for table)
@app.callback(
    Output('specific-table-areas-dropdown', 'options'),
    [Input('table-section-dropdown', 'value')]
)
def set_specific_table_areas_options(selected_section):
    if selected_section == 'Global':
        return [{'label': 'Global', 'value': 'global'}]
    elif selected_section == 'NorthPortugal':
        return [
            {'label': 'Canidelo & Madalena', 'value': 'CanideloMadalena'},
            {'label': 'Espinho', 'value': 'Espinho'},
            {'label': 'Grijó', 'value': 'Grijo'},
            {'label': 'Maia & Gueifães & Castelo da Maia', 'value': 'MaiaGueifaesCasteloMaia'},
            {'label': 'Matosinhos & Foz do Douro', 'value': 'MatosinhosFozDouro'},
            {'label': 'Porto', 'value': 'Porto'},
            {'label': 'Rio Tinto & Pedrouços & Baguim', 'value': 'RioTintoPedroucosBaguim'},
            {'label': 'São Mamede & Senhora da Hora', 'value': 'SaoMamedeSenhoraHora'},
            {'label': 'Vila do Conde & Póvoa de Varzim', 'value': 'VilaCondePovoaVarzim'},
            {'label': 'Vila Nova Gaia', 'value': 'VilaNovaGaia'},
            {'label': 'Vila Real', 'value': 'VilaReal'}
        ]
    elif selected_section == 'CenterPortugal':
        return [
            {'label': 'Agueda', 'value': 'Agueda'},
            {'label': 'Anadia', 'value': 'Anadia'},
            {'label': 'Antuzede & Pedrulha & Lordemão', 'value': 'AntuzedePedrulhaLordemao'},
            {'label': 'Aveiro', 'value': 'AveiroEsgueiraSantaJoana'},
            {'label': 'Barra', 'value': 'Barra'},
            {'label': 'Coimbra & Olivais & Portela', 'value': 'CoimbraOlivaisPortela'},
            {'label': 'Ílhavo', 'value': 'Ilhavo'},
            {'label': 'Oliveirinha & Eixo & São Bernardo', 'value': 'OliveirinhaEixoSaoBernardo'},
            {'label': 'São Martinho Bispo & Santa Clara', 'value': 'SaoMartinhoBispoSantaClara'},            
            {'label': 'Vila Nova de Poiares', 'value': 'Poiares'},
        ]
    elif selected_section == 'LisbonPortugal':
        return [
            {'label': 'Agualva-Cácem', 'value': 'AgualvaCacem'}, 
            {'label': 'Almada', 'value': 'Almada'}, 
            {'label': 'Amadora', 'value': 'Amadora'}, 
            {'label': 'Carcavelos & Parede', 'value': 'CarcavelosParede'}, 
            {'label': 'Carnaxide & Algés', 'value': 'CarnaxideAlges'},
            {'label': 'Cascais', 'value': 'Cascais'}, 
            {'label': 'Lisboa & Surroundings', 'value': 'LisboaCampoGrande'}, 
            {'label': 'Montijo', 'value': 'Montijo'}, 
            {'label': 'Odivelas & Parque das Nações', 'value': 'OdivelasParqueDasNacoes'}, 
            {'label': 'Póvoa de Santa Iria', 'value': 'PovoaSantaIria'}, 
            {'label': 'Porto Salvo & Oeiras', 'value': 'PortoSalvoOeiras'}, 
            {'label': 'Seixal', 'value': 'Seixal'}, 
            {'label': 'Setúbal & Pinhal Novo & Palmela', 'value': 'Setubal'}, 
            {'label': 'Sintra & Algueirão-Mem Martins', 'value': 'SintraAlgueirao'}, 
        ]
    elif selected_section == 'AlentejoPortugal':
        return [
            {'label': 'Almeirim', 'value': 'Almeirim'}, 
            {'label': 'Évora', 'value': 'Evora'}, 
        ] 
    elif selected_section == 'AlgarvePortugal':
        return [
            {'label': 'Quarteira & Vilamoura', 'value': 'QuarteiraVilamoura'}, 
        ]
    elif selected_section == 'Germany':
        return [
            {'label': 'Hermeskeil', 'value': 'Hermeskeil'}, 
            {'label': 'Lebach', 'value': 'Lebach'},  
            {'label': 'Losheim am See', 'value': 'Losheim'}, 
            {'label': 'Saarlouis', 'value': 'Saarlouis'}, 
            {'label': 'Sankt Wendel', 'value': 'Wendel'},                         
        ] 
    elif selected_section == 'Switzerland':
        return [
            {'label': 'Yverdon-les-Bains', 'value': 'Yverdon'},                        
        ]
    elif selected_section == 'Italy':
        return [
            {'label': 'Stezzano & Dalmine & Osio Sotto & Boccaleone', 'value': 'Stezzano'}, 
        ]                                        
    return []


# Callback to show/hide search query box based on area selection
@app.callback(
    Output('search-query-container', 'style'),
    [Input('specific-table-areas-dropdown', 'value')]
)
def toggle_search_query_visibility(selected_area):
    if selected_area:
        return {'display': 'block'}  # Show search box when an area is selected
    else:
        return {'display': 'none'}  # Hide search box when no area is selected


def generate_pagination_controls(current_page, page_count, max_visible_pages=4):
    pagination_items = []

    # Add 'Previous' button
    if current_page > 1:
        prev_page = current_page - 1
        prev_button = html.Button('Previous', id={'type': 'pagination-button', 'index': prev_page}, className='page-link')
        pagination_items.append(html.Li(prev_button, className='page-item'))

    # Calculate start and end page numbers for button display
    half_visible = max_visible_pages // 2
    start_page = max(current_page - half_visible, 1)
    end_page = min(start_page + max_visible_pages - 1, page_count)

    # Adjust if we're at the start or end of the page range
    if start_page <= 3:
        end_page = min(max_visible_pages, page_count)
        start_page = 1
    if end_page > page_count - 2:
        start_page = max(page_count - max_visible_pages + 1, 1)
        end_page = page_count

    # Ensure current page is always shown
    if current_page not in range(start_page, end_page + 1):
        start_page = max(current_page - half_visible, 1)
        end_page = min(start_page + max_visible_pages - 1, page_count)

    # Create page buttons
    if start_page > 1:
        pagination_items.append(html.Li(html.Button('1', id={'type': 'pagination-button', 'index': 1}, className='page-link'), className='page-item'))
        if start_page > 2:
            pagination_items.append(html.Li(html.Span('...', className='page-link'), className='page-item'))

    for page in range(start_page, end_page + 1):
        item_class = 'page-item' + (' active' if page == current_page else '')
        button = html.Button(str(page), id={'type': 'pagination-button', 'index': page}, className='page-link')
        pagination_items.append(html.Li(button, className=item_class))

    if end_page < page_count:
        if end_page < page_count - 1:
            pagination_items.append(html.Li(html.Span('...', className='page-link'), className='page-item'))
        pagination_items.append(html.Li(html.Button(str(page_count), id={'type': 'pagination-button', 'index': page_count}, className='page-link'), className='page-item'))

    # Add 'Next' button
    if current_page < page_count:
        next_page = current_page + 1
        next_button = html.Button('Next', id={'type': 'pagination-button', 'index': next_page}, className='page-link')
        pagination_items.append(html.Li(next_button, className='page-item'))

    # Create the pagination ul component
    pagination_component = html.Ul(pagination_items, className="pagination")

    # Wrap the pagination in a Div and apply margin styling
    return html.Div(pagination_component, style={'margin': '3% 10%', 'marginLeft': 'auto', 'marginRight': 'auto'})

# Function to generate HTML table with images and delimiter bars
def generate_html_table(df_page, sort_by=None, sort_direction='asc'):
    # Define a style for the header buttons
    button_style = {
        'backgroundColor': '#007BFF',
        'color': 'white',
        'border': '1px solid #007BFF',
        'padding': '5px 10px',
        'marginRight': '5px',
        'borderRadius': '5px',
        'cursor': 'pointer'
    }

    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_copy = df_page.copy()

    # Apply column display names
    column_names_mapping = get_column_display_names(df_copy)
    df_copy.rename(columns=column_names_mapping, inplace=True)

    ordered_columns = ['Name'] + [col for col in df_copy.columns if col not in ["pokemon_id", "form", "avg_lat", "avg_lon", "image_path", "Name"]]
    # Determine columns to display (exclude 'pokemon_id' and 'form')
    columns_to_display = [col for col in ordered_columns if col in df_copy.columns]

    # Add a new column for image paths
    df_copy['image_path'] = df_copy.apply(construct_table_image_path, axis=1)

    # Sort the DataFrame if sort parameters are provided
    if sort_by:
        df_copy = df_copy.sort_values(by=sort_by, ascending=(sort_direction == 'asc'))

    # Build the header row with sort buttons
    table_header = [html.Th(html.Div("Pokémon", className='header-label'), className='align-middle header-cell', style={'white-space': 'nowrap'})]
    for col in columns_to_display:
        button_text = column_names_mapping.get(col, col)
        if sort_by == col:
            button_text += ' ↓' if sort_direction == 'asc' else ' ↑'
        header_cell_content = html.Div(
            html.Button(
                button_text,
                id={'type': 'sort-button', 'index': col},
                className='header-button',
                style=button_style
            ),
            className='header-label'
        )
        table_header.append(html.Th(header_cell_content, className='align-middle header-cell', style={'white-space': 'nowrap'}))

    # Build the table rows
    table_rows = []
    for _, row in df_copy.iterrows():
        img_src = row["image_path"]
        img_html = html.Img(src=img_src, style={"max-width": "50px", "max-height": "50px"})
        row_content = [html.Td(img_html, className='align-middle', style={'textAlign': 'center'})] + [
            html.Td(html.Div(row[col], className='content-cell'), className='align-middle', style={'textAlign': 'center'})
            for col in columns_to_display
        ]
        table_rows.append(html.Tr(row_content))

    # Combine header and rows
    table_content = [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)]

    # Create the table component
    table_component = dbc.Table(
        [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)],
        striped=True, bordered=True, hover=True, responsive=True
    )
    # Wrap the table in a Div and apply margin styling
    return html.Div(table_component, style={'margin': '0 10%', 'marginLeft': 'auto', 'marginRight': 'auto', 'maxWidth': '100%'})

# Modified handle_navigation callback
@app.callback(
    [Output('url', 'pathname'),
     Output('selected-table-area-store', 'data'),
     Output('specific-areas-dropdown', 'value'),
     Output('surge-event-dropdown', 'value'),
     Output('surge-specific-dropdown', 'value')],
    [Input('to-table', 'n_clicks'),
     Input('to-map', 'n_clicks'),
     Input('to-surge', 'n_clicks'),
     Input('to-home', 'n_clicks'),
     Input('specific-table-areas-dropdown', 'value'),
     Input({'type': 'pagination-button', 'index': ALL}, 'n_clicks'),
     Input('specific-areas-dropdown', 'value'),
     Input('surge-specific-dropdown', 'value')],
    [State('url', 'pathname'),
     State('selected-table-area-store', 'data')]
)
def handle_navigation(to_table_clicks, to_map_clicks, to_surge_clicks, to_home_clicks, selected_table_area, pagination_clicks, selected_map_area, selected_surge_section, current_path, stored_area):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_stored_area = stored_area['selected_table_area'] if stored_area else selected_table_area    

    # Handle table and map navigation
    if 'to-table' in trigger_id:
        return '/table-areas', None, dash.no_update, None, None
    elif 'to-map' in trigger_id:
        return '/map-areas', dash.no_update, None, None, None
    elif 'to-surge' in trigger_id:
        return '/surge', dash.no_update, None, 'LF', None
    elif 'to-home' in trigger_id:
        return '/', dash.no_update, None, None, None
    elif 'specific-table-areas-dropdown' in trigger_id:
        new_path = f'/table-areas/{selected_table_area}/page=1'
        return new_path, {'selected_table_area': selected_table_area}, dash.no_update, None, None

    # Handle pagination
    if 'pagination-button' in trigger_id:
    
        page_number = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['index']
        new_path = f'/table-areas/{selected_stored_area}/page={page_number}'
        return new_path, {'selected_table_area': selected_stored_area, 'current_page': page_number}, dash.no_update, None, None

    # Handle specific areas dropdown for maps
    if 'specific-areas-dropdown' in trigger_id:
        return current_path, dash.no_update, selected_map_area, None, None

    return current_path, stored_area, selected_map_area, dash.no_update, dash.no_update

# Function to apply the mapping and rename columns
def prepare_dataframe(df_path, mapping_file_path):
    #df = pd.read_csv(df_path, delimiter='\t')
    df = pd.read_csv(df_path)
    # Apply ID to name mapping
    id_to_name_mapping = load_id_to_name_mapping(mapping_file_path)
    df['Name'] = df['pokemon_id'].map(id_to_name_mapping).fillna("Unknown")

    # Apply column display names
    column_names_mapping = get_column_display_names(df)
    df.rename(columns=column_names_mapping, inplace=True)

    # Add a new column for image paths
    df['image_path'] = df.apply(construct_table_image_path, axis=1)

    # Round specified columns
    round_columns(df)

    return df

# Callback for updating the table based on dropdown selections, search, and sort
@app.callback(
    [Output('table-area-content', 'children'),
     Output('pagination-placeholder', 'children'),
     Output('sorting-state', 'data')],
    [Input('url', 'pathname'),  # Add URL as an input
     Input('table-event-dropdown', 'value'),
     Input('specific-table-areas-dropdown', 'value'),
     Input({'type': 'sort-button', 'index': ALL}, 'n_clicks'),
     Input('table-search-input', 'value')],
    [State('sorting-state', 'data')]
)
def update_table_area_content(pathname, event_type, selected_table_area, sort_clicks, search_query, sorting_state):
    # If no area is selected or if the pathname doesn't start with '/table-areas', prompt the user.
    if not pathname.startswith('/table-areas') or not selected_table_area:
        return html.Div(), html.Div(), sorting_state

    # Extract the page number from the pathname
    path_parts = pathname.split('/')
    if len(path_parts) > 3 and path_parts[3].startswith('page='):
        current_page = int(path_parts[3].split('=')[1])
    else:
        current_page = 1


    df_path = f"../CSV/Areas{event_type}/{selected_table_area}{event_type}.csv"
    df = prepare_dataframe(df_path, '../CSV/id_to_name.json')

    # Filter based on search query
    if search_query:
        df_filtered = df[df['Name'].str.contains(search_query, case=False, na=False)].copy()
    else:
        df_filtered = df.copy()

    ctx = dash.callback_context
    if ctx.triggered and 'sort-button' in ctx.triggered[0]['prop_id']:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        sort_column = json.loads(button_id)['index']

        if sorting_state['column'] == sort_column:
            # Toggle the sort direction
            sort_direction = 'asc' if sorting_state['direction'] == 'desc' else 'desc'
        else:
            # New column, start with ascending sort
            sort_direction = 'asc'

        # Update sort state and sort the DataFrame
        sorting_state = {'column': sort_column, 'direction': sort_direction}
        df_filtered = df_filtered.sort_values(by=sort_column, ascending=(sort_direction == 'asc'))

    # Calculate the number of pages and slice the dataframe to only include the current page
    page_count = ceil(len(df_filtered) / ROWS_PER_PAGE)
    start_idx = (current_page - 1) * ROWS_PER_PAGE
    end_idx = start_idx + ROWS_PER_PAGE
    df_page = df_filtered.iloc[start_idx:end_idx]

    # Generate table and pagination
    table = generate_html_table(df_page, sorting_state['column'], sorting_state['direction'])
    pagination_controls = generate_pagination_controls(current_page, page_count)

    return table, pagination_controls, sorting_state


homepage_content = html.Div([
    #html.Img(src="assets/wallpapperpogo.png", style={'width': '50%', 'height': '50%', 'marginLeft': 'auto', 'marginRight': 'auto'}),
    html.Div(
        html.Img(src="assets/wallpapperpogo.png", style={'width': '60%'}),
        style={'display': 'flex', 'justifyContent': 'center'}
    ),

    dcc.Markdown('''
            ## Introduction
        ''', style={'margin': '5%', 'textAlign': 'center'}),
    dcc.Markdown('''
            Welcome to an insightful journey through the world of Pokémon Go. This exploration uncovers the unique patterns and dynamics of this globally beloved game. Whether you're an avid player or simply curious, this analysis brings to light the fascinating aspects of Pokémon Go.
        ''', style={'margin': '5%', 'textAlign': 'justify'}),
    dcc.Markdown('''
            ## Summary
        ''', style={'margin': '5%', 'textAlign': 'center'}),
    dcc.Markdown('''
            In this comprehensive analysis, we delve into an extensive dataset of Pokémon Go, shedding light on the game's dynamics and Pokémon behavior. Our exploration is rooted in a robust database, backed by MySQL, and includes a staggering total of 49,692,539 Pokémon observations, categorized into event and non-event data.
        ''', style={'margin': '5%', 'textAlign': 'justify'}),
    dcc.Markdown('''
            **Highlights of the Analysis:**
            - **Event vs. Non-Event Data:** With 27,173,604 Pokémon recorded during events and 22,518,935 outside these periods, our study offers insights into how special events significantly impact the gaming experience, influencing both Pokémon availability and player interactions.
            - **Rarity and Distribution:** Unravel the patterns of Pokémon rarity and distribution, understanding where and when you're most likely to encounter rare species.
            - **Geolocation Analysis:** Investigate how geographical locations affect Pokémon spawns, providing a tailored experience in various settings.
            - **Surge Analysis:** Decode the strategies behind Pokémon spawns, particularly during times of heightened player activity, to understand the game’s spawning algorithm better.
            
            **Technical Backbone:**
            - My analysis is powered by Python, utilizing Pandas for data filtering and transformation. An automated script facilitates seamless data retrieval from the MySQL database, adaptable for continuous updates with live datasets.
            - The webfront you're navigating is crafted using Dash, enriched with visualizations from libraries like Plotly and Folium.
            - The data, meticulously stored and organized in CSV files, forms the foundation of our analysis.
            
            Join me in this intriguing journey through the world of Pokémon Go, where data reveals untold stories and patterns, offering a fresh perspective on a globally beloved game.

            **Explore the Analysis:**

            Each section offers unique insights into different aspects of Pokémon Go. Choose a topic below to delve into the data and discoveries:

            1. **Areas Table**: For detailed statistical analysis of Pokémon distributions across different areas.
            2. **Areas Map**: To visually explore Pokémon locations and their geospatial patterns.
            3. **Surge Analysis**: Explore hourly Pokémon spawn trends across all event and non-event days. This focused view reveals how Pokémon quality fluctuates throughout a typical 24-hour cycle.

            ---

            Select a button below to begin exploring the corresponding section:
        ''', style={'margin': '5%', 'textAlign': 'justify'}),
    # Add more content as needed
], id='homepage-content')

tablepage_content = html.Div([
    dcc.Markdown('''
        ## Rarity & Distribution
    ''', style={'margin': '5%', 'textAlign': 'center'}),
    dcc.Markdown('''
        Embark on a comprehensive analysis of Pokémon data tailored to your selection. This section presents extensive insights on each species, focusing on attributes and rarity. Explore metrics such as:

        - **IV 100% and IV 0%**: Understand the extremes of Pokémon potential.
        - **Shiny Pokémon**: Track the occurrence of these rare variants.
        - **Top 1 PvP League Ranks**: Assess the competitive edge of Pokémon in player battles.
        - **Average Attributes**: Gauge typical values of Weight, Height, Size, and IVs.

        Enhance your exploration with interactive features:
        - **Search Function**: Quickly find Pokémon using the word search feature.
        - **Sortable Columns**: Organize data ascendingly or descendingly for deeper insights.

        **Important Note:** Rarity affects data. Some Pokémon, observed only a few times, may have inflated statistics.
    ''', style={'margin': '5%', 'textAlign': 'justify'})
], id='tablepage-content')


mappage_content = html.Div([
    dcc.Markdown('''
        ## Geolocation Analysis
    ''', style={'margin': '5%', 'textAlign': 'center'}),
    dcc.Markdown('''
        Dive into an interactive map that brings Pokémon sightings to life! Here's what you'll discover:

        - **Interactive Map**: Spot where Pokémon have been observed, based on average coordinates from their sightings.
        - **Geofences Defined**: Learn about specific areas with virtual geographic boundaries where Pokémon appear.
        - **Pokémon Hotspots**: Identify the best spots for finding certain Pokémon, enhancing your gaming strategy.
        - **Customizable Filters**: Tailor the map to your interests by selecting individual Pokémon or multiple ones for focused insights.

        **Key Considerations:** 
        - Rarity influences data interpretation. 
        - Infrequent appearances of certain Pokémon may alter location insights. 
        - When Pokémon with numerous observations are central on the map, it suggests a bias toward a specific location, indicating their potential presence in the surrounding areas.
    ''', style={'margin': '5%', 'textAlign': 'justify'})
], id='mappage-content')

surgepage_content = html.Div([
    dcc.Markdown('''
        ## Surge Analysis: A 24-Hour Pokémon Dynamics
    ''', style={'margin': '5%', 'textAlign': 'center'}),
    dcc.Markdown('''
        Welcome to the pulse of Pokémon Go - the Surge Analysis. This section unravels the fascinating hourly dynamics of Pokémon activity over a 24-hour cycle. Discover how the game's ecosystem changes with each hour, offering a comprehensive view of Pokémon appearances and qualities, influenced by Events and No Event days.

        Key Aspects of Surge Analysis:
        - **Hourly Insights**: Explore the fluctuating patterns of Pokémon encounters as they evolve hour by hour.
        - **Quality Metrics**: Investigate the variation in Pokémon qualities, focusing on IV (Individual Values) of 100% and 0%, and top rankings in PvP Leagues, providing insights into their combat prowess.
        - **Event vs. No Event Comparison**: Contrast the changes in Pokémon behavior and spawning during special events as compared to normal days.
        - **Interactive Visualization**: Engage with dynamic, easy-to-understand graphs that vividly illustrate the hourly trends in Pokémon activity.

        The Surge Analysis is a treasure trove for players and data enthusiasts alike, offering a deeper understanding of the strategic deployment of Pokémon by the game, especially during peak player hours.

        Embark on this enlightening journey through a day in the world of Pokémon Go, where every hour tells a new story of Pokémon behavior and player interaction.
    ''', style={'margin': '5%', 'textAlign': 'justify'})
], id='surgepage-content')

# Button Container to create a proper margin with the footer.

# Define the footer
footer = html.Footer(
    [
        html.Div("Developed by @Hugo Gomes", style={'textAlign': 'left', 'display': 'inline-block', 'margin': '10px'}),
        html.Div("Development Date: 17-12-2023", style={'textAlign': 'right', 'display': 'inline-block', 'float': 'right', 'margin': '10px'})
    ],
    style={'position': 'fixed', 'bottom': 0, 'width': '100%', 'backgroundColor': '#f8f9fa'}
)

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    homepage_content,
    tablepage_content,
    mappage_content,
    surgepage_content,
    html.Div(
        [
            html.Button('Table Overview', id='to-table', style={
                'margin-right': '10px',
                'background-color': '#007BFF',
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'text-align': 'center',
                'text-decoration': 'none',
                'display': 'inline-block',
                'font-size': '16px',
                'border-radius': '5px',
                'cursor': 'pointer',
                'marginBottom': '10px'
            }),
            html.Button('Map View', id='to-map', style={
                'margin-right': '10px',
                'background-color': '#007BFF',
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'text-align': 'center',
                'text-decoration': 'none',
                'display': 'inline-block',
                'font-size': '16px',
                'border-radius': '5px',
                'cursor': 'pointer',
                'marginBottom': '10px'
            }),
            html.Button('Activity Peaks', id='to-surge', style={
                'margin-right': '10px',
                'background-color': '#007BFF',
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'text-align': 'center',
                'text-decoration': 'none',
                'display': 'inline-block',
                'font-size': '16px',
                'border-radius': '5px',
                'cursor': 'pointer',
                'marginBottom': '10px'
            }),
            html.Button('Home', id='to-home', style={
                'display': 'none',
                'background-color': '#007BFF',
                'color': 'white',
                'border': 'none',
                'padding': '10px 20px',
                'text-align': 'center',
                'text-decoration': 'none',
                'display': 'inline-block',
                'font-size': '16px',
                'border-radius': '5px',
                'cursor': 'pointer',
                'marginBottom': '10px'
            }),
        ],
        style={
            'display': 'flex',
            'justify-content': 'center',
            'align-items': 'center',
            'flex-direction': 'row',
            'margin-top': '10px',
            'margin-bottom': '80px'
        }
    ),
    footer,    
    dcc.Store(id='sorting-state', data={'column': None, 'direction': 'asc'}),
    dcc.Store(id='selected-table-area-store'),
    # Layout for table and map view
    html.Div(id='table-layout', children=create_table_layout()),  # Includes dropdowns for table view
    html.Div(id='map-layout', children=create_map_layout()),      # Includes dropdowns for map view
    html.Div(id='surge-layout', style={'display': 'none'}, children=[
    create_surge_layout(),
    html.Div(id='surge-graph-container')
    ]), # Includes dropdowns for surge view 
    # You'll also need to add a hidden div to your layout for the dummy output
    html.Div(id='dummy-div', style={'display': 'none'}),
    html.Div(id='table-content'),  # Placeholder for table data
    html.Div(id='map-content'),    # Placeholder for map data

])

# Callback for updating the page content based on URL and showing/hiding pagination
@app.callback(
    [Output('table-layout', 'style'),
     Output('map-layout', 'style'),
     Output('surge-layout', 'style'),
     Output('to-home', 'style'),
     Output('homepage-content', 'style'),
     Output('tablepage-content', 'style'),
     Output('mappage-content', 'style'),
     Output('surgepage-content', 'style')],
    [Input('url', 'pathname'),
     Input('specific-table-areas-dropdown', 'value')]
)
def display_page(pathname, selected_area):
    # Define the base style for the home button
    base_home_button_style = {
            'margin-right': '10px',
            'background-color': '#007BFF',
            'color': 'white',
            'border': 'none',
            'padding': '10px 20px',
            'text-align': 'center',
            'text-decoration': 'none',
            'display': 'inline-block',
            'font-size': '16px',
            'border-radius': '5px',
            'cursor': 'pointer',
            'marginBottom': '10px'
    }

    if pathname.startswith('/table-areas'):
        table_layout_style = {'display': 'block'}
        map_layout_style = {'display': 'none'}
        surge_layout_style = {'display': 'none'}
        home_button_style = base_home_button_style
        homepage_content_style = {'display': 'none'} 
        tablepage_contet_style = {'display': 'block'}
        mappage_content_style = {'display': 'none'} 
        surgepage_content_style = {'display': 'none'}       
    elif pathname.startswith('/map-areas'):
        table_layout_style = {'display': 'none'}
        map_layout_style = {'display': 'block'}
        surge_layout_style = {'display': 'none'}
        home_button_style = base_home_button_style
        homepage_content_style = {'display': 'none'} 
        tablepage_contet_style = {'display': 'none'} 
        mappage_content_style = {'display': 'block'} 
        surgepage_content_style = {'display': 'none'}                                 
    elif pathname.startswith('/surge'):
        table_layout_style = {'display': 'none'}
        map_layout_style = {'display': 'none'}
        surge_layout_style = {'display': 'block'}
        home_button_style = base_home_button_style
        homepage_content_style = {'display': 'none'}
        tablepage_contet_style = {'display': 'none'}  
        mappage_content_style = {'display': 'none'} 
        surgepage_content_style = {'display': 'block'}                                
    else:
        table_layout_style = {'display': 'none'}
        map_layout_style = {'display': 'none'}
        surge_layout_style = {'display': 'none'}
        home_button_style = {'display': 'none'}
        homepage_content_style = {'display': 'block'}
        tablepage_contet_style = {'display': 'none'}  
        mappage_content_style = {'display': 'none'}
        surgepage_content_style = {'display': 'none'}                         
    return table_layout_style, map_layout_style, surge_layout_style, home_button_style, homepage_content_style, tablepage_contet_style, mappage_content_style, surgepage_content_style

app.clientside_callback(
    """
    function(pathname, mapContent, tableContent, surgeContent) {
        if(pathname.includes('/map-areas') && mapContent) {
            setTimeout(function() {
                window.scrollToElement('map-area-content');
            }, 500); // Adjust the timeout as needed
        }
        else if(pathname.includes('/table-areas') && tableContent) {
            setTimeout(function() {
                window.scrollToElement('table-area-content');
            }, 500); // Adjust the timeout as needed
        }
        else if(pathname.includes('/surge') && surgeContent) {
            setTimeout(function() {
                window.scrollToElement('surge-graph-container');
            }, 500); // Adjust the timeout as needed
        }
        return '';
    }
    """,
    Output('dummy-div', 'children'),
    [Input('url', 'pathname'), 
     Input('map-area-content', 'children'), 
     Input('table-area-content', 'children'),
     Input('surge-graph-container', 'children')],
    prevent_initial_call=True    
)



if __name__ == '__main__':
    #app.run_server(debug=False, port=8065)    
    #app.run_server(debug=False, host='0.0.0.0', port=8065)
    app.run_server(debug=True, port=8065)