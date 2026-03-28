# MDEC Global Toolkit Core Manager
# Version: 1.0.0 (Codex Aligned)
# Usage: Run this script to access the MDEC Operational Suite.

$mdecVersion = "1.0.0"
$appId = "ODLP-NODE-01"

function Show-Header {
    Clear-Host
    Write-Host "================================================" -ForegroundColor DarkYellow
    Write-Host "     MDEC GLOBAL TOOLKIT CORE - v$mdecVersion" -ForegroundColor Yellow
    Write-Host "     Node: $appId | Mars City Unity" -ForegroundColor Yellow
    Write-Host "================================================" -ForegroundColor DarkYellow
}

function Invoke-Auditor {
    Write-Host "[MGT-AUDITOR] Scanning [RAW] for compliance via Powerhouse Logic..." -ForegroundColor Cyan
    # Call the Powerhouse logic in MdEC-Toolkit-Stargazer
    python "D:\Projects\MdEC-Toolkit-Stargazer\smart_data_organizer_powerhouse.py" --audit --dir "D:\Projects\MDEC-Consortium\RAW"
    Write-Host "AUDIT COMPLETE: Check manifest for compliance results." -ForegroundColor Green
}

function Invoke-Certifier {
    Write-Host "[MGT-CERTIFIER] Calculating Quality Scores via MDEC Scorer..." -ForegroundColor Cyan
    # Call the Quality Scorer logic
    python "D:\Projects\MdEC-Toolkit-Stargazer\mdec_quality_scorer.py" --dir "D:\Projects\MDEC-Consortium\RAW"
    Write-Host "SCORE CALCULATION COMPLETE." -ForegroundColor Green
}

# --- MAIN MENU LOOP ---
$running = $true
while ($running) {
    Show-Header
    Write-Host "1. [AUDITOR]   Check [RAW] for MDEC Compliance"
    Write-Host "2. [CATALOGER] Extract Metadata & Generate Hashes"
    Write-Host "3. [SCRUBBER]  Standardize Filenames (ISO-8601)"
    Write-Host "4. [CERTIFIER] Generate Quality Score Report"
    Write-Host "5. [INGESTOR]  Move Certified Data to [VAULT]"
    Write-Host "Q. Quit"
    Write-Host "------------------------------------------------"
    $choice = Read-Host "Select MDEC Operation"

    switch ($choice) {
        "1" { Invoke-Auditor }
        "2" { Write-Host "MGT-CATALOGER: Functionality coming in v1.1"; Pause }
        "3" { Write-Host "MGT-SCRUBBER: Functionality coming in v1.1"; Pause }
        "4" { Invoke-Certifier }
        "5" { Write-Host "ACCESS DENIED: Quality Score < 70%."; Pause }
        "Q" { $running = $false }
        default { Write-Host "Invalid Operation." -ForegroundColor Red; Start-Sleep -Seconds 1 }
    }
}

Write-Host "MDEC Session Terminated. Excellence is Mandatory." -ForegroundColor Cyan
