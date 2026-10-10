$desktop = [System.Environment]::GetFolderPath('Desktop')
$wsh = New-Object -ComObject WScript.Shell
$scPath = Join-Path $desktop "LIPTIS USA SALs App.lnk"
$sc = $wsh.CreateShortcut($scPath)
$sc.TargetPath = "wscript.exe"
$sc.Arguments = 'C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app\launch.vbs'
$sc.WorkingDirectory = 'C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app'
$sc.IconLocation = 'C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app\static\images\liptis.ico,0'
$sc.Description = "LIPTIS USA SALs App - Corporate Travel Platform"
$sc.Save()

# Also create direct .url shortcut as fallback
$urlPath = Join-Path $desktop "LIPTIS USA SALs App Web.url"
$urlContent = @"
[InternetShortcut]
URL=http://127.0.0.1:8000
IconFile=C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app\static\images\liptis.ico
IconIndex=0
"@
Set-Content -Path $urlPath -Value $urlContent

Write-Host "Created Desktop Shortcuts successfully at: $desktop"
