#!/bin/bash
#chmod +x run_users.sh
#./run_users.sh

echo "Starting App..."
cd products && uvicorn src.main:app --reload