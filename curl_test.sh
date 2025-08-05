#!/bin/bash

echo "Starting FastAPI server..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

sleep 3

echo "Testing health endpoint..."
curl -X GET http://localhost:8000/health

echo -e "\n\nTesting counterfactual endpoint..."
curl -X POST "http://localhost:8000/counterfactual" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I chose to stay home instead of going to the party\nI stayed in my room when feeling overwhelmed\nI focused on my breathing to calm down\nI told myself this feeling was temporary\nI took deep breaths to manage my anxiety"
  }'

echo -e "\n\nStopping server..."
kill $SERVER_PID