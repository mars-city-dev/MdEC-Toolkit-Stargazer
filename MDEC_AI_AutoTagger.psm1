# MDEC Phase 3: AI-Powered Auto-Tagging
# MDEC_AI_AutoTagger.ps1
# Uses content analysis and pattern recognition for intelligent tagging

Import-Module ".\MDEC_Tagging_Taxonomy.psm1"

function Get-ContentKeywords {
    param([string]$Content, [int]$TopN = 5)

    # Simple keyword extraction (in real AI, this would use NLP models)
    $words = $Content -split '\W+' | Where-Object { $_.Length -gt 3 } | ForEach-Object { $_.ToLower() }
    $wordCounts = @{}
    
    foreach ($word in $words) {
        if ($wordCounts.ContainsKey($word)) {
            $wordCounts[$word]++
        } else {
            $wordCounts[$word] = 1
        }
    }
    
    return $wordCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First $TopN | ForEach-Object { $_.Key }
}

function PredictTags {
    param([string]$FileName, [string]$Content = "", [string]$CurrentCategory)

    $predictedTags = @()
    $name = $FileName.ToLower()
    
    # Pattern-based tag prediction
    foreach ($category in $Taxonomy.Keys) {
        foreach ($keyword in $Taxonomy[$category]) {
            if ($name -match $keyword -or ($Content -and $Content -match $keyword)) {
                if ($predictedTags -notcontains $category) {
                    $predictedTags += $category
                }
            }
        }
    }
    
    # Content-based keyword extraction
    if ($Content) {
        $keywords = Get-ContentKeywords -Content $Content
        foreach ($keyword in $keywords) {
            # Map keywords to taxonomy categories
            foreach ($category in $Taxonomy.Keys) {
                if ($Taxonomy[$category] -contains $keyword) {
                    if ($predictedTags -notcontains $category) {
                        $predictedTags += $category
                    }
                }
            }
        }
    }
    
    # Category-specific tag enhancement
    switch ($CurrentCategory) {
        "Neural_DevOps_Protocol" { 
            $predictedTags += @("neural", "protocol", "infrastructure") | Where-Object { $predictedTags -notcontains $_ }
        }
        "Architectures" {
            $predictedTags += @("design", "system", "blueprint") | Where-Object { $predictedTags -notcontains $_ }
        }
        "Deployments" {
            $predictedTags += @("production", "release", "automation") | Where-Object { $predictedTags -notcontains $_ }
        }
    }
    
    return $predictedTags | Select-Object -Unique
}

function ApplyAIAutoTagging {
    param(
        [string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json",
        [switch]$UpdateExisting
    )

    if (-not (Test-Path $MetadataPath)) {
        Write-Host "❌ Metadata file not found: $MetadataPath" -ForegroundColor Red
        return
    }

    $metadata = Get-Content -Path $MetadataPath -Raw | ConvertFrom-Json
    $updated = 0

    foreach ($entry in $metadata.PSObject.Properties) {
        $entryData = $entry.Value
        $filePath = $entryData.path
        
        # Get file content for analysis (limit to .md files for performance)
        $content = ""
        if ($filePath -and (Test-Path $filePath) -and $filePath.EndsWith(".md")) {
            try {
                $content = Get-Content -Path $filePath -Raw
            } catch {
                # Skip content analysis if file can't be read
            }
        }
        
        # Predict tags using AI logic
        $predictedTags = PredictTags -FileName $entryData.name -Content $content -CurrentCategory $entryData.category
        
        # Update tags if better predictions found
        if ($predictedTags.Count -gt 0) {
            if ($UpdateExisting -or -not $entryData.tags -or $entryData.tags.Count -eq 0) {
                $entryData.tags = $predictedTags
                $updated++
            } elseif ($predictedTags.Count -gt $entryData.tags.Count) {
                # Merge with existing tags
                $mergedTags = ($entryData.tags + $predictedTags) | Select-Object -Unique
                $entryData.tags = $mergedTags
                $updated++
            }
        }
    }

    # Save updated metadata
    $metadata | ConvertTo-Json -Depth 10 | Set-Content -Path $MetadataPath -Encoding UTF8
    
    Write-Host "🤖 AI Auto-tagging complete! Updated $updated entries with intelligent tags" -ForegroundColor Green
}

# Export functions
Export-ModuleMember -Function PredictTags, ApplyAIAutoTagging