$ErrorActionPreference = "Stop"

# Save this script in the Mana-Movie project root and run it from there.
$SourceRoot = (Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)).Path
$RepoUrl = "https://github.com/sivakumar9867/movie-recommendation-system.git"
$RepoName = "movie-recommendation-system"
$Parent = Split-Path $SourceRoot -Parent
$CloneDir = Join-Path $Parent ("Mana-Cinema-GitHub-Publish-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupBranch = "backup/before-mana-cinema-500-$Stamp"
$ReplaceBranch = "replace/mana-cinema-500-$Stamp"

function Invoke-Git([string]$Directory, [string[]]$Arguments) {
    & git -C $Directory @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($Arguments -join ' ')"
    }
}

Write-Host "Checking the working Mana Cinema project..." -ForegroundColor Cyan
$CsvPath = Join-Path $SourceRoot "data\movies.csv"
$PosterDir = Join-Path $SourceRoot "static\posters"
$AppPath = Join-Path $SourceRoot "app.py"
$GitignorePath = Join-Path $SourceRoot ".gitignore"

foreach ($required in @($CsvPath, $PosterDir, $AppPath, $GitignorePath)) {
    if (!(Test-Path $required)) { throw "Required project item not found: $required" }
}
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git was not found. Install Git for Windows and sign in to GitHub, then run this script again."
}

$Movies = @(Import-Csv -LiteralPath $CsvPath -Encoding UTF8)
$PosterFiles = @(Get-ChildItem -LiteralPath $PosterDir -File | Where-Object { $_.Extension -match '^\.jpe?g$' })
if ($Movies.Count -ne 500) { throw "Expected 500 movie records in data\movies.csv; found $($Movies.Count)." }
if ($PosterFiles.Count -ne 500) { throw "Expected 500 JPG/JPEG posters in static\posters; found $($PosterFiles.Count)." }

$DuplicateTitles = @($Movies | Group-Object { ([string]$_.title).Trim().ToLowerInvariant() } | Where-Object { $_.Count -gt 1 })
if ($DuplicateTitles.Count -gt 0) {
    $Names = ($DuplicateTitles | ForEach-Object { $_.Name }) -join ", "
    throw "Duplicate movie titles found: $Names"
}

foreach ($movie in $Movies) {
    $url = [string]$movie.poster_url
    if (!$url.StartsWith("/static/posters/")) {
        throw "Non-local poster path for '$($movie.title)': $url"
    }
    $relative = $url.TrimStart('/').Replace('/', '\\')
    if (!(Test-Path (Join-Path $SourceRoot $relative))) {
        throw "Missing poster file for '$($movie.title)': $url"
    }
}

# Confirm the running homepage's requested Gabbar Singh selection is present.
$AppText = Get-Content -LiteralPath $AppPath -Raw
if ($AppText -notmatch '(?i)Pawan Kalyan.{0,100}Gabbar Singh') {
    throw "The Gabbar Singh homepage selection was not found in app.py. Do not publish until the working local fix is present."
}

# Check that the repo's ignore rules do not exclude the poster assets or allow secrets.
$IgnoreText = Get-Content -LiteralPath $GitignorePath -Raw
if ($IgnoreText -notmatch '(?m)^\.env\s*$') { throw ".gitignore must contain a rule for .env." }
if ($IgnoreText -match '(?m)^static/posters/\*') { throw ".gitignore appears to exclude the poster files. Remove that rule before publishing." }

Write-Host "Validated: 500 unique movie records, 500 local posters, and Gabbar Singh homepage selection." -ForegroundColor Green
if (Test-Path (Join-Path $SourceRoot ".env")) {
    Write-Host "A local .env file exists. It will remain on your PC and will NOT be copied to GitHub." -ForegroundColor Yellow
}

# Clone the existing repo into a separate sibling folder. The user's working project is never modified.
Write-Host "Cloning the current GitHub repository..." -ForegroundColor Cyan
& git clone $RepoUrl $CloneDir
if ($LASTEXITCODE -ne 0) { throw "Could not clone the repository. Check network access and GitHub sign-in." }

$MainBranch = (& git -C $CloneDir branch --show-current).Trim()
if (!$MainBranch) { throw "Could not determine the repository's default branch." }

