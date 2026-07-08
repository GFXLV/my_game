@ECHO OFF
REM This script launches the game

REM Change to the correct folder
cd /D %~dp0

REM The path to your resources
SET RES_PATH=%~dp0res

REM The path to the BigWorld resources
SET BW_RES_PATH=..\..\..\bigworld\res

SET EXE_NAME=..\bigworld\bin\client\bwclient.exe

START %EXE_NAME% --res %RES_PATH%;%BW_RES_PATH% %*
