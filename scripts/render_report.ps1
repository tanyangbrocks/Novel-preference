# scripts/render_report.ps1
# 在 Windows（中文系統、使用者名稱含中文）用 Quarto 渲染報告。
# 原因：Quarto 1.11.9 的 Lua 濾鏡在預設暫存路徑（C:\Users\<含中文的使用者名稱>\AppData\Local\Temp）
# 會因 CP950 編碼錯誤失敗（recoverEncode: cannot encode character '\65533'）。
# 做法：只對這次渲染的行程把 TEMP/TMP 指到純英文路徑，不更動系統設定。
#
# 用法（在專案根目錄）：
#   powershell -ExecutionPolicy Bypass -File scripts\render_report.ps1 [-Target report\index.qmd] [-To html]

param(
    [string]$Target = "report",
    [string]$To = ""
)

$quarto = "C:\Program Files\Quarto\bin\quarto.exe"
if (!(Test-Path $quarto)) { Write-Host "[render] 找不到 Quarto：$quarto"; exit 1 }

$tmp = "C:\qtmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TEMP = $tmp
$env:TMP = $tmp
$env:PYTHONIOENCODING = "utf-8"

$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    if ($To -ne "") { & $quarto render $Target --to $To } else { & $quarto render $Target }
    exit $LASTEXITCODE
} finally { Pop-Location }
