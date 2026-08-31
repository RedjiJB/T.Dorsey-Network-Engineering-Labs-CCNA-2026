# CCNA Labs Management Script
# Manage lab documentation, renaming, organization, and git operations

param(
    [string]$Action = "status"
)

$RepoRoot = "C:\Users\jredj\RedjiJB"
$AllLabsDir = "C:\Users\jredj\ALL_LAB_FILES"
$TotalDays = 58

function Show-Status {
    Write-Host "`n=== LAB DOCUMENTATION STATUS ===" -ForegroundColor Cyan

    $complete = 0
    $missing = @()

    for ($i = 1; $i -le $TotalDays; $i++) {
        $dayStr = "{0:D2}" -f $i
        $dayDir = Join-Path $RepoRoot "Day-$dayStr"
        $manual = Join-Path $dayDir "Day-$dayStr-Lab-Manual.md"
        $practice = Join-Path $dayDir "Day-$dayStr-Practice-Lab.md"

        if ((Test-Path $manual) -and (Test-Path $practice)) {
            $complete++
        } else {
            $missing += $dayStr
        }
    }

    Write-Host "Complete days (Manual + Practice): $complete / $TotalDays" -ForegroundColor Green
    Write-Host "Missing days: $($missing.Count)" -ForegroundColor Red
    Write-Host "Coverage: $(([math]::Round(($complete / $TotalDays) * 100, 1)))%`n"

    if ($missing.Count -gt 0) {
        Write-Host "Missing days:" -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host "  Day-$_" }
    }
}

function Rename-AllLabFiles {
    Write-Host "`n=== RENAMING FILES IN ALL_LAB_FILES ===" -ForegroundColor Cyan

    if (-not (Test-Path $AllLabsDir)) {
        Write-Host "Directory not found: $AllLabsDir" -ForegroundColor Red
        return
    }

    Push-Location $AllLabsDir

    # Rename *-manual.md to Day-NN-Lab-Manual.md
    Get-ChildItem -Filter "*-manual.md" -File | ForEach-Object {
        $day = $_.BaseName -replace "-manual", ""
        if ($day -match "^\d+$") {
            $dayPadded = "{0:D2}" -f [int]$day
            $newName = "Day-$dayPadded-Lab-Manual.md"
            Rename-Item -Path $_.FullName -NewName $newName -Force
            Write-Host "Renamed: $($_.Name) to $newName" -ForegroundColor Green
        }
    }

    # Rename *-practice.md to Day-NN-Practice-Lab.md
    Get-ChildItem -Filter "*-practice.md" -File | ForEach-Object {
        $day = $_.BaseName -replace "-practice", ""
        if ($day -match "^\d+$") {
            $dayPadded = "{0:D2}" -f [int]$day
            $newName = "Day-$dayPadded-Practice-Lab.md"
            Rename-Item -Path $_.FullName -NewName $newName -Force
            Write-Host "Renamed: $($_.Name) to $newName" -ForegroundColor Green
        }
    }

    Pop-Location
    Write-Host "Renaming complete!`n" -ForegroundColor Green
}

function Copy-LabFiles {
    Write-Host "`n=== COPYING FILES TO REPO ===" -ForegroundColor Cyan

    if (-not (Test-Path $AllLabsDir)) {
        Write-Host "Source directory not found: $AllLabsDir" -ForegroundColor Red
        return
    }

    $copiedCount = 0

    # Copy all Day-NN Lab Manuals
    Get-ChildItem $AllLabsDir -Filter "Day-??-Lab-Manual.md" -File | ForEach-Object {
        $day = $_.BaseName -replace "Day-", "" -replace "-Lab-Manual", ""
        $destDir = Join-Path $RepoRoot "Day-$day"

        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        Copy-Item -Path $_.FullName -Destination $destDir -Force
        Write-Host "Copied: $($_.Name) to Day-$day/" -ForegroundColor Green
        $copiedCount++
    }

    # Copy all Day-NN Practice Labs
    Get-ChildItem $AllLabsDir -Filter "Day-??-Practice-Lab.md" -File | ForEach-Object {
        $day = $_.BaseName -replace "Day-", "" -replace "-Practice-Lab", ""
        $destDir = Join-Path $RepoRoot "Day-$day"

        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }

        Copy-Item -Path $_.FullName -Destination $destDir -Force
        Write-Host "Copied: $($_.Name) to Day-$day/" -ForegroundColor Green
        $copiedCount++
    }

    Write-Host "`nCopied $copiedCount files total!`n" -ForegroundColor Green
}

