@echo off
title Launching Agentic Video Engine...
echo ====================================================
echo 🎬 STARTING AGENTIC VIDEO ENGINE ENVIRONMENT
echo ====================================================

:: 1. Check and start Ollama if it is not already running
tasklist /NH /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if %ERRORLEVEL% neq 0 (
    echo      Ollama is stopped. Launching background engine...
    start "" "%USERPROFILE%\AppData\Local\Programs\Ollama\ollama app.exe"
    
    :: Wait for Ollama port binding to complete
    :wait_ollama
    timeout /t 1 >nul
    netstat -ano | findstr 11434 >nul
    if %ERRORLEVEL% neq 0 (
        echo      Waiting for Ollama to bind to port 11434...
        goto wait_ollama
    )
) else (
    echo      Ollama is already active.
)

:: 2. Change directory and activate virtual environment
cd /d C:\Projectsai
call .venv\Scripts\activate

:: 3. Run desktop GUI interface
python gui_app.py
deactivate
exit