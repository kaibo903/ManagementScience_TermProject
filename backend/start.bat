@echo off
echo 啟動後端 API 服務器...
cd /d %~dp0
uvicorn main:app --reload --host 0.0.0.0 --port 8000

