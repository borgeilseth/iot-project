#!/bin/bash

# Set the folder path from the argument, default to current directory if not provided
USERINPUT_FOLDER="${1:-.}"

# Check if the folder exists
if [ ! -d "$USERINPUT_FOLDER" ]; then
    echo "Error: Folder does not exist."
    exit 1
fi

# Activate PlatformIO virtual environment
source ~/.platformio/penv/bin/activate

# Change to the specified directory
cd "$USERINPUT_FOLDER" || exit

# Run PlatformIO build
pio run