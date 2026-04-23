"""
E16: Manual-calibrated small-sample bounds for cross-provider API evidence.

Inputs:
- experiments/results/e14_cross_provider_manual_audit.json
- experiments/results/e15_manual_adjudication_robustness.json

Outputs:
- experiments/results/e16_manual_calibrated_small_sample_bounds.json
- experiments/results/e16_manual_calibrated_small_sample_bounds.md
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
E14_JSON = RESULTS_DIR / "e14_cross_provider_manual_audit.json"
E15_JSON = RESULTS_DIR / "e15_manual_adjudication_robustness.json"
OUT_JSON = RESULTS_DIR / "e16_manual_calibrated_small_sample_bounds.json"
OUT_MD = RESULTS_DIR / "e16_manual_calibrated_small_sample_bounds.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def wilson_interval(k: int, n: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    half = (z / denom) * math.sqrt((p * (1 - p) / n) + ((z * z) / (4 * n * n)))
    lo = max(0.0, center - half)
    hi = min(1.0, center + half)
    return (lo, hi)


def exact_one_sided_upper(k: int, n: int, alpha: float = 0.05) -> float:
    # For k=0, Clopper-Pearson one-sided upper has closed form:
    #   p_u = 1 - alpha^(1/n)
    if n <= 0:
        return 0.0
    if k == 0:
        return 1.0 - (alpha ** (1.0 / n))
    # For k>0 we report Wilson upper in this lightweight script.
    return wilson_interval(k, n)[1]


def fisher_exact_two_sided(a: int, b: int, c: int, d: int) -> float:
    # Table:
    # [a b]
    # [c d]
    r1 = a + b
    r2 = c + d
    c1 = a + c
    n = r1 + r2
    if n == 0:
        return 1.0

    def hypergeom_p(x: int) -> float:
        return (
            math.comb(c1, x)
            * math.comb(n - c1, r1 - x)
            / math.comb(n, r1)
        )

    xmin = max(0, r1 - (n - c1))
    xmax = min(r1, c1)
    p_obs = hypergeom_p(a)
    p_two = 0.0
    for x in range(xmin, xmax + 1):
        px = hypergeom_p(x)
        if px <= p_obs + 1e-12:
            p_two += px
    return min(1.0, p_two)


def build() -> Dict[str, object]:
    e14 = json.loads(E14_JSON.read_text(encoding="utf-8"))
    e15 = json.loads(E15_JSON.read_text(encoding="utf-8"))

    per_model: Dict[str, object] = {}
    pooled_v_k = 0
    pooled_v_n = 0
    pooled_r_k = 0
    pooled_r_n = 0

    for alias, row in e14["models"].items():
        v_rate = float(row["clear_positive_rate"]["vanilla"])
        r_rate = float(row["clear_positive_rate"]["rtg"])
        n_each = int(row["n_total_episodes"]) // 2
        v_k = int(round(v_rate * n_each))
        r_k = int(round(r_rate * n_each))
        v_n = n_each
        r_n = n_each

        pooled_v_k += v_k
        pooled_v_n += v_n
        pooled_r_k += r_k
        pooled_r_n += r_n

        v_ci = wilson_interval(v_k, v_n)
        r_ci = wilson_interval(r_k, r_n)

        per_model[alias] = {
            "model": row["model"],
            "vanilla": {
                "k": v_k,
                "n": v_n,
                "rate": round(v_k / v_n, 3),
                "wilson_ci95": [round(v_ci[0], 3), round(v_ci[1], 3)],
            },
            "rtg": {
                "k": r_k,
                "n": r_n,
                "rate": round(r_k / r_n, 3),
                "wilson_ci95": [round(r_ci[0], 3), round(r_ci[1], 3)],
                "one_sided_95_upper": round(exact_one_sided_upper(r_k, r_n), 3),
            },
        }

    pooled_v_ci = wilson_interval(pooled_v_k, pooled_v_n)
    pooled_r_ci = wilson_interval(pooled_r_k, pooled_r_n)
    fisher_p = fisher_exact_two_sided(
        pooled_v_k,
        pooled_v_n - pooled_v_k,
        pooled_r_k,
        pooled_r_n - pooled_r_k,
    )

    summary = {
        "pooled_manual_clear_positive": {
            "vanilla": {
                "k": pooled_v_k,
                "n": pooled_v_n,
                "rate": round(pooled_v_k / pooled_v_n, 3),
                "wilson_ci95": [round(pooled_v_ci[0], 3), round(pooled_v_ci[1], 3)],
            },
            "rtg": {
                "k": pooled_r_k,
                "n": pooled_r_n,
                "rate": round(pooled_r_k / pooled_r_n, 3),
                "wilson_ci95": [round(pooled_r_ci[0], 3), round(pooled_r_ci[1], 3)],
                "one_sided_95_upper": round(exact_one_sided_upper(pooled_r_k, pooled_r_n), 3),
            },
            "fisher_two_sided_p": round(fisher_p, 3),
        },
        "adjudication_robustness_hook": {
            "three_way_agreement_rate": float(e15["summary"]["agreement_three_way"]["rate"]),
            "three_way_kappa": float(e15["summary"]["agreement_three_way"]["cohen_kappa"]),
            "binary_agreement_rate": float(e15["summary"]["agreement_binary_clear_vs_non_clear"]["rate"]),
            "binary_kappa": float(e15["summary"]["agreement_binary_clear_vs_non_clear"]["cohen_kappa"]),
        },
    }

    return {
        "meta": {
            "experiment_id": "E16",
            "name": "Manual-Calibrated Small-Sample Bounds (Cross-Provider API)",
            "generated_at_utc": now_iso(),
            "note": (
                "Uses S14 manual labels for prevalence-oriented bounds and S15 replay agreement "
                "as an adjudication-robustness hook."
            ),
        },
        "models": per_model,
        "summary": summary,
    }


def render_md(payload: Dict[str, object]) -> str:
    s = payload["summary"]["pooled_manual_clear_positive"]
    lines: List[str] = []
    lines.append("# E16 Manual-Calibrated Small-Sample Bounds")
    lines.append("")
    lines.append(f"Generated at: {payload['meta']['generated_at_utc']}")
    lines.append("")
    lines.append(payload["meta"]["note"])
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(
        f"| Pooled vanilla clear positives | {s['vanilla']['k']}/{s['vanilla']['n']} ({s['vanilla']['rate']:.3f}), "
        f"Wilson [{s['vanilla']['wilson_ci95'][0]:.3f}, {s['vanilla']['wilson_ci95'][1]:.3f}] |"
    )
    lines.append(
        f"| Pooled RTG clear positives | {s['rtg']['k']}/{s['rtg']['n']} ({s['rtg']['rate']:.3f}), "
        f"Wilson [{s['rtg']['wilson_ci95'][0]:.3f}, {s['rtg']['wilson_ci95'][1]:.3f}] |"
    )
    lines.append(f"| Pooled RTG one-sided 95% upper bound | {s['rtg']['one_sided_95_upper']:.3f} |")
    lines.append(f"| Fisher exact p (vanilla vs RTG) | {s['fisher_two_sided_p']:.3f} |")
    lines.append("")
    h = payload["summary"]["adjudication_robustness_hook"]
    lines.append("| Adjudication Robustness Hook (from S15) | Value |")
    lines.append("|---|---:|")
    lines.append(f"| 3-way agreement rate | {h['three_way_agreement_rate']:.3f} |")
    lines.append(f"| 3-way kappa | {h['three_way_kappa']:.3f} |")
    lines.append(f"| Binary agreement rate | {h['binary_agreement_rate']:.3f} |")
    lines.append(f"| Binary kappa | {h['binary_kappa']:.3f} |")
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
