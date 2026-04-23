"""
E20: Bayesian posterior sensitivity for pooled manual API counts.

Purpose:
- Quantify low-sample uncertainty under different priors using posterior draws
  on pooled S16 counts (vanilla 1/48, RTG 0/48).

Inputs:
- experiments/results/e16_manual_calibrated_small_sample_bounds.json

Outputs:
- experiments/results/e20_bayesian_posterior_sensitivity.json
- experiments/results/e20_bayesian_posterior_sensitivity.md
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
E16_JSON = RESULTS_DIR / "e16_manual_calibrated_small_sample_bounds.json"
OUT_JSON = RESULTS_DIR / "e20_bayesian_posterior_sensitivity.json"
OUT_MD = RESULTS_DIR / "e20_bayesian_posterior_sensitivity.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def beta_sample(a: float, b: float) -> float:
    x = random.gammavariate(a, 1.0)
    y = random.gammavariate(b, 1.0)
    return x / (x + y)


def posterior_summary(
    v_k: int,
    v_n: int,
    r_k: int,
    r_n: int,
    prior_a: float,
    prior_b: float,
    n_draws: int,
) -> Dict[str, object]:
    a_v = prior_a + v_k
    b_v = prior_b + (v_n - v_k)
    a_r = prior_a + r_k
    b_r = prior_b + (r_n - r_k)

    deltas: List[float] = []
    non_worse = 0
    rope = 0
    rope_eps = 0.02
    for _ in range(n_draws):
        p_v = beta_sample(a_v, b_v)
        p_r = beta_sample(a_r, b_r)
        d = p_r - p_v
        deltas.append(d)
        if d <= 0.0:
            non_worse += 1
        if -rope_eps <= d <= rope_eps:
            rope += 1

    deltas.sort()
    lo = deltas[int(0.025 * n_draws)]
    hi = deltas[int(0.975 * n_draws)]

    return {
        "prior": {"a": prior_a, "b": prior_b},
        "posterior_shapes": {
            "vanilla": {"a": a_v, "b": b_v},
            "rtg": {"a": a_r, "b": b_r},
        },
        "prob_rtg_non_worsening": non_worse / n_draws,
        "prob_delta_in_rope_abs_le_0p02": rope / n_draws,
        "delta_credible_interval_95": [lo, hi],
    }


def build() -> Dict[str, object]:
    e16 = json.loads(E16_JSON.read_text(encoding="utf-8"))
    pooled = e16["summary"]["pooled_manual_clear_positive"]
    v_k = int(pooled["vanilla"]["k"])
    v_n = int(pooled["vanilla"]["n"])
    r_k = int(pooled["rtg"]["k"])
    r_n = int(pooled["rtg"]["n"])

    n_draws = 400000
    seed = 20260412
    random.seed(seed)

    prior_grid: List[Tuple[str, float, float]] = [
        ("uniform_beta_1_1", 1.0, 1.0),
        ("jeffreys_beta_0p5_0p5", 0.5, 0.5),
        ("symmetric_beta_2_2", 2.0, 2.0),
    ]

    rows: Dict[str, object] = {}
    for name, a, b in prior_grid:
        rows[name] = posterior_summary(
            v_k=v_k,
            v_n=v_n,
            r_k=r_k,
            r_n=r_n,
            prior_a=a,
            prior_b=b,
            n_draws=n_draws,
        )

    non_worse_vals = [float(rows[n]["prob_rtg_non_worsening"]) for n, _, _ in prior_grid]
    rope_vals = [float(rows[n]["prob_delta_in_rope_abs_le_0p02"]) for n, _, _ in prior_grid]
    lo_vals = [float(rows[n]["delta_credible_interval_95"][0]) for n, _, _ in prior_grid]
    hi_vals = [float(rows[n]["delta_credible_interval_95"][1]) for n, _, _ in prior_grid]

    return {
        "meta": {
            "experiment_id": "E20",
            "name": "Bayesian Posterior Sensitivity (Pooled Manual API Counts)",
            "generated_at_utc": now_iso(),
            "seed": seed,
            "n_draws_per_prior": n_draws,
            "note": (
                "Posterior sensitivity over three symmetric priors using pooled S16 counts; "
                "delta is defined as RTG rate minus vanilla rate."
            ),
        },
        "base_counts_from_s16": {
            "vanilla": {"k": v_k, "n": v_n},
            "rtg": {"k": r_k, "n": r_n},
        },
        "priors": rows,
        "summary": {
            "prob_rtg_non_worsening_range": [min(non_worse_vals), max(non_worse_vals)],
            "prob_delta_in_rope_abs_le_0p02_range": [min(rope_vals), max(rope_vals)],
            "delta_credible_interval_lower_range": [min(lo_vals), max(lo_vals)],
            "delta_credible_interval_upper_range": [min(hi_vals), max(hi_vals)],
        },
    }


def render_md(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# E20 Bayesian Posterior Sensitivity")
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
    lines.append("| Prior | Pr(RTG <= Vanilla) | Pr(|Delta| <= 0.02) | 95% CrI of Delta (RTG - Vanilla) |")
    lines.append("|---|---:|---:|---:|")
    for key in ["uniform_beta_1_1", "jeffreys_beta_0p5_0p5", "symmetric_beta_2_2"]:
        row = payload["priors"][key]
        lo, hi = row["delta_credible_interval_95"]
        lines.append(
            f"| {key} | "
            f"{row['prob_rtg_non_worsening']:.3f} | "
            f"{row['prob_delta_in_rope_abs_le_0p02']:.3f} | "
            f"[{lo:.3f}, {hi:.3f}] |"
        )
    lines.append("")
    s = payload["summary"]
    lines.append("| Summary | Range |")
    lines.append("|---|---:|")
    lines.append(
        f"| Pr(RTG <= Vanilla) across priors | "
        f"[{s['prob_rtg_non_worsening_range'][0]:.3f}, {s['prob_rtg_non_worsening_range'][1]:.3f}] |"
    )
    lines.append(
        f"| Pr(|Delta| <= 0.02) across priors | "
        f"[{s['prob_delta_in_rope_abs_le_0p02_range'][0]:.3f}, {s['prob_delta_in_rope_abs_le_0p02_range'][1]:.3f}] |"
    )
    lines.append(
        f"| 95% CrI lower bound range | "
        f"[{s['delta_credible_interval_lower_range'][0]:.3f}, {s['delta_credible_interval_lower_range'][1]:.3f}] |"
    )
    lines.append(
        f"| 95% CrI upper bound range | "
        f"[{s['delta_credible_interval_upper_range'][0]:.3f}, {s['delta_credible_interval_upper_range'][1]:.3f}] |"
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
