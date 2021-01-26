@echo off

start cmd /c SCHTASKS /CREATE /SC DAILY /TN "HeartbeatAutostart" /TR ".\heartbeat.exe" /ST 18:15
