import dash
from dash import html, dcc, callback, State
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

def construct_image_path(row):
    # Assuming you have a function to generate image paths based on pokemon_id and form
    # Modify this function based on your actual image path structure
     return f"https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/pokemon/{row['pokemon_id']}_f{row['form']}.png"


def generate_html_table(df, current_page, rows_per_page):
    # Add a new column for image paths
    df['image_path'] = df.apply(construct_image_path, axis=1)
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
        # Add more mappings as needed
    }

    # Determine columns to display (exclude 'pokemon_id' and 'form')
    columns_to_display = [col for col in df.columns if col not in ["pokemon_id", "form", "avg_lat", "avg_lon", "image_path"]]

    # Calculate start and end index based on the current page
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    # Extract the rows for the current page
    current_page_df = df.iloc[start_idx:end_idx]

    # Add an empty row at the end to extend the vertical line of the column header
    empty_row = pd.Series()
    current_page_df = pd.concat([current_page_df, pd.DataFrame([empty_row])])

    # Build HTML table dynamically with Bootstrap styling
    table_content = [html.Thead([html.Tr([html.Th("Pokemon", className='align-middle header-cell', style={'white-space': 'nowrap'})] + [html.Th(column_display_names.get(col, col), className='align-middle header-cell', style={'white-space': 'nowrap'}) for col in columns_to_display])])]
    for _, row in current_page_df.iterrows():
        img_src = row["image_path"]
        img_html = html.Img(src=img_src, style={"max-width": "50px", "max-height": "50px"})
        row_content = [html.Td(img_html, className='align-middle')] + [
            html.Td([html.Div(row[col], className='content', style={'white-space': 'nowrap'})], className='align-middle')
            for col in columns_to_display
        ]
        table_content.append(html.Tr(row_content, className='table-row'))

    return dbc.Table(table_content, striped=True, bordered=True, hover=True, responsive=True)

def create_table_dashboard(df_path):
    # Load the DataFrame
    df = pd.read_csv(df_path, delimiter='\t')

    # Set the number of rows per page
    rows_per_page = 10

    # Create an initial table with the first page
    table_content = generate_html_table(df, current_page=1, rows_per_page=rows_per_page)

    return html.Div([
        html.H1("Pokémon Table Dashboard"),
        dcc.Graph(id="table-graph", figure={}, config={'editable': False}),
        html.Div(id='table-content', children=[table_content]),
        dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
        State('table-graph', 'relayoutData'),
        State('interval-component', 'n_intervals'),
    ])

if __name__ == '__main__':
    #df_path = "path/to/your/data.csv"  # Replace with your actual data path
    app.layout = html.Div([
        create_table_dashboard(df_path)
    ])

    app.run_server(debug=True)
