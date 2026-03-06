# MDEC Phase 3: Predictive Categorization
# MDEC_Predictive_Categorizer.ps1
# Uses machine learning patterns to predict file categories

Import-Module ".\MDEC_Category_Mapper.psm1"

function AnalyzeCategoryPatterns {
    param([string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json")

    $metadata = Get-Content -Path $MetadataPath -Raw | ConvertFrom-Json
    $patterns = @{}
    
    foreach ($entry in $metadata.PSObject.Properties) {
        $data = $entry.Value
        $category = $data.category
        $name = $data.name.ToLower()
        $path = $data.path.ToLower()
        
        if (-not $patterns.ContainsKey($category)) {
            $patterns[$category] = @{
                NamePatterns = @()
                PathPatterns = @()
                Keywords = @()
                Count = 0
            }
        }
        
        $patterns[$category].Count++
        
        # Extract patterns from names
        $nameWords = $name -split '[^a-zA-Z0-9]' | Where-Object { $_.Length -gt 2 }
        $patterns[$category].NamePatterns += $nameWords
        
        # Extract path segments
        $pathSegments = $path -split '\\|/' | Where-Object { $_ -and $_.Length -gt 2 }
        $patterns[$category].PathPatterns += $pathSegments
        
        # Extract keywords from tags
        if ($data.tags) {
            $patterns[$category].Keywords += $data.tags
        }
    }
    
    # Calculate frequency and create pattern models
    foreach ($category in $patterns.Keys) {
        $patterns[$category].NamePatterns = $patterns[$category].NamePatterns | Group-Object | Sort-Object Count -Descending | Select-Object -First 10 | ForEach-Object { $_.Name }
        $patterns[$category].PathPatterns = $patterns[$category].PathPatterns | Group-Object | Sort-Object Count -Descending | Select-Object -First 5 | ForEach-Object { $_.Name }
        $patterns[$category].Keywords = $patterns[$category].Keywords | Group-Object | Sort-Object Count -Descending | Select-Object -First 10 | ForEach-Object { $_.Name }
    }
    
    return $patterns
}

function PredictCategory {
    param([string]$FileName, [string]$FilePath, [array]$ExistingTags = @(), [hashtable]$Patterns)

    $name = $FileName.ToLower()
    $path = $FilePath.ToLower()
    $predictions = @{}
    
    foreach ($category in $Patterns.Keys) {
        $score = 0
        
        # Name pattern matching
        foreach ($pattern in $Patterns[$category].NamePatterns) {
            if ($name -match $pattern) { $score += 3 }
        }
        
        # Path pattern matching
        foreach ($pattern in $Patterns[$category].PathPatterns) {
            if ($path -match $pattern) { $score += 2 }
        }
        
        # Tag matching
        foreach ($tag in $ExistingTags) {
            if ($Patterns[$category].Keywords -contains $tag) { $score += 4 }
        }
        
        # Category frequency bonus
        $score += [math]::Log($Patterns[$category].Count + 1)
        
        $predictions[$category] = $score
    }
    
    # Return top prediction
    return $predictions.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1 | ForEach-Object { $_.Key }
}

function ApplyPredictiveCategorization {
    param(
        [string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json",
        [switch]$ForceUpdate
    )

    Write-Host "🔮 Analyzing category patterns..." -ForegroundColor Cyan
    $patterns = AnalyzeCategoryPatterns -MetadataPath $MetadataPath
    
    $metadata = Get-Content -Path $MetadataPath -Raw | ConvertFrom-Json
    $updated = 0
    
    foreach ($entry in $metadata.PSObject.Properties) {
        $data = $entry.Value
        
        # Skip if category already exists and not forcing update
        if ($data.category -and -not $ForceUpdate) { continue }
        
        $predictedCategory = PredictCategory -FileName $data.name -FilePath $data.path -ExistingTags $data.tags -Patterns $patterns
        
        if ($predictedCategory -and $predictedCategory -ne $data.category) {
            $data.category = $predictedCategory
            $updated++
        }
    }
    
    # Save updated metadata
    $metadata | ConvertTo-Json -Depth 10 | Set-Content -Path $MetadataPath -Encoding UTF8
    
    Write-Host "🎯 Predictive categorization complete! Updated $updated entries" -ForegroundColor Green
}

# Export functions
Export-ModuleMember -Function AnalyzeCategoryPatterns, PredictCategory, ApplyPredictiveCategorization