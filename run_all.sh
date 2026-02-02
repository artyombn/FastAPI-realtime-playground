#!/bin/bash
#chmod +x run_all.sh
#./run_all.sh

echo "Starting App..."
uvicorn main:app --reload