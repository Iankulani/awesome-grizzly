@echo off
REM ============================================================
REM AWESOME-GRIZZLY-V1 - Installation Script (Windows)
REM ============================================================
setlocal EnableDelayedExpansion

title AWESOME-GRIZZLY-V1 Installer
color 0C
cls

echo.
echo  ============================================================
echo    AWESOME-GRIZZLY-V1 - WINDOWS INSTALLER
echo    Ultimate Cyber Command and Control Platform
echo  ============================================================
echo.

cd /d "%~dp0"

REM ============================================================
REM CHECK PYTHON
REM ============================================================
echo [INFO] Checking Python installation...
where python >nul 2>&1
if errorlevel 1 (
    echo [FAIL] Python not found in PATH.
    echo        Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PY_VERSION=%%i
echo [ OK ] Python !PY_VERSION! detected.

python -c "import sys; sys.exit(0 if sys.version_info >= (3,7) else 1)"
if errorlevel 1 (
    echo [FAIL] Python 3.7+ required. Found !PY_VERSION!
    pause
    exit /b 1
)

REM ============================================================
REM CHECK CHOCOLATEY (optional, for system tools)
REM ============================================================
echo.
echo [INFO] Checking for Chocolatey...
where choco >nul 2>&1
if errorlevel 1 (
    echo [WARN] Chocolatey not found.
    echo        Optional tools (nmap, curl, wget) may not be installed.
    echo        To install Chocolatey: https://chocolatey.org/install
) else (
    echo [ OK ] Chocolatey found.
    echo [INFO] Installing system tools via Chocolatey...
    choco install -y nmap curl wget netcat 7zip git 2>nul
    if errorlevel 1 (
        echo [WARN] Some system tools failed to install. Continue anyway.
    ) else (
        echo [ OK ] System tools installed.
    )
)

REM ============================================================
REM CREATE VIRTUAL ENV
REM ============================================================
echo.
echo [INFO] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    if errorlevel 1 (
        echo [FAIL] Failed to create venv.
        pause
        exit /b 1
    )
    echo [ OK ] Virtual environment created.
) else (
    echo [INFO] Virtual environment already exists.
)

REM ============================================================
REM INSTALL REQUIREMENTS
REM ============================================================
echo.
echo [INFO] Upgrading pip, setuptools, wheel...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel --quiet

echo.
if exist "requirements.txt" (
    echo [INFO] Installing requirements from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARN] Some packages may have failed. Continue anyway.
    ) else (
        echo [ OK ] Requirements installed.
    )
) else (
    echo [WARN] requirements.txt not found. Installing core packages...
    pip install colorama requests psutil paramiko scapy dnspython ^
                Flask Flask-SocketIO Flask-CORS ^
                discord.py telethon slack-sdk selenium ^
                matplotlib numpy reportlab python-docx ^
                pynput pyautogui pyperclip Pillow ^
                python-whois shodan qrcode pyshorteners ^
                cryptography tqdm tabulate rich click
)

REM ============================================================
REM CREATE DIRECTORIES
REM ============================================================
echo.
echo [INFO] Creating configuration directories...
if not exist ".awesome_grizzly_v1" mkdir ".awesome_grizzly_v1"
if not exist ".awesome_grizzly_v1\payloads" mkdir ".awesome_grizzly_v1\payloads"
if not exist ".awesome_grizzly_v1\scans" mkdir ".awesome_grizzly_v1\scans"
if not exist ".awesome_grizzly_v1\phishing_pages" mkdir ".awesome_grizzly_v1\phishing_pages"
if not exist ".awesome_grizzly_v1\captured_credentials" mkdir ".awesome_grizzly_v1\captured_credentials"
if not exist ".awesome_grizzly_v1\ssh_keys" mkdir ".awesome_grizzly_v1\ssh_keys"
if not exist ".awesome_grizzly_v1\traffic_logs" mkdir ".awesome_grizzly_v1\traffic_logs"
if not exist ".awesome_grizzly_v1\keylogs" mkdir ".awesome_grizzly_v1\keylogs"
if not exist ".awesome_grizzly_v1\keylog_screenshots" mkdir ".awesome_grizzly_v1\keylog_screenshots"
if not exist ".awesome_grizzly_v1\malware" mkdir ".awesome_grizzly_v1\malware"
if not exist ".awesome_grizzly_v1\saas" mkdir ".awesome_grizzly_v1\saas"
if not exist ".awesome_grizzly_v1\shodan" mkdir ".awesome_grizzly_v1\shodan"
if not exist ".awesome_grizzly_v1\c2_logs" mkdir ".awesome_grizzly_v1\c2_logs"
if not exist "awesome_grizzly_reports" mkdir "awesome_grizzly_reports"
if not exist "awesome_grizzly_reports\pdf_reports" mkdir "awesome_grizzly_reports\pdf_reports"
if not exist "awesome_grizzly_reports\graphics" mkdir "awesome_grizzly_reports\graphics"
if not exist "awesome_grizzly_reports\charts" mkdir "awesome_grizzly_reports\charts"
echo [ OK ] Directories created.

REM ============================================================
REM VERIFY
REM ============================================================
echo.
echo [INFO] Verifying installation...
if exist "requirement-check.py" (
    python requirement-check.py
)

REM ============================================================
REM DONE
REM ============================================================
echo.
echo  ============================================================
echo    INSTALLATION SUCCESSFUL!
echo  ============================================================
echo.
echo   To start AWESOME-GRIZZLY-V1:
echo     venv\Scripts\activate.bat
echo     python awesome_grizzly.py
echo.
echo   To run tests:
echo     python test-commands.py
echo.
echo   To re-check requirements:
echo     python requirement-check.py
echo.
echo   NOTE: For full functionality (raw sockets, firewall),
echo         run as Administrator.
echo.
pause
endlocal
