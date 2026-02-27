#!/bin/bash
#chmod +x run_users.sh
#./run_users.sh

echo "Starting App..."
cd products && uvicorn products.main:app --port 7000 --reload