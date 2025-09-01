#!/bin/sh

while true; do
    python3 ./plex_unmonitorr/plex_unmonitorr.py
    sleep $SCHEDULE
done
