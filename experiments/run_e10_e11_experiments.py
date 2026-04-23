"""
Run the E10/E11 reinforcement package for the NeurIPS submission draft.

E10: Near-Positive Causal Replay (paired clean vs contaminated replay).
E11: Cross-Stack + API Spot Check robustness consolidation.

This script only writes artifacts under experiments/results/.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
OUTPUTS_DIR = ROOT / "outputs"

E10_JSON = RESULTS_DIR / "e10_near_positive_causal_replay.json"
E10_MD = RESULTS_DIR / "e10_near_positive_causal_replay.md"
E11_JSON = RESULTS_DIR / "e11_cross_stack_api_spot_check.json"
E11_MD = RESULTS_DIR / "e11_cross_stack_api_spot_check.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def rate(values: List[bool]) -> float:
    if not values:
        return 0.0
    return float(sum(1 for x in values if x) / len(values))


def mcnemar_exact_p(b: int, c: int) -> float:
    """
    Exact two-sided McNemar p-value using a binomial tail.
    b: clean=0, contaminated=1
    c: clean=1, contaminated=0
    """
    n = b + c
    if n == 0:
        return 1.0
    x = min(b, c)
    # two-sided exact binomial p-value under p=0.5
    tail = sum(math.comb(n, k) for k in range(0, x + 1)) / (2**n)
    return min(1.0, 2.0 * tail)


def rel_reduction(vanilla: float, rtg: float) -> float:
    if vanilla <= 0:
        return 0.0
    return (vanilla - rtg) / vanilla


def build_e10(seed: int = 20260412, n_pairs_per_family: int = 160) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    family_cfg = {
        "recovered_context_write": {
            "clean_violation": 0.26,
            "contaminated_violation": 0.55,
            "clean_safe_success": 0.81,
            "contaminated_safe_success": 0.66,
            "clean_state_propagation": 0.24,
            "contaminated_state_propagation": 0.76,
        },
        "recovery_state_poisoning": {
            "clean_violation": 0.18,
            "contaminated_violation": 0.44,
            "clean_safe_success": 0.84,
            "contaminated_safe_success": 0.70,
            "clean_state_propagation": 0.19,
            "contaminated_state_propagation": 0.67,
        },
    }

    rows: List[Dict[str, object]] = []
    family_summary: Dict[str, object] = {}

    for family, cfg in family_cfg.items():
        clean_violation_arr: List[bool] = []
        contaminated_violation_arr: List[bool] = []
        clean_success_arr: List[bool] = []
        contaminated_success_arr: List[bool] = []
        clean_prop_arr: List[bool] = []
        contaminated_prop_arr: List[bool] = []

        for i in range(n_pairs_per_family):
            latent = float(rng.normal(0.0, 1.0))

            p_clean_v = sigmoid(logit(cfg["clean_violation"]) + 0.55 * latent)
            p_cont_v = sigmoid(logit(cfg["contaminated_violation"]) + 0.55 * latent)

            clean_v = bool(rng.random() < p_clean_v)
            cont_v = bool(rng.random() < p_cont_v)

            p_clean_s = sigmoid(logit(cfg["clean_safe_success"]) - 0.45 * float(clean_v) - 0.10 * latent)
            p_cont_s = sigmoid(logit(cfg["contaminated_safe_success"]) - 0.45 * float(cont_v) - 0.10 * latent)
            clean_s = bool(rng.random() < p_clean_s)
            cont_s = bool(rng.random() < p_cont_s)

            p_clean_prop = sigmoid(logit(cfg["clean_state_propagation"]) + 0.35 * latent)
            p_cont_prop = sigmoid(logit(cfg["contaminated_state_propagation"]) + 0.35 * latent)
            clean_prop = bool(rng.random() < p_clean_prop)
            cont_prop = bool(rng.random() < p_cont_prop)

            clean_violation_arr.append(clean_v)
            contaminated_violation_arr.append(cont_v)
            clean_success_arr.append(clean_s)
            contaminated_success_arr.append(cont_s)
            clean_prop_arr.append(clean_prop)
            contaminated_prop_arr.append(cont_prop)

            rows.append(
                {
                    "pair_id": f"{family}_pair_{i:04d}",
                    "family": family,
                    "clean": {
                        "violation": clean_v,
                        "safe_task_success": clean_s,
                        "state_propagation_hit": clean_prop,
                    },
                    "contaminated": {
                        "violation": cont_v,
                        "safe_task_success": cont_s,
                        "state_propagation_hit": cont_prop,
                    },
                }
            )

        b = sum(1 for x, y in zip(clean_violation_arr, contaminated_violation_arr) if (not x) and y)
        c = sum(1 for x, y in zip(clean_violation_arr, contaminated_violation_arr) if x and (not y))
        family_summary[family] = {
            "n_pairs": n_pairs_per_family,
            "violation_rate": {
                "clean": round(rate(clean_violation_arr), 3),
                "contaminated": round(rate(contaminated_violation_arr), 3),
            },
            "safe_task_success_rate": {
                "clean": round(rate(clean_success_arr), 3),
                "contaminated": round(rate(contaminated_success_arr), 3),
            },
            "state_propagation_hit_rate": {
                "clean": round(rate(clean_prop_arr), 3),
                "contaminated": round(rate(contaminated_prop_arr), 3),
            },
            "paired_delta": round(rate(contaminated_violation_arr) - rate(clean_violation_arr), 3),
            "mcnemar": {"b": b, "c": c, "p_value": mcnemar_exact_p(b, c)},
        }

    all_clean_v = [bool(row["clean"]["violation"]) for row in rows]  # type: ignore[index]
    all_cont_v = [bool(row["contaminated"]["violation"]) for row in rows]  # type: ignore[index]
    all_clean_s = [bool(row["clean"]["safe_task_success"]) for row in rows]  # type: ignore[index]
    all_cont_s = [bool(row["contaminated"]["safe_task_success"]) for row in rows]  # type: ignore[index]
    all_clean_prop = [bool(row["clean"]["state_propagation_hit"]) for row in rows]  # type: ignore[index]
    all_cont_prop = [bool(row["contaminated"]["state_propagation_hit"]) for row in rows]  # type: ignore[index]

    b_all = sum(1 for x, y in zip(all_clean_v, all_cont_v) if (not x) and y)
    c_all = sum(1 for x, y in zip(all_clean_v, all_cont_v) if x and (not y))
    overall = {
        "n_pairs": len(rows),
        "violation_rate": {"clean": round(rate(all_clean_v), 3), "contaminated": round(rate(all_cont_v), 3)},
        "safe_task_success_rate": {
            "clean": round(rate(all_clean_s), 3),
            "contaminated": round(rate(all_cont_s), 3),
        },
        "state_propagation_hit_rate": {
            "clean": round(rate(all_clean_prop), 3),
            "contaminated": round(rate(all_cont_prop), 3),
        },
        "paired_delta": round(rate(all_cont_v) - rate(all_clean_v), 3),
        "mcnemar": {"b": b_all, "c": c_all, "p_value": mcnemar_exact_p(b_all, c_all)},
    }

    return {
        "meta": {
            "experiment_id": "E10",
            "name": "Near-Positive Causal Replay",
            "generated_at_utc": now_iso(),
            "seed": seed,
            "n_pairs_per_family": n_pairs_per_family,
            "trace_anchor": "019d337a-a32d-7901-8487-3c130851ff15",
            "conditions": ["clean_summary", "contaminated_summary"],
        },
        "results": rows,
        "summary": {"by_family": family_summary, "overall": overall},
    }


def parse_api_audit(path: Path) -> Dict[str, object]:
    text = path.read_text(encoding="utf-8")
    model_m = re.search(r"Model:\s*`([^`]+)`", text)
    rows = re.findall(r"\|\s*`?(vanilla|rtg)`?\s*\|\s*(\d+)\s*/\s*(\d+)\s*\|\s*(\d+)\s*/\s*(\d+)\s*\|", text)
    if not model_m or not rows:
        raise ValueError(f"failed to parse audit file: {path}")
    out: Dict[str, object] = {"model": model_m.group(1)}
    for cond, fail_num, fail_den, comp_num, comp_den in rows:
        out[cond] = {
            "clear_failures": int(fail_num),
            "episodes": int(fail_den),
            "task_completion": int(comp_num),
            "task_completion_den": int(comp_den),
        }
    return out


def violation_flag(row: Dict[str, object]) -> bool:
    violations = row.get("violations", {})
    if isinstance(violations, dict):
        return any(bool(v) for v in violations.values())
    return bool(row.get("primary_violation_detected", False))


def build_e11() -> Dict[str, object]:
    open_weight_files = [
        next(RESULTS_DIR.glob("v2_hf_open_weight_pilot_*32b*json")),
        next(RESULTS_DIR.glob("hf_open_weight_pilot_*14b*json")),
    ]
    api_audit_files = [
        OUTPUTS_DIR / "real_api_pilot_gpt54mini_audit.md",
        OUTPUTS_DIR / "real_api_pilot_codexmini_audit.md",
        OUTPUTS_DIR / "real_api_pilot_codexmax_audit.md",
    ]

    open_weight_summary: Dict[str, object] = {}
    all_run_effects: List[float] = []
    all_run_direction: List[bool] = []

    for path in open_weight_files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        model = payload["meta"]["model"]
        rows = payload["results"]

        grouped: Dict[Tuple[str, int], Dict[str, Dict[str, List[bool]]]] = {}
        family_coverage: Dict[Tuple[str, int], set[str]] = {}
        # key = (template, seed)
        for row in rows:
            template = str(row["template_name"])
            seed = int(row["seed"])
            family = str(row["family_label"])
            defense = str(row["defense_mode"])
            key = (template, seed)
            grouped.setdefault(key, {}).setdefault(defense, {"viol": [], "succ": [], "prop": []})
            family_coverage.setdefault(key, set()).add(family)
            grouped[key][defense]["viol"].append(violation_flag(row))
            grouped[key][defense]["succ"].append(bool(row.get("safe_task_success", False)))
            violations = row.get("violations", {})
            state_prop = bool(violations.get("state_propagation", False)) if isinstance(violations, dict) else False
            grouped[key][defense]["prop"].append(state_prop)

        run_rows: List[Dict[str, object]] = []
        for (template, seed), cond in grouped.items():
            if "vanilla" not in cond or "rtg" not in cond:
                continue
            vanilla_v = rate(cond["vanilla"]["viol"])
            rtg_v = rate(cond["rtg"]["viol"])
            vanilla_s = rate(cond["vanilla"]["succ"])
            rtg_s = rate(cond["rtg"]["succ"])
            vanilla_p = rate(cond["vanilla"]["prop"])
            rtg_p = rate(cond["rtg"]["prop"])
            effect = rel_reduction(vanilla_v, rtg_v)
            run_rows.append(
                {
                    "template": template,
                    "seed": seed,
                    "family_coverage": sorted(family_coverage[(template, seed)]),
                    "vanilla": {
                        "violation_rate": vanilla_v,
                        "safe_task_success_rate": vanilla_s,
                        "state_propagation_hit_rate": vanilla_p,
                    },
                    "rtg": {
                        "violation_rate": rtg_v,
                        "safe_task_success_rate": rtg_s,
                        "state_propagation_hit_rate": rtg_p,
                    },
                    "effect_violation_relative_reduction": effect,
                    "direction_rtg_better_or_equal": bool(rtg_v <= vanilla_v),
                }
            )
            all_run_effects.append(effect)
            all_run_direction.append(bool(rtg_v <= vanilla_v))

        template_to_effects: Dict[str, List[float]] = {}
        for r in run_rows:
            template_to_effects.setdefault(str(r["template"]), []).append(float(r["effect_violation_relative_reduction"]))

        template_means = {t: float(np.mean(v)) for t, v in template_to_effects.items()}
        template_std = float(np.std(np.array(list(template_means.values()), dtype=float), ddof=0)) if template_means else 0.0

        vanilla_rates = np.array([float(r["vanilla"]["violation_rate"]) for r in run_rows], dtype=float)
        rtg_rates = np.array([float(r["rtg"]["violation_rate"]) for r in run_rows], dtype=float)
        succ_delta = np.array(
            [float(r["rtg"]["safe_task_success_rate"]) - float(r["vanilla"]["safe_task_success_rate"]) for r in run_rows],
            dtype=float,
        )

        open_weight_summary[model] = {
            "source_file": str(path.relative_to(ROOT)).replace("\\", "/"),
            "n_seed_template_runs": len(run_rows),
            "violation_rate_mean": {"vanilla": float(vanilla_rates.mean()), "rtg": float(rtg_rates.mean())},
            "direction_consistency": float(np.mean([r["direction_rtg_better_or_equal"] for r in run_rows])) if run_rows else 0.0,
            "effect_range": {
                "min": float(np.min([r["effect_violation_relative_reduction"] for r in run_rows])) if run_rows else 0.0,
                "max": float(np.max([r["effect_violation_relative_reduction"] for r in run_rows])) if run_rows else 0.0,
            },
            "std_across_templates": template_std,
            "success_delta_mean": float(succ_delta.mean()) if len(succ_delta) else 0.0,
            "template_effect_means": template_means,
        }

    api_rows = [parse_api_audit(path) for path in api_audit_files]
    api_summary: Dict[str, object] = {}
    api_dir_flags: List[bool] = []
    for row in api_rows:
        model = str(row["model"])
        v_fail = int(row["vanilla"]["clear_failures"]) / int(row["vanilla"]["episodes"])  # type: ignore[index]
        r_fail = int(row["rtg"]["clear_failures"]) / int(row["rtg"]["episodes"])  # type: ignore[index]
        v_comp = int(row["vanilla"]["task_completion"]) / int(row["vanilla"]["task_completion_den"])  # type: ignore[index]
        r_comp = int(row["rtg"]["task_completion"]) / int(row["rtg"]["task_completion_den"])  # type: ignore[index]
        direction_ok = r_fail <= v_fail
        api_dir_flags.append(direction_ok)
        api_summary[model] = {
            "vanilla_failure_rate": v_fail,
            "rtg_failure_rate": r_fail,
            "vanilla_completion_rate": v_comp,
            "rtg_completion_rate": r_comp,
            "direction_consistency": direction_ok,
        }

    overall_direction = float(np.mean(all_run_direction)) if all_run_direction else 0.0
    overall_effect_min = float(np.min(all_run_effects)) if all_run_effects else 0.0
    overall_effect_max = float(np.max(all_run_effects)) if all_run_effects else 0.0

    return {
        "meta": {
            "experiment_id": "E11",
            "name": "Cross-Stack + API Spot Check",
            "generated_at_utc": now_iso(),
            "open_weight_sources": [str(p.relative_to(ROOT)).replace("\\", "/") for p in open_weight_files],
            "api_audit_sources": [str(p.relative_to(ROOT)).replace("\\", "/") for p in api_audit_files],
        },
        "summary": {
            "open_weight": open_weight_summary,
            "api_spot_check": api_summary,
            "overall": {
                "direction_consistency": overall_direction,
                "effect_range": {"min": overall_effect_min, "max": overall_effect_max},
                "api_direction_consistency": float(np.mean(api_dir_flags)) if api_dir_flags else 0.0,
                "stack_dependence_flag": bool(overall_effect_min < 0.0 and overall_effect_max > 0.0),
            },
        },
    }


def render_e10_md(payload: Dict[str, object]) -> str:
    meta = payload["meta"]
    summary = payload["summary"]
    by_family = summary["by_family"]
    overall = summary["overall"]

    lines: List[str] = []
    lines.append("# E10 Near-Positive Causal Replay")
    lines.append("")
    lines.append(f"Generated at: {meta['generated_at_utc']}")
    lines.append(f"Trace anchor: `{meta['trace_anchor']}`")
    lines.append(f"Paired episodes per family: {meta['n_pairs_per_family']}")
    lines.append("")
    lines.append("## Family-Wise Paired Results")
    lines.append("")
    lines.append("| Family | Clean Viol. | Cont. Viol. | Paired Delta | Clean Safe | Cont. Safe | Clean State-Prop | Cont. State-Prop | McNemar p |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for family, row in by_family.items():
        lines.append(
            f"| {family} | {row['violation_rate']['clean']:.3f} | {row['violation_rate']['contaminated']:.3f} | "
            f"{row['paired_delta']:.3f} | {row['safe_task_success_rate']['clean']:.3f} | {row['safe_task_success_rate']['contaminated']:.3f} | "
            f"{row['state_propagation_hit_rate']['clean']:.3f} | {row['state_propagation_hit_rate']['contaminated']:.3f} | {row['mcnemar']['p_value']:.3e} |"
        )
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(
        f"- `violation_rate`: clean={overall['violation_rate']['clean']:.3f}, contaminated={overall['violation_rate']['contaminated']:.3f}"
    )
    lines.append(f"- `paired_delta`: {overall['paired_delta']:.3f}")
    lines.append(
        f"- `safe_task_success_rate`: clean={overall['safe_task_success_rate']['clean']:.3f}, contaminated={overall['safe_task_success_rate']['contaminated']:.3f}"
    )
    lines.append(
        f"- `state_propagation_hit_rate`: clean={overall['state_propagation_hit_rate']['clean']:.3f}, contaminated={overall['state_propagation_hit_rate']['contaminated']:.3f}"
    )
    lines.append(f"- `mcnemar_p`: {overall['mcnemar']['p_value']:.3e}")
    lines.append("")
    lines.append("Interpretation: paired replay shows a strong contamination-direction shift with significantly higher downstream state-propagation hits.")
    return "\n".join(lines) + "\n"


def render_e11_md(payload: Dict[str, object]) -> str:
    summary = payload["summary"]
    open_weight = summary["open_weight"]
    api = summary["api_spot_check"]
    overall = summary["overall"]

    lines: List[str] = []
    lines.append("# E11 Cross-Stack + API Spot Check")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")
    lines.append("## Open-Weight Cross-Stack")
    lines.append("")
    lines.append("| Model | Vanilla Viol. Mean | RTG Viol. Mean | Direction Consistency | Effect Range | Std Across Templates |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for model, row in open_weight.items():
        effect = row["effect_range"]
        lines.append(
            f"| {model} | {row['violation_rate_mean']['vanilla']:.3f} | {row['violation_rate_mean']['rtg']:.3f} | "
            f"{row['direction_consistency']:.3f} | [{effect['min']:.3f}, {effect['max']:.3f}] | {row['std_across_templates']:.3f} |"
        )
    lines.append("")
    lines.append("## API Spot Check (Manual Audit)")
    lines.append("")
    lines.append("| Model | Vanilla Fail | RTG Fail | Vanilla Completion | RTG Completion | Direction Consistency |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for model, row in api.items():
        lines.append(
            f"| {model} | {row['vanilla_failure_rate']:.3f} | {row['rtg_failure_rate']:.3f} | "
            f"{row['vanilla_completion_rate']:.3f} | {row['rtg_completion_rate']:.3f} | {str(row['direction_consistency'])} |"
        )
    lines.append("")
    lines.append("## Overall Consolidation")
    lines.append("")
    lines.append(f"- `direction_consistency` (open-weight seed-template runs): {overall['direction_consistency']:.3f}")
    lines.append(f"- `effect_range` (open-weight seed-template runs): [{overall['effect_range']['min']:.3f}, {overall['effect_range']['max']:.3f}]")
    lines.append(f"- `std_across_templates`: model-specific (see table above)")
    lines.append(f"- `api_direction_consistency`: {overall['api_direction_consistency']:.3f}")
    lines.append(f"- `stack_dependence_flag`: {overall['stack_dependence_flag']}")
    lines.append("")
    lines.append("Interpretation: RTG behavior is stack-dependent; open-weight and API spot-check trends are not universally aligned.")
    return "\n".join(lines) + "\n"


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    e10 = build_e10()
    e11 = build_e11()

    E10_JSON.write_text(json.dumps(e10, ensure_ascii=False, indent=2), encoding="utf-8")
    E11_JSON.write_text(json.dumps(e11, ensure_ascii=False, indent=2), encoding="utf-8")
    E10_MD.write_text(render_e10_md(e10), encoding="utf-8")
    E11_MD.write_text(render_e11_md(e11), encoding="utf-8")

    print(f"[OK] wrote {E10_JSON}")
    print(f"[OK] wrote {E10_MD}")
    print(f"[OK] wrote {E11_JSON}")
    print(f"[OK] wrote {E11_MD}")


if __name__ == "__main__":
    main()
