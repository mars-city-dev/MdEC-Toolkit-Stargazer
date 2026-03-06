# MDEC Category Mapping Algorithm
# Intelligent categorization of files based on content, path, and metadata

Import-Module ".\MDEC_Tagging_Taxonomy.psm1"

function Get-SmartCategory {
    param(
        [string]$FileName,
        [string]$FilePath,
        [object]$Metadata = $null
    )

    $name = $FileName.ToLower()
    $path = $FilePath.ToLower()
    
    # Priority-based categorization
    $categoryScores = @{}
    
    # Path-based scoring
    if ($path -match "neural.*devops" -or $name -match "neural.*devops") {
        $categoryScores["Neural_DevOps_Protocol"] = 100
    }
    if ($path -match "open.*data.*legacy" -or $name -match "open.*data.*legacy") {
        $categoryScores["Open_Data_Legacy"] = 90
    }
    if ($name -match "architecture") {
        $categoryScores["Architectures"] = 80
    }
    if ($name -match "deployment") {
        $categoryScores["Deployments"] = 70
    }
    if ($name -match "guide") {
        $categoryScores["User_Guides"] = 60
    }
    if ($name -match "protocol") {
        $categoryScores["Protocols"] = 50
    }
    
    # Content-based scoring (if metadata available)
    if ($Metadata -and $Metadata.content_metadata) {
        $topics = $Metadata.content_metadata.primary_topics
        foreach ($topic in $topics) {
            switch -Wildcard ($topic) {
                "neural*" { $categoryScores["Neural_DevOps_Protocol"] += 20 }
                "quantum*" { $categoryScores["Technical_Reports"] += 15 }
                "deploy*" { $categoryScores["Deployments"] += 15 }
                "architect*" { $categoryScores["Architectures"] += 15 }
            }
        }
    }
    
    # Tag-based scoring
    if ($Metadata -and $Metadata.tags) {
        foreach ($tag in $Metadata.tags) {
            if ($Taxonomy.neural -contains $tag) { $categoryScores["Neural_DevOps_Protocol"] += 10 }
            if ($Taxonomy.architecture -contains $tag) { $categoryScores["Architectures"] += 10 }
            if ($Taxonomy.deployment -contains $tag) { $categoryScores["Deployments"] += 10 }
        }
    }
    
    # Return highest scoring category
    if ($categoryScores.Count -gt 0) {
        $bestCategory = $categoryScores.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 1
        return $bestCategory.Name
    }
    
    # Default fallback
    return "Technical_Reports"
}

function Update-MetadataCategories {
    param(
        [string]$MetadataPath = "S:\Projects\Mars-City-Unity\metadata_database.json"
    )

    if (-not (Test-Path $MetadataPath)) {
        Write-Host "❌ Metadata file not found: $MetadataPath" -ForegroundColor Red
        return
    }

    $metadata = Get-Content -Path $MetadataPath -Raw | ConvertFrom-Json
    $updated = 0

    foreach ($entry in $metadata.PSObject.Properties) {
        $entryData = $entry.Value
        $smartCategory = Get-SmartCategory -FileName $entryData.name -FilePath $entryData.path -Metadata $entryData
        
        if ($entryData.category -ne $smartCategory) {
            $entryData.category = $smartCategory
            $updated++
        }
    }

    # Save updated metadata
    $metadata | ConvertTo-Json -Depth 10 | Set-Content -Path $MetadataPath -Encoding UTF8
    
    Write-Host "✅ Updated $updated entries with smart categorization" -ForegroundColor Green
}

# Export functions
Export-ModuleMember -Function Get-SmartCategory, Update-MetadataCategories