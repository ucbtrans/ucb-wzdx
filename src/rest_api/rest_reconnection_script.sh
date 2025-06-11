#!/bin/bash

#export SRCDIR="/home/alexk/ucb-wzdx/src/rest_api"
export SRCDIR="/home/alex/ucb-wzdx/src/rest_api"
export RESTAPI="$SRCDIR"/api.py

#export PORTSTR=`netstat -nlp |grep "128.32.234.154:8900"`
export PORTSTR=`netstat -nlp |grep "98.85.181.13:8900"`

if [ -z "$PORTSTR" ]; then
	cd $SRCDIR
	source "$SRCDIR"/.venv/bin/activate
	echo "Starting WZDx REST API..."
	nohup python3 $RESTAPI >nohup.out &
	deactivate
else
	echo "WZDx REST API is already running..."
fi

