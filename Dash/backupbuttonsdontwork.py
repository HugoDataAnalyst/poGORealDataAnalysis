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
import os
sys.path.insert(0, '../Python/')
sys.path.insert(0, '../Dash/')
from verynicefoliummap import quicktestmapv2


import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

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
        'avg_weight': 'Avg Weight',
        'avg_height': 'Avg Height',
        'avg_size': 'Avg Size',
        'avg_atk': 'Avg Atk',
        'avg_def': 'Avg Def',
        'avg_sta': 'Avg Sta',
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
        'Avg Weight',
        'Avg Height',
        'Avg Size',
        'Avg Atk',
        'Avg Def',
        'Avg Sta',
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
    [Input('url', 'pathname'),
     Input('event-dropdown', 'value'),
     Input('specific-areas-dropdown', 'value'),
     Input('checklist-state', 'data')],
     prevent_initial_call=True # Prevent the callback from running upon initilization
)
def update_map_content(pathname, event_type, selected_area, checklist_state):
    # Only update map content when the pathname indicates map areas
    if not pathname.startswith('/map-areas') or not selected_area:
        return html.Div("Please select an area or navigate to the map view.")

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
    return html.Div([
        dcc.Dropdown(
            id='table-event-dropdown',
            options=[
                {'label': 'Lights Festival Event', 'value': 'LF'},
                {'label': 'No Event', 'value': 'NE'}
            ],
            value='LF',
            style={'font-weight': 'bold'}
        ),
        dcc.Dropdown(
            id='table-section-dropdown',
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
            id='specific-table-areas-dropdown',
            options=[], # Options will be set by callback
            value=None
        ),
        html.Div(
            dcc.Input(id='table-search-input', type='text', placeholder='Search by Name', debounce=True),
            id='search-query-container',
            style={'display': 'none'}  # Initially hidden
        ),        
        html.Div(id='table-area-content'),
        dcc.Store(id='table-sort-state', data={'column': None, 'direction': 'asc'})
    ])

# Callback to update areas dropdown (for table)
@app.callback(
    Output('specific-table-areas-dropdown', 'options'),
    [Input('table-section-dropdown', 'value')]
)
def set_specific_table_areas_options(selected_section):
    if selected_section == 'NorthPortugal':
        return [{'label': 'Porto', 'value': 'Porto'}]
    elif selected_section == 'CenterPortugal':
        return [
            {'label': 'Aveiro', 'value': 'Aveiro_Esgueira_SantaJoana'},
            {'label': 'Espinho', 'value': 'Espinho'},
            {'label': 'Grijó', 'value': 'Grijo'},
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


# Function to generate HTML table with images and delimiter bars
def generate_html_table(df, current_page, rows_per_page, sort_by=None, sort_direction='asc'):
    # Apply column display names
    column_names_mapping = get_column_display_names(df)
    df.rename(columns=column_names_mapping, inplace=True)

    ordered_columns = ['Name'] + [col for col in df.columns if col not in ["pokemon_id", "form", "avg_lat", "avg_lon", "image_path", "Name"]]
    # Determine columns to display (exclude 'pokemon_id' and 'form')
    columns_to_display = [col for col in ordered_columns if col in df.columns]

    # Add a new column for image paths
    df['image_path'] = df.apply(construct_table_image_path, axis=1)

    # Sort the DataFrame if sort parameters are provided
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=(sort_direction == 'asc'))

    # Pagination logic
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    page_df = df.iloc[start_idx:end_idx]

    # Build the header row with sort buttons
    table_header = [html.Th(html.Div("Pokemon", className='header-label'), className='align-middle header-cell', style={'white-space': 'nowrap'})]
    for col in columns_to_display:
        button_text = column_names_mapping.get(col, col)
        if sort_by == col:
            button_text += ' ↓' if sort_direction == 'asc' else ' ↑'
        header_cell_content = html.Div(
            html.Button(
                button_text,
                id={'type': 'sort-button', 'index': col},
                className='header-button'
            ),
            className='header-label'
        )
        table_header.append(html.Th(header_cell_content, className='align-middle header-cell', style={'white-space': 'nowrap'}))

    # Build the table rows
    table_rows = []
    for _, row in page_df.iterrows():
        img_src = row["image_path"]
        img_html = html.Img(src=img_src, style={"max-width": "50px", "max-height": "50px"})
        row_content = [html.Td(img_html, className='align-middle')] + [
            html.Td(html.Div(row[col], className='content-cell'), className='align-middle')
            for col in columns_to_display
        ]
        table_rows.append(html.Tr(row_content))

    # Combine header and rows
    table_content = [html.Thead(html.Tr(table_header))] + [html.Tbody(table_rows)]

    return dbc.Table(table_content, striped=True, bordered=True, hover=True, responsive=True)

