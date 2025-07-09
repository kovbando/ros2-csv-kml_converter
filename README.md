# ros2-csv-kml_converter
A singe python script, converting a csv file generated with ros2bag-convert containing a GNSS trajectory, to .kml to view it using Google Earth.  \
The ros2bag-converter is available at the author's github: https://github.com/fishros/ros2bag_convert  
## Dependencies
pandas 
## Usage
When you have your fix.csv exported from the rosbag you call the script, with the folder containing the fix.csv as the sole aragument.\
If you have your fix.csv in "~/ros2_ws/bagfiles/example/csvs/fix.csv" then you need to run  "python csv-to-kml.py ~/ros2_ws/bagfiles/example/csvs"
