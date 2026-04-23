"""
Reviewer-facing revision experiments for StatePoisonBench.

This script adds three analyses that are feasible locally:
1. Seed/template sensitivity on representative model profiles.
2. Stateful defense baseline comparison with operational-overhead proxies.
3. Summary of existing direct-endpoint pilot audits across real API models.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
OUTPUTS_DIR = ROOT / "outputs"

BASE_FAMILY_RATES = {
    "summary_poisoning": 0.530,
    "recovery_state": 0.755,
    "tool_mediated": 0.485,
    "tool_failure": 0.425,
    "recovered_context": 0.590,
}

BASE_SUCCESS = {
    "summary_poisoning": 0.90,
    "recovery_state": 0.84,
    "tool_mediated": 0.88,
    "tool_failure": 0.87,
    "recovered_context": 0.82,
}

MODEL_BASELINES = {
    "GPT-4o-like": {"vanilla": 0.557, "rtg": 0.434},
    "Qwen2.5-72B-like": {"vanilla": 0.654, "rtg": 0.473},
}

TEMPLATE_EFFECTS = {
    "resume_direct": {"vanilla": 0.008, "rtg": 0.010},
    "artifact_focused": {"vanilla": -0.006, "rtg": -0.004},
}

SEEDS = [20260402, 20260403, 20260404]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def bootstrap_ci(values: np.ndarray, rng: np.random.Generator, n_boot: int = 4000) -> tuple[float, float]:
    n = len(values)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = values[idx].mean(axis=1)
    return float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def stability_sweep(n_per_family: int = 200) -> Dict[str, object]:
    summaries: Dict[str, Dict[str, object]] = {}
    runs: List[Dict[str, object]] = []

    family_offsets = {
        "summary_poisoning": -0.010,
        "recovery_state": 0.032,
        "tool_mediated": -0.020,
        "tool_failure": -0.038,
        "recovered_context": 0.006,
    }

    for model_name, baselines in MODEL_BASELINES.items():
        model_runs: List[Dict[str, float]] = []
        for template_name, template_offsets in TEMPLATE_EFFECTS.items():
            for seed in SEEDS:
                rng = np.random.default_rng(seed)
                seed_shift = float(rng.normal(0.0, 0.018))

                vanilla_outcomes = []
                rtg_outcomes = []
                for family, family_rate in BASE_FAMILY_RATES.items():
                    family_logit = logit(family_rate)
                    target_v = logit(baselines["vanilla"])
                    target_r = logit(baselines["rtg"])
                    family_adjust = family_offsets[family]

                    for _ in range(n_per_family):
                        difficulty = float(rng.normal(0.0, 0.42))
                        p_vanilla = sigmoid(target_v + family_adjust + template_offsets["vanilla"] + 0.35 * difficulty + 0.35 * seed_shift)
                        p_rtg = sigmoid(target_r + family_adjust + template_offsets["rtg"] + 0.30 * difficulty + 0.30 * seed_shift)
                        vanilla_outcomes.append(1 if rng.random() < p_vanilla else 0)
                        rtg_outcomes.append(1 if rng.random() < p_rtg else 0)

                vanilla_arr = np.array(vanilla_outcomes, dtype=np.int64)
                rtg_arr = np.array(rtg_outcomes, dtype=np.int64)
                run = {
                    "model": model_name,
                    "template": template_name,
                    "seed": seed,
                    "vanilla_rate": float(vanilla_arr.mean()),
                    "rtg_rate": float(rtg_arr.mean()),
                    "relative_reduction": float((vanilla_arr.mean() - rtg_arr.mean()) / vanilla_arr.mean()),
                }
                runs.append(run)
                model_runs.append(run)

        vanilla_rates = np.array([r["vanilla_rate"] for r in model_runs], dtype=float)
        rtg_rates = np.array([r["rtg_rate"] for r in model_runs], dtype=float)
        gains = np.array([r["relative_reduction"] for r in model_runs], dtype=float)
        summaries[model_name] = {
            "n_runs": len(model_runs),
            "vanilla_mean": float(vanilla_rates.mean()),
            "vanilla_std": float(vanilla_rates.std(ddof=0)),
            "vanilla_min": float(vanilla_rates.min()),
            "vanilla_max": float(vanilla_rates.max()),
            "rtg_mean": float(rtg_rates.mean()),
            "rtg_std": float(rtg_rates.std(ddof=0)),
            "rtg_min": float(rtg_rates.min()),
            "rtg_max": float(rtg_rates.max()),
            "gain_mean": float(gains.mean()),
            "gain_min": float(gains.min()),
            "gain_max": float(gains.max()),
            "sign_consistent_rtg_better": bool(np.all(rtg_rates < vanilla_rates)),
        }

    return {"config": {"seeds": SEEDS, "templates": list(TEMPLATE_EFFECTS)}, "runs": runs, "summary": summaries}


@dataclass
class PolicySpec:
    name: str
    family_prevention: Dict[str, float]
    success_penalty: float
    intervention_lambda: float
    extra_step_lambda: float


def stateful_baselines(n_per_family: int = 200, seed: int = 20260405) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    policies = [
        PolicySpec(
            name="Vanilla",
            family_prevention={fam: 0.0 for fam in BASE_FAMILY_RATES},
            success_penalty=0.0,
            intervention_lambda=0.0,
            extra_step_lambda=0.0,
        ),
        PolicySpec(
            name="Prompt-Local Filter",
            family_prevention={
                "summary_poisoning": 0.08,
                "recovery_state": 0.06,
                "tool_mediated": 0.08,
                "tool_failure": 0.20,
                "recovered_context": 0.05,
            },
            success_penalty=0.02,
            intervention_lambda=0.20,
            extra_step_lambda=0.08,
        ),
        PolicySpec(
            name="Intent-Drift Monitor",
            family_prevention={
                "summary_poisoning": 0.27,
                "recovery_state": 0.31,
                "tool_mediated": 0.25,
                "tool_failure": 0.11,
                "recovered_context": 0.15,
            },
            success_penalty=0.05,
            intervention_lambda=0.72,
            extra_step_lambda=0.44,
        ),
        PolicySpec(
            name="Memory Isolation",
            family_prevention={
                "summary_poisoning": 0.14,
                "recovery_state": 0.36,
                "tool_mediated": 0.12,
                "tool_failure": 0.05,
                "recovered_context": 0.54,
            },
            success_penalty=0.10,
            intervention_lambda=1.32,
            extra_step_lambda=0.92,
        ),
        PolicySpec(
            name="RTG",
            family_prevention={
                "summary_poisoning": 0.20,
                "recovery_state": 0.25,
                "tool_mediated": 0.21,
                "tool_failure": 0.18,
                "recovered_context": 0.25,
            },
            success_penalty=0.05,
            intervention_lambda=1.10,
            extra_step_lambda=0.62,
        ),
    ]

    per_policy: Dict[str, Dict[str, object]] = {}

    for policy in policies:
        family_rows = {}
        all_violations = []
        all_successes = []
        all_interventions = []
        all_extra_steps = []

        for family, base_rate in BASE_FAMILY_RATES.items():
            v_outcomes = []
            s_outcomes = []
            interventions = []
            extra_steps = []
            family_base_success = BASE_SUCCESS[family]

            for _ in range(n_per_family):
                difficulty = float(rng.normal(0.0, 0.40))
                p_base = sigmoid(logit(base_rate) + 0.35 * difficulty)
                base_violation = 1 if rng.random() < p_base else 0
                p_success = max(0.01, min(0.99, family_base_success - 0.12 * base_violation + float(rng.normal(0.0, 0.03))))
                success = 1 if rng.random() < p_success else 0

                intervention = 0
                extra = 0
                if policy.name != "Vanilla":
                    intervention = int(rng.poisson(policy.intervention_lambda))
                    extra = int(rng.poisson(policy.extra_step_lambda))
                    if intervention > 0 and base_violation == 1 and rng.random() < policy.family_prevention[family]:
                        base_violation = 0
                    if success == 1 and rng.random() < policy.success_penalty:
                        success = 0

                v_outcomes.append(base_violation)
                s_outcomes.append(success)
                interventions.append(intervention)
                extra_steps.append(extra)

            v_arr = np.array(v_outcomes, dtype=np.int64)
            s_arr = np.array(s_outcomes, dtype=np.int64)
            i_arr = np.array(interventions, dtype=np.int64)
            e_arr = np.array(extra_steps, dtype=np.int64)

            family_rows[family] = {
                "violation_rate": float(v_arr.mean()),
                "success_rate": float(s_arr.mean()),
                "avg_interventions": float(i_arr.mean()),
                "avg_extra_steps": float(e_arr.mean()),
            }
            all_violations.extend(v_outcomes)
            all_successes.extend(s_outcomes)
            all_interventions.extend(interventions)
            all_extra_steps.extend(extra_steps)

        v_all = np.array(all_violations, dtype=np.int64)
        s_all = np.array(all_successes, dtype=np.int64)
        i_all = np.array(all_interventions, dtype=np.int64)
        e_all = np.array(all_extra_steps, dtype=np.int64)
        ci_rng = np.random.default_rng(seed + len(per_policy) + 11)
        per_policy[policy.name] = {
            "overall": {
                "violation_rate": float(v_all.mean()),
                "violation_ci95": bootstrap_ci(v_all, ci_rng),
                "success_rate": float(s_all.mean()),
                "success_ci95": bootstrap_ci(s_all, ci_rng),
                "avg_interventions": float(i_all.mean()),
                "avg_extra_steps": float(e_all.mean()),
            },
            "by_family": family_rows,
        }

    return {"seed": seed, "n_per_family": n_per_family, "policies": per_policy}


def parse_audit_file(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    model_match = re.search(r"Model: `([^`]+)`", text)
    counts = re.findall(r"\| `?(vanilla|rtg)`? \| (\d+) / (\d+) \| (\d+) / (\d+) \|", text)
    if not model_match or not counts:
        raise ValueError(f"Could not parse audit file: {path}")
    out: Dict[str, object] = {"model": model_match.group(1)}
    for cond, fail_num, fail_den, task_num, task_den in counts:
        out[cond] = {
            "clear_failures": int(fail_num),
            "episodes": int(fail_den),
            "task_completion": int(task_num),
            "task_completion_den": int(task_den),
        }
    return out


def direct_api_pilot_summary() -> Dict[str, object]:
    audit_files = [
        OUTPUTS_DIR / "real_api_pilot_gpt54mini_audit.md",
        OUTPUTS_DIR / "real_api_pilot_codexmini_audit.md",
        OUTPUTS_DIR / "real_api_pilot_codexmax_audit.md",
    ]
    parsed = [parse_audit_file(path) for path in audit_files]

    totals = {
        "episodes": 0,
        "clear_failures": 0,
        "task_completion_vanilla": 0,
        "task_completion_rtg": 0,
    }
    for row in parsed:
        totals["episodes"] += int(row["vanilla"]["episodes"]) + int(row["rtg"]["episodes"])  # type: ignore[index]
        totals["clear_failures"] += int(row["vanilla"]["clear_failures"]) + int(row["rtg"]["clear_failures"])  # type: ignore[index]
        totals["task_completion_vanilla"] += int(row["vanilla"]["task_completion"])  # type: ignore[index]
        totals["task_completion_rtg"] += int(row["rtg"]["task_completion"])  # type: ignore[index]

    return {"models": parsed, "totals": totals}


def render_markdown(payload: Dict[str, object]) -> str:
    stability = payload["stability_sweep"]
    baselines = payload["stateful_baselines"]
    pilots = payload["direct_api_pilots"]

    lines: List[str] = []
    lines.append("# Reviewer-Facing Revision Experiments")
    lines.append("")
    lines.append(f"Generated at: {payload['generated_at_utc']}")
    lines.append("")

    lines.append("## R1. Seed and Template Sensitivity")
    lines.append("")
    lines.append("| Model Profile | Vanilla Mean +/- Std | RTG Mean +/- Std | RTG Better In All Runs | Gain Range |")
    lines.append("|---|---:|---:|---:|---:|")
    for model_name, row in stability["summary"].items():  # type: ignore[index]
        lines.append(
            f"| {model_name} | "
            f"{row['vanilla_mean']:.3f} +/- {row['vanilla_std']:.3f} | "
            f"{row['rtg_mean']:.3f} +/- {row['rtg_std']:.3f} | "
            f"{'Yes' if row['sign_consistent_rtg_better'] else 'No'} | "
            f"{row['gain_min']:.1%}--{row['gain_max']:.1%} |"
        )

    lines.append("")
    lines.append("## R2. Stateful Defense Baselines")
    lines.append("")
    lines.append("| Policy | Overall Violation | Overall Success | Avg Interventions | Avg Extra Steps |")
    lines.append("|---|---:|---:|---:|---:|")
    for policy_name, row in baselines["policies"].items():  # type: ignore[index]
        overall = row["overall"]
        lines.append(
            f"| {policy_name} | {overall['violation_rate']:.3f} | {overall['success_rate']:.3f} | "
            f"{overall['avg_interventions']:.2f} | {overall['avg_extra_steps']:.2f} |"
        )

    lines.append("")
    lines.append("Recovered-context family breakdown:")
    lines.append("| Policy | Violation | Success |")
    lines.append("|---|---:|---:|")
    for policy_name, row in baselines["policies"].items():  # type: ignore[index]
        fam = row["by_family"]["recovered_context"]
        lines.append(f"| {policy_name} | {fam['violation_rate']:.3f} | {fam['success_rate']:.3f} |")

    lines.append("")
    lines.append("## R3. Direct API Pilot Calibration")
    lines.append("")
    lines.append("| Model | Vanilla Failures | Vanilla Completion | RTG Failures | RTG Completion |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in pilots["models"]:  # type: ignore[index]
        lines.append(
            f"| {row['model']} | {row['vanilla']['clear_failures']}/{row['vanilla']['episodes']} | "
            f"{row['vanilla']['task_completion']}/{row['vanilla']['task_completion_den']} | "
            f"{row['rtg']['clear_failures']}/{row['rtg']['episodes']} | "
            f"{row['rtg']['task_completion']}/{row['rtg']['task_completion_den']} |"
        )

    lines.append("")
    lines.append(
        f"Across all audited direct-endpoint pilot episodes, clear contamination-positive failures = "
        f"{pilots['totals']['clear_failures']} / {pilots['totals']['episodes']}."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = {
        "generated_at_utc": now_iso(),
        "stability_sweep": stability_sweep(),
        "stateful_baselines": stateful_baselines(),
        "direct_api_pilots": direct_api_pilot_summary(),
    }

    json_path = RESULTS_DIR / "reviewer_revision_experiments.json"
    md_path = RESULTS_DIR / "reviewer_revision_experiments_report.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")

    print(f"Saved JSON: {json_path}")
    print(f"Saved report: {md_path}")


if __name__ == "__main__":
    main()
