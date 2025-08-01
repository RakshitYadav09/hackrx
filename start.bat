@echo off
echo Starting LLM-Powered Query Retrieval System...
echo.

:: Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo Installing dependencies...
pip install -r requirements.txt

:: Check if .env file exists
if not exist .env (
    echo.
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    echo.
    pause
    exit /b 1
)

:: Start the application
echo.
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo.
python main.py

pause
