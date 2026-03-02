@echo off
REM Script pour démarrer le worker Celery
REM Haroo - Plateforme Agricole Intelligente du Togo

echo ========================================
echo DEMARRAGE CELERY WORKER - HAROO
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

REM Vérifier que Redis est accessible
echo [INFO] Verification de Redis...
python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping()" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Redis n'est pas accessible
    echo.
    echo Demarrez Redis:
    echo   redis-server
    echo.
    echo Ou installez Redis:
    echo   https://redis.io/download
    echo.
    pause
    exit /b 1
)

echo [OK] Redis est accessible
echo.

echo [INFO] Demarrage du worker Celery...
echo.
echo Configuration:
echo   - Broker: Redis (localhost:6379/2)
echo   - Backend: Redis (localhost:6379/3)
echo   - Timezone: Africa/Lome
echo   - Log level: INFO
echo.
echo Appuyez sur Ctrl+C pour arreter le worker
echo ========================================
echo.

REM Démarrer le worker
celery -A haroo worker -l info --pool=solo

echo.
echo [INFO] Worker Celery arrete
pause
