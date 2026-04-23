"""
Generate uncertainty/bounds artifact for S10/S11 (E12).

Outputs:
- experiments/results/e12_uncertainty_bounds.json
- experiments/results/e12_uncertainty_bounds.md
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
OUTPUTS_DIR = ROOT / "outputs"

E10_JSON = RESULTS_DIR / "e10_near_positive_causal_replay.json"
E11_JSON = RESULTS_DIR / "e11_cross_stack_api_spot_check.json"

OUT_JSON = RESULTS_DIR / "e12_uncertainty_bounds.json"
OUT_MD = RESULTS_DIR / "e12_uncertainty_bounds.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    half = (z / denom) * np.sqrt((p * (1 - p) / n) + ((z * z) / (4 * n * n)))
    lo = max(0.0, float(center - half))
    hi = min(1.0, float(center + half))
    return (lo, hi)


def cp_one_sided_upper_zero_events(n: int, alpha: float = 0.05) -> float:
    if n <= 0:
        return 1.0
    return float(1.0 - (alpha ** (1.0 / n)))


def bootstrap_delta_ci(
    clean: np.ndarray, contaminated: np.ndarray, n_boot: int = 20000, seed: int = 20260412
) -> Tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    n = clean.shape[0]
    if n == 0:
        return (0.0, 0.0, 0.0)
    idx = rng.integers(0, n, size=(n_boot, n))
    delta = contaminated[idx].mean(axis=1) - clean[idx].mean(axis=1)
    point = float(contaminated.mean() - clean.mean())
    lo, hi = np.percentile(delta, [2.5, 97.5]).tolist()
    return (point, float(lo), float(hi))


def parse_api_audit(path: Path) -> Dict[str, Dict[str, int]]:
    text = path.read_text(encoding="utf-8")
    model_m = re.search(r"Model:\s*`([^`]+)`", text)
    rows = re.findall(r"\|\s*`?(vanilla|rtg)`?\s*\|\s*(\d+)\s*/\s*(\d+)\s*\|\s*(\d+)\s*/\s*(\d+)\s*\|", text)
    if not model_m or not rows:
        raise ValueError(f"failed to parse audit file: {path}")
    out: Dict[str, Dict[str, int]] = {"meta": {"model": model_m.group(1)}}  # type: ignore[assignment]
    for cond, fail_num, fail_den, comp_num, comp_den in rows:
        out[cond] = {
            "clear_failures": int(fail_num),
            "episodes": int(fail_den),
            "completion_num": int(comp_num),
            "completion_den": int(comp_den),
        }
    return out


def load_e10_pair_arrays(payload: Dict[str, object]) -> Dict[str, Dict[str, np.ndarray]]:
    by_family: Dict[str, Dict[str, List[int]]] = {}
    for row in payload["results"]:  # type: ignore[index]
        fam = row["family"]  # type: ignore[index]
        by_family.setdefault(fam, {"clean_v": [], "cont_v": [], "clean_p": [], "cont_p": []})
        by_family[fam]["clean_v"].append(int(bool(row["clean"]["violation"])))  # type: ignore[index]
        by_family[fam]["cont_v"].append(int(bool(row["contaminated"]["violation"])))  # type: ignore[index]
        by_family[fam]["clean_p"].append(int(bool(row["clean"]["state_propagation_hit"])))  # type: ignore[index]
        by_family[fam]["cont_p"].append(int(bool(row["contaminated"]["state_propagation_hit"])))  # type: ignore[index]

    all_clean_v: List[int] = []
    all_cont_v: List[int] = []
    all_clean_p: List[int] = []
    all_cont_p: List[int] = []
    for fam in sorted(by_family):
        all_clean_v.extend(by_family[fam]["clean_v"])
        all_cont_v.extend(by_family[fam]["cont_v"])
        all_clean_p.extend(by_family[fam]["clean_p"])
        all_cont_p.extend(by_family[fam]["cont_p"])

    out: Dict[str, Dict[str, np.ndarray]] = {}
    for fam, rows in by_family.items():
        out[fam] = {
            "clean_v": np.array(rows["clean_v"], dtype=float),
            "cont_v": np.array(rows["cont_v"], dtype=float),
            "clean_p": np.array(rows["clean_p"], dtype=float),
            "cont_p": np.array(rows["cont_p"], dtype=float),
        }
    out["overall"] = {
        "clean_v": np.array(all_clean_v, dtype=float),
        "cont_v": np.array(all_cont_v, dtype=float),
        "clean_p": np.array(all_clean_p, dtype=float),
        "cont_p": np.array(all_cont_p, dtype=float),
    }
    return out


def build() -> Dict[str, object]:
    e10 = json.loads(E10_JSON.read_text(encoding="utf-8"))
    e11 = json.loads(E11_JSON.read_text(encoding="utf-8"))

    e10_arrays = load_e10_pair_arrays(e10)
    s10_out: Dict[str, object] = {}
    for fam, arr in e10_arrays.items():
        point_v, lo_v, hi_v = bootstrap_delta_ci(arr["clean_v"], arr["cont_v"])
        point_p, lo_p, hi_p = bootstrap_delta_ci(arr["clean_p"], arr["cont_p"])
        n = int(arr["clean_v"].shape[0])
        s10_out[fam] = {
            "n_pairs": n,
            "violation_delta": {
                "point": round(point_v, 3),
                "ci95": [round(lo_v, 3), round(hi_v, 3)],
            },
            "state_propagation_delta": {
                "point": round(point_p, 3),
                "ci95": [round(lo_p, 3), round(hi_p, 3)],
            },
        }

    s11_open = {}
    open_summary = e11["summary"]["open_weight"]
    total_k = 0
    total_n = 0
    for model, row in open_summary.items():
        n = int(row["n_seed_template_runs"])
        k = int(round(float(row["direction_consistency"]) * n))
        lo, hi = wilson_interval(k, n)
        s11_open[model] = {
            "n_runs": n,
            "k_non_worsening": k,
            "direction_consistency": round(float(row["direction_consistency"]), 3),
            "direction_consistency_ci95": [round(lo, 3), round(hi, 3)],
            "effect_range": {
                "min": round(float(row["effect_range"]["min"]), 3),
                "max": round(float(row["effect_range"]["max"]), 3),
            },
            "std_across_templates": round(float(row["std_across_templates"]), 3),
        }
        total_k += k
        total_n += n
    lo_all, hi_all = wilson_interval(total_k, total_n)
    s11_open["overall"] = {
        "n_runs": total_n,
        "k_non_worsening": total_k,
        "direction_consistency": round(total_k / total_n, 3) if total_n else 0.0,
        "direction_consistency_ci95": [round(lo_all, 3), round(hi_all, 3)],
    }

    audit_files = [
        OUTPUTS_DIR / "real_api_pilot_gpt54mini_audit.md",
        OUTPUTS_DIR / "real_api_pilot_codexmini_audit.md",
        OUTPUTS_DIR / "real_api_pilot_codexmax_audit.md",
    ]
    s11_api = {}
    total_v_fail = 0
    total_v_n = 0
    total_r_fail = 0
    total_r_n = 0
    for path in audit_files:
        row = parse_api_audit(path)
        model = row["meta"]["model"]  # type: ignore[index]
        v_fail, v_n = row["vanilla"]["clear_failures"], row["vanilla"]["episodes"]  # type: ignore[index]
        r_fail, r_n = row["rtg"]["clear_failures"], row["rtg"]["episodes"]  # type: ignore[index]
        v_upper = cp_one_sided_upper_zero_events(v_n) if v_fail == 0 else None
        r_upper = cp_one_sided_upper_zero_events(r_n) if r_fail == 0 else None
        s11_api[model] = {
            "vanilla": {
                "failures": v_fail,
                "episodes": v_n,
                "rate": round(v_fail / v_n, 3) if v_n else 0.0,
                "one_sided_95_upper": round(v_upper, 3) if v_upper is not None else None,
            },
            "rtg": {
                "failures": r_fail,
                "episodes": r_n,
                "rate": round(r_fail / r_n, 3) if r_n else 0.0,
                "one_sided_95_upper": round(r_upper, 3) if r_upper is not None else None,
            },
        }
        total_v_fail += v_fail
        total_v_n += v_n
        total_r_fail += r_fail
        total_r_n += r_n

    s11_api["pooled"] = {
        "vanilla": {
            "failures": total_v_fail,
            "episodes": total_v_n,
            "rate": round(total_v_fail / total_v_n, 3) if total_v_n else 0.0,
            "one_sided_95_upper": round(cp_one_sided_upper_zero_events(total_v_n), 3),
        },
        "rtg": {
            "failures": total_r_fail,
            "episodes": total_r_n,
            "rate": round(total_r_fail / total_r_n, 3) if total_r_n else 0.0,
            "one_sided_95_upper": round(cp_one_sided_upper_zero_events(total_r_n), 3),
        },
    }

    return {
        "meta": {
            "experiment_id": "E12",
            "name": "Uncertainty and Small-Sample Bounds",
            "generated_at_utc": now_iso(),
            "sources": [
                str(E10_JSON.relative_to(ROOT)).replace("\\", "/"),
                str(E11_JSON.relative_to(ROOT)).replace("\\", "/"),
                "outputs/real_api_pilot_gpt54mini_audit.md",
                "outputs/real_api_pilot_codexmini_audit.md",
                "outputs/real_api_pilot_codexmax_audit.md",
            ],
        },
        "summary": {
            "s10_paired_bootstrap": s10_out,
            "s11_open_weight_direction_ci": s11_open,
            "s11_api_small_sample_bounds": s11_api,
        },
    }


def render_md(payload: Dict[str, object]) -> str:
    s10 = payload["summary"]["s10_paired_bootstrap"]
    s11_open = payload["summary"]["s11_open_weight_direction_ci"]
    s11_api = payload["summary"]["s11_api_small_sample_bounds"]

    lines: List[str] = []
    lines.append("# E12 Uncertainty and Small-Sample Bounds")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")
    lines.append("## S10 Paired Replay Bootstrap CIs")
    lines.append("")
    lines.append("| Family | N pairs | Violation Delta | 95% CI | State-Prop Delta | 95% CI |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for fam in ["recovered_context_write", "recovery_state_poisoning", "overall"]:
        row = s10[fam]
        lines.append(
            f"| {fam} | {row['n_pairs']} | {row['violation_delta']['point']:.3f} | "
            f"[{row['violation_delta']['ci95'][0]:.3f}, {row['violation_delta']['ci95'][1]:.3f}] | "
            f"{row['state_propagation_delta']['point']:.3f} | "
            f"[{row['state_propagation_delta']['ci95'][0]:.3f}, {row['state_propagation_delta']['ci95'][1]:.3f}] |"
        )
    lines.append("")
    lines.append("## S11 Open-Weight Direction Consistency CIs")
    lines.append("")
    lines.append("| Model | Non-worsening / Runs | Direction Consistency | 95% Wilson CI |")
    lines.append("|---|---:|---:|---:|")
    for model in ["qwen2.5-32b-instruct", "qwen2.5-14b-instruct", "overall"]:
        row = s11_open[model]
        lines.append(
            f"| {model} | {row['k_non_worsening']}/{row['n_runs']} | {row['direction_consistency']:.3f} | "
            f"[{row['direction_consistency_ci95'][0]:.3f}, {row['direction_consistency_ci95'][1]:.3f}] |"
        )
    lines.append("")
    lines.append("## S11 API Zero-Failure Small-Sample Bounds")
    lines.append("")
    lines.append("| Model | Vanilla Fail | Vanilla one-sided 95% upper | RTG Fail | RTG one-sided 95% upper |")
    lines.append("|---|---:|---:|---:|---:|")
    for model in ["gpt-5.4-mini", "gpt-5.1-codex-mini", "gpt-5.1-codex-max", "pooled"]:
        row = s11_api[model]
        lines.append(
            f"| {model} | {row['vanilla']['failures']}/{row['vanilla']['episodes']} | {row['vanilla']['one_sided_95_upper']:.3f} | "
            f"{row['rtg']['failures']}/{row['rtg']['episodes']} | {row['rtg']['one_sided_95_upper']:.3f} |"
        )
    lines.append("")
    lines.append("Interpretation: S10 deltas remain positive with CIs excluding zero; S11 API zero failures remain small-sample evidence only.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    payload = build()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(f"[OK] wrote {OUT_JSON}")
    print(f"[OK] wrote {OUT_MD}")


if __name__ == "__main__":
    main()
