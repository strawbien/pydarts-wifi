# ============================================================
# pyDarts-WiFi — Script d'installation Windows
# https://github.com/strawbien/pydarts-wifi
# ============================================================

$REPO_URL    = "https://github.com/strawbien/pydarts-wifi/archive/refs/heads/main.zip"
$INSTALL_DIR = "$env:USERPROFILE\pydarts-wifi"
$ZIP_TMP     = "$env:TEMP\pydarts-wifi.zip"
$MAIN_SCRIPT = "$INSTALL_DIR\pydarts.py"

function Write-Step($msg) {
    Write-Host "`n>>> $msg" -ForegroundColor Cyan
}
function Write-OK($msg) {
    Write-Host "    [OK] $msg" -ForegroundColor Green
}
function Write-Err($msg) {
    Write-Host "    [ERREUR] $msg" -ForegroundColor Red
}

# ── Bannière ────────────────────────────────────────────────
Clear-Host
Write-Host @"
  ____        ____             _          __        ___ _____ _
 |  _ \ _   _|  _ \  __ _ _ __| |_ ___   \ \      / (_)  ___(_)
 | |_) | | | | | | |/ _' | '__| __/ __|   \ \ /\ / /| | |_  | |
 |  __/| |_| | |_| | (_| | |  | |_\__ \    \ V  V / | |  _| | |
 |_|    \__, |____/ \__,_|_|   \__|___/     \_/\_/  |_|_|   |_|
        |___/
"@ -ForegroundColor Magenta
Write-Host "  Installation de pyDarts-WiFi`n" -ForegroundColor White

# ── Vérification Python ─────────────────────────────────────
Write-Step "Vérification de Python..."
try {
    $pyVersion = python --version 2>&1
    Write-OK "Python détecté : $pyVersion"
} catch {
    Write-Err "Python non trouvé. Installe Python depuis https://python.org puis relance ce script."
    Pause
    Exit 1
}

# ── Vérification pip ────────────────────────────────────────
Write-Step "Vérification de pip..."
try {
    $pipVersion = pip --version 2>&1
    Write-OK "pip détecté : $pipVersion"
} catch {
    Write-Err "pip non trouvé. Lance : python -m ensurepip --upgrade"
    Pause
    Exit 1
}

# ── Téléchargement du repo ──────────────────────────────────
Write-Step "Téléchargement de pyDarts-WiFi depuis GitHub..."
try {
    Invoke-WebRequest -Uri $REPO_URL -OutFile $ZIP_TMP -UseBasicParsing
    Write-OK "Téléchargement terminé"
} catch {
    Write-Err "Impossible de télécharger le repo : $($_.Exception.Message)"
    Pause
    Exit 1
}

# ── Extraction ──────────────────────────────────────────────
Write-Step "Extraction des fichiers..."
if (Test-Path $INSTALL_DIR) {
    Remove-Item $INSTALL_DIR -Recurse -Force
}
Expand-Archive -Path $ZIP_TMP -DestinationPath "$env:USERPROFILE" -Force
$extracted = "$env:USERPROFILE\pydarts-wifi-main"
if (Test-Path $extracted) {
    Rename-Item $extracted $INSTALL_DIR
}
Remove-Item $ZIP_TMP -Force
Write-OK "Installé dans : $INSTALL_DIR"

# ── Installation des dépendances Python ─────────────────────
Write-Step "Installation des dépendances Python..."
$requirementsFile = "$INSTALL_DIR\requirements.txt"
if (Test-Path $requirementsFile) {
    pip install -r $requirementsFile --quiet
    Write-OK "Dépendances installées depuis requirements.txt"
} else {
    Write-Host "    [INFO] Pas de requirements.txt — installation des dépendances de base" -ForegroundColor Yellow
    pip install pyserial websockets pygame --quiet
    Write-OK "Dépendances de base installées (pyserial, websockets, pygame)"
}

# ── Raccourci bureau ────────────────────────────────────────
Write-Step "Création du raccourci bureau..."
$desktop  = [Environment]::GetFolderPath("Desktop")
$shortcut = "$desktop\pyDarts-WiFi.lnk"

$shell = New-Object -ComObject WScript.Shell
$lnk   = $shell.CreateShortcut($shortcut)
$lnk.TargetPath       = "python"
$lnk.Arguments        = "`"$MAIN_SCRIPT`""
$lnk.WorkingDirectory = $INSTALL_DIR
$lnk.IconLocation     = "python.exe"
$lnk.Description      = "pyDarts WiFi"
$lnk.Save()
Write-OK "Raccourci créé sur le bureau : pyDarts-WiFi"

# ── Résumé ──────────────────────────────────────────────────
Write-Host "`n============================================" -ForegroundColor Magenta
Write-Host "  Installation terminée !" -ForegroundColor Green
Write-Host "  Dossier    : $INSTALL_DIR" -ForegroundColor White
Write-Host "  Démarrage  : double-clic sur pyDarts-WiFi (bureau)" -ForegroundColor White
Write-Host "  Ou en CLI  : python `"$MAIN_SCRIPT`"" -ForegroundColor White
Write-Host "============================================`n" -ForegroundColor Magenta

Pause
