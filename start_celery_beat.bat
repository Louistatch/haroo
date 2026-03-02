@echo off
REM Script pour démarrer Celery Beat (tâches planifiées)
REM Haroo - Plateforme Agricole Intelligente du Togo

echo ========================================
echo DEMARRAGE CELERY BEAT - HAROO
echo ========================================
echo.

REM Vérifier que l'environnement virtuel est activé
if not defined VIRTUAL_ENV (
    echo [ERREUR] Environnement virtuel non active
    echo.
    echo Activez l'environnement virtuel:
    echo   .venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

echo [OK] Environnement virtuel active
echo.

echo [INFO] Taches planifiees:
echo   - Rappels d'expiration: Toutes les heures
echo   - Anonymisation logs: Quotidien a 2h00
echo   - Nettoyage liens: Toutes les heures
echo.

echo [INFO] Demarrage de Celery Beat...
echo.
echo Appuyez sur Ctrl+C pour arreter Beat
echo ========================================
echo.

REM Démarrer Beat
celery -A haroo beat -l info

echo.
echo [INFO] Celery Beat arrete
pause
