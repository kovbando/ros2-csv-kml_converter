import pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os

# Load the CSV file
csv_file = 'fix.csv'  # Update with your local CSV file path
data = pd.read_csv(csv_file)

# Filter out coordinates near (0, 0) within a radius of 0.5
data = data[(data['latitude'].abs() > 0.5) | (data['longitude'].abs() > 0.5)]

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

# Define output file path
output_kml = os.path.join(os.getcwd(), 'output.kml')

# Create the KML file with a trajectory
create_kml_trajectory(data, output_kml)

print(f"KML file created: {output_kml}")

