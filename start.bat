@echo off
REM ===============================
REM Auto Job Applier - Starter
REM ===============================

REM Schimba directorul de lucru in folderul proiectului
cd /d "c:\Users\glang\Documents\Site-uri\Auto_job_applier_linkedIn-main"

REM Creeaza (la nevoie) mediul virtual
if not exist "venv" (
    echo [INFO] Creez mediul virtual Python...
    python -m venv venv
)

REM Activeaza mediul virtual
call "venv\Scripts\activate.bat"

echo [INFO] Actualizez pip si instalez/verific dependentele...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Creeaza directoarele necesare (daca nu exista deja)
if not exist "logs" mkdir "logs"
if not exist "logs\screenshots" mkdir "logs\screenshots"
if not exist "all excels" mkdir "all excels"
if not exist "all resumes" mkdir "all resumes"
if not exist "all resumes\default" mkdir "all resumes\default"
if not exist "all resumes\temp" mkdir "all resumes\temp"

echo.
echo ==========================================
echo Pornesc Auto Job Applier pentru LinkedIn...
echo ==========================================
echo.

python runAiBot.py

echo.
echo Programul s-a incheiat. Poti inchide fereastra.
pause

