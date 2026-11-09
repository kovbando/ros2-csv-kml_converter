import importlib.util
import math
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

import pandas as pd


SCRIPT = os.path.join(os.path.dirname(__file__), 'csv-to-kml.py')
spec = importlib.util.spec_from_file_location('csv_to_kml', SCRIPT)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)
KML = {'k': 'http://www.opengis.net/kml/2.2', 'gx': 'http://www.google.com/kml/ext/2.2'}


class ConverterTests(unittest.TestCase):
    def test_heading_matching_and_kml(self):
        fixes = pd.DataFrame([
            {'header_stamp_secs': 3, 'header_stamp_nsecs': 0, 'latitude': 47, 'longitude': 19, 'altitude': 1},
            {'header_stamp_secs': 1, 'header_stamp_nsecs': 0, 'latitude': 48, 'longitude': 20, 'altitude': 2},
            {'header_stamp_secs': 5, 'header_stamp_nsecs': 0, 'latitude': 49, 'longitude': 21, 'altitude': 3},
        ])
        headings = pd.DataFrame([
            {'header_stamp_secs': 1, 'header_stamp_nsecs': 100, 'quaternion_x': 0, 'quaternion_y': 0, 'quaternion_z': 0, 'quaternion_w': 2},
            {'header_stamp_secs': 3, 'header_stamp_nsecs': 100, 'quaternion_x': 0, 'quaternion_y': 0, 'quaternion_z': math.sqrt(0.5), 'quaternion_w': math.sqrt(0.5)},
            {'header_stamp_secs': 5, 'header_stamp_nsecs': 0, 'quaternion_x': 0, 'quaternion_y': 0, 'quaternion_z': 0, 'quaternion_w': 0},
        ])
        result = converter.match_headings(fixes, headings)
        self.assertEqual(result['latitude'].tolist(), [47, 48, 49])
        self.assertAlmostEqual(result.iloc[0]['heading'], 0)
        self.assertAlmostEqual(result.iloc[1]['heading'], 90)
        self.assertTrue(pd.isna(result.iloc[2]['heading']))
        with tempfile.TemporaryDirectory() as folder:
            output = os.path.join(folder, 'fix.kml')
            converter.create_kml_trajectory(result, output)
            root = ET.parse(output).getroot()
            self.assertEqual(len(root.findall('.//k:LineString', KML)), 1)
            self.assertEqual(len(root.findall('.//k:Placemark', KML)), 2)
            self.assertEqual(len(root.findall('.//k:Point', KML)), 0)
            track = root.find('.//gx:Track', KML)
            self.assertEqual([item.text for item in track.findall('k:when', KML)], [
                '1970-01-01T00:00:01Z', '1970-01-01T00:00:03Z', '1970-01-01T00:00:05Z',
            ])
            self.assertEqual([item.text for item in track.findall('gx:coord', KML)], [
                '20 48 2', '19 47 1', '21 49 3',
            ])
            angles = track.findall('gx:angles', KML)
            self.assertEqual(len(angles), 3)
            self.assertAlmostEqual(float(angles[0].text.split()[0]), 90)
            self.assertAlmostEqual(float(angles[1].text.split()[0]), 0)
            self.assertIsNone(angles[2].text)

    def test_no_heading_file(self):
        with tempfile.TemporaryDirectory() as folder:
            pd.DataFrame([{'latitude': 47, 'longitude': 19, 'altitude': 1}]).to_csv(os.path.join(folder, 'fix.csv'), index=False)
            subprocess.run([sys.executable, SCRIPT, folder], check=True, capture_output=True)
            root = ET.parse(os.path.join(folder, 'fix.kml')).getroot()
            self.assertEqual(len(root.findall('.//k:LineString', KML)), 1)
            self.assertEqual(len(root.findall('.//k:Point', KML)), 0)
            self.assertEqual(len(root.findall('.//gx:Track', KML)), 0)


if __name__ == '__main__':
    unittest.main()