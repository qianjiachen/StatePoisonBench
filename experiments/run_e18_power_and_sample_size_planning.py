"""
E18: Power and sample-size planning for manual-calibrated API evidence.

Inputs:
- experiments/results/e16_manual_calibrated_small_sample_bounds.json

Outputs:
- experiments/results/e18_power_and_sample_size_planning.json
- experiments/results/e18_power_and_sample_size_planning.md
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
E16_JSON = RESULTS_DIR / "e16_manual_calibrated_small_sample_bounds.json"
OUT_JSON = RESULTS_DIR / "e18_power_and_sample_size_planning.json"
OUT_MD = RESULTS_DIR / "e18_power_and_sample_size_planning.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def n_required_two_prop(p1: float, p2: float, power: float, alpha: float = 0.05) -> float:
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    z_beta = NormalDist().inv_cdf(power)
    d = abs(p1 - p2)
    if d <= 0.0:
        return float("inf")
    pbar = (p1 + p2) / 2.0
    num = (
        z_alpha * math.sqrt(2.0 * pbar * (1.0 - pbar))
        + z_beta * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))
    ) ** 2
    return num / (d * d)


def power_two_prop(p1: float, p2: float, n_per_arm: float, alpha: float = 0.05) -> float:
    z_alpha = NormalDist().inv_cdf(1.0 - alpha / 2.0)
    pbar = (p1 + p2) / 2.0
    se1 = math.sqrt((p1 * (1.0 - p1) + p2 * (1.0 - p2)) / n_per_arm)
    if se1 <= 0.0:
        return 0.0
    z_eff = abs(p1 - p2) / se1
    nd = NormalDist()
    return (1.0 - nd.cdf(z_alpha - z_eff)) + nd.cdf(-z_alpha - z_eff)


def build() -> Dict[str, object]:
    e16 = json.loads(E16_JSON.read_text(encoding="utf-8"))
    pooled = e16["summary"]["pooled_manual_clear_positive"]
    p_v = float(pooled["vanilla"]["rate"])
    p_r = float(pooled["rtg"]["rate"])
    n_v = int(pooled["vanilla"]["n"])
    n_r = int(pooled["rtg"]["n"])
    n_current = min(n_v, n_r)
    delta = abs(p_v - p_r)

    current_power = power_two_prop(p_v, p_r, float(n_current))
    n80 = n_required_two_prop(p_v, p_r, power=0.80)
    n90 = n_required_two_prop(p_v, p_r, power=0.90)

    scenario_deltas = [0.02, 0.03, 0.05]
    scenario_rows: List[Dict[str, float]] = []
    for d in scenario_deltas:
        n80_s = n_required_two_prop(d, 0.0, power=0.80)
        n90_s = n_required_two_prop(d, 0.0, power=0.90)
        scenario_rows.append(
            {
                "delta_assumed": round(d, 3),
                "n_per_arm_power80": int(math.ceil(n80_s)),
                "n_per_arm_power90": int(math.ceil(n90_s)),
            }
        )

    return {
        "meta": {
            "experiment_id": "E18",
            "name": "Power and Sample-Size Planning (Manual-Calibrated API Subset)",
            "generated_at_utc": now_iso(),
            "note": (
                "Two-proportion normal-approximation planning on S16 pooled manual rates; "
                "used to contextualize small-sample interpretability."
            ),
        },
        "summary": {
            "observed_rates": {
                "vanilla": round(p_v, 3),
                "rtg": round(p_r, 3),
                "absolute_delta": round(delta, 3),
            },
            "current_design": {
                "n_per_arm": int(n_current),
                "approx_power_two_sided_alpha_0_05": round(current_power, 3),
            },
            "required_n_per_arm_for_observed_delta": {
                "power_0_80": int(math.ceil(n80)),
                "power_0_90": int(math.ceil(n90)),
            },
            "low_rate_scenario_grid": scenario_rows,
        },
    }


def render_md(payload: Dict[str, object]) -> str:
    s = payload["summary"]
    lines: List[str] = []
    lines.append("# E18 Power and Sample-Size Planning")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")
    lines.append(payload["meta"]["note"])
    lines.append("")
    lines.append("| Statistic | Value |")
    lines.append("|---|---:|")
    lines.append(
        f"| Observed pooled absolute delta (manual clear-positive rate) | {s['observed_rates']['absolute_delta']:.3f} |"
    )
    lines.append(f"| Current per-arm sample size | {s['current_design']['n_per_arm']} |")
    lines.append(
        f"| Approx two-sided power at current n | {s['current_design']['approx_power_two_sided_alpha_0_05']:.3f} |"
    )
    lines.append(
        f"| Required n/arm for 80% power (observed delta) | {s['required_n_per_arm_for_observed_delta']['power_0_80']} |"
    )
    lines.append(
        f"| Required n/arm for 90% power (observed delta) | {s['required_n_per_arm_for_observed_delta']['power_0_90']} |"
    )
    lines.append("")
    lines.append("| Assumed Delta (low-rate, p vs 0) | n/arm for 80% power | n/arm for 90% power |")
    lines.append("|---:|---:|---:|")
    for row in s["low_rate_scenario_grid"]:
        lines.append(
            f"| {row['delta_assumed']:.3f} | {row['n_per_arm_power80']} | {row['n_per_arm_power90']} |"
        )
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
