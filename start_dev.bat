@echo off
REM Script de démarrage pour Windows
REM Plateforme Agricole Togo

echo.
echo ========================================
echo   Plateforme Agricole Togo - Demarrage
echo ========================================
echo.

REM Vérifier Python
echo Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe
    pause
    exit /b 1
)
echo [OK] Python trouve
echo.

REM Vérifier Node.js
echo Verification de Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js n'est pas installe
    pause
    exit /b 1
)
echo [OK] Node.js trouve
echo.

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo [OK] Environnement virtuel active
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [OK] Environnement virtuel active
) else (
    echo [ATTENTION] Aucun environnement virtuel trouve
    echo Creez-en un avec: python -m venv .venv
)
echo.

REM Démarrer le backend dans un nouveau terminal
echo Demarrage du backend Django...
echo URL: http://localhost:8000
start cmd /k "cd /d %CD% && .venv\Scripts\activate.bat && python manage.py runserver"
timeout /t 3 >nul

REM Démarrer le frontend dans un nouveau terminal
echo Demarrage du frontend Vite...
echo URL: http://localhost:5173
start cmd /k "cd /d %CD%\frontend && npm run dev"

echo.
echo ========================================
echo Serveurs en cours de demarrage...
echo.
echo Commandes utiles:
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:5173
echo   - Admin: http://localhost:8000/admin
echo.
echo Pour arreter les serveurs:
echo   Fermez les fenetres de terminal
echo.
echo Documentation:
echo   - DEMARRAGE_RAPIDE.md
echo   - MARKETPLACE_DOCUMENTS_SUMMARY.md
echo ========================================
echo.

pause
