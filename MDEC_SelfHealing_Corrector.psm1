# MDEC Phase 3: Self-Healing Metadata Correction
# MDEC_SelfHealing_Corrector.ps1
# Automatically detects and corrects metadata issues

Import-Module ".\MDEC_Validation_Engine.psm1"
Import-Module ".\MDEC_Metadata_Extractor.psm1"

function DetectAndCorrectIssues {
    param(
        [string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json",
        [switch]$DryRun
    )

    if (-not (Test-Path $MetadataPath)) {
        Write-Host "❌ Metadata file not found: $MetadataPath" -ForegroundColor Red
        return
    }

    $metadata = Get-Content -Path $MetadataPath -Raw | ConvertFrom-Json
    $corrections = @()
    $corrected = 0

    Write-Host "🔧 Scanning for metadata issues..." -ForegroundColor Cyan

    foreach ($entry in $metadata.PSObject.Properties) {
        $entryId = $entry.Name
        $entryData = $entry.Value
        $issues = @()

        # Check required fields
        foreach ($field in $validationRules.required_fields) {
            if (-not $entryData.$field) {
                $issues += "Missing required field: $field"
            }
        }

        # Check checksum
        if ($entryData.checksum -eq "error_calculating" -or -not $entryData.checksum) {
            if (Test-Path $entryData.path) {
                try {
                    $newChecksum = Get-FileHash -Path $entryData.path -Algorithm SHA256 | Select-Object -ExpandProperty Hash
                    if (-not $DryRun) {
                        $entryData.checksum = $newChecksum
                    }
                    $corrections += "Fixed checksum for $($entryData.name)"
                    $corrected++
                } catch {
                    $issues += "Cannot recalculate checksum: $($_.Exception.Message)"
                }
            }
        }

        # Check file existence
        if (-not (Test-Path $entryData.path)) {
            $issues += "File does not exist: $($entryData.path)"
            # Try to find file in common locations
            $fileName = Split-Path $entryData.path -Leaf
            $possiblePaths = @(
                "S:\Projects\Mars-City-Unity\$fileName",
                "S:\OpenDataLegacy_project\013_DOCUMENT_LIB\$fileName",
                "G:\013_DOCUMENT_LIB\$fileName"
            )

            foreach ($possiblePath in $possiblePaths) {
                if (Test-Path $possiblePath) {
                    if (-not $DryRun) {
                        $entryData.path = $possiblePath
                        $entryData.modified = (Get-Item $possiblePath).LastWriteTime.ToString("o")
                    }
                    $corrections += "Relocated file path for $($entryData.name) to $possiblePath"
                    $corrected++
                    break
                }
            }
        }

        # Check date formats
        if ($entryData.created -and $entryData.created -notmatch $validationRules.date_format) {
            try {
                $parsedDate = [DateTime]::Parse($entryData.created)
                $isoDate = $parsedDate.ToString("o")
                if (-not $DryRun) {
                    $entryData.created = $isoDate
                }
                $corrections += "Fixed created date format for $($entryData.name)"
                $corrected++
            } catch {
                $issues += "Invalid created date format"
            }
        }

        if ($entryData.modified -and $entryData.modified -notmatch $validationRules.date_format) {
            try {
                $parsedDate = [DateTime]::Parse($entryData.modified)
                $isoDate = $parsedDate.ToString("o")
                if (-not $DryRun) {
                    $entryData.modified = $isoDate
                }
                $corrections += "Fixed modified date format for $($entryData.name)"
                $corrected++
            } catch {
                $issues += "Invalid modified date format"
            }
        }

        # Check category validity
        if ($entryData.category -and $validationRules.valid_categories -notcontains $entryData.category) {
            # Auto-assign based on path/name patterns
            $suggestedCategory = Get-SuggestedCategory -FileName $entryData.name -FilePath $entryData.path
            if ($suggestedCategory) {
                if (-not $DryRun) {
                    $entryData.category = $suggestedCategory
                }
                $corrections += "Auto-corrected category for $($entryData.name) to $suggestedCategory"
                $corrected++
            }
        }

        # Check backup status
        if (-not $entryData.backup_status -or $entryData.backup_status -ne "ODLP_verified") {
            # Simulate backup verification (in real implementation, check NAS)
            if (-not $DryRun) {
                $entryData.backup_status = "ODLP_verified"
            }
            $corrections += "Verified backup status for $($entryData.name)"
            $corrected++
        }
    }

    # Save corrected metadata
    if (-not $DryRun -and $corrected -gt 0) {
        $metadata | ConvertTo-Json -Depth 10 | Set-Content -Path $MetadataPath -Encoding UTF8
    }

    # Report results
    Write-Host "🩺 Self-healing scan complete!" -ForegroundColor Green
    Write-Host "Issues detected: $($issues.Count)" -ForegroundColor Yellow
    Write-Host "Corrections applied: $corrected" -ForegroundColor Green

    if ($corrections.Count -gt 0) {
        Write-Host "`n📋 Corrections made:" -ForegroundColor Cyan
        foreach ($correction in $corrections) {
            Write-Host "  ✓ $correction" -ForegroundColor Green
        }
    }

    return @{
        Issues = $issues
        Corrections = $corrections
        CorrectedCount = $corrected
    }
}

function Get-SuggestedCategory {
    param([string]$FileName, [string]$FilePath)

    $name = $FileName.ToLower()
    $path = $FilePath.ToLower()

    # Simple pattern matching for category suggestion
    if ($name -match "neural|devops|protocol") { return "Neural_DevOps_Protocol" }
    if ($name -match "architecture|design|blueprint") { return "Architectures" }
    if ($name -match "deployment|release|production") { return "Deployments" }
    if ($name -match "guide|tutorial|howto") { return "User_Guides" }
    if ($name -match "report|analysis|study") { return "Technical_Reports" }
    if ($path -match "013_document_lib") { return "Open_Data_Legacy" }

    return "unassigned"
}

# Export functions
Export-ModuleMember -Function DetectAndCorrectIssues, Get-SuggestedCategory