# Function to generate pagination buttons
def generate_pagination_buttons(total_pages, current_page, selected_area):
    buttons = []

    # Check if an area is selected; if not, return an empty div to hide pagination
    if not selected_area:
        return html.Div()    

    # Previous Button
    if current_page > 1:
        prev_button = html.Button("Previous", id='prev-page-button', n_clicks=0, className="pagination-button")
        buttons.append(prev_button)

    # Page numbers, input field, and ellipses
    for page in range(1, total_pages + 1):
        if current_page - 2 < page < current_page + 2:
            button_text = str(page)
            button = dbc.Button(button_text, color="primary", className="pagination-button" if page != current_page else "pagination-button active")
            link = dcc.Link(button, href=f"/table-areas/{selected_area}/page-{page}")
            buttons.append(link)
        elif page == current_page + 2 or page == current_page - 2:
            # Ellipsis for jumping more than one page
            buttons.append(html.Span("...", className="pagination-ellipsis"))

    # Next Button
    if current_page < total_pages:
        next_button = html.Button("Next", id='next-page-button', n_clicks=0, className="pagination-button")
        buttons.append(next_button)

    # Input field and go button
    input_field = dcc.Input(
        id='page-number-input',
        type='number',
        value=current_page,
        style={'width': '50px', 'margin': '0 10px'}
    )
    go_button = html.Button("Go", id='go-button', n_clicks=0, className="pagination-button")
    # Include the selected area in the href for the go button as well
    go_link = dcc.Link(go_button, href=f"/table-areas/{selected_area}/page-{input_field.value}")
    buttons.extend([input_field, go_link])

    return html.Div(buttons, className="pagination-container")

def calculate_new_page(current_page_data, trigger_id, go_page_number):
    current_page = current_page_data['current_page']
    if 'prev-page-button' in trigger_id and current_page > 1:
        return current_page - 1
    elif 'next-page-button' in trigger_id:
        return current_page + 1
    elif 'go-button' in trigger_id:
        # Ensure the go_page_number is within valid range
        return max(1, min(go_page_number, current_page_data['total_pages']))
    return current_page

# Modified handle_navigation callback
@app.callback(
    [Output('url', 'pathname'),
     Output('specific-table-areas-dropdown', 'value'),  # Reset selection for table
     Output('specific-areas-dropdown', 'value')],       # Reset selection for map
    [Input('prev-page-button', 'n_clicks'),
     Input('next-page-button', 'n_clicks'),
     Input('go-button', 'n_clicks'),
     Input('to-table', 'n_clicks'),
     Input('to-map', 'n_clicks'),
     Input('specific-table-areas-dropdown', 'value'),  # Area selection for table
     Input('specific-areas-dropdown', 'value')],       # Area selection for map
    [State('url', 'pathname'),  # Current URL
     State('current-page-store', 'data'),
     State('page-number-input', 'value')]
)
def handle_navigation(prev_clicks, next_clicks, go_clicks, to_table_clicks, to_map_clicks, 
                      selected_table_area, selected_map_area, current_path, current_page_data, go_page_number):
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if 'to-table' in trigger_id:
        # Reset table area selection and navigate to table-areas
        return '/table-areas', None, dash.no_update
    elif 'to-map' in trigger_id:
        # Reset map area selection and navigate to map-areas
        return '/map-areas', dash.no_update, None

    # Pagination and navigation logic
    if 'prev-page-button' in trigger_id or 'next-page-button' in trigger_id or 'go-button' in trigger_id:
        new_page = calculate_new_page(current_page_data, trigger_id, go_page_number)
        area = current_path.split('/')[2] if len(current_path.split('/')) > 2 else ''
        return f'/table-areas/{selected_table_area}/page-{new_page}', dash.no_update, dash.no_update

    elif 'specific-table-areas-dropdown' in trigger_id:
        # Navigate to selected table area
        return f'/table-areas/{selected_table_area}' if selected_table_area else '/table-areas', dash.no_update, dash.no_update
    elif 'specific-areas-dropdown' in trigger_id:
        # Navigate to selected map area
        return f'/map-areas/{selected_map_area}' if selected_map_area else '/map-areas', dash.no_update, dash.no_update

    # Return no update if none of the above conditions are met
    return dash.no_update, dash.no_update, dash.no_update



# Function to apply the mapping and rename columns
def prepare_dataframe(df_path, mapping_file_path):
    df = pd.read_csv(df_path, delimiter='\t')

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
     Output('sorting-state', 'data')],
    [Input('url', 'pathname'),  # Add URL as an input
     Input('table-event-dropdown', 'value'),
     Input('specific-table-areas-dropdown', 'value'),
     Input({'type': 'sort-button', 'index': ALL}, 'n_clicks'),
     Input('table-search-input', 'value'),
     Input('current-page-store', 'data')],
    [State('sorting-state', 'data')]
    #prevent_initial_call=True # Prevent the callback from running upon initilization
)
def update_table_area_content(pathname, event_type, selected_area, sort_clicks, search_query, current_page_data, sorting_state):
    # If no area is selected or if the pathname doesn't start with '/table-areas', prompt the user.
    if not pathname.startswith('/table-areas') or not selected_area:
        return html.Div("Please select an area or navigate to the table view."), sorting_state

    df_path = f"../CSV/Areas{event_type}/{selected_area}{event_type}.csv"
    df = prepare_dataframe(df_path, '../CSV/id_to_name.json')

    # Filter based on search query
    if search_query:
        df = df[df['Name'].str.contains(search_query, case=False, na=False)]

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
        df = df.sort_values(by=sort_column, ascending=(sort_direction == 'asc'))

    current_page = current_page_data['current_page']
    rows_per_page = 10
    table = generate_html_table(df, current_page, rows_per_page, sorting_state['column'], sorting_state['direction'])

    return table, sorting_state