# Preserve the existing repo state on a remote backup branch before preparing replacement files.
Write-Host "Creating a remote backup of the current repository..." -ForegroundColor Cyan
Invoke-Git $CloneDir @("switch", "-c", $BackupBranch)
Invoke-Git $CloneDir @("push", "-u", "origin", $BackupBranch)
Invoke-Git $CloneDir @("switch", $MainBranch)
Invoke-Git $CloneDir @("pull", "--ff-only", "origin", $MainBranch)
Invoke-Git $CloneDir @("switch", "-c", $ReplaceBranch)

Write-Host "Copying the current Mana-Movie project into the clean clone..." -ForegroundColor Cyan
$RobocopyArgs = @(
    $SourceRoot, $CloneDir, "/MIR", "/R:2", "/W:2", "/NFL", "/NDL",
    "/XD", (Join-Path $CloneDir ".git"), (Join-Path $SourceRoot ".git"),
            ".venv", "venv", "__pycache__", ".pytest_cache", ".idea", ".vscode",
    "/XF", ".env", "*.pyc", "*.pyo", "*.log"
)
& robocopy @RobocopyArgs
$RobocopyCode = $LASTEXITCODE
if ($RobocopyCode -ge 8) { throw "Robocopy failed with exit code $RobocopyCode." }

# Remove any nested environment-secret files from the publish clone, but keep .env.example.
Get-ChildItem -LiteralPath $CloneDir -Recurse -Force -File | Where-Object {
    $_.Name -eq ".env" -or ($_.Name.StartsWith(".env.") -and $_.Name -ne ".env.example")
} | Remove-Item -Force

$StagedEnvironmentFiles = @(Get-ChildItem -LiteralPath $CloneDir -Recurse -Force -File | Where-Object {
    $_.Name -eq ".env" -or ($_.Name.StartsWith(".env.") -and $_.Name -ne ".env.example")
})
if ($StagedEnvironmentFiles.Count -gt 0) { throw "Environment secret file remains in publish clone. Stopping." }

Invoke-Git $CloneDir @("add", "-A")
$Staged = @(& git -C $CloneDir diff --cached --name-only)
if ($LASTEXITCODE -ne 0) { throw "Could not inspect staged files." }
if ($Staged | Where-Object {
    $_ -match '(^|/)\.env($|/)' -or $_ -match '(^|/)\.env\.(?!example$)' -or
    $_ -match '(^|/)(\.venv|venv|__pycache__|\.pytest_cache)(/|$)'
}) {
    throw "A secret or local environment file is staged. Stopping before commit."
}

$StagedPosters = @($Staged | Where-Object { $_ -match '^static/posters/[^/]+\.jpe?g$' })
if ($StagedPosters.Count -ne 500) {
    throw "Expected 500 staged poster files, found $($StagedPosters.Count). Check .gitignore and static\posters."
}

Write-Host "`nReady to publish the replacement branch." -ForegroundColor Green
Write-Host "  Existing GitHub main: unchanged until the pull request is merged"
Write-Host "  Backup branch:        $BackupBranch"
Write-Host "  Replacement branch:  $ReplaceBranch"
Write-Host "  Movie records:        $($Movies.Count)"
Write-Host "  Poster images:        $($StagedPosters.Count)"
Write-Host "  .env / .venv:         excluded"
Write-Host "`nIMPORTANT: this will make all 500 included poster image files visible in your PUBLIC GitHub repository. Continue only if you have permission to redistribute those artworks." -ForegroundColor Yellow
Write-Host "`nStaged change summary:"
& git -C $CloneDir diff --cached --stat
if ($LASTEXITCODE -ne 0) { throw "Could not display staged summary." }

$Answer = Read-Host "Type YES to commit and push the replacement branch"
if ($Answer -cne "YES") {
    Write-Host "Cancelled. The old main branch is unchanged. Remote backup branch (if created): $BackupBranch" -ForegroundColor Yellow
    Write-Host "Publish clone: $CloneDir"
    exit 0
}

Invoke-Git $CloneDir @("commit", "-m", "Replace legacy project with Mana Cinema 500-movie edition")
Invoke-Git $CloneDir @("push", "-u", "origin", $ReplaceBranch)

Write-Host "`nThe replacement branch is now on GitHub. The old main branch is still safe." -ForegroundColor Green
Write-Host "Compare and open a pull request:"
Write-Host "https://github.com/sivakumar9867/movie-recommendation-system/compare/$MainBranch...$ReplaceBranch?expand=1"
Write-Host "After opening the pull request, review it and merge it to replace main."
Write-Host "Publish clone: $CloneDir"
