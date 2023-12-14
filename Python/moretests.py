import dash
from dash import html, dcc, callback, State
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
def create_table_dashboard(df_path):


 
    # Load the DataFrame
    df = pd.read_csv(df_path, delimiter='\t')
    print("Loaded DataFrame successfully:", df.head())  # Add this line to check if the DataFrame is loaded correctly    
    # Function to construct image path based on pokemon_id and form
    def construct_image_path(row):
        if row['form'] == 0:
            return f"https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/pokemon/{row['pokemon_id']}.png"
        else:
            return f"https://github.com/HugoDataAnalyst/poGORealDataAnalysis/raw/main/Dash/UICONS/pokemon/{row['pokemon_id']}_f{row['form']}.png"


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
        # Add more mappings as needed
    }
    # Rename columns
    df.columns = [column_display_names.get(col, col) for col in df.columns]

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
    
    # Determine columns to display (exclude 'pokemon_id' and 'form')
    columns_to_display = [col for col in df.columns if col not in ["pokemon_id", "form", "avg_lat", "avg_lon", "image_path"]]    
    
    #Create a dictionary containing the processed data
    processed_data = {
        'columns_to_display': columns_to_display,
        'table_data': current_page_df.to_dict('records'),
    }
    return processed_data
    # Function to generate HTML table with images and delimiter bars
    def generate_html_table(df, current_page, rows_per_page):
        # Add a new column for image paths
        df['image_path'] = df.apply(construct_image_path, axis=1)



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

    # Function to generate pagination buttons
    def generate_pagination_buttons(total_pages, current_page):
        buttons = []

        # Previous page button
        if current_page > 1:
            prev_button = dbc.Button("Previous", color="primary", className="pagination-button")
            prev_link = dcc.Link(prev_button, href=f"/page-{current_page - 1}")
            buttons.append(prev_link)

        # Page numbers, input field, and ellipses
        for page in range(1, total_pages + 1):
            if current_page - 2 < page < current_page + 2:
                if page == current_page:
                    button = dbc.Button(f"{page}", color="primary", className="pagination-button active")
                else:
                    button = dbc.Button(f"{page}", color="primary", className="pagination-button")
                buttons.append(dcc.Link(button, href=f"/page-{page}"))
            elif buttons[-1] is not None:
                buttons.append(None)  # Add an ellipsis

        # Next page button
        if current_page < total_pages:
            next_button = dbc.Button("Next", color="primary", className="pagination-button")
            next_link = dcc.Link(next_button, href=f"/page-{current_page + 1}")
            buttons.append(next_link)

        # Input field
        input_field = dcc.Input(
            id='page-number-input',
            type='number',
            value=current_page,
            style={'width': '50px', 'margin': '0 10px'}
        )
        buttons.append(input_field)

        # Go to page button
        go_button = dbc.Button("Go", color="primary", className="pagination-button")
        go_link = dcc.Link(go_button, id='go-link', href='')
        buttons.append(go_link)

        return buttons

    # Example usage
    rows_per_page = 15  # Adjust the number of rows per page as needed
    total_rows = len(df)
    total_pages = (total_rows - 1) // rows_per_page + 1
    print("Total Rows:", total_rows)
    print("Total Pages:", total_pages)
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
    ])

    @app.callback(
        Output('go-link', 'href'),
        [Input('page-number-input', 'value')]
    )
    def update_go_link(page_number):
        if page_number:
            return f"/page-{page_number}"
        else:
            return ""

# Modify the callback to include the page-number-input value as an input
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('page-number-input', 'value')]  # Add this line
)
def display_page(pathname, current_page):
    if current_page is None:
        current_page = 1  # Default to page 1 if not provided
    else:
        current_page = int(current_page)  # Convert current_page to int
    content = [
        dbc.Row(dbc.Col(generate_html_table(df, current_page, rows_per_page), width=8), className='justify-content'),
        dbc.Row(dbc.Col(generate_pagination_buttons(total_pages, current_page), width=8), className='justify-content-center'),
    ]
    print("Content:", content)  # Add this line for debugging
    return content



    if __name__ == '__main__':
        app.run_server(debug=True)

# Example usage:
# create_table_dashboard("../CSV/AreasLF/EspinhoLF.csv")
