@echo off
cd C:\Users\Raghu\tradingbot

:: Create logs folder if not exists
if not exist logs mkdir logs

:: Generate log filename with date
set logfile=logs\bot_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log

:: Run and log everything
echo Starting Trading Bot - %date% %time% > %logfile%
python alpaca_scheduler.py --interval -5m >> %logfile% 2>&1

echo Bot stopped - %date% %time% >> %logfile%
