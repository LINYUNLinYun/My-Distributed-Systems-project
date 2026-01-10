@echo off
setlocal
title DFS Project Test Runner

:START_SERVER
echo.
echo ==========================================
echo      Starting DFS Server in background...
echo ==========================================
start "DFS_Server_Window" cmd /k "python server/main_server.py"
:: 等待服务器启动
timeout /t 2 /nobreak >nul

:MENU
cls
echo ==========================================
echo      Distributed File System Tests
echo ==========================================
echo.
echo  1. Run Basic Operations Demo (Create/Read/Write/Delete)
echo  2. Run Caching Demo (Prove memory cache works)
echo  3. Run Locking/Concurrency Demo (Multi-user test)
echo  4. Run Interactive Shell (Manual Mode)
echo.
echo  Q. Quit and Stop Server
echo.
echo ==========================================
set /p choice="Enter your choice (1/2/3/4/Q): "

if /i "%choice%"=="1" goto RUN_BASIC
if /i "%choice%"=="2" goto RUN_CACHE
if /i "%choice%"=="3" goto RUN_LOCK
if /i "%choice%"=="4" goto RUN_SHELL
if /i "%choice%"=="Q" goto STOP_SERVER

echo Invalid choice, please try again.
pause
goto MENU

:RUN_BASIC
cls
echo Running Basic Operations Demo...
python tests/demo01_basic.py
echo.
pause
goto MENU

:RUN_CACHE
cls
echo Running Caching Demo...
python tests/demo02_cache.py
echo.
pause
goto MENU

:RUN_LOCK
cls
echo Running Locking Demo...
python tests/demo03_lock.py
echo.
pause
goto MENU

:RUN_SHELL
cls
echo Starting Interactive Shell...
python interactive_shell.py
goto MENU

:STOP_SERVER
echo.
echo Stopping Server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq DFS_Server_Window*" >nul
echo Done.
exit