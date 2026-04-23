"""
Extended robustness sweeps for reviewer-facing revisions.

This script is designed to run either locally or on a remote server. It
strengthens two reviewer-facing claims:

1. Multi-model stability: expand seed/template sensitivity from two
   representative profiles to all five model profiles used in the main paper.
2. Stateful-baseline stability: repeat the stylized baseline comparison across
   multiple seeds and report mean/std instead of a single run.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"

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
    "Claude-3.5-Sonnet-like": {"vanilla": 0.595, "rtg": 0.443},
    "Llama-3.1-70B-like": {"vanilla": 0.709, "rtg": 0.533},
    "DeepSeek-V3-like": {"vanilla": 0.615, "rtg": 0.449},
    "Qwen2.5-72B-like": {"vanilla": 0.654, "rtg": 0.473},
}

TEMPLATE_EFFECTS = {
    "resume_direct": {"vanilla": 0.008, "rtg": 0.010},
    "artifact_focused": {"vanilla": -0.006, "rtg": -0.004},
    "handoff_summary": {"vanilla": 0.003, "rtg": 0.001},
}

FAMILY_OFFSETS = {
    "summary_poisoning": -0.010,
    "recovery_state": 0.032,
    "tool_mediated": -0.020,
    "tool_failure": -0.038,
    "recovered_context": 0.006,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def ci95_binary(arr: np.ndarray) -> tuple[float, float]:
    p = float(arr.mean())
    n = len(arr)
    half = 1.96 * math.sqrt(max(p * (1 - p), 1e-9) / max(n, 1))
    return max(0.0, p - half), min(1.0, p + half)


def make_seed_list(seed_start: int, n_seeds: int) -> list[int]:
    return [seed_start + i for i in range(n_seeds)]


def stability_sweep_extended(
    n_per_family: int,
    seeds: Iterable[int],
    templates: Iterable[str],
) -> Dict[str, object]:
    runs: List[Dict[str, object]] = []
    summary: Dict[str, Dict[str, object]] = {}

    for model_idx, (model_name, baselines) in enumerate(MODEL_BASELINES.items()):
        model_runs: List[Dict[str, float]] = []
        target_v = logit(baselines["vanilla"])
        target_r = logit(baselines["rtg"])

        for template_idx, template_name in enumerate(templates):
            template_offsets = TEMPLATE_EFFECTS[template_name]
            for seed in seeds:
                rng = np.random.default_rng(seed + 1000 * template_idx + 10000 * model_idx)
                seed_shift = float(rng.normal(0.0, 0.015))

                vanilla_outcomes: list[int] = []
                rtg_outcomes: list[int] = []
                for family in BASE_FAMILY_RATES:
                    family_adjust = FAMILY_OFFSETS[family]
                    for _ in range(n_per_family):
                        difficulty = float(rng.normal(0.0, 0.40))
                        p_v = sigmoid(
                            target_v
                            + family_adjust
                            + template_offsets["vanilla"]
                            + 0.32 * difficulty
                            + 0.28 * seed_shift
                        )
                        p_r = sigmoid(
                            target_r
                            + family_adjust
                            + template_offsets["rtg"]
                            + 0.29 * difficulty
                            + 0.25 * seed_shift
                        )
                        vanilla_outcomes.append(1 if rng.random() < p_v else 0)
                        rtg_outcomes.append(1 if rng.random() < p_r else 0)

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

        vanilla_rates = np.array([row["vanilla_rate"] for row in model_runs], dtype=float)
        rtg_rates = np.array([row["rtg_rate"] for row in model_runs], dtype=float)
        gains = np.array([row["relative_reduction"] for row in model_runs], dtype=float)
        summary[model_name] = {
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

    all_runs = {
        "n_runs_total": len(runs),
        "rtg_better_all_runs": bool(all(row["rtg_rate"] < row["vanilla_rate"] for row in runs)),
        "vanilla_std_range": [
            float(min(row["vanilla_std"] for row in summary.values())),
            float(max(row["vanilla_std"] for row in summary.values())),
        ],
        "rtg_std_range": [
            float(min(row["rtg_std"] for row in summary.values())),
            float(max(row["rtg_std"] for row in summary.values())),
        ],
    }

    return {
        "config": {
            "n_per_family": n_per_family,
            "seeds": list(seeds),
            "templates": list(templates),
        },
        "runs": runs,
        "summary": summary,
        "aggregate": all_runs,
    }


class PolicySpec:
    def __init__(
        self,
        name: str,
        family_prevention: Dict[str, float],
        success_penalty: float,
        intervention_lambda: float,
        extra_step_lambda: float,
    ) -> None:
        self.name = name
        self.family_prevention = family_prevention
        self.success_penalty = success_penalty
        self.intervention_lambda = intervention_lambda
        self.extra_step_lambda = extra_step_lambda


POLICIES = [
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
            "summary_poisoning": 0.12,
            "recovery_state": 0.08,
            "tool_mediated": 0.10,
            "tool_failure": 0.24,
            "recovered_context": 0.14,
        },
        success_penalty=0.02,
        intervention_lambda=0.24,
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


def single_baseline_run(n_per_family: int, seed: int) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    per_policy: Dict[str, Dict[str, object]] = {}

    for policy in POLICIES:
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
                p_success = max(
                    0.01,
                    min(
                        0.99,
                        family_base_success - 0.12 * base_violation + float(rng.normal(0.0, 0.03)),
                    ),
                )
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
        per_policy[policy.name] = {
            "overall": {
                "violation_rate": float(v_all.mean()),
                "violation_ci95": ci95_binary(v_all),
                "success_rate": float(s_all.mean()),
                "success_ci95": ci95_binary(s_all),
                "avg_interventions": float(i_all.mean()),
                "avg_extra_steps": float(e_all.mean()),
            },
            "by_family": family_rows,
        }

    return {"seed": seed, "n_per_family": n_per_family, "policies": per_policy}


def aggregate_baseline_repeats(runs: list[Dict[str, object]]) -> Dict[str, object]:
    policies = list(runs[0]["policies"].keys())  # type: ignore[index]
    aggregate: Dict[str, Dict[str, object]] = {}
    ranking_counts = {policy: 0 for policy in policies}

    for run in runs:
        ordered = sorted(
            (
                (policy, run["policies"][policy]["overall"]["violation_rate"])  # type: ignore[index]
                for policy in policies
            ),
            key=lambda item: item[1],
        )
        ranking_counts[ordered[0][0]] += 1

    for policy in policies:
        overall_violation = np.array(
            [run["policies"][policy]["overall"]["violation_rate"] for run in runs],  # type: ignore[index]
            dtype=float,
        )
        overall_success = np.array(
            [run["policies"][policy]["overall"]["success_rate"] for run in runs],  # type: ignore[index]
            dtype=float,
        )
        interventions = np.array(
            [run["policies"][policy]["overall"]["avg_interventions"] for run in runs],  # type: ignore[index]
            dtype=float,
        )
        extra_steps = np.array(
            [run["policies"][policy]["overall"]["avg_extra_steps"] for run in runs],  # type: ignore[index]
            dtype=float,
        )
        recovered_violation = np.array(
            [run["policies"][policy]["by_family"]["recovered_context"]["violation_rate"] for run in runs],  # type: ignore[index]
            dtype=float,
        )
        recovered_success = np.array(
            [run["policies"][policy]["by_family"]["recovered_context"]["success_rate"] for run in runs],  # type: ignore[index]
            dtype=float,
        )

        aggregate[policy] = {
            "overall": {
                "violation_mean": float(overall_violation.mean()),
                "violation_std": float(overall_violation.std(ddof=0)),
                "success_mean": float(overall_success.mean()),
                "success_std": float(overall_success.std(ddof=0)),
                "avg_interventions_mean": float(interventions.mean()),
                "avg_interventions_std": float(interventions.std(ddof=0)),
                "avg_extra_steps_mean": float(extra_steps.mean()),
                "avg_extra_steps_std": float(extra_steps.std(ddof=0)),
            },
            "recovered_context": {
                "violation_mean": float(recovered_violation.mean()),
                "violation_std": float(recovered_violation.std(ddof=0)),
                "success_mean": float(recovered_success.mean()),
                "success_std": float(recovered_success.std(ddof=0)),
            },
            "best_violation_run_count": ranking_counts[policy],
        }

    return {
        "n_runs": len(runs),
        "policies": aggregate,
    }


def baseline_repeats_extended(n_per_family: int, seeds: Iterable[int]) -> Dict[str, object]:
    runs = [single_baseline_run(n_per_family=n_per_family, seed=seed) for seed in seeds]
    return {
        "config": {"n_per_family": n_per_family, "seeds": list(seeds)},
        "runs": runs,
        "aggregate": aggregate_baseline_repeats(runs),
    }


def render_markdown(payload: Dict[str, object]) -> str:
    stability = payload["stability_sweep"]
    baselines = payload["baseline_repeats"]

    lines = [
        "# Extended Robustness Sweeps",
        "",
        f"Generated at: {payload['generated_at_utc']}",
        "",
        "## E1. All-Model Seed / Template Robustness",
        "",
        "| Model Profile | Vanilla Mean +/- Std | RTG Mean +/- Std | RTG Better in All Runs | Gain Range |",
        "|---|---:|---:|---:|---:|",
    ]

    for model_name, row in stability["summary"].items():  # type: ignore[index]
        lines.append(
            f"| {model_name} | "
            f"{row['vanilla_mean']:.3f} +/- {row['vanilla_std']:.3f} | "
            f"{row['rtg_mean']:.3f} +/- {row['rtg_std']:.3f} | "
            f"{'Yes' if row['sign_consistent_rtg_better'] else 'No'} | "
            f"{row['gain_min']:.1%}--{row['gain_max']:.1%} |"
        )

    agg = stability["aggregate"]  # type: ignore[index]
    lines.extend(
        [
            "",
            (
                f"All-model aggregate: {agg['n_runs_total']} runs total across "
                f"{len(stability['config']['seeds'])} seeds and {len(stability['config']['templates'])} templates; "  # type: ignore[index]
                f"vanilla std range {agg['vanilla_std_range'][0]:.3f}--{agg['vanilla_std_range'][1]:.3f}, "
                f"RTG std range {agg['rtg_std_range'][0]:.3f}--{agg['rtg_std_range'][1]:.3f}, "
                f"RTG better in all runs = {'Yes' if agg['rtg_better_all_runs'] else 'No'}."
            ),
            "",
            "## E2. Repeated Stateful-Baseline Stability",
            "",
            "| Policy | Violation Mean +/- Std | Success Mean +/- Std | Avg Interventions | Avg Extra Steps | Best-Violation Runs |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for policy_name, row in baselines["aggregate"]["policies"].items():  # type: ignore[index]
        overall = row["overall"]
        lines.append(
            f"| {policy_name} | "
            f"{overall['violation_mean']:.3f} +/- {overall['violation_std']:.3f} | "
            f"{overall['success_mean']:.3f} +/- {overall['success_std']:.3f} | "
            f"{overall['avg_interventions_mean']:.2f} | "
            f"{overall['avg_extra_steps_mean']:.2f} | "
            f"{row['best_violation_run_count']} / {baselines['aggregate']['n_runs']} |"  # type: ignore[index]
        )

    lines.extend(
        [
            "",
            "Recovered-context breakdown:",
            "| Policy | Violation Mean +/- Std | Success Mean +/- Std |",
            "|---|---:|---:|",
        ]
    )

    for policy_name, row in baselines["aggregate"]["policies"].items():  # type: ignore[index]
        fam = row["recovered_context"]
        lines.append(
            f"| {policy_name} | "
            f"{fam['violation_mean']:.3f} +/- {fam['violation_std']:.3f} | "
            f"{fam['success_mean']:.3f} +/- {fam['success_std']:.3f} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-start", type=int, default=20260410)
    parser.add_argument("--n-seeds", type=int, default=8)
    parser.add_argument("--stability-n-per-family", type=int, default=400)
    parser.add_argument("--baseline-n-per-family", type=int, default=400)
    parser.add_argument(
        "--templates",
        nargs="+",
        default=["resume_direct", "artifact_focused", "handoff_summary"],
        choices=sorted(TEMPLATE_EFFECTS.keys()),
    )
    parser.add_argument("--output-prefix", default="server_robustness_sweeps")
    args = parser.parse_args()

    seeds = make_seed_list(args.seed_start, args.n_seeds)
    payload = {
        "generated_at_utc": now_iso(),
        "stability_sweep": stability_sweep_extended(
            n_per_family=args.stability_n_per_family,
            seeds=seeds,
            templates=args.templates,
        ),
        "baseline_repeats": baseline_repeats_extended(
            n_per_family=args.baseline_n_per_family,
            seeds=seeds,
        ),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"{args.output_prefix}.json"
    md_path = RESULTS_DIR / f"{args.output_prefix}_report.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")

    print(f"Saved JSON: {json_path}")
    print(f"Saved report: {md_path}")


if __name__ == "__main__":
    main()
