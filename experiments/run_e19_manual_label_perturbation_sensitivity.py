"""
E19: Manual-label perturbation sensitivity on pooled cross-provider API counts.

Purpose:
- Stress-test how low-count prevalence interpretation changes under small,
  plausible relabel perturbations around S16 pooled manual counts.

Inputs:
- experiments/results/e16_manual_calibrated_small_sample_bounds.json

Outputs:
- experiments/results/e19_manual_label_perturbation_sensitivity.json
- experiments/results/e19_manual_label_perturbation_sensitivity.md
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
E16_JSON = RESULTS_DIR / "e16_manual_calibrated_small_sample_bounds.json"
OUT_JSON = RESULTS_DIR / "e19_manual_label_perturbation_sensitivity.json"
OUT_MD = RESULTS_DIR / "e19_manual_label_perturbation_sensitivity.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    # 2x2 table:
    # [a b]
    # [c d]
    r1 = a + b
    r2 = c + d
    c1 = a + c
    n = r1 + r2
    if n == 0:
        return 1.0

    def hypergeom_p(x: int) -> float:
        return (math.comb(c1, x) * math.comb(n - c1, r1 - x)) / math.comb(n, r1)

    xmin = max(0, r1 - (n - c1))
    xmax = min(r1, c1)
    p_obs = hypergeom_p(a)
    p_two = 0.0
    for x in range(xmin, xmax + 1):
        px = hypergeom_p(x)
        if px <= p_obs + 1e-12:
            p_two += px
    return min(1.0, p_two)


def clamp_count(k: int, n: int) -> int:
    return max(0, min(k, n))


def scenario_row(name: str, vk: int, vn: int, rk: int, rn: int, note: str) -> Dict[str, object]:
    vr = vk / vn if vn else 0.0
    rr = rk / rn if rn else 0.0
    delta = rr - vr
    fisher_p = fisher_exact_two_sided(vk, vn - vk, rk, rn - rk)
    return {
        "scenario": name,
        "description": note,
        "vanilla": {"k": vk, "n": vn, "rate": round(vr, 3)},
        "rtg": {"k": rk, "n": rn, "rate": round(rr, 3)},
        "delta_rtg_minus_vanilla": round(delta, 3),
        "direction_non_worsening": bool(rr <= vr),
        "fisher_two_sided_p": round(fisher_p, 3),
    }


def build() -> Dict[str, object]:
    e16 = json.loads(E16_JSON.read_text(encoding="utf-8"))
    pooled = e16["summary"]["pooled_manual_clear_positive"]
    v_k = int(pooled["vanilla"]["k"])
    v_n = int(pooled["vanilla"]["n"])
    r_k = int(pooled["rtg"]["k"])
    r_n = int(pooled["rtg"]["n"])

    scenarios: List[Dict[str, object]] = []
    scenarios.append(
        scenario_row(
            "observed",
            v_k,
            v_n,
            r_k,
            r_n,
            "Observed pooled manual counts from S16.",
        )
    )
    scenarios.append(
        scenario_row(
            "vanilla_downgrade_1",
            clamp_count(v_k - 1, v_n),
            v_n,
            r_k,
            r_n,
            "Single-label stress: the only vanilla clear-positive is downgraded.",
        )
    )
    scenarios.append(
        scenario_row(
            "rtg_upgrade_1",
            v_k,
            v_n,
            clamp_count(r_k + 1, r_n),
            r_n,
            "Single-label stress: one RTG ambiguous episode is upgraded to clear-positive.",
        )
    )
    scenarios.append(
        scenario_row(
            "swap_stress_2",
            clamp_count(v_k - 1, v_n),
            v_n,
            clamp_count(r_k + 1, r_n),
            r_n,
            "Two-label stress: vanilla downgrade plus RTG upgrade (direction-flip stress).",
        )
    )
    scenarios.append(
        scenario_row(
            "vanilla_plus2_stress",
            clamp_count(v_k + 2, v_n),
            v_n,
            r_k,
            r_n,
            "Higher-prevalence stress: add two vanilla clear-positive episodes.",
        )
    )

    non_worse_k = sum(1 for row in scenarios if row["direction_non_worsening"])
    p_values = [float(row["fisher_two_sided_p"]) for row in scenarios]
    deltas = [float(row["delta_rtg_minus_vanilla"]) for row in scenarios]

    summary = {
        "n_scenarios": len(scenarios),
        "direction_non_worsening": {
            "k": non_worse_k,
            "n": len(scenarios),
            "rate": round(non_worse_k / len(scenarios), 3),
        },
        "delta_range_rtg_minus_vanilla": {
            "min": round(min(deltas), 3),
            "max": round(max(deltas), 3),
        },
        "fisher_p_range": {
            "min": round(min(p_values), 3),
            "max": round(max(p_values), 3),
        },
    }

    return {
        "meta": {
            "experiment_id": "E19",
            "name": "Manual-Label Perturbation Sensitivity (Cross-Provider API Subset)",
            "generated_at_utc": now_iso(),
            "note": (
                "Scenario-based perturbation on S16 pooled manual counts; "
                "used to stress-test low-count directional fragility."
            ),
        },
        "base_counts_from_s16": {
            "vanilla": {"k": v_k, "n": v_n},
            "rtg": {"k": r_k, "n": r_n},
        },
        "scenarios": scenarios,
        "summary": summary,
    }


def render_md(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# E19 Manual-Label Perturbation Sensitivity")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")
    lines.append(payload["meta"]["note"])
    lines.append("")
    base = payload["base_counts_from_s16"]
    lines.append(
        f"Base pooled counts from S16: vanilla {base['vanilla']['k']}/{base['vanilla']['n']}, "
        f"RTG {base['rtg']['k']}/{base['rtg']['n']}."
    )
    lines.append("")
    lines.append("| Scenario | Vanilla k/n (rate) | RTG k/n (rate) | Delta (RTG - Vanilla) | Fisher p | Non-worsening |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in payload["scenarios"]:
        lines.append(
            f"| {row['scenario']} | "
            f"{row['vanilla']['k']}/{row['vanilla']['n']} ({row['vanilla']['rate']:.3f}) | "
            f"{row['rtg']['k']}/{row['rtg']['n']} ({row['rtg']['rate']:.3f}) | "
            f"{row['delta_rtg_minus_vanilla']:.3f} | "
            f"{row['fisher_two_sided_p']:.3f} | "
            f"{'Yes' if row['direction_non_worsening'] else 'No'} |"
        )
    lines.append("")
    s = payload["summary"]
    lines.append("| Summary | Value |")
    lines.append("|---|---:|")
    lines.append(
        f"| Direction non-worsening across scenarios | "
        f"{s['direction_non_worsening']['k']}/{s['direction_non_worsening']['n']} "
        f"({s['direction_non_worsening']['rate']:.3f}) |"
    )
    lines.append(
        f"| Delta range (RTG - Vanilla) | "
        f"[{s['delta_range_rtg_minus_vanilla']['min']:.3f}, {s['delta_range_rtg_minus_vanilla']['max']:.3f}] |"
    )
    lines.append(
        f"| Fisher p range | "
        f"[{s['fisher_p_range']['min']:.3f}, {s['fisher_p_range']['max']:.3f}] |"
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
