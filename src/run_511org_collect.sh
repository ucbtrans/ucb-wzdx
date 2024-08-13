#!/bin/bash

export SRCDIR="/home/alexk/ucb-wzdx/src"
export LOGDIR="$SRCDIR"/logs
export LOGFILE="$LOGDIR"/511org_$(date + '%Y-%m-%d_%H-%M')

if [ ! -d "$LOGDIR" ]; then
	mkdir "$LOGDIR"
fi

source "$SRCDIR"/.venv/bin/activate
python3 wzd_collect_sf511org.py >"$LOGFILE".log 2>"$LOGFILE".err
deactivate
