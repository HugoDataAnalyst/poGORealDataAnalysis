import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import sys

sys.path.insert(0, '../Python/')  # Add the path to Python files
from Test import quicktestmap  # Import the function

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Pokémon GO Data Analysis"),
    dcc.Markdown("### Welcome to an intensive analysis with data from the video game called Pokémon GO. \n We will endorse in a search for patterns of spawns for each pokémon in the data set as well as their statistics."),
   
    # Space for images and text (you can add components here)

    dcc.Tabs(id='tabs', value='pokemon-tab', children=[
        dcc.Tab(label='', value='pokemon-tab', style={
        'background-image': 'url("https://github.com/HugoDataAnalyst/UICONS/raw/main/pokemon/4_f896.png")',
        'background-size': 'auto',
        'background-position': 'center',
        'color': 'black'
        },
        selected_style={
            'background-image': 'url("https://github.com/HugoDataAnalyst/UICONS/raw/main/pokemon/4_f896.png")',
            'background-size': 'auto',
            'background-position': 'center',
            'color': 'black'
        },
        children=[
            dcc.Tabs(id='pokemon-subtabs', value='lights-festival-tab', children=[
                dcc.Tab(label='Lights Festival Event', value='lights-festival-tab'),
                dcc.Tab(label='No Event', value='no-event-tab'),
            ]),
            html.Div(id='pokemon-subtabs-content')
        ]),
        dcc.Tab(label='Raids', value='raids-tab', style={'background-image': 'url("/path/to/raids_image.jpg")'}),
        dcc.Tab(label='Quests', value='quests-tab', style={'background-image': 'url("/path/to/quests_image.jpg")'}),
        dcc.Tab(label='Invasions', value='invasions-tab', style={'background-image': 'url("/path/to/invasions_image.jpg")'}),
    ]),

    html.Div(id='tabs-content')
])

# Define callback to update the content based on the selected sub-tab in the "Pokemon" tab
@app.callback(Output('pokemon-subtabs-content', 'children'),
              [Input('pokemon-subtabs', 'value')])
def update_pokemon_subtabs_content(selected_subtab):
    if selected_subtab == 'lights-festival-tab':
        return html.Div([
            dcc.Tabs(id='lights-festival-subtabs', value='areas-tab', children=[
                dcc.Tab(label='Areas', value='areas-tab'),
                dcc.Tab(label='Global', value='global-tab'),
            ]),
            html.Div(id='lights-festival-subtabs-content')
        ])
    elif selected_subtab == 'no-event-tab':
        return html.Div("Content for No Event tab")

    # If no sub-tab is selected, prevent updating the content
    raise PreventUpdate

# Define callback to update the content based on the selected sub-sub-tab in the "Lights Festival Event" tab
@app.callback(Output('lights-festival-subtabs-content', 'children'),
              [Input('lights-festival-subtabs', 'value')])
def update_lights_festival_subtabs_content(selected_subsubtab):
    if selected_subsubtab == 'areas-tab':
        return html.Div([
            dcc.Dropdown(
                id='section-dropdown',
                options=[
                    {'label': 'Portugal Norte', 'value': 'Portugal Norte'},
                    {'label': 'Portugal Centro', 'value': 'Portugal Centro'},
                ],
                value='Portugal Centro',  # Default selected value
                style={'font-weight': 'bold'}
            ),
            dcc.Dropdown(
                id='areas-dropdown',
                options=[],
                value='Espinho', # Default selected value 
            ),
            html.Div(id='selected-area-content')
        ])
    elif selected_subsubtab == 'global-tab':
        return html.Div("Content for Global tab")
    elif selected_subsubtab == 'no-event-tab':
        return html.Div("Content for No Event sub-tab")

    # If no sub-sub-tab is selected, prevent updating the content
    raise PreventUpdate

# Define callback to update the options in the areas dropdown based on the selected section
@app.callback(
    Output('areas-dropdown', 'options'),
    [Input('section-dropdown', 'value')]
)
def update_areas_options(selected_section):
    if selected_section == 'Portugal Norte':
        return [
            {'label': 'Porto', 'value': 'Porto'}
        ]
    elif selected_section == 'Portugal Centro':
        return [
            {'label': 'Aveiro', 'value': 'Aveiro_Esgueira_SantaJoana'},
            {'label': 'Espinho', 'value': 'Espinho'},
            {'label': 'Grijó', 'value': 'Grijo'},
        ]
    else:
        return []

# Define callback to update the content based on the selected area in the dropdown
@app.callback(Output('selected-area-content', 'children'),
              [Input('areas-dropdown', 'value')])
def update_selected_area_content(selected_area):
    try:
        # Call the modified quicktestmap function and get the Plotly figure based on the selected area
        fig = quicktestmap(f"../CSV/AreasLF/{selected_area}LF.csv")

        # Convert the Plotly figure to HTML and display it in the layout
        graph_content = dcc.Graph(figure=fig)
        return [graph_content]
    except Exception as e:
        print(str(e))
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)
