# PoGO Game Data Analysis - [LIVE DEMO](https://godata.databyhugo.com/)
![PokémonGO](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/Dash/UICONS/misc/pogodex.png)

This project revolves around real game data from the widely popular video game Pokémon GO. It encompasses the analysis of 49 million Pokémon observations across multiple areas (geofences) during distinct in-game periods (Event vs. No Event). The analysis is presented through three interactive visualization options:

- Interactive Tables
- Maps with Geofences
- Surge Graphics

The project highlights key skills essential for a Data Analyst, including:

- Data engineering
- Data filtering and processing
- Automation
- Visual interactive graphics
- Python Dashboard development
- Self-hosted visuals for production environments

## Data Engineering

For this high-volume data project (49 million rows - 70 Gigabytes), I opted to create a data warehouse. Utilizing temporary tables, I selected relevant data for insertion into the warehouse. [View the script here.](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/SQL/warehouse.sh)

I also introduced [new columns](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/9392b471b5bc25001abc36b7cdea9b38f7de832b/Python/queryscript.py#L19) in the data warehouse to avoid slow JSON filtering and to enable index creation for improved query performance.

## Data Filtering and Processing

To manage the large dataset, I utilized SQL for effective grouping and metric generation, focusing on aspects like Pokémon ID, forms, IVs, and counts. An interesting twist was applying geofence-based filters, allowing for precise data collection and enabling map-based visualization of Pokémon sightings.

Python's pandas library transformed SQL-filtered data into actionable insights, such as matching Pokémon IDs/forms with their corresponding images and names.

The Surge Analysis was particularly intriguing, revealing potential strategies in Pokémon GO for spawning rarer Pokémon variants, especially during Event vs. No Event comparisons.

## Automation

Considering the project's scope, I developed the [queryscript.py](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/Python/queryscript.py), enabling re-analysis with updated data by simply modifying the SQL WHERE clause. Execute the script using:

```shell
python queryscript.py -h
```
The [converttogeofence.py script](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/Python/converttogeofence.py) automates geofence CSV file generation, based on [areas.csv format.](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/CSV/areas.csv)

This also allows for the usage of programs such as **crontab** where you can then create for example a python file and run it at anytime you wish and only the setting you want!

## Visual Interactive Graphics

Visual representation of data plays a pivotal role in conveying the story behind the numbers. In this project, I delved into Python's Plotly library for its robust plotting capabilities. However, I encountered a limitation: Plotly did not support custom images/icons for the map visuals. To overcome this, I ventured into custom code development, ensuring that the visual aspects were not compromised.

Folium was chosen for mapping due to its flexibility in handling custom images, which was essential for representing Pokémon sightings accurately. This decision allowed for an optimized and engaging user experience.

Furthermore, the need for detailed and tailored data representation led me to manually create the interactive tables. Using HTML, I could customize these tables to fit the specific requirements of the project, providing a level of detail and customization that standard table formats could not offer.

These decisions, while challenging, were crucial in ensuring that the visuals were not only informative but also captivating, enhancing the overall impact of the data analysis.


## Python Dashboard

The project's culmination was the creation of a dynamic dashboard using Dash, a powerful Python library. Dash opened a realm of possibilities, allowing for the seamless integration of complex visuals with HTML/CSS. Its distinctive feature is the extensive customization it offers, granting the freedom to tailor every aspect of the dashboard to fit the project's narrative and aesthetic.

One of Dash's most powerful features is its callback functionality, which I employed extensively. Callbacks in Dash are game-changers for interactivity, enabling the dashboard to respond dynamically to user inputs. This meant that users could filter data and see real-time updates on the visuals, making the dashboard not just a static display of information, but an interactive exploration tool.

This level of customization and interactivity, provided by Dash, was crucial in transforming the analyzed data into a compelling, engaging, and interactive story. The dashboard became more than just a presentation of data; it evolved into an interactive platform that invites exploration and discovery, enhancing the user experience significantly.

## Self-hosted Visuals for production

Thanks to Dash I was able to host it by simply running python [stats_pogo_dash.py](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/Dash/stats_pogo_dash.py) in my Ubuntu Server.

The [dashboard](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/Dash/stats_pogo_dash.py), hosted on an Ubuntu server, was made production-ready using [NGINX](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/NGINX/nginx_example.conf) for secure traffic redirection and domain protection.

## Limitations & Further Improvements

**Limitations:**

- Map visual speed could be improved with webp images.

- Temporary files for map visuals prevent caching, impacting efficiency.

**Improvements:**

- Implementing a Bytes library for map visuals, allowing caching and speed optimization.

- Adding geofence data for known Pokémon nests.

- Incorporating logic to display Ditto's disguises correctly.


## Requirements

This Project requires Python3 and the following dependencies can be found [here](https://github.com/HugoDataAnalyst/poGORealDataAnalysis/blob/main/requirements.txt).