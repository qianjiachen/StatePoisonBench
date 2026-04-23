#!/usr/bin/env python
"""Generate paper data figures from frozen experiment JSON artifacts.

Usage:
  python scripts/plot_paper_data_figures.py \
    --results-dir experiments/results \
    --out-dir neurips2026_submission/figures \
    --format pdf \
    --dpi 300
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _assert_close(name: str, value: float, expected: float, tol: float = 1e-3) -> None:
    if abs(value - expected) > tol:
        raise ValueError(
            f"{name} mismatch: got {value:.6f}, expected {expected:.6f} (tol={tol})"
        )


def _save_figure(
    fig: plt.Figure,
    out_dir: Path,
    stem: str,
    fmt: str,
    dpi: int,
    write_preview_png: bool,
) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    main_path = out_dir / f"{stem}.{fmt}"
    fig.savefig(main_path, dpi=dpi, bbox_inches="tight")

    preview_path = None
    if write_preview_png and fmt.lower() != "png":
        preview_path = out_dir / f"{stem}.png"
        fig.savefig(preview_path, dpi=dpi, bbox_inches="tight")

    plt.close(fig)
    return {
        "stem": stem,
        "main_output": str(main_path.as_posix()),
        "preview_png": str(preview_path.as_posix()) if preview_path else None,
    }


def _prepare_exp1(data: Dict[str, Any]) -> Tuple[List[str], np.ndarray]:
    order = ["agentdojo", "harmbench", "naive", "statepoison"]
    labels = ["AgentDojo-style", "HarmBench-style", "Naive LLM", "StatePoisonBench"]

    metrics = data["metrics"]
    values = np.array(
        [
            [
                metrics[k]["detection_rate"],
                metrics[k]["false_positive_rate"],
                metrics[k]["f1"],
            ]
            for k in order
        ]
    )

    _assert_close("exp1 statepoison detection_rate", values[3, 0], 0.839)
    _assert_close("exp1 statepoison fpr", values[3, 1], 0.082)
    _assert_close("exp1 statepoison f1", values[3, 2], 0.891)
    return labels, values


def _plot_exp1(labels: List[str], values: np.ndarray) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    metric_names = ["Detection Rate", "False Positive Rate", "F1 Score"]
    notes = ["higher is better", "lower is better", "higher is better"]
    colors = ["#2563eb", "#f59e0b", "#10b981", "#7c3aed"]

    for j, ax in enumerate(axes):
        bars = ax.bar(labels, values[:, j], color=colors, alpha=0.9)
        ax.set_ylim(0, 1.0)
        ax.set_title(f"{metric_names[j]} ({notes[j]})", fontsize=10)
        ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45)
        ax.tick_params(axis="x", rotation=18, labelsize=8)
        ax.tick_params(axis="y", labelsize=8)
        for b in bars:
            h = b.get_height()
            ax.text(
                b.get_x() + b.get_width() / 2,
                h + 0.015,
                f"{h:.3f}",
                ha="center",
                va="bottom",
                fontsize=7,
            )

    fig.suptitle(
        "Experiment 1: Detector Metrics on the Frozen Core Split",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()
    return fig


def _prepare_exp2(data: Dict[str, Any]) -> Tuple[List[str], np.ndarray, np.ndarray]:
    model_order = ["GPT-4o", "Claude-3.5", "Llama-70B", "DeepSeek-V3", "Qwen-72B"]
    summary = data["summary"]
    vanilla = np.array([summary[m]["vanilla"] for m in model_order])
    rtg = np.array([summary[m]["rtg"] for m in model_order])
    improvement = np.array([summary[m]["improvement"] for m in model_order])

    _assert_close("exp2 GPT-4o vanilla", vanilla[0], 0.557)
    _assert_close("exp2 GPT-4o rtg", rtg[0], 0.434)
    _assert_close("exp2 Qwen improvement", improvement[-1], 0.277, tol=2e-3)
    return model_order, vanilla, rtg, improvement


def _plot_exp2(
    model_order: List[str], vanilla: np.ndarray, rtg: np.ndarray, improvement: np.ndarray
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    x = np.arange(len(model_order))
    w = 0.34
    bars_v = ax.bar(x - w / 2, vanilla, width=w, label="Vanilla", color="#ef4444", alpha=0.9)
    bars_r = ax.bar(x + w / 2, rtg, width=w, label="RTG", color="#2563eb", alpha=0.9)

    ax.set_ylabel("Violation Rate", fontsize=9)
    ax.set_ylim(0, 0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(model_order, rotation=15, ha="right", fontsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45)
    ax.legend(fontsize=8, frameon=False)
    ax.set_title("Experiment 2: Cross-Model Scaling (lower is better)", fontsize=10)

    for i, (bv, br, imp) in enumerate(zip(bars_v, bars_r, improvement)):
        y = max(bv.get_height(), br.get_height()) + 0.02
        ax.text(i, y, f"-{imp * 100:.1f}%", ha="center", va="bottom", fontsize=8, color="#374151")

    fig.tight_layout()
    return fig


def _prepare_exp3(data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    turns = np.array(sorted([int(k) for k in data["summary"].keys()]))
    violation = np.array([data["summary"][str(t)]["violation_rate"] for t in turns])
    drift = np.array([data["summary"][str(t)]["avg_cumulative_drift"] for t in turns])
    threshold = float(data["threshold_turn"])

    _assert_close("exp3 turn=1 violation", violation[0], 0.16)
    _assert_close("exp3 turn=50 violation", violation[-1], 0.97)
    _assert_close("exp3 threshold", threshold, 11.654, tol=1e-2)
    return turns, violation, drift, threshold


def _plot_exp3(
    turns: np.ndarray, violation: np.ndarray, drift: np.ndarray, threshold: float
) -> plt.Figure:
    fig, ax1 = plt.subplots(figsize=(8.4, 3.9))
    ax2 = ax1.twinx()

    l1 = ax1.plot(turns, violation, color="#dc2626", marker="o", linewidth=2.2, label="Violation Rate")[0]
    l2 = ax2.plot(
        turns, drift, color="#1d4ed8", marker="s", linewidth=2.0, linestyle="--", label="Avg Cumulative Drift"
    )[0]

    ax1.axvline(threshold, color="#6b7280", linestyle=":", linewidth=1.5)
    ax1.text(threshold + 0.3, 0.08, f"x0≈{threshold:.2f}", fontsize=8, color="#4b5563")

    ax1.set_xlabel("Turns", fontsize=9)
    ax1.set_ylabel("Violation Rate", fontsize=9, color="#dc2626")
    ax2.set_ylabel("Average Cumulative Drift", fontsize=9, color="#1d4ed8")
    ax1.set_ylim(0, 1.02)
    ax2.set_ylim(0, max(drift) * 1.08)
    ax1.set_xticks(turns)
    ax1.tick_params(axis="x", labelsize=8)
    ax1.tick_params(axis="y", labelsize=8, colors="#dc2626")
    ax2.tick_params(axis="y", labelsize=8, colors="#1d4ed8")
    ax1.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45)
    ax1.set_title("Experiment 3: Turn Scaling and Threshold-like Accumulation", fontsize=10)

    ax1.legend([l1, l2], [l1.get_label(), l2.get_label()], fontsize=8, frameon=False, loc="upper left")
    fig.tight_layout()
    return fig


def _prepare_calibration(
    e14: Dict[str, Any], e22: Dict[str, Any], e24: Dict[str, Any], s24: Dict[str, Any]
) -> Dict[str, Any]:
    panel_a = [
        {
            "name": "S14 clear positive",
            "k": int(e14["summary"]["pooled"]["clear_contamination_positive"]),
            "n": int(e14["summary"]["pooled"]["n_total_episodes"]),
        },
        {
            "name": "S21 hidden clear\n(negatives)",
            "k": int(e22["negative_slice_hidden_clear_positives"]["k"]),
            "n": int(e22["negative_slice_hidden_clear_positives"]["n"]),
        },
        {
            "name": "S23 hidden clear\n(negatives)",
            "k": int(e24["negative_slice_hidden_clear"]["k"]),
            "n": int(e24["negative_slice_hidden_clear"]["n"]),
        },
    ]
    for item in panel_a:
        item["rate"] = item["k"] / item["n"] if item["n"] else 0.0

    any_v = s24["paired_summaries"]["any_violation"]
    panel_b = {
        "clean_rate": float(any_v["clean_violation_rate"]),
        "contaminated_rate": float(any_v["contaminated_violation_rate"]),
        "discordant_clean_only": int(any_v["discordant_pairs"]["clean_only_violation"]),
        "discordant_contaminated_only": int(any_v["discordant_pairs"]["contaminated_only_violation"]),
        "n_pairs": int(any_v["n_pairs_completed"]),
        "mcnemar_p": float(any_v["mcnemar_exact_p"]),
    }

    _assert_close("s14 clear positive rate", panel_a[0]["rate"], 1.0 / 304.0, tol=5e-4)
    _assert_close("s21 hidden clear rate", panel_a[1]["rate"], 0.0)
    _assert_close("s23 hidden clear rate", panel_a[2]["rate"], 1.0 / 34.0, tol=5e-4)
    _assert_close("s24 clean any_violation", panel_b["clean_rate"], 0.5)
    _assert_close("s24 contaminated any_violation", panel_b["contaminated_rate"], 0.5)
    return {"panel_a": panel_a, "panel_b": panel_b}


def _plot_calibration(prepared: Dict[str, Any]) -> plt.Figure:
    panel_a = prepared["panel_a"]
    panel_b = prepared["panel_b"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 3.8))

    names = [x["name"] for x in panel_a]
    rates = [x["rate"] for x in panel_a]
    bars = ax1.bar(names, rates, color=["#f97316", "#10b981", "#2563eb"], alpha=0.9)
    ax1.set_ylim(0, max(rates) * 1.4 + 0.005)
    ax1.set_ylabel("Rate", fontsize=9)
    ax1.set_title("Panel A: Calibrated clear/hidden-clear rates", fontsize=10)
    ax1.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45)
    ax1.tick_params(axis="x", labelsize=8)
    ax1.tick_params(axis="y", labelsize=8)

    for b, item in zip(bars, panel_a):
        ax1.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 0.002,
            f"{item['k']}/{item['n']} ({item['rate']:.3f})",
            ha="center",
            va="bottom",
            fontsize=7,
        )

    bar2 = ax2.bar(
        ["Clean", "Contaminated"],
        [panel_b["clean_rate"], panel_b["contaminated_rate"]],
        color=["#22c55e", "#ef4444"],
        alpha=0.9,
    )
    ax2.set_ylim(0, 0.8)
    ax2.set_ylabel("Any-violation rate", fontsize=9)
    ax2.set_title("Panel B: S24 paired starter slice (any_violation)", fontsize=10)
    ax2.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45)
    ax2.tick_params(axis="x", labelsize=8)
    ax2.tick_params(axis="y", labelsize=8)

    for b in bar2:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width() / 2, h + 0.02, f"{h:.3f}", ha="center", fontsize=8)

    ax2.text(
        0.5,
        0.72,
        (
            f"Discordant pairs: clean-only={panel_b['discordant_clean_only']}, "
            f"contaminated-only={panel_b['discordant_contaminated_only']}\n"
            f"n_pairs={panel_b['n_pairs']}, McNemar p={panel_b['mcnemar_p']:.3f}"
        ),
        ha="center",
        va="top",
        fontsize=8,
        transform=ax2.transAxes,
    )

    fig.suptitle(
        "S13–S24 Calibration Snapshot (visualization of reported numbers; non-prevalence)",
        fontsize=11,
        fontweight="bold",
    )
    fig.tight_layout()
    return fig


def _make_manifest(results_dir: Path, output_entries: List[Dict[str, Any]], extracted: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "results_dir": str(results_dir.as_posix()),
        "figures": output_entries,
        "key_values": extracted,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper data figures from result JSON files.")
    parser.add_argument("--results-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--format", choices=["pdf", "png", "svg"], default="pdf")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument(
        "--no-preview-png",
        action="store_true",
        help="Disable extra PNG preview outputs when main format is not PNG.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    results_dir = args.results_dir
    out_dir = args.out_dir
    fmt = args.format.lower()
    preview_png = not args.no_preview_png

    exp1 = _load_json(results_dir / "experiment_1_baseline.json")
    exp2 = _load_json(results_dir / "experiment_2_scaling.json")
    exp3 = _load_json(results_dir / "experiment_3_turns.json")
    e14 = _load_json(results_dir / "e14_cross_provider_manual_audit.json")
    e22 = _load_json(results_dir / "e22_independent_audit_calibration.json")
    e24 = _load_json(results_dir / "e24_single_external_calibration.json")
    s24 = _load_json(
        results_dir
        / "e25_realpaired_new12ai_gpt41mini_6pairs"
        / "e25_real_paired_gpt_4_1_mini_6pairs.json"
    )

    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.titleweight"] = "bold"

    manifest_entries: List[Dict[str, Any]] = []
    extracted: Dict[str, Any] = {}

    exp1_labels, exp1_values = _prepare_exp1(exp1)
    fig = _plot_exp1(exp1_labels, exp1_values)
    manifest_entries.append(
        _save_figure(fig, out_dir, "fig4_exp1_detector_metrics", fmt, args.dpi, preview_png)
    )
    extracted["fig4_exp1_detector_metrics"] = {
        "sources": ["experiment_1_baseline.json"],
        "methods": exp1_labels,
        "metrics": exp1_values.round(6).tolist(),
    }

    model_order, vanilla, rtg, improvement = _prepare_exp2(exp2)
    fig = _plot_exp2(model_order, vanilla, rtg, improvement)
    manifest_entries.append(
        _save_figure(fig, out_dir, "fig5_exp2_model_scaling", fmt, args.dpi, preview_png)
    )
    extracted["fig5_exp2_model_scaling"] = {
        "sources": ["experiment_2_scaling.json"],
        "models": model_order,
        "vanilla": vanilla.round(6).tolist(),
        "rtg": rtg.round(6).tolist(),
        "relative_improvement": improvement.round(6).tolist(),
    }

    turns, violation, drift, threshold = _prepare_exp3(exp3)
    fig = _plot_exp3(turns, violation, drift, threshold)
    manifest_entries.append(
        _save_figure(fig, out_dir, "fig6_exp3_turn_scaling", fmt, args.dpi, preview_png)
    )
    extracted["fig6_exp3_turn_scaling"] = {
        "sources": ["experiment_3_turns.json"],
        "turns": turns.tolist(),
        "violation_rate": violation.round(6).tolist(),
        "avg_cumulative_drift": drift.round(6).tolist(),
        "threshold_turn": round(float(threshold), 6),
    }

    calib = _prepare_calibration(e14, e22, e24, s24)
    fig = _plot_calibration(calib)
    manifest_entries.append(
        _save_figure(fig, out_dir, "figA4_s13_s24_calibration_snapshot", fmt, args.dpi, preview_png)
    )
    extracted["figA4_s13_s24_calibration_snapshot"] = {
        "sources": [
            "e14_cross_provider_manual_audit.json",
            "e22_independent_audit_calibration.json",
            "e24_single_external_calibration.json",
            "e25_realpaired_new12ai_gpt41mini_6pairs/e25_real_paired_gpt_4_1_mini_6pairs.json",
        ],
        "panel_a": calib["panel_a"],
        "panel_b": calib["panel_b"],
    }

    manifest = _make_manifest(results_dir, manifest_entries, extracted)
    manifest_path = out_dir / "fig_data_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(manifest_entries)} figures to {out_dir}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
