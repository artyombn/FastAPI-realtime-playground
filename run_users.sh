#!/bin/bash
#chmod +x run_users.sh
#./run_users.sh

echo "Starting App..."
cd users && uvicorn users.main:app --reload