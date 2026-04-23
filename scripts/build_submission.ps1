param(
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$submissionDir = Join-Path $root "neurips2026_submission"
$buildDir = Join-Path $submissionDir "_build"
$referencesFile = Join-Path $submissionDir "references.bib"

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
  throw "latexmk was not found in PATH."
}

if (-not (Test-Path -LiteralPath $submissionDir)) {
  throw "Submission directory not found: $submissionDir"
}

if (-not (Test-Path -LiteralPath $referencesFile)) {
  throw "Bibliography file not found: $referencesFile"
}

if (-not (Test-Path -LiteralPath $buildDir)) {
  New-Item -ItemType Directory -Path $buildDir | Out-Null
}

if ($Clean) {
  $resolvedBuildDir = (Resolve-Path -LiteralPath $buildDir).Path
  if ($resolvedBuildDir -notlike (Join-Path $submissionDir "*")) {
    throw "Refusing to clean an unexpected build directory: $resolvedBuildDir"
  }
  Get-ChildItem -LiteralPath $buildDir -Force | Remove-Item -Recurse -Force
}

Push-Location -LiteralPath $submissionDir
try {
  Copy-Item -LiteralPath $referencesFile -Destination (Join-Path $buildDir "references.bib") -Force
  & latexmk -g -pdf -interaction=nonstopmode -halt-on-error -outdir=_build main.tex
  if ($LASTEXITCODE -ne 0) {
    throw "latexmk failed with exit code $LASTEXITCODE"
  }

  Copy-Item -LiteralPath (Join-Path $buildDir "main.pdf") -Destination (Join-Path $submissionDir "main.pdf") -Force
  Write-Output "Build complete: neurips2026_submission/_build/main.pdf"
  Write-Output "Synced release copy: neurips2026_submission/main.pdf"
}
finally {
  Pop-Location
}
