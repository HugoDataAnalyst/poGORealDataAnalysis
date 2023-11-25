import geopandas as gpd
import pandas as pd
import requests
import io
import plotly.graph_objects as go
import shapely.geometry
from PIL import Image
import os

def quicktestmap(df_path):
    # Load the DataFrame
    df = pd.read_csv(df_path, delimiter='\t')

    def construct_image_path(row):
        if row['form'] == 0:
            return f"{row['pokemon_id']}.png"
        else:
            return f"../../UICONS/pokemon/{row['pokemon_id']}_f{row['form']}.png"

    df['pokemon_images'] = df.apply(construct_image_path, axis=1)

    # create shapely multi-polygon from Pokémon images
    def pokemon_image(image_path):
        image = Image.open(image_path)
        width, height = image.size
        coords = [(0, 0), (width, 0), (width, height), (0, height), (0, 0)]
        return shapely.geometry.Polygon(coords)

    # create mapbox layers for Pokémon images
    def pokemon_image_mapbox(df, lat="avg_lat", lon="avg_lon"):
        layers = []
        for _, r in df.iterrows():
            image_path = os.path.abspath(f"UICONS/pokemon/{r['pokemon_images']}")  # Assuming images are in the PokemonImages folder
            image_geom = pokemon_image(image_path)
            layers.append(
                {
                    "source": f"/UICONS/{r['pokemon_images']}",
                    "x": r[lon],
                    "y": r[lat],
                    "xanchor": "center",
                    "yanchor": "middle",
                    "sizex": 100,  # Adjust the size as needed
                    "sizey": 100,
                    "sizing": "fill",
                    "opacity": 1,
                    "layer": "below",
                }
            )
        return layers

    data = []
    data.append(
        {
            "type": "scattermapbox",
            "lat": df["avg_lat"],
            "lon": df["avg_lon"],
            "name": "Location",
            "showlegend": False,
            "customdata": df.loc[:, ["pokemon_id", "count_poke", "iv_100", "iv_0", "shinies", "little_top_1", "great_top_1", "ultra_top_1"]].values,
            "hoverinfo": "text",
            "mode": "markers",
            "customdata": df.loc[:, ["pokemon_id"]].values,
        }
    )

    fig = go.Figure(data).update_layout(
        mapbox={
            "style": "carto-positron",
            "center": df.sample(1)
            .loc[:, ["avg_lat", "avg_lon"]]
            .rename(columns={"avg_lat": "lat", "avg_lon": "lon"})
            .to_dict("records")[0],
            "zoom": 10,
        },
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
    )

    # Add Pokémon images
    for layer in pokemon_image_mapbox(df):
        fig.add_layout_image(**layer)

    # Set the hover text format
    hover_text = [
        "Pokemon ID: {}<br>Count: {}<br>IV 100: {}<br>IV 0: {}<br>Shinies: {}<br>Little Top 1: {}<br>Great Top 1: {}<br>Ultra Top 1: {}".format(
            pid, count, iv100, iv0, shinies, little_top_1, great_top_1, ultra_top_1
        )
        for pid, count, iv100, iv0, shinies, little_top_1, great_top_1, ultra_top_1 in zip(
            df["pokemon_id"],
            df["count_poke"],
            df["iv_100"],
            df["iv_0"],
            df["shinies"],
            df["little_top_1"],
            df["great_top_1"],
            df["ultra_top_1"],
        )
    ]
    fig.data[0].update(hovertext=hover_text)

    return fig  # Return the Plotly figure

# Example usage
# fig = quicktestmap("../CSV/AreasLF/EspinhoLF.csv")
# fig.show()  # Uncomment these lines for testing the function outside Dash
