param(
  [string]$PackageName = "StatePoisonBench_CodeProof_Anonymous_2026-04-23"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$packageBase = Join-Path $root "outputs\submission_packages"
$packageRoot = Join-Path $packageBase $PackageName
$zipPath = Join-Path $packageBase "$PackageName.zip"

function Assert-InWorkspace {
  param([string]$PathToCheck)
  $resolvedRoot = (Resolve-Path -LiteralPath $root).Path
  $parent = Split-Path -Parent $PathToCheck
  if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent | Out-Null
  }
  if (Test-Path -LiteralPath $PathToCheck) {
    $resolved = (Resolve-Path -LiteralPath $PathToCheck).Path
    if ($resolved -notlike (Join-Path $resolvedRoot "*")) {
      throw "Refusing to operate outside workspace: $resolved"
    }
  }
}

function Copy-RootFile {
  param([string]$RelativePath)
  $src = Join-Path $root $RelativePath
  $dst = Join-Path $packageRoot $RelativePath
  $dstParent = Split-Path -Parent $dst
  if (-not (Test-Path -LiteralPath $dstParent)) {
    New-Item -ItemType Directory -Path $dstParent | Out-Null
  }
  Copy-Item -LiteralPath $src -Destination $dst -Force
}

function Copy-Directory {
  param([string]$RelativePath)
  $src = Join-Path $root $RelativePath
  $dst = Join-Path $packageRoot $RelativePath
  Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
}

Assert-InWorkspace -PathToCheck $packageRoot
Assert-InWorkspace -PathToCheck $zipPath

if (Test-Path -LiteralPath $packageRoot) {
  Remove-Item -LiteralPath $packageRoot -Recurse -Force
}
if (Test-Path -LiteralPath $zipPath) {
  Remove-Item -LiteralPath $zipPath -Force
}

New-Item -ItemType Directory -Path $packageRoot | Out-Null

foreach ($file in @(
  "README.md",
  "LICENSE",
  "DATA_LICENSE.md",
  "DATASET_CARD.md",
  "croissant_metadata.jsonld",
  "requirements.txt"
)) {
  Copy-RootFile $file
}

foreach ($doc in @(
  "docs\release_boundary.md",
  "docs\asset_license_matrix.md",
  "docs\compute_runtime.md",
  "docs\anonymous_hosting_instructions.md",
  "docs\ed_submission_checklist.md"
)) {
  Copy-RootFile $doc
}

Copy-Directory "tasks"
Copy-Directory "scripts"

$experimentsDst = Join-Path $packageRoot "experiments"
New-Item -ItemType Directory -Path $experimentsDst | Out-Null
Get-ChildItem -LiteralPath (Join-Path $root "experiments") -File | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $experimentsDst $_.Name) -Force
}

$resultsDst = Join-Path $experimentsDst "results"
New-Item -ItemType Directory -Path $resultsDst | Out-Null
Get-ChildItem -LiteralPath (Join-Path $root "experiments\results") -File | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $resultsDst $_.Name) -Force
}

foreach ($dir in @("e25_realpaired_new12ai_gpt41mini_6pairs")) {
  $srcDir = Join-Path $root "experiments\results\$dir"
  if (Test-Path -LiteralPath $srcDir) {
    $dstDir = Join-Path $resultsDst $dir
    New-Item -ItemType Directory -Path $dstDir | Out-Null
    Get-ChildItem -LiteralPath $srcDir -File | ForEach-Object {
      Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dstDir $_.Name) -Force
    }
  }
}

$submissionDst = Join-Path $packageRoot "neurips2026_submission"
New-Item -ItemType Directory -Path $submissionDst | Out-Null
foreach ($file in @(
  ".gitignore",
  "FIGURE_ASSET_MAP.md",
  "latexmkrc",
  "main.tex",
  "neurips_2026.sty",
  "references.bib"
)) {
  Copy-RootFile "neurips2026_submission\$file"
}
Copy-Directory "neurips2026_submission\figures"
Copy-Directory "neurips2026_submission\sections"
if (Test-Path -LiteralPath (Join-Path $root "neurips2026_submission\_build\main.pdf")) {
  Copy-Item -LiteralPath (Join-Path $root "neurips2026_submission\_build\main.pdf") -Destination (Join-Path $submissionDst "main.pdf") -Force
}

$outputsDst = Join-Path $packageRoot "outputs"
New-Item -ItemType Directory -Path $outputsDst | Out-Null
foreach ($file in @(
  "README.md",
  "reviewer_code_proof_packet_2026-04-23.md",
  "final_submission_snapshot.md",
  "ed_openreview_resource_blurb.md",
  "rebuttal_ready_packet_s13_s24.md"
)) {
  $src = Join-Path $root "outputs\$file"
  if (Test-Path -LiteralPath $src) {
    Copy-Item -LiteralPath $src -Destination (Join-Path $outputsDst $file) -Force
  }
}

Compress-Archive -LiteralPath $packageRoot -DestinationPath $zipPath -Force

Write-Output "Built package directory: $packageRoot"
Write-Output "Built package zip: $zipPath"
