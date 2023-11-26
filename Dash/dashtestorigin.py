import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import sys
import folium
from folium import plugins

sys.path.insert(0, '../Python/')  # Add the path to Python files
from Test import quicktestmap  # Import the function
from Test import quicktestmapv2

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Pokémon GO Data Analysis"),
    dcc.Markdown("### Welcome to an intensive analysis with data from the video game called Pokémon GO. \n We will endorse in a search for patterns of spawns for each pokémon in the data set as well as their statistics."),
   
    dcc.Tabs(id='tabs', value='pokemon-tab', children=[
        dcc.Tab(label='', value='pokemon-tab', style={
            'background-image': 'url("https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/pokemon.png")',
            'background-size': 'cover',  # Use 'cover' to maintain aspect ratio and cover the entire tab
            'background-position': 'center',
            'color': 'black',
            'width': '300px',
            'height': '250px',  # Adjust the width as needed
            'margin-right': '10px'
        },
        selected_style={
            'background-image': 'url("https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/pokemon.png")',
            'background-size': 'cover',
            'background-position': 'center',
            'color': 'black',
            'width': '300px',
            'height': '250px',
            'margin-right': '10px'
        },
        children=[
            dcc.Tabs(id='pokemon-subtabs', value='lights-festival-tab', children=[
                dcc.Tab(label='Lights Festival Event', value='lights-festival-tab'),
                dcc.Tab(label='No Event', value='no-event-tab'),
            ]),
            html.Div(id='pokemon-subtabs-content')
        ]),
        dcc.Tab(label='', value='raids-tab', style={
            'background-image': 'url("https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/raid.png")',
            'background-size': 'cover',
            'background-position': 'center',
            'color': 'black',
            'width': '300px',
            'height': '250px',
            'margin-right': '10px'
        }),
        dcc.Tab(label='', value='quests-tab', style={
            'background-image': 'url("https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/quest.png")',
            'background-size': 'cover',
            'background-position': 'center',
            'color': 'black',
            'width': '300px',
            'height': '250px',
            'margin-right': '10px'
        }),
        dcc.Tab(label='', value='invasions-tab', style={
            'background-image': 'url("https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/misc/invasion.png")',
            'background-size': 'cover',
            'background-position': 'center',
            'color': 'black',
            'width': '300px',
            'height': '250px'
            
        }),
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
        return html.Div([
            dcc.Tabs(id='no-event-subtabs', value='areas-tab', children=[
                dcc.Tab(label='Areas', value='areas-tab'),
                dcc.Tab(label='Global', value='global-tab'),
            ]),
            html.Div(id='no-event-subtabs-content')
        ])

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
                    {'label': 'North Portugal', 'value': 'North Portugal'},
                    {'label': 'Center Portugal', 'value': 'Center Portugal'},
                ],
                value='Center Portugal',  # Default selected value
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
# Define callback to update the content based on the selected sub-sub-tab in the "No Event" tab
@app.callback(Output('no-event-subtabs-content', 'children'),
              [Input('no-event-subtabs', 'value')])
def update_no_event_subtabs_content(selected_subsubtab):
    if selected_subsubtab == 'areas-tab':
        return html.Div([
            dcc.Dropdown(
                id='no-event-section-dropdown',
                options=[
                    {'label': 'North Portugal', 'value': 'North Portugal'},
                    {'label': 'Center Portugal', 'value': 'Center Portugal'},
                ],
                value='Center Portugal',  # Default selected value
                style={'font-weight': 'bold'}
            ),
            dcc.Dropdown(
                id='no-event-areas-dropdown',
                options=[],
                value='Espinho',  # Default selected value
            ),
            html.Div(id='no-event-selected-area-content')
        ])
    elif selected_subsubtab == 'global-tab':
        return html.Div("Content for Global tab - No Event")
    
    # If no sub-sub-tab is selected, prevent updating the content
    raise PreventUpdate

# Define callback to update the options in the areas dropdown based on the selected section
@app.callback(
    Output('areas-dropdown', 'options'),
    [Input('section-dropdown', 'value')]
)
def update_areas_options(selected_section):
    if selected_section == 'North Portugal':
        return [
            {'label': 'Porto', 'value': 'Porto'}
        ]
    elif selected_section == 'Center Portugal':
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
        # Call the modified quicktestmapv2 function and get the Folium map based on the selected area
        folium_map = quicktestmapv2(f"../CSV/AreasLF/{selected_area}LF.csv")
        
        # Save the Folium map as an HTML file
        folium_map.save("folium_map.html")
        
        # Use html.Iframe to embed the Folium map in the Dash layout
        iframe_content = html.Iframe(srcDoc=open("folium_map.html", "r").read(), width="100%", height="600px")
        
        return [iframe_content]
    except Exception as e:
        print(str(e))
        raise PreventUpdate

# Define callback to update the options in the areas dropdown based on the selected section for No Event
@app.callback(
    Output('no-event-areas-dropdown', 'options'),
    [Input('no-event-section-dropdown', 'value')]
)
def update_no_event_areas_options(selected_section):
    if selected_section == 'North Portugal':
        return [
            {'label': 'Porto', 'value': 'Porto'}
        ]
    elif selected_section == 'Center Portugal':
        return [
            {'label': 'Aveiro', 'value': 'Aveiro_Esgueira_SantaJoana'},
            {'label': 'Espinho', 'value': 'Espinho'},
            {'label': 'Grijó', 'value': 'Grijo'},
        ]
    else:
        return []

# Define callback to update the content based on the selected area in the dropdown for No Event
@app.callback(Output('no-event-selected-area-content', 'children'),
              [Input('no-event-areas-dropdown', 'value')])
def update_no_event_selected_area_content(selected_area):
    try:
        # Call the modified quicktestmapv2 function and get the Folium map based on the selected area
        folium_map = quicktestmapv2(f"../CSV/AreasNE/{selected_area}NE.csv")
        
        # Save the Folium map as an HTML file
        folium_map.save("folium_map_no_event.html")
        
        # Use html.Iframe to embed the Folium map in the Dash layout
        iframe_content = html.Iframe(srcDoc=open("folium_map_no_event.html", "r").read(), width="100%", height="600px")
        
        return [iframe_content]
    except Exception as e:
        print(str(e))
        raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)