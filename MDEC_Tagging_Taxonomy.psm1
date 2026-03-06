# MDEC Universal Tagging Taxonomy
# Standardized metadata tags for the Meta Data Excellence Consortium

# Core Categories
$Taxonomy = @{
    # Content Types
    "documentation" = @("guide", "manual", "reference", "tutorial", "readme")
    "code" = @("script", "algorithm", "function", "class", "module")
    "research" = @("study", "analysis", "experiment", "theory", "hypothesis")
    "architecture" = @("design", "blueprint", "system", "infrastructure", "framework")
    
    # Domains
    "neural" = @("neural", "brain", "cognition", "synapse", "neuron")
    "quantum" = @("quantum", "physics", "entanglement", "superposition", "wave")
    "ai" = @("artificial", "intelligence", "machine", "learning", "model")
    "data" = @("database", "storage", "indexing", "retrieval", "metadata")
    
    # Operations
    "deployment" = @("deploy", "production", "staging", "release", "launch")
    "development" = @("develop", "build", "test", "debug", "prototype")
    "maintenance" = @("monitor", "backup", "update", "patch", "audit")
    "security" = @("encrypt", "authenticate", "authorize", "protect", "secure")
    
    # File Types
    "markdown" = @("md", "markdown", "text")
    "script" = @("ps1", "py", "sh", "bat", "js")
    "config" = @("json", "yaml", "xml", "ini", "conf")
    "media" = @("wav", "mp4", "jpg", "png", "pdf")
}

# Tag Priority (higher number = more important)
$TagPriority = @{
    "neural" = 10
    "quantum" = 9
    "architecture" = 8
    "deployment" = 7
    "security" = 6
    "ai" = 5
    "data" = 4
    "research" = 3
    "documentation" = 2
    "code" = 1
}

# Export for use in other scripts
Export-ModuleMember -Variable Taxonomy, TagPriority