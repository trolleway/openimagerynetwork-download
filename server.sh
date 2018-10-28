#!/bin/bash

python __main__.py --storage files --last 52
rm -f files/footprints.geojson #-f ommit return error if file not exists 
ogr2ogr -oo GEOM_POSSIBLE_NAMES=footprint -oo KEEP_GEOM_COLUMNS=NO -s_srs EPSG:4326 -t_srs EPSG:3857 files/footprints.geojson files/footprints.csv
