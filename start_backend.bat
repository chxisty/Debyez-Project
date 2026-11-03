@echo off
echo ==============================================================================
echo Starting Aegis Series-7 HCS Backend API on port 8000...
echo ==============================================================================
set PYTHONPATH=%CD%
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
pause

