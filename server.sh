#!/bin/bash

python __main__.py --storage files 
rm -f files/footprints.geojson #-f ommit return error if file not exists 
ogr2ogr -oo GEOM_POSSIBLE_NAMES=footprint \
 -skipfailures \
 -oo KEEP_GEOM_COLUMNS=NO \
  -fieldTypeToString All\
  -s_srs EPSG:4326 -t_srs EPSG:3857\
  -nlt PROMOTE_TO_MULTI\
  -lco COORDINATE_PRECISION=8 \
  files/footprints.geojson files/footprints.csv
python update_ngw_from_geojson.py --ngw_url "$NEXTGISCOM_INSTANCE_URL"\
 --ngw_resource_id "$NEXTGISCOM_VECTOR_LAYER_ID"\
 --ngw_login "$NEXTGISCOM_LOGIN"\
 --ngw_password "$NEXTGISCOM_PASSWORD"\
 --check_field uuid \
 --filename files/footprints.geojson
