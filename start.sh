#!/bin/bash
echo "Starting Aegis Full-Stack Application..."
export PYTHONPATH=$(pwd)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

cd frontend
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait

