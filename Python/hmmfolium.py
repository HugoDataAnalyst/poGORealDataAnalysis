import pandas as pd
import folium
from folium.plugins import MarkerCluster

def quicktestmapv3(df_path):
    # Load the DataFrame
    df = pd.read_csv(df_path, delimiter='\t')

    def construct_image_path(row):
        if row['form'] == 0:
            return f"{row['pokemon_id']}.png"
        else:
            return f"{row['pokemon_id']}_f{row['form']}.png"

    df['pokemon_images'] = df.apply(construct_image_path, axis=1)

    # Create a Folium Map centered at a random location
    map_center = [df["avg_lat"].mean(), df["avg_lon"].mean()]
    m = folium.Map(location=map_center, zoom_start=10)

    # Create a MarkerCluster group
    marker_cluster = MarkerCluster(sticky=False).add_to(m)

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
            f"<img src='../Dash/UICONS/misc/pokemon.png' alt='Icon 1' height='20' width='20'>" f": {row['count_poke']}<br>"
            f"<img src='../Dash/UICONS/misc/100iv.png' alt='Icon 3' height='20' width='20'>" f": {row['iv_100']}<br>"
            f"<img src='../Dash/UICONS/misc/0iv.png' alt='Icon 4' height='20' width='20'> "f": {row['iv_0']}<br>"
            f"<img src='../Dash/UICONS/misc/sparkles.png' alt='Icon 2' height='20' width='20'> " f": {row['shinies']}<br>"
            f"<img src='../Dash/UICONS/misc/500.png' alt='Icon 2' height='20' width='20'> " f"<img src='../../UICONS/misc/first.png' alt='Icon 2' height='20' width='20'>: {row['little_top_1']}<br>"
            f"<img src='../Dash/UICONS/misc/1500.png' alt='Icon 2' height='20' width='20'> " f"<img src='../../UICONS/misc/first.png' alt='Icon 2' height='20' width='20'>: {row['great_top_1']}<br>"
            f"<img src='../Dash/UICONS/misc/2500.png' alt='Icon 2' height='20' width='20'> "f"<img src='../../UICONS/misc/first.png' alt='Icon 2' height='20' width='20'>: {row['ultra_top_1']}<br>"
        )

        folium.Marker(
            location=[row["avg_lat"], row["avg_lon"]],
            tooltip=f"Pokemon ID: {row['pokemon_id']}",
            icon=img,
            popup=folium.Popup(html=hover_text, max_width=300)
        ).add_to(marker_cluster)

    return m

# Example usage
map_figure = quicktestmapv3("../CSV/AreasNE/EspinhoNE.csv")
map_figure.save("pokemon_map.html")
