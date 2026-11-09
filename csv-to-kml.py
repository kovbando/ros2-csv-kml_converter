import pandas as pd
import numpy as np
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

    heading_file = os.path.join(folder_path, 'heading.csv')
    if os.path.isfile(heading_file):
        data = match_headings(data, pd.read_csv(heading_file))

    # Create the KML file with a trajectory
    create_kml_trajectory(data, output_kml)
    print(f"KML file created: {output_kml}")

def match_headings(data, headings):
    data = data.copy().reset_index(drop=True)
    headings = headings.copy()
    quaternion_columns = ['quaternion_x', 'quaternion_y', 'quaternion_z', 'quaternion_w']
    for column in quaternion_columns:
        headings[column] = pd.to_numeric(headings[column], errors='coerce')
    norm_squared = sum(headings[column] ** 2 for column in quaternion_columns)
    headings = headings[np.isfinite(norm_squared) & (norm_squared > 0)].copy()
    norm_squared = norm_squared.loc[headings.index]
    x, y, z, w = (headings[column] for column in quaternion_columns)
    yaw = np.degrees(np.arctan2(2 * (w * z + x * y), norm_squared - 2 * (y * y + z * z)))
    headings['heading'] = (90 - yaw) % 360

    for frame in (data, headings):
        frame['timestamp'] = frame['header_stamp_secs'].astype('int64') * 1_000_000_000 + frame['header_stamp_nsecs'].astype('int64')

    data['original_order'] = np.arange(len(data))
    matched = pd.merge_asof(
        data.sort_values('timestamp'),
        headings[['timestamp', 'heading']].sort_values('timestamp'),
        on='timestamp', direction='nearest', tolerance=500_000_000,
    )
    return matched.sort_values('original_order')

# Function to create a KML file with a single trajectory
def create_kml_trajectory(data, output_file):
    kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2", **{'xmlns:gx': 'http://www.google.com/kml/ext/2.2'})
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

    if 'heading' in data and not data.empty:
        marker = SubElement(document, 'Placemark')
        SubElement(marker, 'name').text = 'Heading track'
        marker_style = SubElement(marker, 'Style')
        icon_style = SubElement(marker_style, 'IconStyle')
        SubElement(icon_style, 'scale').text = '0.7'
        icon = SubElement(icon_style, 'Icon')
        SubElement(icon, 'href').text = 'https://maps.google.com/mapfiles/kml/shapes/arrow.png'
        label_style = SubElement(marker_style, 'LabelStyle')
        SubElement(label_style, 'scale').text = '0'
        line_style = SubElement(marker_style, 'LineStyle')
        SubElement(line_style, 'color').text = '00000000'
        track = SubElement(marker, 'gx:Track')
        track_data = data.sort_values('timestamp', kind='stable')
        for timestamp in track_data['timestamp']:
            SubElement(track, 'when').text = pd.Timestamp(timestamp, unit='ns', tz='UTC').isoformat().replace('+00:00', 'Z')
        for row in track_data.itertuples():
            SubElement(track, 'gx:coord').text = f'{row.longitude} {row.latitude} {row.altitude}'
        for heading in track_data['heading']:
            angles = SubElement(track, 'gx:angles')
            if pd.notna(heading):
                angles.text = f'{heading} 0 0'

    # Beautify the XML output
    kml_string = tostring(kml, 'utf-8')
    pretty_kml = parseString(kml_string).toprettyxml(indent="  ")

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(pretty_kml)

if __name__ == "__main__":
    main()

