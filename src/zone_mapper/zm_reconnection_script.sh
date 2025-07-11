#!/bin/bash

export SRCDIR="/home/alexk/ucb-wzdx/src"
export WZMAPPER="$SRCDIR"/zone_mapper/leaflet_app.py

export PORTSTR=`netstat -nlp |grep "0.0.0.0:8901`

if [ -z "$PORTSTR" ]; then
	cd $SRCDIR
	source "$SRCDIR"/.venv/bin/activate
	cd zone_mapper
	echo "Starting WZ Mapper..."
	nohup python3 $WZMAPPER >nohup.out &
	deactivate
else
	echo "WZ Mapper is already running..."
fi

