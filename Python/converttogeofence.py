import csv
import os

def process_area_file(input_file, output_dir):
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            area_name = row['AreaName']
            coordinates = row['Coordinates'].split(', ')

            # Create fieldnames dynamically based on the number of coordinates
            fieldnames = ['AreaName']
            for i in range(len(coordinates)):
                fieldnames.extend([f'Lat{i+1}', f'Lon{i+1}'])

            output_file = f"{output_dir}/{area_name}.csv"
            with open(output_file, 'w', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                coord_dict = {'AreaName': area_name}
                for i, coord in enumerate(coordinates):
                    lat, lon = coord.split(' ')
                    coord_dict[f'Lat{i+1}'] = lat
                    coord_dict[f'Lon{i+1}'] = lon
                writer.writerow(coord_dict)

if __name__ == "__main__":
    input_file = '../CSV/areas.csv'
    output_dir = '../CSV/Geofences'
    os.makedirs(output_dir, exist_ok=True)
    process_area_file(input_file, output_dir)
