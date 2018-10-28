#!/bin/bash

python __main__.py --storage files --last 52
rm files/footprints.geojson
ogr2ogr -oo GEOM_POSSIBLE_NAMES=footprint -oo KEEP_GEOM_COLUMNS=NO -s_srs EPSG:4326 -t_srs EPSG:3857 files/footprints.geojson files/footprints.csv
