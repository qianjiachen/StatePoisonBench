param(
  [string]$PackageName = "StatePoisonBench_HF_Dataset_Anonymous_2026-04-23"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$packageBase = Join-Path $root "outputs\hf_dataset_packages"
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

function Copy-RelativeFile {
  param(
    [string]$SourceRelativePath,
    [string]$DestinationRelativePath = $SourceRelativePath
  )
  $src = Join-Path $root $SourceRelativePath
  $dst = Join-Path $packageRoot $DestinationRelativePath
  $dstParent = Split-Path -Parent $dst
  if (-not (Test-Path -LiteralPath $dstParent)) {
    New-Item -ItemType Directory -Path $dstParent | Out-Null
  }
  Copy-Item -LiteralPath $src -Destination $dst -Force
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

Copy-RelativeFile "docs\hf_dataset_repo_readme.md" "README.md"
Copy-RelativeFile "DATASET_CARD.md"
Copy-RelativeFile "DATA_LICENSE.md"
Copy-RelativeFile "croissant_metadata.jsonld"

foreach ($doc in @(
  "docs\release_boundary.md",
  "docs\asset_license_matrix.md",
  "docs\compute_runtime.md"
)) {
  Copy-RelativeFile $doc
}

Copy-Item -LiteralPath (Join-Path $root "tasks") -Destination (Join-Path $packageRoot "tasks") -Recurse -Force

$resultsDst = Join-Path $packageRoot "experiments\results"
New-Item -ItemType Directory -Path $resultsDst -Force | Out-Null

$topLevelArtifacts = @(
  "experiment_1_baseline.json",
  "experiment_2_scaling.json",
  "experiment_3_turns.json",
  "supplementary_experiments.json",
  "supplementary_experiments_report.md",
  "server_robustness_sweeps_full.json",
  "server_robustness_sweeps_full_report.md",
  "e10_near_positive_causal_replay.json",
  "e10_near_positive_causal_replay.md",
  "e11_cross_stack_api_spot_check.json",
  "e11_cross_stack_api_spot_check.md",
  "e12_uncertainty_bounds.json",
  "e12_uncertainty_bounds.md",
  "e13_cross_provider_api_auto_check.json",
  "e13_cross_provider_api_auto_check.md",
  "e14_cross_provider_manual_audit.json",
  "e14_cross_provider_manual_audit.md",
  "e15_manual_adjudication_robustness.json",
  "e15_manual_adjudication_robustness.md",
  "e16_manual_calibrated_small_sample_bounds.json",
  "e16_manual_calibrated_small_sample_bounds.md",
  "e18_power_and_sample_size_planning.json",
  "e18_power_and_sample_size_planning.md",
  "e19_manual_label_perturbation_sensitivity.json",
  "e19_manual_label_perturbation_sensitivity.md",
  "e20_bayesian_posterior_sensitivity.json",
  "e20_bayesian_posterior_sensitivity.md",
  "e21_api_negative_probe_and_taxonomy.json",
  "e21_api_negative_probe_and_taxonomy.md",
  "e22_independent_audit_calibration.json",
  "e22_independent_audit_calibration.md",
  "e23_c1_decoupled_audit_calibration.json",
  "e23_c1_decoupled_audit_calibration.md",
  "e24_single_external_calibration.json",
  "e24_single_external_calibration.md",
  "e26_c1_observability_ladder.json",
  "e26_c1_observability_ladder.md",
  "e26_c1_observability_ladder_qwen7b.json",
  "e26_c1_observability_ladder_qwen7b.md",
  "e27_c1_observability_ladder_strict_qwen3b.json",
  "e27_c1_observability_ladder_strict_qwen3b.md",
  "e27_c1_observability_ladder_strict_qwen7b.json",
  "e27_c1_observability_ladder_strict_qwen7b.md",
  "table_artifact_consistency_report.json",
  "table_artifact_consistency_report.md"
)

foreach ($artifact in $topLevelArtifacts) {
  Copy-RelativeFile "experiments\results\$artifact" "experiments\results\$artifact"
}

$s24Src = Join-Path $root "experiments\results\e25_realpaired_new12ai_gpt41mini_6pairs"
$s24Dst = Join-Path $packageRoot "experiments\results\e25_realpaired_new12ai_gpt41mini_6pairs"
New-Item -ItemType Directory -Path $s24Dst -Force | Out-Null
Get-ChildItem -LiteralPath $s24Src -File | ForEach-Object {
  Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $s24Dst $_.Name) -Force
}

$packSpecs = @(
  @{
    Source = "experiments\results\_packs\e22_independent_audit_pack"
    Destination = "experiments\results\_packs\e22_independent_audit_pack"
    Exclude = @("author_assisted", "author_primary_sheet")
  },
  @{
    Source = "experiments\results\_packs\e23_c1_decoupled_audit_pack"
    Destination = "experiments\results\_packs\e23_c1_decoupled_audit_pack"
    Exclude = @("reference_sheet", "simulated_example", "smoke")
  },
  @{
    Source = "experiments\results\_packs\e24_single_external_expanded_pack"
    Destination = "experiments\results\_packs\e24_single_external_expanded_pack"
    Exclude = @("author_reference", "simulated_example", "smoke")
  }
)

foreach ($spec in $packSpecs) {
  $srcRoot = Join-Path $root $spec.Source
  $dstRoot = Join-Path $packageRoot $spec.Destination
  New-Item -ItemType Directory -Path $dstRoot -Force | Out-Null
  Get-ChildItem -LiteralPath $srcRoot -Recurse -File | ForEach-Object {
    $name = $_.Name
    foreach ($needle in $spec.Exclude) {
      if ($name -like "*$needle*") {
        return
      }
    }
    $relative = $_.FullName.Substring($srcRoot.Length).TrimStart('\')
    $dst = Join-Path $dstRoot $relative
    $dstParent = Split-Path -Parent $dst
    if (-not (Test-Path -LiteralPath $dstParent)) {
      New-Item -ItemType Directory -Path $dstParent -Force | Out-Null
    }
    Copy-Item -LiteralPath $_.FullName -Destination $dst -Force
  }
}

$manifestPath = Join-Path $packageRoot "MANIFEST.md"
$manifestLines = @(
  "# HF Dataset Package Manifest",
  "",
  "This package is the upload-ready Hugging Face Dataset payload for the anonymous StatePoisonBench ED submission.",
  "",
  "## Included",
  "",
  "- `tasks/`: all released synthetic JSONL task packs",
  "- `experiments/results/`: paper-linked JSON/Markdown artifacts only",
  "- `experiments/results/_packs/`: blind audit packet materials referenced by E22/E23/E24 provenance",
  "- `docs/`: release boundary, asset/license matrix, and compute/runtime notes",
  "- `README.md`, `DATASET_CARD.md`, `croissant_metadata.jsonld`, `DATA_LICENSE.md`",
  "",
  "## Excluded",
  "",
  "- raw account-linked traces",
  "- raw response directories under E25",
  "- smoke/simulated-only calibration side artifacts",
  "- author-assisted or author-reference audit sheets",
  "- local caches and build outputs",
  "",
  "## Provenance Notes",
  "",
  "- Some JSON artifacts retain relative provenance fields such as `trajectory_path`, `audit_sheet`, or `internal_manifest`.",
  "- Those references are preserved for traceability even when the corresponding raw trajectory files are intentionally not redistributed."
)
$manifestLines | Set-Content -LiteralPath $manifestPath -Encoding utf8

Compress-Archive -LiteralPath $packageRoot -DestinationPath $zipPath -Force

Write-Output "Built HF dataset directory: $packageRoot"
Write-Output "Built HF dataset zip: $zipPath"
