$ErrorActionPreference = 'Stop'
$ue = 'T:\Program Files\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe'
$proj = 'D:\DEVELOPMENT\Games\IsekaiVillage\IsekaiVillage.uproject'
$map = '/Game/IsekaiVillage/AdventureWorld/Maps/Map_AnimeAdventure'
$py = 'D:\DEVELOPMENT\Games\IsekaiVillage\Scripts\run_hub_and_dungeon_v37.py'
Add-Type -Name Native -Namespace Win32 -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool LockSetForegroundWindow(uint uLockCode);
[DllImport("user32.dll")] public static extern bool ShowWindow(System.IntPtr hWnd, int nCmdShow);
[DllImport("user32.dll")] public static extern bool SetWindowPos(System.IntPtr hWnd, System.IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
'@
[Win32.Native]::LockSetForegroundWindow(1) | Out-Null
$p = Start-Process -FilePath $ue -ArgumentList @(
    "`"$proj`"", $map, '-nosplash', '-nop4',
    '-ResX=1280', '-ResY=720', '-WINDOWED'
) -PassThru -WindowStyle Minimized
Start-Sleep -Seconds 8
if ($p.MainWindowHandle -ne [IntPtr]::Zero) {
    [Win32.Native]::SetWindowPos($p.MainWindowHandle, [IntPtr]::Zero, 1920, 80, 1280, 720, 0x0040) | Out-Null
    [Win32.Native]::ShowWindow($p.MainWindowHandle, 6) | Out-Null
}
Write-Output ("LAUNCHED pid=" + $p.Id)
# reused for later one-shot applies via Saved/run_vXX.flag
