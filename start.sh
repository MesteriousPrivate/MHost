#!/bin/bash

# Set up environment variables from .env file
set -a
source .env
set +a

# Run the main script
exec python3 -m ShrutiMusicBot
