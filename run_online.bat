@ECHO OFF
REM This script launches the game in online mode (connected to server)

cd /D %~dp0

SET RES_PATH=%~dp0res
SET BW_RES_PATH=..\bigworld\res

SET EXE_NAME=..\bigworld\bin\client\bwclient.exe

START %EXE_NAME% --res %RES_PATH%;%BW_RES_PATH% %*
