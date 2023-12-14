import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import sys
import folium
from folium import plugins
from folium.plugins import MarkerCluster


sys.path.insert(0, '../Python/')  # Add the path to Python files
from Test import quicktestmapv2
from table_dashboard import create_table_dashboard

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
                value='Espinho',  # Default selected value
            ),
            dcc.Dropdown(
                id='display-option-dropdown',  # Added display option dropdown
                options=[
                    {'label': 'Map', 'value': 'Map'},
                    {'label': 'Table', 'value': 'Table'},
                ],
                value='Map',  # Default selected value
            ),
            dcc.Checklist(
                id='pokemon-image-filter',
                options=[],  # You will populate this dynamically in the callback
                value=[],  # Default selected options
                inline=True
            ),            
            html.Div(id='map-or-table-content')
        ])
    elif selected_subsubtab == 'global-tab':
        return html.Div("Content for Global tab")
    elif selected_subsubtab == 'no-event-tab':
        return html.Div("Content for No Event sub-tab")

    # If no sub-sub-tab is selected, prevent updating the content
    raise PreventUpdate
# Define callback to update the content based on the selected area in the dropdown
@app.callback(
    Output('map-or-table-content', 'children'),
    [Input('areas-dropdown', 'value'),
     Input('display-option-dropdown', 'value'),
     Input('pokemon-image-filter', 'value')],  # Add input for the filter box
    [State('section-dropdown', 'value')]
)
def update_selected_area_content(selected_area, filter_value, selected_images, selected_section):
    try:
        # Define the path to your DataFrame
        df_path = f"../CSV/AreasLF/{selected_area}LF.csv"    
        # Load the DataFrame
        df = pd.read_csv(df_path, delimiter='\t')

        def construct_image_path(row):
            if row['form'] == 0:
                return f"{row['pokemon_id']}.png"
            else:
                return f"{row['pokemon_id']}_f{row['form']}.png"

        df['pokemon_images'] = df.apply(construct_image_path, axis=1)

        # Add the filter box with checklist
        filter_box = dcc.Checklist(
            id='pokemon-image-filter',
            options=[{'label': img, 'value': img} for img in df['pokemon_images'].unique()],
            value=df['pokemon_images'].unique(),  # Default selected options
            inline=True
        )

        # Create a Folium Map centered at a random location
        map_center = [df["avg_lat"].mean(), df["avg_lon"].mean()]
        m = folium.Map(location=map_center, zoom_start=10)

        # Create a MarkerCluster group
        marker_cluster = MarkerCluster(
            sticky=False,
            maxClusterRadius=30
        ).add_to(m)

        # Add markers for each Pokémon with custom images to the MarkerCluster
        for _, row in df.iterrows():
            img_path = f"../Dash/UICONS/pokemon/{row['pokemon_images']}"
            img = folium.CustomIcon(
                icon_image=img_path,
                icon_size=(40, 40),
                icon_anchor=(15, 15),
                popup_anchor=(0, -35)
            )
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

            # Check if the image is selected in the filter box
            if row['pokemon_images'] in selected_images:
                folium.Marker(
                    location=[row["avg_lat"], row["avg_lon"]],
                    tooltip=f"Pokemon ID: {row['pokemon_id']}",
                    icon=img,
                    popup=folium.Popup(html=hover_text, max_width=300)
                ).add_to(marker_cluster)

        # Convert the Folium Map to HTML
        map_html = m._repr_html_()
        #return m

        # Save the Folium map as an HTML file
        m.save("folium_map.html")
        return [html.Iframe(srcDoc=map_html, width="100%", height="600px")]
        
    except Exception as e:
        print(str(e))
        raise PreventUpdate
# Define callback to update the options in the areas dropdown based on the selected section
@app.callback(
    [Output('areas-dropdown', 'options'),
     Output('pokemon-image-filter', 'options')],
    [Input('areas-dropdown', 'value')]  # Corrected the id to 'areas-dropdown'
)
def update_areas_options(selected_section):
    try:
        # Define the path to your DataFrame
        df_path = f"../CSV/AreasLF/{selected_section}LF.csv"    
        # Load the DataFrame
        df = pd.read_csv(df_path, delimiter='\t')

        # Define the 'pokemon_images' column
        def construct_image_path(row):
            if row['form'] == 0:
                return f"{row['pokemon_id']}.png"
            else:
                return f"{row['pokemon_id']}_f{row['form']}.png"

        df['pokemon_images'] = df.apply(construct_image_path, axis=1)

        area_options = [{'label': selected_section, 'value': selected_section}]
        pokemon_image_options = [{'label': img, 'value': img} for img in df['pokemon_images'].unique()]

        return [area_options, pokemon_image_options]
    except Exception as e:
        print(str(e))
        return [[], []]

# Add a new callback to update the page-number-input when the page is loaded without a specific page number
@app.callback(
    Output('page-number-input', 'value'),
    [Input('url', 'pathname')]
)
def set_default_page_number(pathname):
    return 1  # Set the default page number to 1






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