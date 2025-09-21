@echo off
echo 🚀 Setting up Code Quality Intelligence Agent...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo 📦 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
pip install --upgrade pip

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist "data" mkdir data
if not exist "data\faiss_index" mkdir data\faiss_index
if not exist "temp" mkdir temp

echo 📦 Setting up frontend...
cd ../frontend

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install

echo ✅ Setup complete!
echo.
echo To start the application:
echo 1. Start MongoDB: docker run -d --name mongodb -p 27017:27017 mongo:7.0
echo 2. Backend: cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo 3. Frontend: cd frontend && npm start
echo.
echo Access the application at: http://localhost:3000
echo API documentation at: http://localhost:8000/docs
pause
