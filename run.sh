#!/bin/sh

# Create config directory if it doesn't exist
mkdir -p ./config

# Always copy/update the example config file
cp config.example.yaml ./config/config.example.yaml

# Set default schedule if not provided
SCHEDULE=${SCHEDULE:-3600}

while true; do
    python3 -m plex_unmonitorr.main
    exit_code=$?
    
    # Exit container if the script fails
    if [ $exit_code -ne 0 ]; then
        echo "Script exited with code $exit_code. Container will exit."
        exit $exit_code
    fi
    
    sleep $SCHEDULE
done
