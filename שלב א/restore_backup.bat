@echo off
REM ====================================================================
REM  restore_backup.bat
REM  Restores backup_2026-11-22.sql into a fresh PostgreSQL container.
REM  Needs Docker Desktop running.
REM  Keep this file and backup_2026-11-22.sql in the SAME folder.
REM ====================================================================
echo.
echo Computer name : %COMPUTERNAME%
echo Date and time : %DATE% %TIME%
echo.

if not exist "%~dp0backup_2026-11-22.sql" (
  echo ERROR: backup_2026-11-22.sql was not found next to this file.
  pause
  exit /b 1
)

docker version >nul 2>&1
if errorlevel 1 (
  echo ERROR: Docker is not running. Start Docker Desktop, wait for the green icon, then run this file again.
  pause
  exit /b 1
)

echo [1/6] Removing any old test container...
docker rm -f pgtest >nul 2>&1

echo [2/6] Starting an empty PostgreSQL. The first time, Docker downloads the image, please wait...
docker run -d --name pgtest -e POSTGRES_PASSWORD=test postgres >nul
if errorlevel 1 (
  echo ERROR: could not start the PostgreSQL container.
  pause
  exit /b 1
)

echo [3/6] Waiting for the database to be ready...
set tries=0
:wait
set /a tries+=1
if %tries% GTR 90 (
  echo ERROR: the database did not start in time.
  pause
  exit /b 1
)
docker exec pgtest psql -U postgres -h 127.0.0.1 -c "select 1" >nul 2>&1
if errorlevel 1 (
  timeout /t 2 /nobreak >nul
  goto wait
)

echo [4/6] Copying the backup into the container...
docker cp "%~dp0backup_2026-11-22.sql" pgtest:/tmp/backup.sql

echo [5/6] Creating an empty database and restoring the backup...
docker exec pgtest psql -U postgres -c "CREATE DATABASE restore_test;"
docker exec pgtest psql -U postgres -d restore_test -q -v ON_ERROR_STOP=1 -f /tmp/backup.sql
if errorlevel 1 (
  echo.
  echo RESTORE FAILED. Send a screenshot of this window.
  pause
  exit /b 1
)

echo [6/6] Checking the restored data. Expected: tables=13, person=10560, invoice=20000, payment=28004
docker exec pgtest psql -U postgres -d restore_test -c "SELECT (SELECT count(*) FROM information_schema.tables WHERE table_schema='public') AS tables, (SELECT count(*) FROM person) AS person, (SELECT count(*) FROM invoice) AS invoice, (SELECT count(*) FROM payment) AS payment;"

echo.
echo DONE. Take a screenshot of this whole window and send it back.
echo.
pause
