# Load KEY=VALUE pairs from .env (same pattern as FreshBooks repo).

function Get-DotEnvPath {
    param([string]$EnvPath)
    if ($EnvPath) { return $EnvPath }
    return Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
}

function Read-DotEnv {
    param([string]$Path)
    $result = @{}
    if (-not (Test-Path -LiteralPath $Path)) {
        return $result
    }
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) { continue }
        $idx = $trimmed.IndexOf("=")
        if ($idx -lt 1) { continue }
        $key = $trimmed.Substring(0, $idx).Trim()
        $value = $trimmed.Substring($idx + 1).Trim()
        $result[$key] = $value
    }
    return $result
}

function Set-DotEnvValue {
    param(
        [string]$Path,
        [hashtable]$Updates
    )
    $lines = @()
    $seen = @{}
    if (Test-Path -LiteralPath $Path) {
        $lines = Get-Content -LiteralPath $Path -Encoding UTF8
    }
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        if ($trimmed -and -not $trimmed.StartsWith("#") -and $trimmed.Contains("=")) {
            $key = $trimmed.Split("=", 2)[0].Trim()
            if ($Updates.ContainsKey($key)) {
                $out.Add("$key=$($Updates[$key])")
                $seen[$key] = $true
                continue
            }
        }
        $out.Add($line)
    }
    foreach ($key in $Updates.Keys) {
        if (-not $seen[$key]) {
            $out.Add("$key=$($Updates[$key])")
        }
    }
    Set-Content -LiteralPath $Path -Value $out -Encoding UTF8
}

function Import-DotEnv {
    param([string]$Path)
    $vars = Read-DotEnv -Path $Path
    foreach ($key in $vars.Keys) {
        Set-Item -Path "Env:$key" -Value $vars[$key]
    }
    return $vars
}

# Simple loader for scripts that only dot-source this file
$envPath = Get-DotEnvPath
if (Test-Path $envPath) {
    Import-DotEnv -Path $envPath | Out-Null
}
