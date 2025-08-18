@echo off
echo Starting React Frontend...
echo.

cd frontend

echo [1/2] Installing dependencies...
call npm install

echo.
echo [2/2] Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo.
npm start