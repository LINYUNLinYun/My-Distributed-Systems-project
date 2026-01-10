@echo off
echoString Starting Distributed File System Server...
start "DFS Server" cmd /k "python server/main_server.py"

echo Waiting for server to initialize (3 seconds)...
timeout /t 3 /nobreak >nul

echo.
echo ==============================================
echo        Running Automated Test Suite
echo ==============================================
echo.

python tests/auto_test.py

echo.
echo ==============================================
echo        Tests Completed.
echo ==============================================
echo.
echo You can inspect the "storage_server" folder to see created files.
echo Close the Server window manually when done, or press any key to kill python processes.
pause

taskkill /F /IM python.exe /FI "WINDOWTITLE eq DFS Server*"
echo Done.