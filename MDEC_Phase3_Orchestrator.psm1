# MDEC Phase 3: AI Automation Orchestrator
# MDEC_Phase3_Orchestrator.ps1
# Coordinates all Phase 3 AI automation components

Import-Module ".\MDEC_AI_AutoTagger.psm1"
Import-Module ".\MDEC_Predictive_Categorizer.psm1"
Import-Module ".\MDEC_SelfHealing_Corrector.psm1"
Import-Module ".\MDEC_Validation_Engine.psm1"

function Start-MDECAIAutomation {
    param(
        [string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json",
        [switch]$FullCycle,
        [switch]$RealTimeMode,
        [int]$CycleIntervalMinutes = 60
    )

    Write-Host "🚀 MDEC Phase 3: AI Automation Starting..." -ForegroundColor Magenta
    Write-Host "🤖 AI-Powered Metadata Excellence Consortium" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════" -ForegroundColor White

    if ($RealTimeMode) {
        Write-Host "🔄 Starting real-time validation mode..." -ForegroundColor Yellow
        Start-RealTimeValidation -MetadataPath $MetadataPath
        return
    }

    if ($FullCycle) {
        Write-Host "🔄 Running full AI automation cycle..." -ForegroundColor Yellow

        # Step 1: Self-healing corrections
        Write-Host "`n1️⃣ Self-Healing Corrections" -ForegroundColor Cyan
        $healingResults = DetectAndCorrectIssues -MetadataPath $MetadataPath
        Write-Host "   ✅ Applied $($healingResults.CorrectedCount) corrections" -ForegroundColor Green

        # Step 2: Predictive categorization
        Write-Host "`n2️⃣ Predictive Categorization" -ForegroundColor Cyan
        ApplyPredictiveCategorization -MetadataPath $MetadataPath -ForceUpdate
        Write-Host "   ✅ AI categorization applied" -ForegroundColor Green

        # Step 3: AI auto-tagging
        Write-Host "`n3️⃣ AI Auto-Tagging" -ForegroundColor Cyan
        ApplyAIAutoTagging -MetadataPath $MetadataPath -UpdateExisting
        Write-Host "   ✅ Intelligent tagging completed" -ForegroundColor Green

        # Step 4: Validation and quality scoring
        Write-Host "`n4️⃣ Quality Validation" -ForegroundColor Cyan
        $validationResults = Test-MetadataDatabase -MetadataPath $MetadataPath -ReportOnly
        Write-Host "   ✅ Validation complete: $($validationResults.valid) valid, $($validationResults.invalid) issues" -ForegroundColor Green

        Write-Host "`n🎉 Phase 3 AI Automation Cycle Complete!" -ForegroundColor Magenta
        Write-Host "📊 Quality Score: $([math]::Round(($validationResults.valid / ($validationResults.valid + $validationResults.invalid)) * 100, 1))%" -ForegroundColor Cyan

    } else {
        # Interactive mode - show menu
        do {
            Write-Host "`n🤖 MDEC Phase 3 AI Automation Menu" -ForegroundColor Cyan
            Write-Host "══════════════════════════════════" -ForegroundColor White
            Write-Host "1. Run Self-Healing Corrections" -ForegroundColor Yellow
            Write-Host "2. Apply Predictive Categorization" -ForegroundColor Yellow
            Write-Host "3. Execute AI Auto-Tagging" -ForegroundColor Yellow
            Write-Host "4. Start Real-Time Validation" -ForegroundColor Yellow
            Write-Host "5. Run Full Automation Cycle" -ForegroundColor Yellow
            Write-Host "6. Exit" -ForegroundColor Gray
            Write-Host ""

            $choice = Read-Host "Select option (1-6)"

            switch ($choice) {
                "1" {
                    Write-Host "`n🔧 Running Self-Healing Corrections..." -ForegroundColor Cyan
                    DetectAndCorrectIssues -MetadataPath $MetadataPath
                }
                "2" {
                    Write-Host "`n🎯 Applying Predictive Categorization..." -ForegroundColor Cyan
                    ApplyPredictiveCategorization -MetadataPath $MetadataPath
                }
                "3" {
                    Write-Host "`n🤖 Executing AI Auto-Tagging..." -ForegroundColor Cyan
                    ApplyAIAutoTagging -MetadataPath $MetadataPath -UpdateExisting
                }
                "4" {
                    Write-Host "`n🔄 Starting Real-Time Validation..." -ForegroundColor Cyan
                    Start-RealTimeValidation -MetadataPath $MetadataPath
                    return  # This runs indefinitely
                }
                "5" {
                    Write-Host "`n🚀 Running Full Automation Cycle..." -ForegroundColor Cyan
                    Start-MDECAIAutomation -MetadataPath $MetadataPath -FullCycle
                }
                "6" {
                    Write-Host "`n👋 Exiting MDEC Phase 3 Automation" -ForegroundColor Green
                    return
                }
                default {
                    Write-Host "❌ Invalid choice. Please select 1-6." -ForegroundColor Red
                }
            }

            if ($choice -ne "4") {
                Read-Host "`nPress Enter to continue"
            }

        } while ($choice -ne "6")
    }
}

# Scheduled automation function
function Start-ScheduledAutomation {
    param(
        [string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json",
        [int]$IntervalMinutes = 60
    )

    Write-Host "⏰ Starting scheduled MDEC AI automation (every $IntervalMinutes minutes)..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray

    while ($true) {
        $startTime = Get-Date
        Write-Host "`n$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Running scheduled automation cycle..." -ForegroundColor Yellow

        try {
            Start-MDECAIAutomation -MetadataPath $MetadataPath -FullCycle
        } catch {
            Write-Host "❌ Automation cycle failed: $($_.Exception.Message)" -ForegroundColor Red
        }

        $endTime = Get-Date
        $duration = $endTime - $startTime
        Write-Host "✅ Cycle completed in $([math]::Round($duration.TotalSeconds, 1)) seconds" -ForegroundColor Green

        # Wait for next cycle
        $nextRun = $startTime.AddMinutes($IntervalMinutes)
        $waitSeconds = [math]::Max(0, ($nextRun - (Get-Date)).TotalSeconds)
        Write-Host "⏳ Next cycle at $(Get-Date $nextRun -Format 'HH:mm:ss')..." -ForegroundColor Gray

        Start-Sleep -Seconds $waitSeconds
    }
}

# Export functions
Export-ModuleMember -Function Start-MDECAIAutomation, Start-ScheduledAutomation