function List-Missing {
    Write-Host "`n=== MISSING DAYS ===" -ForegroundColor Cyan

    $missing = @()
    for ($i = 1; $i -le $TotalDays; $i++) {
        $dayStr = "{0:D2}" -f $i
        $dayDir = Join-Path $RepoRoot "Day-$dayStr"
        $manual = Join-Path $dayDir "Day-$dayStr-Lab-Manual.md"
        $practice = Join-Path $dayDir "Day-$dayStr-Practice-Lab.md"

        if (-not ((Test-Path $manual) -and (Test-Path $practice))) {
            $missing += $dayStr
        }
    }

    if ($missing.Count -gt 0) {
        Write-Host "Days without complete documentation:" -ForegroundColor Red
        $missing | ForEach-Object { Write-Host "  Day-$_" }
        Write-Host "`nTotal missing: $($missing.Count) days`n"
    } else {
        Write-Host "All days have complete documentation!`n" -ForegroundColor Green
    }
}

function Full-Workflow {
    Write-Host "`n=== COMPLETE WORKFLOW ===" -ForegroundColor Cyan
    Write-Host "This will:" -ForegroundColor Yellow
    Write-Host "  1. Rename all files in ALL_LAB_FILES"
    Write-Host "  2. Copy files to repo Day-NN directories"
    Write-Host "  3. Stage and commit changes"
    Write-Host "  4. Push to git remote`n"

    $confirm = Read-Host "Continue? (y/n)"
    if ($confirm -ne "y") {
        Write-Host "Cancelled." -ForegroundColor Yellow
        return
    }

    # Step 1: Rename
    Rename-AllLabFiles

    # Step 2: Copy
    Copy-LabFiles

    # Step 3: Git operations
    Write-Host "`n=== GIT OPERATIONS ===" -ForegroundColor Cyan
    Push-Location $RepoRoot

    Write-Host "Staging files..." -ForegroundColor Cyan
    git add "Day-*/"

    $status = git status --short
    if ($status) {
        Write-Host "Staged files:" -ForegroundColor Green
        $status | Write-Host

        Write-Host "`nEnter commit message (or press Enter for default):" -ForegroundColor Cyan
        $commitMsg = Read-Host
        if ([string]::IsNullOrEmpty($commitMsg)) {
            $commitMsg = "Add/update base lab documentation - multiple days`n`nCo-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
        }

        Write-Host "`nCommitting..." -ForegroundColor Cyan
        git commit -m $commitMsg

        Write-Host "`nPushing to remote..." -ForegroundColor Cyan
        git push origin redjijb-ccna-labs-expansion

        Write-Host "`nWorkflow complete!`n" -ForegroundColor Green
    } else {
        Write-Host "No files to commit." -ForegroundColor Yellow
    }

    Pop-Location
}

function Show-Help {
    Write-Host @"

CCNA Labs Management Script

Usage: .\manage-labs.ps1 -Action <action>

Actions:
  status       Show documentation coverage (default)
  rename       Rename files in ALL_LAB_FILES directory
  copy         Copy renamed files to repo directories
  list-missing List days without complete documentation
  full         Complete workflow: rename + copy + commit + push
  help         Show this help message

Examples:
  .\manage-labs.ps1 -Action status
  .\manage-labs.ps1 -Action rename
  .\manage-labs.ps1 -Action copy
  .\manage-labs.ps1 -Action full

Directories:
  Repo: $RepoRoot
  Source: $AllLabsDir

"@
}

# Main
$Action = $Action.ToLower()

switch ($Action) {
    "status" { Show-Status }
    "rename" { Rename-AllLabFiles }
    "copy" { Copy-LabFiles }
    "list-missing" { List-Missing }
    "full" { Full-Workflow }
    "help" { Show-Help }
    default { Show-Status }
}
