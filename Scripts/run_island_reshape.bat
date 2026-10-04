@echo off
setlocal
set UE="T:\Program Files\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
set PROJECT="F:\DEVELOPMENT\Games\SpellCraft\SpellCraft.uproject"

echo Step 1: Generate island heightmap (system Python)...
python "F:\DEVELOPMENT\Games\SpellCraft\Scripts\create_island_heightmap_v2.py"
if errorlevel 1 exit /b 1

echo.
echo Step 2: Apply heightmap to Height_DemoCopy (close editor first)...
%UE% %PROJECT% -run=pythonscript -script="F:\DEVELOPMENT\Games\SpellCraft\Scripts\reshape_height_democopy_island.py" -AllowCommandletRendering -stdout -unattended -nosplash

echo Done. Open Height_DemoCopy — SW crescent beach, NE mountain range.
pause
