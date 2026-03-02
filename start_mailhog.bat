@echo off
REM Script pour démarrer MailHog et ouvrir l'interface web
REM Haroo - Plateforme Agricole Intelligente du Togo

echo ========================================
echo DEMARRAGE MAILHOG - HAROO
echo ========================================
echo.

REM Vérifier si MailHog est installé
where mailhog >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] MailHog n'est pas installe ou pas dans le PATH
    echo.
    echo Installation:
    echo   1. Avec Chocolatey: choco install mailhog
    echo   2. Ou telecharger depuis: https://github.com/mailhog/MailHog/releases
    echo.
    pause
    exit /b 1
)

echo [OK] MailHog est installe
echo.

REM Vérifier si MailHog est déjà en cours d'exécution
netstat -ano | findstr :1025 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [INFO] MailHog semble deja en cours d'execution
    echo.
    echo Voulez-vous ouvrir l'interface web? (O/N)
    set /p OPEN_WEB=
    if /i "%OPEN_WEB%"=="O" (
        start http://localhost:8025
    )
    pause
    exit /b 0
)

echo [INFO] Demarrage de MailHog...
echo.
echo Interface web: http://localhost:8025
echo Serveur SMTP: localhost:1025
echo.
echo Appuyez sur Ctrl+C pour arreter MailHog
echo ========================================
echo.

REM Démarrer MailHog
start "MailHog" mailhog

REM Attendre 2 secondes
timeout /t 2 /nobreak >nul

REM Ouvrir l'interface web
start http://localhost:8025

echo.
echo [OK] MailHog demarre!
echo [OK] Interface web ouverte dans le navigateur
echo.
echo Pour envoyer des emails de test:
echo   1. Ouvrir un nouveau terminal
echo   2. Activer l'environnement virtuel: .venv\Scripts\activate
echo   3. Executer: python send_test_emails.py
echo.
pause
