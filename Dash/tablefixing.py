import dash
from dash import html, dcc, callback, State, ALL
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
# Load the DataFrame
df_path = "../CSV/AreasLF/EspinhoLF.csv"
df = pd.read_csv(df_path, delimiter='\t')

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
# Apply the mapping
id_to_name_mapping = load_id_to_name_mapping('../CSV/id_to_name.json')
df = apply_name_mapping(df, id_to_name_mapping)

# Function to construct image path based on pokemon_id and form
def construct_image_path(row):
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


# Use the function to rename columns
column_names_mapping = get_column_display_names(df)
df.rename(columns=column_names_mapping, inplace=True)

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
# Apply the rounding function
round_columns(df)

# Function to generate HTML table with images and delimiter bars
def generate_html_table(df, current_page, rows_per_page, sort_by=None, sort_direction='asc'):
    # Rename columns using the provided display names
    df.rename(columns=column_names_mapping, inplace=True)
    
    # Round specified columns
    round_columns(df)

    # Sort the DataFrame
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=(sort_direction == 'asc'))

    # Add a new column for image paths
    df['image_path'] = df.apply(construct_image_path, axis=1)

    ordered_columns = ['Name'] + [col for col in df.columns if col not in ["pokemon_id", "form", "avg_lat", "avg_lon", "image_path", "Name"]]
    
    # Determine columns to display (exclude 'pokemon_id' and 'form')
    columns_to_display = [col for col in ordered_columns if col in df.columns]

    # Calculate start and end index based on the current page
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    # Extract the rows for the current page
    current_page_df = df.iloc[start_idx:end_idx]

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
    for _, row in current_page_df.iterrows():
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
def generate_pagination_buttons(total_pages, current_page):
    buttons = []

    # Previous page button
    if current_page > 1:
        prev_button = dbc.Button("Previous", color="primary", className="pagination-button")
        prev_link = dcc.Link(prev_button, href=f"/table-areas/page-{current_page - 1}")
        buttons.append(prev_link)

    # Page numbers, input field, and ellipses
    for page in range(1, total_pages + 1):
        if current_page - 2 < page < current_page + 2:
            button_text = str(page)
            button = dbc.Button(button_text, color="primary", className="pagination-button" if page != current_page else "pagination-button active")
            link = dcc.Link(button, href=f"/table-areas/page-{page}")
            buttons.append(link)
        elif page == current_page + 2 or page == current_page - 2:
            # Ellipsis for jumping more than one page
            buttons.append(html.Span("...", className="pagination-ellipsis"))

    # Next page button
    if current_page < total_pages:
        next_button = dbc.Button("Next", color="primary", className="pagination-button")
        next_link = dcc.Link(next_button, href=f"/table-areas/page-{current_page + 1}")
        buttons.append(next_link)

    # Input field and go button
    input_field = dcc.Input(
        id='page-number-input',
        type='number',
        value=current_page,
        style={'width': '50px', 'margin': '0 10px'}
    )
    go_button = dbc.Button("Go", color="primary", className="pagination-button")
    go_link = dcc.Link(go_button, id='go-link', href='')
    buttons.extend([input_field, go_link])

    return html.Div(buttons, className="pagination-container")


# Example usage
rows_per_page = 10  # Adjust the number of rows per page as needed
total_rows = len(df)
total_pages = (total_rows - 1) // rows_per_page + 1

app.layout = html.Div([
    dcc.Store(id='sort-state', data={'column': None, 'direction': 'asc'}),
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(dcc.Input(id='search-input', type='text', placeholder='Search by Name', debounce=True), width=4)
    ], justify='end', className='mb-2'),
    html.Div(id='page-content'),
])


# Callback for both sorting and searching
@app.callback(
    [Output('page-content', 'children'),
     Output('sort-state', 'data')],
    [Input({'type': 'sort-button', 'index': ALL}, 'n_clicks'),
     Input('search-input', 'value'),
     Input('url', 'pathname')],
    [State('sort-state', 'data')]
)
def update_page_content(n_clicks, search_query, pathname, sort_state):
    global mapping_applied
    
    if not mapping_applied:
        # Reapply mapping only if it hasn't been done before
        df['name'] = df['pokemon_id'].map(id_to_name_mapping).fillna("Unknown")
        mapping_applied = True
        
    ctx = dash.callback_context

    # Check if the trigger was a sort button
    if ctx.triggered and 'sort-button' in ctx.triggered[0]['prop_id']:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        sort_column = json.loads(button_id)['index']

        if 'column' not in sort_state:
            sort_state = {'column': sort_column, 'direction': 'asc'}
        else:
            if sort_state['column'] == sort_column:
                sort_direction = 'desc' if sort_state['direction'] == 'asc' else 'asc'
            else:
                sort_direction = 'asc'

            sort_state['column'] = sort_column
            sort_state['direction'] = sort_direction

        # Call the display_page function with updated sort state and current search query
        return display_page(pathname, sort_state, search_query), sort_state

    # If the trigger was not a sort button, it's either a page change or a search query change
    else:
        return display_page(pathname, sort_state, search_query), sort_state



# Callback for displaying page content
def display_page(pathname, sort_state, search_query=''):
    print("Search Query:", search_query)  # Debugging
    filtered_df = df[df['Name'].str.contains(search_query, case=False, na=False)] if search_query else df
    print("Number of rows after filter:", len(filtered_df))  # Debugging

    # Default to page 1 if the pathname is None or doesn't contain a valid page number
    try:
        if pathname and 'page-' in pathname:
            current_page = int(pathname.split('-')[-1])
        else:
            current_page = 1
    except (ValueError, IndexError):
        current_page = 1

    # Pass sort state to the table generation function
    sort_by = sort_state['column']
    sort_direction = sort_state['direction']
    content = [
        dbc.Row(dbc.Col(generate_html_table(filtered_df, current_page, rows_per_page, sort_by, sort_direction), width=12, style={'width': '80%', 'margin': '0 auto'},), className='justify-content-md-center'),
        dbc.Row(dbc.Col(generate_pagination_buttons(total_pages, current_page), width=12, style={'width': '80%', 'margin': 'auto'}), className='justify-content-md-center'),
    ]
    return content
if __name__ == '__main__':
    app.run_server(debug=True)