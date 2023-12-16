import csv
import pymysql
import argparse

def read_areas(file_name):
    areas = []
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            areas.append((row['AreaName'], row['Coordinates']))
    return areas

def query_database(area_name, coordinates, connection, query_option):
    def column_exists(cursor, table, column):
        cursor.execute(f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '{table}' AND column_name = '{column}'")
        return cursor.fetchone()[0] > 0

    with connection.cursor() as cursor:
        if query_option == 'createpvpcolumns':
            print("Checking and adding columns for 'createpvpcolumns' option...")
            columns_added = 0
            for column in ['little_rank_1', 'great_rank_1', 'ultra_rank_1']:
                if not column_exists(cursor, 'pokemon', column):
                    cursor.execute(f"ALTER TABLE pokemon ADD COLUMN {column} INT;")
                    print(f"Added column {column} to pokemon table.")
                    columns_added += 1
                else:
                    print(f"Column {column} already exists in pokemon table.")
            if columns_added > 0:
                connection.commit()
                print(f"Successfully added {columns_added} columns to pokemon table.")
            else:
                print("No new columns were added. All columns already exist.")
            return None  # Return early as no query execution is needed here
        elif query_option == 'updatepvptables':
            query = f"""
            UPDATE pokemon
            SET 
                ultra_rank_1 = (
                    CASE 
                        WHEN EXISTS (
                            SELECT 1
                            FROM JSON_TABLE(pvp->'$.ultra[*]', '$[*]' COLUMNS (
                                competition_rank INT PATH '$.competition_rank'
                            )) AS t
                            WHERE t.competition_rank = 1
                        )
                        THEN 1
                        ELSE 0
                    END
                ),
                great_rank_1 = (
                    CASE 
                        WHEN EXISTS (
                            SELECT 1
                            FROM JSON_TABLE(pvp->'$.great[*]', '$[*]' COLUMNS (
                                competition_rank INT PATH '$.competition_rank'
                            )) AS t
                            WHERE t.competition_rank = 1
                        )
                        THEN 1
                        ELSE 0
                    END
                ),
                little_rank_1 = (
                    CASE 
                        WHEN EXISTS (
                            SELECT 1
                            FROM JSON_TABLE(pvp->'$.little[*]', '$[*]' COLUMNS (
                                competition_rank INT PATH '$.competition_rank'
                            )) AS t
                            WHERE t.competition_rank = 1
                        )
                        THEN 1
                        ELSE 0
                    END
                )
            """
            print("Executing query:", query)
        elif query_option == 'areadataLF':
            query = f"""
            WITH pokemonevent AS (
                SELECT
                    pokemon_id,
                    form,
                    COUNT(pokemon_id) AS count_poke,
                    AVG(level) AS avg_level,
                    AVG(iv) AS avg_iv,
                    AVG(lat) AS avg_lat,
                    AVG(lon) AS avg_lon,
                    SUM(
                        CASE
                            WHEN iv = 100
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_100,
                    SUM(
                        CASE
                            WHEN iv = 0
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_0,
                    SUM(
                        CASE
                            WHEN shiny = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS shinies,
                    SUM(
                        CASE
                            WHEN ultra_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS ultra_top_1,
                    SUM(
                        CASE
                            WHEN great_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS great_top_1,
                    SUM(
                        CASE
                            WHEN little_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS little_top_1   
                FROM pokemon
                WHERE 
                    ST_WITHIN(POINT(lat, lon),ST_GEOMFROMTEXT('POLYGON(({coordinates}))'))
                    AND
                    (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')                
                GROUP BY pokemon_id, form
                ORDER BY count_poke DESC
            )
            SELECT
                pokemon_id,
                form,
                count_poke,
                ROUND((count_poke / (SELECT SUM(count_poke) FROM pokemonevent) * 100),10) AS percentage,
                avg_level,
                avg_iv,
                avg_lat,
                avg_lon,
                iv_100,
                ROUND(((iv_100 / count_poke) * 100),10) AS iv100_percentage,    
                iv_0,
                ROUND(((iv_0 / count_poke) * 100 ),10) AS iv0_percentage,
                shinies,
                ROUND(((shinies / count_poke) * 100),10) AS shiny_odds,
                little_top_1,
                ROUND(((little_top_1 / count_poke) * 100),10) AS little_top1_percentage,
                great_top_1,
                ROUND(((great_top_1 / count_poke) * 100),10) AS great_top1_percentage,
                ultra_top_1,
                ROUND(((ultra_top_1 / count_poke) * 100),10) AS ultra_top1_percentage
            FROM pokemonevent
            ORDER BY count_poke DESC"""
            print("Executing query:", query)            
        elif query_option =='areadataNE':
            query = f"""
            WITH pokemonevent AS (
                SELECT
                    pokemon_id,
                    form,
                    COUNT(pokemon_id) AS count_poke,
                    AVG(level) AS avg_level,
                    AVG(iv) AS avg_iv,
                    AVG(lat) AS avg_lat,
                    AVG(lon) AS avg_lon,
                    SUM(
                        CASE
                            WHEN iv = 100
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_100,
                    SUM(
                        CASE
                            WHEN iv = 0
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_0,
                    SUM(
                        CASE
                            WHEN shiny = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS shinies,
                    SUM(
                        CASE
                            WHEN ultra_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS ultra_top_1,
                    SUM(
                        CASE
                            WHEN great_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS great_top_1,
                    SUM(
                        CASE
                            WHEN little_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS little_top_1   
                FROM pokemon
                WHERE 
                    ST_WITHIN(POINT(lat, lon),ST_GEOMFROMTEXT('POLYGON(({coordinates}))'))
                    AND NOT
                    (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')                
                GROUP BY pokemon_id, form
                ORDER BY count_poke DESC
            )
            SELECT
                pokemon_id,
                form,
                count_poke,
                ROUND((count_poke / (SELECT COUNT(pokemon_id) FROM pokemonevent) * 100),10) AS percentage,
                avg_level,
                avg_iv,
                avg_lat,
                avg_lon,
                iv_100,
                ROUND(((iv_100 / count_poke) * 100),10) AS iv100_percentage,    
                iv_0,
                ROUND(((iv_0 / count_poke) * 100 ),10) AS iv0_percentage,
                shinies,
                ROUND(((shinies / count_poke) * 100),10) AS shiny_odds,
                little_top_1,
                ROUND(((little_top_1 / count_poke) * 100),10) AS little_top1_percentage,
                great_top_1,
                ROUND(((great_top_1 / count_poke) * 100),10) AS great_top1_percentage,
                ultra_top_1,
                ROUND(((ultra_top_1 / count_poke) * 100),10) AS ultra_top1_percentage
            FROM pokemonevent
            ORDER BY count_poke DESC"""
            print("Executing query:", query)
        elif query_option =='globalLF':
            query = f"""
            WITH pokemonevent AS (
                SELECT
                    pokemon_id,
                    form,
                    COUNT(pokemon_id) AS count_poke,
                    AVG(level) AS avg_level,
                    AVG(iv) AS avg_iv,
                    SUM(
                        CASE
                            WHEN iv = 100
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_100,
                    SUM(
                        CASE
                            WHEN iv = 0
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_0,
                    SUM(
                        CASE
                            WHEN shiny = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS shinies,
                    SUM(
                        CASE
                            WHEN ultra_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS ultra_top_1,
                    SUM(
                        CASE
                            WHEN great_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS great_top_1,
                    SUM(
                        CASE
                            WHEN little_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS little_top_1   
                FROM pokemon
                WHERE 
                    (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')                
                GROUP BY pokemon_id, form
                ORDER BY count_poke DESC
            )
            SELECT
                pokemon_id,
                form,
                count_poke,
                ROUND((count_poke / (SELECT COUNT(pokemon_id) FROM pokemonevent) * 100),10) AS percentage,
                avg_level,
                avg_iv,
                iv_100,
                ROUND(((iv_100 / count_poke) * 100),10) AS iv100_percentage,    
                iv_0,
                ROUND(((iv_0 / count_poke) * 100 ),10) AS iv0_percentage,
                shinies,
                ROUND(((shinies / count_poke) * 100),10) AS shiny_odds,
                little_top_1,
                ROUND(((little_top_1 / count_poke) * 100),10) AS little_top1_percentage,
                great_top_1,
                ROUND(((great_top_1 / count_poke) * 100),10) AS great_top1_percentage,
                ultra_top_1,
                ROUND(((ultra_top_1 / count_poke) * 100),10) AS ultra_top1_percentage
            FROM pokemonevent
            ORDER BY count_poke DESC"""
            print("Executing query:", query)
        elif query_option =='globalNE':
            query = f"""
            WITH pokemonevent AS (
                SELECT
                    pokemon_id,
                    form,
                    COUNT(pokemon_id) AS count_poke,
                    AVG(level) AS avg_level,
                    AVG(iv) AS avg_iv,
                    SUM(
                        CASE
                            WHEN iv = 100
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_100,
                    SUM(
                        CASE
                            WHEN iv = 0
                            THEN 1
                            ELSE 0
                        END
                    ) AS iv_0,
                    SUM(
                        CASE
                            WHEN shiny = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS shinies,
                    SUM(
                        CASE
                            WHEN ultra_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS ultra_top_1,
                    SUM(
                        CASE
                            WHEN great_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS great_top_1,
                    SUM(
                        CASE
                            WHEN little_rank_1 = 1
                            THEN 1
                            ELSE 0
                        END
                    ) AS little_top_1   
                FROM pokemon
                WHERE 
                    NOT (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')                
                GROUP BY pokemon_id, form
                ORDER BY count_poke DESC
            )
            SELECT
                pokemon_id,
                form,
                count_poke,
                ROUND((count_poke / (SELECT COUNT(pokemon_id) FROM pokemonevent) * 100),10) AS percentage,
                avg_level,
                avg_iv,
                iv_100,
                ROUND(((iv_100 / count_poke) * 100),10) AS iv100_percentage,    
                iv_0,
                ROUND(((iv_0 / count_poke) * 100 ),10) AS iv0_percentage,
                shinies,
                ROUND(((shinies / count_poke) * 100),10) AS shiny_odds,
                little_top_1,
                ROUND(((little_top_1 / count_poke) * 100),10) AS little_top1_percentage,
                great_top_1,
                ROUND(((great_top_1 / count_poke) * 100),10) AS great_top1_percentage,
                ultra_top_1,
                ROUND(((ultra_top_1 / count_poke) * 100),10) AS ultra_top1_percentage
            FROM pokemonevent
            ORDER BY count_poke DESC"""
            print("Executing query:", query)
        elif query_option == 'surgeglobaliv100LF':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS 100_iv
            FROM pokemon 
            WHERE iv = 100 AND (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY iv, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)
        elif query_option =='surgeglobaliv100NE':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS 100_iv
            FROM pokemon 
            WHERE iv = 100 AND NOT (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY iv, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query) 
        elif query_option =='surgeglobaliv0LF':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS 0_iv
            FROM pokemon 
            WHERE iv = 0 AND (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY iv, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)
        elif query_option =='surgeglobaliv0NE':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS 0_iv
            FROM pokemon 
            WHERE iv = 0 AND NOT (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY iv, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query) 
        elif query_option =='surgegloballittletop1LF':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS little_top_1
            FROM pokemon 
            WHERE little_rank_1 = 1 AND (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY little_rank_1, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)
        elif query_option =='surgegloballittletop1NE':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS little_top_1
            FROM pokemon 
            WHERE little_rank_1 = 1 AND NOT (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY little_rank_1, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)
        elif query_option =='surgeglobalgreattop1LF':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS great_top_1
            FROM pokemon 
            WHERE great_rank_1 = 1 AND (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY great_rank_1, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)
        elif query_option =='surgeglobalgreattop1NE':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS great_top_1
            FROM pokemon 
            WHERE great_rank_1 = 1 AND NOT (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY great_rank_1, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)      
        elif query_option =='surgeglobalultratop1LF':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS ultra_top_1
            FROM pokemon 
            WHERE ultra_rank_1 = 1 AND (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY ultra_rank_1, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)
        elif query_option =='surgeglobalultratop1NE':
            query = f"""
            SELECT 
                HOUR(FROM_UNIXTIME(expire_timestamp)) AS hourly_date, 
                COUNT(*) AS ultra_top_1
            FROM pokemon 
            WHERE ultra_rank_1 = 1 AND NOT (FROM_UNIXTIME(expire_timestamp) BETWEEN '2023-11-15 14:00:00' AND '2023-11-19 20:00:00')
            GROUP BY ultra_rank_1, hourly_date
            ORDER BY hourly_date"""
            print("Executing query:", query)                         
        else:
            raise ValueError("Invalid query option")
        if query:
            cursor.execute(query)
            connection.commit()
            results = cursor.fetchall()
            print(f"Fetched {len(results)} records for area '{area_name}'")  # Print number of records fetched
            return results
        else:
            return None

def save_to_csv(area_name, data, query_option):
    # Define column headers for each query option
    column_headers = {
        'areadataLF': ['pokemon_id', 'form', 'count_poke', 'percentage', 'avg_level', 'avg_iv', 'avg_lat', 'avg_lon', 'iv_100', 'iv100_percentage', 'iv_0', 'iv0_percentage', 'shinies', 'shiny_odds', 'little_top_1', 'little_top1_percentage', 'great_top_1', 'great_top1_percentage', 'ultra_top_1', 'ultra_top1_percentage'],
        'areadataNE': ['pokemon_id', 'form', 'count_poke', 'percentage', 'avg_level', 'avg_iv', 'avg_lat', 'avg_lon', 'iv_100', 'iv100_percentage', 'iv_0', 'iv0_percentage', 'shinies', 'shiny_odds', 'little_top_1', 'little_top1_percentage', 'great_top_1', 'great_top1_percentage', 'ultra_top_1', 'ultra_top1_percentage'],
        'globalLF': ['pokemon_id', 'form', 'count_poke', 'percentage', 'avg_level', 'avg_iv', 'iv_100', 'iv100_percentage', 'iv_0', 'iv0_percentage', 'shinies', 'shiny_odds', 'little_top_1', 'little_top1_percentage', 'great_top_1', 'great_top1_percentage', 'ultra_top_1', 'ultra_top1_percentage'],
        'globalNE': ['pokemon_id', 'form', 'count_poke', 'percentage', 'avg_level', 'avg_iv', 'iv_100', 'iv100_percentage', 'iv_0', 'iv0_percentage', 'shinies', 'shiny_odds', 'little_top_1', 'little_top1_percentage', 'great_top_1', 'great_top1_percentage', 'ultra_top_1', 'ultra_top1_percentage'],
        'surgeglobaliv100LF': ['hourly_date', 'iv100'],
        'surgeglobaliv100NE': ['hourly_date', 'iv100'],
        'surgeglobaliv0LF': ['hourly_date', 'iv0'],
        'surgeglobaliv0NE': ['hourly_date', 'iv0'],
        'surgegloballittletop1LF': ['hourly_date', 'little_top_1'],
        'surgegloballittletop1NE': ['hourly_date', 'little_top_1'],
        'surgeglobalgreattop1LF': ['hourly_date', 'great_top_1'],
        'surgeglobalgreattop1NE': ['hourly_date', 'great_top_1'],
        'surgeglobalultratop1LF': ['hourly_date', 'ultra_top_1'],
        'surgeglobalultratop1NE': ['hourly_date', 'ultra_top_1'],
        #'query_option': [...]  # Define columns 
    }

    # Get the appropriate column headers for the current query option
    headers = column_headers.get(query_option, [])
    if not headers:
        raise ValueError("Invalid or undefined query option for column headers")


    # Customize the directory and file name based on the query option
    if query_option == 'areadataLF':
        directory = "../CSV/AreasLF"
        filename = f"{area_name}LF.csv"
    elif query_option == 'areadataNE':
        directory = "../CSV/AreasNE"
        filename = f"{area_name}NE.csv"
    elif query_option == 'globalLF':
        directory = "../CSV/AreasLF"
        filename = f"GlobalLF.csv"
    elif query_option == 'globalNE':
        directory = "../CSV/AreasNE"
        filename = f"GlobalNE.csv"
    elif query_option == 'surgeglobaliv100LF':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobaliv100LF.csv"
    elif query_option == 'surgeglobaliv100NE':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobaliv100NE.csv"
    elif query_option == 'surgeglobaliv0LF':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobaliv0LF.csv" 
    elif query_option == 'surgeglobaliv0NE':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobaliv0NE.csv"
    elif query_option == 'surgegloballittletop1LF':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobalLittleTop1LF.csv" 
    elif query_option == 'surgegloballittletop1NE':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobalLittleTop1NE.csv"
    elif query_option == 'surgeglobalgreattop1LF':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobalGreatTop1LF.csv" 
    elif query_option == 'surgeglobalgreattop1NE':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobalGreatTop1NE.csv"
    elif query_option == 'surgeglobalultratop1LF':
        directory = "../CSV/Surge"
        filename = f"SurgeGlobalUltraTop1LF.csv" 
    elif query_option == 'surgeglobalultratop1NE':
        directory = "../CSV/Surge"
    else:
        raise ValueError("Invalid query option")

    file_path = f"{directory}/{filename}"
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in data:
            writer.writerow(row)
    print(f"Data saved to {file_path}")  # Print the path of the file

def main(host, db_name, user, password, query_option):
    connection = pymysql.connect(host=host, db=db_name, user=user, passwd=password)
    try:
        # All query options
        #'createpvpcolumns', 'updatepvptables',
        all_query_options = [
            'areadataLF', 
            'areadataNE', 'globalLF', 'globalNE', 
            'surgeglobaliv100NE', 'surgegloballittletop1NE', 'surgeglobalgreattop1LF',
            'surgeglobalgreattop1NE', 'surgeglobalultratop1LF', 'surgeglobalultratop1NE'
        ]

        # Query options that don't require looping through areas
        global_options = [
            'globalLF', 'globalNE', 'surgeglobaliv100LF', 
            'surgeglobaliv100NE', 'surgeglobaliv0LF', 'surgeglobaliv0NE', 
            'surgegloballittletop1LF', 'surgegloballittletop1NE', 'surgeglobalgreattop1LF', 
            'surgeglobalgreattop1NE', 'surgeglobalultratop1LF', 'surgeglobalultratop1NE',
            'createpvpcolumns', 'updatepvptables'
        ]

        if query_option == 'all':
            for option in all_query_options:
                if option in global_options:
                    results = query_database(None, None, connection, option)
                    if results:
                        save_to_csv(None, results, option)
                    else:
                        print(f"No data found for global query option {option}")
                else:
                    areas = read_areas("../CSV/areas.csv")
                    print(f"Processing {len(areas)} areas for {option}")
                    for area_name, coordinates in areas:
                        try:
                            results = query_database(area_name, coordinates, connection, option)
                            if results:
                                save_to_csv(area_name, results, option)
                            else:
                                print(f"No data found for {area_name} in {option}")
                        except Exception as e:
                            print(f"Error processing {area_name} for {option}: {e}")
        elif query_option == 'createpvpcolumns':
            query_database(None, None, connection, 'createpvpcolumns')
        else:
            if query_option in global_options:
                results = query_database(None, None, connection, query_option)
                if results:
                    save_to_csv(None, results, query_option)
                else:
                    print(f"No data found for global query option {query_option}")
            else:
                areas = read_areas("../CSV/areas.csv")
                print(f"Processing {len(areas)} areas")
                for area_name, coordinates in areas:
                    try:
                        results = query_database(area_name, coordinates, connection, query_option)
                        if results:
                            save_to_csv(area_name, results, query_option)
                        else:
                            print(f"No data found for {area_name}")
                    except Exception as e:
                        print(f"Error processing {area_name}: {e}")

    except Exception as e:
        print(f"Error connecting to the database: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run SQL queries for different areas and save results to CSV files.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('host', help="Database host")
    parser.add_argument('db_name', help="Database name")
    parser.add_argument('user', help="Database user")
    parser.add_argument('password', help="Database password")
    parser.add_argument('query_option', 
        help="""Query option:

createpvpcolumns - Adds new columns for PVP rankings if they do not exist.

updatepvptables - Updates the PVP tables with the latest rankings.

areadata - Processes data for specific areas. Options:
    NE (Non-Event)
    LF (Lights Festival)
    Example: areadataNE

global - Processes global data. Options:
    NE (Non-Event)
    LF (Lights Festival)
    Example: globalNE

surgeglobal options - Processes surge data for global trends. Options:
    iv100 NE or LF
    iv0 NE or LF
    littletop1 NE or LF
    greatop1 NE or LF
    ultratop1 NE or LF
    Example: iv100NE""")

    args = parser.parse_args()
    main(args.host, args.db_name, args.user, args.password, args.query_option)
