#!/bin/bash

if [ -d /Users/samuel/Desktop/Projects/puckViewSnap ]; then
    export SNAP_ROOT=/Users/samuel/Desktop/Projects/puckViewSnap
    source ${SNAP_ROOT}/venv/bin/activate
fi

python puckViewSnap.py
