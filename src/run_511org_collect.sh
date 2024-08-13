#!/bin/bash

export SRCDIR="/home/alexk/ucb-wzdx/src"
export LOGDIR="$SRCDIR"/logs
export LOGFILE="$LOGDIR"/511org_$(date +'%Y-%m-%d_%H-%M')

if [ ! -d "$LOGDIR" ]; then
	mkdir "$LOGDIR"
fi

source "$SRCDIR"/.venv/bin/activate
python3 "$SRCDIR"/wzd_collect_sf511.py 2>&1 >"$LOGFILE".log
deactivate
