# Discover installed 3D applications without assuming a drive letter or version.
$ErrorActionPreference = 'SilentlyContinue'
$targets = @{
    '3ds Max batch' = '3dsmaxbatch.exe'; '3ds Max' = '3dsmax.exe'; 'Maya Python' = 'mayapy.exe'
    'Blender' = 'blender.exe'; 'Rhino' = 'Rhino.exe'; 'RhinoCode' = 'rhinocode.exe'
    'Cinema 4D Python' = 'c4dpy.exe'; 'Cinema 4D' = 'Cinema 4D.exe'
}
$found = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
function Add-AppPath([string]$path, [string]$kind) {
    if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) { [void]$found.Add("$kind|$((Resolve-Path -LiteralPath $path).Path)") }
}
foreach ($pair in $targets.GetEnumerator()) { $cmd = Get-Command $pair.Value -ErrorAction SilentlyContinue | Select-Object -First 1; if ($cmd) { Add-AppPath $cmd.Source $pair.Key } }
Get-ChildItem Env: | Where-Object { $_.Name -match 'AUTODESK|3DSMAX|MAYA|BLENDER|RHINO|C4D|MAXON' } | ForEach-Object {
    if (Test-Path -LiteralPath $_.Value -PathType Container) { foreach ($pair in $targets.GetEnumerator()) { Get-ChildItem -LiteralPath $_.Value -Filter $pair.Value -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object { Add-AppPath $_.FullName $pair.Key } } }
}
$keys = 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
Get-ItemProperty $keys -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match '3ds Max|Autodesk Maya|Blender|Rhino|Rhinoceros|Cinema 4D|Maxon' } | ForEach-Object {
    @($_.InstallLocation,(Split-Path $_.DisplayIcon -Parent)) | Where-Object { $_ -and (Test-Path -LiteralPath $_ -PathType Container) } | ForEach-Object { $root=$_; foreach ($pair in $targets.GetEnumerator()) { Get-ChildItem -LiteralPath $root -Filter $pair.Value -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object { Add-AppPath $_.FullName $pair.Key } } }
}
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { Test-Path $_.Root }
foreach ($drive in $drives) {
    @('Program Files','Program Files (x86)','Applications','Autodesk','Maxon','Software','YSL-Software') | ForEach-Object { Join-Path $drive.Root $_ } | Where-Object { Test-Path -LiteralPath $_ -PathType Container } | ForEach-Object { $root=$_; foreach ($pair in $targets.GetEnumerator()) { Get-ChildItem -LiteralPath $root -Filter $pair.Value -File -Recurse -ErrorAction SilentlyContinue | ForEach-Object { Add-AppPath $_.FullName $pair.Key } } }
}
foreach ($drive in $drives) { foreach ($pair in $targets.GetEnumerator()) { Get-ChildItem -LiteralPath $drive.Root -Filter $pair.Value -File -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\Windows\\|\\\$Recycle\.Bin\\|\\AppData\\Local\\Temp\\' } | ForEach-Object { Add-AppPath $_.FullName $pair.Key } } }
$found | ForEach-Object { $p=$_ -split '\|',2; [pscustomobject]@{Application=$p[0];Executable=$p[1]} } | Sort-Object Application,Executable
