# ros2-csv-kml_converter
A singe python script, converting a csv file generated with ros2bag-convert containing a GNSS trajectory, to .kml to view it using Google Earth.  \
The ros2bag-converter is available at the author's github: https://github.com/fishros/ros2bag_convert  
## Dependencies
pandas 
## Usage
When you have your fix.csv exported from the rosbag you call the script, with the folder containing the fix.csv as the sole aragument.\
If you have your fix.csv in "~/ros2_ws/bagfiles/example/csvs/fix.csv" then you need to run  "python csv-to-kml.py ~/ros2_ws/bagfiles/example/csvs"

If the same folder also contains `heading.csv`, the KML includes a time-aware heading track alongside the trajectory. In Google Earth, use the time slider to move a single arrow along the track; there are no per-point arrows or labels. The files are matched by the closest ROS header timestamp within 0.5 seconds; fixes without a nearby valid quaternion have no recorded heading. The heading quaternion is assumed to use the standard ROS ENU convention (yaw zero points east, positive yaw turns toward north). The arrow uses a Google-hosted icon, which requires network access to load. The track uses Google's `gx:Track` extension, which may not be supported by other KML viewers. Without `heading.csv`, the output contains only the trajectory as before.
