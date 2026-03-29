<#
.SYNOPSIS
    Search-Neural-Cortex.ps1 - Next Generation Search Tool v1.0
    
.DESCRIPTION
    High-performance network-wide search for the Quad-Cortex federation.
    Optimized for the Spline 1016 discovery of 10,000+ items.
    
    Nodes: UNITY (U:), STARGAZER (S:), MARSTHREE (M:), TITANESS (T:)

.EXAMPLE
    .\Search-Neural-Cortex.ps1 "Discovery Report"
    .\Search-Neural-Cortex.ps1 -Category "01_Documents" "Spline"
#>

param(
    [Parameter(Position=0, Mandatory=$true)]
    [string]$Query,

    [ValidateSet("01_Documents", "02_Media", "03_Data", "04_Code", "05_Archives", "01_Ingest", "07_Vault", "08_Archive")]
    [string]$Category
)

Write-Host "--- [ TITANESS NEURAL SEARCH v1.0 ONLINE ] ---" -ForegroundColor Cyan
Write-Host "Resonance: LOCKED at 60 BPM" -ForegroundColor Yellow

# Define the Synaptic Mapping (Standard Drives)
$SynapticNodes = @{
    "U:" = "Coordination"
    "S:" = "Vision/LTM"
    "M:" = "Logic/Motor"
    "T:" = "Awareness/Dev"
}

$Results = @()

foreach ($Drive in $SynapticNodes.Keys) {
    if (Test-Path "$Drive\SubCortices") {
        $SearchPath = "$Drive\SubCortices"
        
        # Apply Category filtering if requested
        if ($Category) {
            $SearchPath = Join-Path $SearchPath "**\$Category"
        }

        Write-Host "Scanning $($SynapticNodes[$Drive]) ($Drive)..." -ForegroundColor Gray
        
        try {
            # Fast-twitch recursive search (Limited depth for speed if no category)
            $NeuralMatches = Get-ChildItem -Path $SearchPath -Filter "*$Query*" -Recurse -ErrorAction SilentlyContinue | 
                       Where-Object { $_.PSIsContainer -eq $false }
            
            foreach ($Match in $NeuralMatches) {
                $Results += [PSCustomObject]@{
                    Node = $SynapticNodes[$Drive]
                    Drive = $Drive
                    Name = $Match.Name
                    Path = $Match.FullName
                    Size = "$([math]::Round($Match.Length / 1KB, 2)) KB"
                }
            }
        } catch {
            Write-Warning "Synapse Blocked: $($Drive) is non-responsive."
        }
    }
}

# --- RENDER RESULTS ---
if ($Results.Count -gt 0) {
    Write-Host "`n[ $($Results.Count) NEURAL SIGNALS DETECTED ]" -ForegroundColor Green
    foreach ($Res in $Results) {
        Write-Host "`n[ $($Res.Node) ($($Res.Drive)) ]" -ForegroundColor Cyan
        Write-Host "File: $($Res.Name)" -ForegroundColor White
        Write-Host "Path: $($Res.Path)" -ForegroundColor Gray
        Write-Host "Size: $($Res.Size)"
    }
} else {
    Write-Host "`nNo matches found in long-term memory." -ForegroundColor Gray
}

Write-Host "`n--- [ SEARCH COMPLETE ] ---" -ForegroundColor Cyan
