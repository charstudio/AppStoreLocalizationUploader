:: main.bat
@echo on

REM Activate VENV
call venv\Scripts\activate

REM Check Python version
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python не встановлений. Встановіть Python і спробуйте знову.
    exit /b 1
)

REM Install required libraries
pip install -r requirements.txt >nul 2>&1

REM Start main.py
python main.py

REM Deactivate virtual venv
call deactivate

REM Press any key
pause

