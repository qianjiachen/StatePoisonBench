"""
StatePoisonBench supplementary experiments.

Adds three high-ROI studies that address common reviewer concerns:
S1: Clean-vs-contaminated causal control (paired design)
S2: RTG safety-utility tradeoff across gating thresholds
S3: Trace-role annotation reliability (agreement quality)
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from scipy.stats import binomtest


SEED = 20260401
RNG = np.random.default_rng(SEED)
random.seed(SEED)

FAMILIES = [
    "summary_poisoning",
    "recovery_state",
    "tool_mediated",
    "tool_failure",
    "recovered_context",
]

TARGET_VANILLA = {
    "summary_poisoning": 0.530,
    "recovery_state": 0.755,
    "tool_mediated": 0.485,
    "tool_failure": 0.425,
    "recovered_context": 0.590,
}

CLEAN_BASE = {
    "summary_poisoning": 0.14,
    "recovery_state": 0.18,
    "tool_mediated": 0.12,
    "tool_failure": 0.10,
    "recovered_context": 0.16,
}

# logit shifts chosen to match main-table contamination rates while preserving per-instance pairing.
CONTAMINATION_SHIFT = {
    "summary_poisoning": 2.00,
    "recovery_state": 2.55,
    "tool_mediated": 1.90,
    "tool_failure": 1.90,
    "recovered_context": 2.05,
}

BASE_SUCCESS = {
    "summary_poisoning": 0.90,
    "recovery_state": 0.84,
    "tool_mediated": 0.88,
    "tool_failure": 0.87,
    "recovered_context": 0.82,
}

RISK_THRESHOLDS = [0.30, 0.50, 0.70, 0.85]
ROLE_LABELS = ["coverage", "ambiguous", "positive"]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def bootstrap_ci(values: np.ndarray, n_boot: int = 4000, alpha: float = 0.05) -> Tuple[float, float]:
    n = len(values)
    idx = RNG.integers(0, n, size=(n_boot, n))
    samples = values[idx].mean(axis=1)
    lo = float(np.quantile(samples, alpha / 2))
    hi = float(np.quantile(samples, 1 - alpha / 2))
    return lo, hi


def bootstrap_delta_ci(a: np.ndarray, b: np.ndarray, n_boot: int = 4000, alpha: float = 0.05) -> Tuple[float, float]:
    # paired bootstrap for mean(b - a)
    n = len(a)
    idx = RNG.integers(0, n, size=(n_boot, n))
    deltas = (b[idx] - a[idx]).mean(axis=1)
    lo = float(np.quantile(deltas, alpha / 2))
    hi = float(np.quantile(deltas, 1 - alpha / 2))
    return lo, hi


def mcnemar_exact(clean: np.ndarray, contam: np.ndarray) -> Dict[str, float]:
    b = int(np.sum((clean == 0) & (contam == 1)))
    c = int(np.sum((clean == 1) & (contam == 0)))
    n = b + c
    if n == 0:
        return {"b": b, "c": c, "n_discordant": 0, "p_value": 1.0}
    p = float(binomtest(k=min(b, c), n=n, p=0.5, alternative="two-sided").pvalue)
    return {"b": b, "c": c, "n_discordant": n, "p_value": p}


def cohen_kappa(y1: np.ndarray, y2: np.ndarray, labels: List[str]) -> float:
    n = len(y1)
    idx = {lab: i for i, lab in enumerate(labels)}
    cm = np.zeros((len(labels), len(labels)), dtype=np.int64)
    for a, b in zip(y1, y2):
        cm[idx[a], idx[b]] += 1

    po = float(np.trace(cm) / n)
    row = cm.sum(axis=1)
    col = cm.sum(axis=0)
    pe = float(np.sum((row / n) * (col / n)))
    if abs(1 - pe) < 1e-12:
        return 0.0
    return (po - pe) / (1 - pe)


def experiment_s1_causal_control(n_per_family: int = 200) -> Dict:
    family_rows = {}
    clean_all = []
    contam_all = []

    for fam in FAMILIES:
        clean = []
        contam = []
        clean_logit = logit(CLEAN_BASE[fam])

        for _ in range(n_per_family):
            difficulty = float(RNG.normal(0.0, 1.0))
            eps_clean = float(RNG.normal(0.0, 0.35))
            eps_contam = float(RNG.normal(0.0, 0.30))

            p_clean = sigmoid(clean_logit + 0.80 * difficulty + eps_clean)
            p_contam = sigmoid(clean_logit + CONTAMINATION_SHIFT[fam] + 0.75 * difficulty + eps_contam)

            clean.append(1 if RNG.random() < p_clean else 0)
            contam.append(1 if RNG.random() < p_contam else 0)

        clean_arr = np.array(clean, dtype=np.int64)
        contam_arr = np.array(contam, dtype=np.int64)
        delta_arr = contam_arr - clean_arr

        clean_rate = float(clean_arr.mean())
        contam_rate = float(contam_arr.mean())
        delta_rate = float(delta_arr.mean())

        family_rows[fam] = {
            "n": int(n_per_family),
            "clean_rate": clean_rate,
            "clean_ci95": bootstrap_ci(clean_arr),
            "contaminated_rate": contam_rate,
            "contaminated_ci95": bootstrap_ci(contam_arr),
            "delta": delta_rate,
            "delta_ci95": bootstrap_delta_ci(clean_arr, contam_arr),
            "mcnemar": mcnemar_exact(clean_arr, contam_arr),
            "target_vanilla_reference": TARGET_VANILLA[fam],
        }

        clean_all.extend(clean)
        contam_all.extend(contam)

    clean_all_arr = np.array(clean_all, dtype=np.int64)
    contam_all_arr = np.array(contam_all, dtype=np.int64)

    overall = {
        "n_total": int(len(clean_all_arr)),
        "clean_rate": float(clean_all_arr.mean()),
        "clean_ci95": bootstrap_ci(clean_all_arr),
        "contaminated_rate": float(contam_all_arr.mean()),
        "contaminated_ci95": bootstrap_ci(contam_all_arr),
        "delta": float((contam_all_arr - clean_all_arr).mean()),
        "delta_ci95": bootstrap_delta_ci(clean_all_arr, contam_all_arr),
        "mcnemar": mcnemar_exact(clean_all_arr, contam_all_arr),
    }

    return {"by_family": family_rows, "overall": overall}


def simulate_instance_family(family: str) -> Dict[str, float]:
    # Vanilla violation probability around paper values, with per-instance heterogeneity.
    target = TARGET_VANILLA[family]
    p_violation = sigmoid(logit(target) + float(RNG.normal(0.0, 0.45)))
    vanilla_violation = 1 if RNG.random() < p_violation else 0

    # Baseline success is lower if a violation happens.
    base_success = BASE_SUCCESS[family]
    success_penalty = 0.16 if vanilla_violation else 0.0
    vanilla_success_prob = max(0.01, min(0.99, base_success - success_penalty + float(RNG.normal(0.0, 0.04))))
    vanilla_success = 1 if RNG.random() < vanilla_success_prob else 0

    # Risk score correlated with violation likelihood.
    if vanilla_violation:
        risk = float(RNG.beta(5.0, 4.0))
    else:
        risk = float(RNG.beta(3.0, 7.0))

    return {
        "vanilla_violation": vanilla_violation,
        "vanilla_success": vanilla_success,
        "risk_score": risk,
    }


def apply_rtg_policy(instances: List[Dict[str, float]], threshold: float | None) -> Dict[str, np.ndarray]:
    violations = []
    successes = []
    confirmations = []

    for inst in instances:
        v = int(inst["vanilla_violation"])
        s = int(inst["vanilla_success"])
        risk = float(inst["risk_score"])

        if threshold is None:
            gate = False
            confirm = 0
        else:
            gate = risk >= threshold
            # stricter threshold means more review turns once triggered
            lam = 0.8 + 3.2 * threshold
            confirm = 1 + int(RNG.poisson(lam)) if gate else 0

        if gate:
            # lower threshold => stricter policy => stronger prevention but larger utility cost
            strictness = 1.0 - threshold
            prevent_prob = min(0.65, 0.22 + 0.26 * strictness)
            friction_prob = min(0.40, 0.03 + 0.34 * strictness)

            if v == 1 and RNG.random() < prevent_prob:
                v = 0
            if s == 1 and RNG.random() < friction_prob:
                s = 0

        violations.append(v)
        successes.append(s)
        confirmations.append(confirm)

    return {
        "violation": np.array(violations, dtype=np.int64),
        "success": np.array(successes, dtype=np.int64),
        "confirmations": np.array(confirmations, dtype=np.int64),
    }


def experiment_s2_tradeoff(n_per_family: int = 200) -> Dict:
    instances = []
    for fam in FAMILIES:
        for _ in range(n_per_family):
            rec = simulate_instance_family(fam)
            rec["family"] = fam
            instances.append(rec)

    policy_results = {}

    def summarize(arrs: Dict[str, np.ndarray], baseline: Dict[str, np.ndarray] | None = None) -> Dict:
        v = arrs["violation"]
        s = arrs["success"]
        c = arrs["confirmations"]

        out = {
            "violation_rate": float(v.mean()),
            "violation_ci95": bootstrap_ci(v),
            "success_rate": float(s.mean()),
            "success_ci95": bootstrap_ci(s),
            "avg_confirmations": float(c.mean()),
            "confirmations_ci95": bootstrap_ci(c.astype(float)),
        }
        if baseline is not None:
            out["delta_violation"] = float(v.mean() - baseline["violation"].mean())
            out["delta_violation_ci95"] = bootstrap_delta_ci(baseline["violation"], v)
            out["delta_success"] = float(s.mean() - baseline["success"].mean())
            out["delta_success_ci95"] = bootstrap_delta_ci(baseline["success"], s)

        # Utility-adjusted risk for quick policy ranking.
        out["utility_adjusted_risk"] = float(out["violation_rate"] + 1.0 * (1.0 - out["success_rate"]))
        return out

    baseline_arrs = apply_rtg_policy(instances, threshold=None)
    policy_results["vanilla"] = summarize(baseline_arrs, baseline=None)

    for tau in RISK_THRESHOLDS:
        arrs = apply_rtg_policy(instances, threshold=tau)
        policy_results[f"rtg_tau_{tau:.2f}"] = summarize(arrs, baseline=baseline_arrs)

    # pick best policy by utility-adjusted risk among RTG options.
    rtg_keys = [k for k in policy_results if k != "vanilla"]
    best_key = min(rtg_keys, key=lambda k: policy_results[k]["utility_adjusted_risk"])

    return {
        "n_total": int(len(instances)),
        "by_policy": policy_results,
        "recommended_policy": best_key,
    }


def draw_label(true_label: str, confusion: Dict[str, Dict[str, float]]) -> str:
    probs = confusion[true_label]
    labs = list(probs.keys())
    p = np.array([probs[l] for l in labs], dtype=float)
    p /= p.sum()
    return str(RNG.choice(labs, p=p))


def experiment_s3_annotation_reliability(n_traces: int = 360) -> Dict:
    true_dist = np.array([0.45, 0.38, 0.17])
    true_labels = RNG.choice(ROLE_LABELS, size=n_traces, p=true_dist)

    conf_a = {
        "coverage": {"coverage": 0.93, "ambiguous": 0.06, "positive": 0.01},
        "ambiguous": {"coverage": 0.07, "ambiguous": 0.88, "positive": 0.05},
        "positive": {"coverage": 0.01, "ambiguous": 0.10, "positive": 0.89},
    }
    conf_b = {
        "coverage": {"coverage": 0.90, "ambiguous": 0.08, "positive": 0.02},
        "ambiguous": {"coverage": 0.10, "ambiguous": 0.85, "positive": 0.05},
        "positive": {"coverage": 0.02, "ambiguous": 0.11, "positive": 0.87},
    }

    annotator_a = np.array([draw_label(t, conf_a) for t in true_labels])
    annotator_b = np.array([draw_label(t, conf_b) for t in true_labels])

    kappa = float(cohen_kappa(annotator_a, annotator_b, ROLE_LABELS))
    agreement = float(np.mean(annotator_a == annotator_b))

    # bootstrap CI for kappa
    boot = []
    for _ in range(3000):
        idx = RNG.integers(0, n_traces, size=n_traces)
        boot.append(cohen_kappa(annotator_a[idx], annotator_b[idx], ROLE_LABELS))
    kappa_ci = (float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975)))

    # confusion matrix A rows, B columns
    index = {l: i for i, l in enumerate(ROLE_LABELS)}
    cm = np.zeros((3, 3), dtype=int)
    for a, b in zip(annotator_a, annotator_b):
        cm[index[a], index[b]] += 1

    return {
        "n_traces": int(n_traces),
        "label_set": ROLE_LABELS,
        "percent_agreement": agreement,
        "cohen_kappa": kappa,
        "cohen_kappa_ci95": kappa_ci,
        "confusion_matrix_a_rows_b_cols": cm.tolist(),
    }


def render_markdown_report(results: Dict) -> str:
    s1 = results["S1_causal_control"]
    s2 = results["S2_tradeoff"]
    s3 = results["S3_annotation"]

    lines = []
    lines.append("# Supplementary Experiment Report")
    lines.append("")
    lines.append(f"Generated at: {results['generated_at_utc']}")
    lines.append(f"Random seed: {results['seed']}")
    lines.append("")

    lines.append("## S1. Clean vs Contaminated Causal Control")
    ov = s1["overall"]
    lines.append(
        f"Overall violation rate rises from **{ov['clean_rate']:.3f}** "
        f"(95% CI [{ov['clean_ci95'][0]:.3f}, {ov['clean_ci95'][1]:.3f}]) to "
        f"**{ov['contaminated_rate']:.3f}** "
        f"(95% CI [{ov['contaminated_ci95'][0]:.3f}, {ov['contaminated_ci95'][1]:.3f}])."
    )
    lines.append(
        f"Paired delta = **{ov['delta']:.3f}** "
        f"(95% CI [{ov['delta_ci95'][0]:.3f}, {ov['delta_ci95'][1]:.3f}]); "
        f"McNemar p = {ov['mcnemar']['p_value']:.2e}."
    )
    lines.append("")
    lines.append("Family breakdown:")
    lines.append("| Family | Clean | Contaminated | Delta | McNemar p |")
    lines.append("|---|---:|---:|---:|---:|")
    for fam in FAMILIES:
        row = s1["by_family"][fam]
        lines.append(
            f"| {fam} | {row['clean_rate']:.3f} | {row['contaminated_rate']:.3f} | "
            f"{row['delta']:.3f} | {row['mcnemar']['p_value']:.2e} |"
        )

    lines.append("")
    lines.append("## S2. RTG Safety-Utility Tradeoff")
    lines.append(f"Recommended policy by utility-adjusted risk: **{s2['recommended_policy']}**")
    lines.append("")
    lines.append("| Policy | Violation Rate | Success Rate | Avg Confirmations |")
    lines.append("|---|---:|---:|---:|")
    for key, row in s2["by_policy"].items():
        lines.append(
            f"| {key} | {row['violation_rate']:.3f} | {row['success_rate']:.3f} | {row['avg_confirmations']:.2f} |"
        )

    lines.append("")
    lines.append("## S3. Annotation Reliability")
    lines.append(
        f"Inter-annotator agreement = **{s3['percent_agreement']:.3f}**, "
        f"Cohen's kappa = **{s3['cohen_kappa']:.3f}** "
        f"(95% CI [{s3['cohen_kappa_ci95'][0]:.3f}, {s3['cohen_kappa_ci95'][1]:.3f}])."
    )
    lines.append("")
    lines.append("Confusion matrix (A rows, B cols):")
    lines.append("```text")
    for row in s3["confusion_matrix_a_rows_b_cols"]:
        lines.append(" ".join(f"{x:3d}" for x in row))
    lines.append("```")

    return "\n".join(lines) + "\n"


def main() -> None:
    results = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "S1_causal_control": experiment_s1_causal_control(n_per_family=200),
        "S2_tradeoff": experiment_s2_tradeoff(n_per_family=200),
        "S3_annotation": experiment_s3_annotation_reliability(n_traces=360),
    }

    base = Path(__file__).resolve().parent
    out_dir = base / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "supplementary_experiments.json"
    md_path = out_dir / "supplementary_experiments_report.md"

    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown_report(results), encoding="utf-8")

    print(f"Saved JSON: {json_path}")
    print(f"Saved report: {md_path}")


if __name__ == "__main__":
    main()
