@echo off
REM run.bat

REM Activate virtual environment
call venv\Scripts\activate

REM Set PYTHONPATH
set PYTHONPATH=%cd%

REM Start FastAPI server
start cmd /k "uvicorn backend.main:app --reload --port 8000"

REM Wait a moment for the server to start
timeout /t 2

REM Start Streamlit
streamlit run frontend/app.py