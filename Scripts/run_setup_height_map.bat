@echo off
setlocal
set UE="T:\Program Files\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set PROJECT="F:\DEVELOPMENT\Games\SpellCraft\SpellCraft.uproject"
set SCRIPT="F:\DEVELOPMENT\Games\SpellCraft\Scripts\replace_height_with_demonstration.py"

echo Close Unreal Editor before running.
echo Replacing Height map with full SoStylized Demonstration copy...
%UE% %PROJECT% -run=pythonscript -script=%SCRIPT% -stdout -unattended -nosplash -nullrhi
echo Done. Check Saved\Logs\SpellCraft_2.log for details.
pause