# Pagination buttons included in the initial layout
pagination_buttons = html.Div([
    html.Button("Previous", id='prev-page-button', n_clicks=0, className="pagination-button"),
    html.Button("Next", id='next-page-button', n_clicks=0, className="pagination-button"),
    dcc.Input(id='page-number-input', type='number', value=1, style={'margin': '0 10px'}),
    html.Button("Go", id='go-button', n_clicks=0, className="pagination-button")
], id='pagination-buttons')  # This div is now part of the initial layout

# Main app layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Button('Areas-Table', id='to-table'),
    html.Button('Areas-Map', id='to-map'),
    dcc.Store(id='current-page-store', data={'current_page': 1}),
    dcc.Store(id='sorting-state', data={'column': None, 'direction': 'asc'}),
    # Layout for table and map view
    html.Div(id='table-layout', children=create_table_layout()),  # Includes dropdowns for table view
    html.Div(id='map-layout', children=create_map_layout()),      # Includes dropdowns for map view
    html.Div(id='table-content'),  # Placeholder for table data
    html.Div(id='map-content'),    # Placeholder for map data
    # Pagination buttons (initially hidden)
    html.Div(id='pagination-buttons', style={'display': 'none'}, children=[
        html.Button("Previous", id='prev-page-button', n_clicks=0, className="pagination-button"),
        html.Button("Next", id='next-page-button', n_clicks=0, className="pagination-button"),
        dcc.Input(id='page-number-input', type='number', value=1, style={'margin': '0 10px'}),
        html.Button("Go", id='go-button', n_clicks=0, className="pagination-button")
    ])
])


# Callback for updating the table and pagination
@app.callback(
    Output('pagination-placeholder', 'children'),
    [Input('url', 'pathname'),
     Input('table-event-dropdown', 'value'),
     Input('specific-table-areas-dropdown', 'value'),
     Input('table-search-input', 'value'),
     Input('current-page-store', 'data')],
    [State('table-sort-state', 'data')]
)
def update_table_and_pagination(pathname, event_type, selected_area, search_query, current_page_data, sort_state):
    # If we're not on a specific area page or no area is selected, don't show pagination
    if not pathname.startswith('/table-areas/') or not selected_area:
        return html.Div()  # Return empty Div to hide pagination

    total_pages = 1  # Default to 1 in case there is no data

    if selected_area and event_type:
        df_path = f"../CSV/Areas{event_type}/{selected_area}{event_type}.csv"
        df = pd.read_csv(df_path, delimiter='\t')

        # Apply filtering and sorting if necessary
        if search_query:
            df = df[df['Name'].str.contains(search_query, case=False, na=False)]
        if sort_state['column']:
            sort_direction = 'asc' if sort_state['direction'] == 'asc' else 'desc'
            df = df.sort_values(by=sort_state['column'], ascending=(sort_direction == 'asc'))

        # Calculate the total number of pages
        rows_per_page = 10  # or any other number
        total_rows = len(df)
        total_pages = max(1, (total_rows - 1) // rows_per_page + 1)

    # Update the store for total pages (if you're using a separate store for total pages, update that store instead)
    current_page_data['total_pages'] = total_pages

    # Call generate_pagination_buttons with selected_area
    current_page = current_page_data['current_page'] if 'current_page' in current_page_data else 1
    pagination_buttons = generate_pagination_buttons(total_pages, current_page, selected_area)

    return pagination_buttons

 
# Callback for updating the page content based on URL and showing/hiding pagination
@app.callback(
    [Output('pagination-buttons', 'style'),
     Output('table-layout', 'style'),
     Output('map-layout', 'style')],
    [Input('url', 'pathname'),
     Input('specific-table-areas-dropdown', 'value')]
)
def display_page(pathname, selected_area):
    if pathname.startswith('/table-areas'):
        table_layout_style = {'display': 'block'}
        map_layout_style = {'display': 'none'}
        # Show pagination buttons only if a specific area is selected
        pagination_buttons_style = {'display': 'block'} if selected_area else {'display': 'none'}
    elif pathname.startswith('/map-areas'):
        table_layout_style = {'display': 'none'}
        map_layout_style = {'display': 'block'}
        pagination_buttons_style = {'display': 'none'}
    else:
        table_layout_style = {'display': 'none'}
        map_layout_style = {'display': 'none'}
        pagination_buttons_style = {'display': 'none'}

    return pagination_buttons_style, table_layout_style, map_layout_style


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