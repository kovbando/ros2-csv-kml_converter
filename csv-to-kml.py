import pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os
import sys

def main():
    # Check for path argument
    if len(sys.argv) < 2:
        print("Usage: python csv-to-kml.py <folder_path>")
        sys.exit(1)

    folder_path = sys.argv[1]
    csv_file = os.path.join(folder_path, 'fix.csv')
    output_kml = os.path.join(folder_path, 'fix.kml')

    # Load the CSV file
    if not os.path.isfile(csv_file):
        print(f"CSV file not found: {csv_file}")
        sys.exit(1)
    data = pd.read_csv(csv_file)

    # Filter out coordinates near (0, 0) within a radius of 0.5
    data = data[(data['latitude'].abs() > 0.5) | (data['longitude'].abs() > 0.5)]

    # Create the KML file with a trajectory
    create_kml_trajectory(data, output_kml)
    print(f"KML file created: {output_kml}")

# Function to create a KML file with a single trajectory
def create_kml_trajectory(data, output_file):
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = SubElement(kml, 'Document')

    # Add a single Placemark for the trajectory
    placemark = SubElement(document, 'Placemark')
    name = SubElement(placemark, 'name')
    name.text = "Trajectory"

    description = SubElement(placemark, 'description')
    description.text = "This is a trajectory of all points."

    # Add style for the line
    style = SubElement(document, 'Style', id="lineStyle")
    linestyle = SubElement(style, 'LineStyle')
    color = SubElement(linestyle, 'color')
    color.text = "ffffffff"  # White color in AABBGGRR format
    width = SubElement(linestyle, 'width')
    width.text = "3"  # Line thickness

    # Link style to Placemark
    style_url = SubElement(placemark, 'styleUrl')
    style_url.text = "#lineStyle"

    # Create a LineString for the trajectory
    linestring = SubElement(placemark, 'LineString')
    coordinates = SubElement(linestring, 'coordinates')

    # Add all points to the LineString, one per line
    coords = "\n".join(
        f"{row['longitude']},{row['latitude']},{row['altitude']}" for _, row in data.iterrows()
    )
    coordinates.text = coords

    # Beautify the XML output
    kml_string = tostring(kml, 'utf-8')
    pretty_kml = parseString(kml_string).toprettyxml(indent="  ")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(pretty_kml)

if __name__ == "__main__":
    main()

