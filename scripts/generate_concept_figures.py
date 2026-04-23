from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "figures"
SUBMISSION_FIG_DIR = ROOT / "neurips2026_submission" / "figures"


def add_round_box(
    ax,
    xy,
    width,
    height,
    *,
    fc,
    ec,
    text,
    title_size=22,
    body=None,
    body_size=13,
    ha="center",
    title_weight="bold",
    linewidth=2.4,
    rounding=0.03,
):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0.012,rounding_size={rounding}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=linewidth,
    )
    ax.add_patch(patch)
    tx = x + (0.5 * width if ha == "center" else 0.08 * width)
    ax.text(
        tx,
        y + height * 0.66,
        text,
        fontsize=title_size,
        fontweight=title_weight,
        ha=ha,
        va="center",
        color="#17202A",
    )
    if body:
        ax.text(
            tx,
            y + height * 0.33,
            body,
            fontsize=body_size,
            ha=ha,
            va="center",
            color="#34495E",
            linespacing=1.35,
        )
    return patch


def add_arrow(ax, start, end, *, color="#334155", lw=3.0, style="-|>", mutation=22, ls="-", rad=0.0):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=mutation,
        linewidth=lw,
        color=color,
        linestyle=ls,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(arrow)
    return arrow


def save_figure(fig, *output_paths: Path) -> None:
    for output_path in output_paths:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {"bbox_inches": "tight", "facecolor": fig.get_facecolor()}
        if output_path.suffix.lower() == ".png":
            save_kwargs["dpi"] = 300
        fig.savefig(output_path, **save_kwargs)


def add_ladder_card(
    ax,
    xy,
    width,
    height,
    *,
    accent,
    fill,
    tier,
    title,
    body,
    footer,
    footer_color=None,
    border=None,
    linestyle="-",
    title_size=16.5,
    body_size=10.8,
    footer_size=9.2,
):
    x, y = xy
    shadow = FancyBboxPatch(
        (x + 0.010, y - 0.012),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.028",
        facecolor="#C7D3E3",
        edgecolor="none",
        alpha=0.35,
        zorder=1,
    )
    ax.add_patch(shadow)

    card = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.028",
        facecolor=fill,
        edgecolor=border or "#CBD5E1",
        linewidth=1.6,
        linestyle=linestyle,
        zorder=2,
    )
    ax.add_patch(card)

    ax.add_patch(
        FancyBboxPatch(
            (x + width * 0.030, y + height * 0.085),
            width * 0.020,
            height * 0.83,
            boxstyle="round,pad=0.0,rounding_size=0.008",
            facecolor=accent,
            edgecolor=accent,
            linewidth=0,
            zorder=3,
        )
    )

    badge_w = width * 0.18
    badge_h = height * 0.14
    badge_x = x + width * 0.075
    badge_y = y + height * 0.73
    ax.add_patch(
        FancyBboxPatch(
            (badge_x, badge_y),
            badge_w,
            badge_h,
            boxstyle="round,pad=0.010,rounding_size=0.016",
            facecolor=accent,
            edgecolor=accent,
            linewidth=0,
            zorder=4,
        )
    )
    ax.text(
        badge_x + badge_w / 2,
        badge_y + badge_h / 2,
        tier,
        fontsize=10.2,
        fontweight="bold",
        ha="center",
        va="center",
        color="white",
        zorder=5,
    )

    tx = x + width * 0.11
    ax.text(
        tx,
        y + height * 0.56,
        title,
        fontsize=title_size,
        fontweight="bold",
        ha="left",
        va="center",
        color="#0F172A",
        zorder=5,
    )
    ax.text(
        tx,
        y + height * 0.29,
        body,
        fontsize=body_size,
        ha="left",
        va="center",
        color="#334155",
        linespacing=1.35,
        zorder=5,
    )
    ax.text(
        tx,
        y + height * 0.10,
        footer,
        fontsize=footer_size,
        fontweight="bold",
        ha="left",
        va="center",
        color=footer_color or accent,
        zorder=5,
    )
    return card


def draw_persistent_state_pipeline(*output_paths: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Aptos", "Segoe UI", "DejaVu Sans"],
            "font.size": 12,
        }
    )
    fig, ax = plt.subplots(figsize=(14.2, 8.6), dpi=220)
    fig.patch.set_facecolor("#FCFDFE")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.50,
        0.95,
        "Persistent State Contamination in Long-Horizon Agents",
        ha="center",
        va="center",
        fontsize=28,
        fontweight="bold",
        color="#111827",
    )

    panel_style = dict(boxstyle="round,pad=0.012,rounding_size=0.03", linewidth=1.2, edgecolor="#E2E8F0")
    left_panel = FancyBboxPatch((0.05, 0.10), 0.27, 0.72, facecolor="#F3F8FC", **panel_style)
    mid_panel = FancyBboxPatch((0.39, 0.10), 0.25, 0.72, facecolor="#FCFAEF", **panel_style)
    right_panel = FancyBboxPatch((0.72, 0.10), 0.23, 0.72, facecolor="#F7F7FB", **panel_style)
    for panel in (left_panel, mid_panel, right_panel):
        ax.add_patch(panel)

    ax.text(0.185, 0.85, "State Artifacts", ha="center", va="center", fontsize=20, fontweight="bold", color="#111827")
    ax.text(0.515, 0.85, "Recovery Window", ha="center", va="center", fontsize=20, fontweight="bold", color="#111827")
    ax.text(0.835, 0.85, "Downstream Actions", ha="center", va="center", fontsize=20, fontweight="bold", color="#111827")

    artifact_boxes = [
        ((0.085, 0.64), 0.09, 0.09, "summary"),
        ((0.185, 0.64), 0.09, 0.09, "tracker"),
        ((0.135, 0.50), 0.13, 0.09, "recovery note"),
        ((0.125, 0.37), 0.15, 0.08, "session state"),
        ((0.10, 0.18), 0.20, 0.10, "historical / compacted\ncontext"),
    ]
    for (x, y), w, h, text in artifact_boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.010,rounding_size=0.02",
                facecolor="#E8F5E9",
                edgecolor="#0F4C5C",
                linewidth=2.0,
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=15, color="#111827")

    workflow_boxes = [
        ((0.45, 0.65), 0.14, 0.09, "state restore"),
        ((0.45, 0.49), 0.14, 0.09, "plan / use tools"),
        ((0.45, 0.33), 0.14, 0.09, "decide"),
    ]
    for (x, y), w, h, text in workflow_boxes:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.010,rounding_size=0.02",
                facecolor="#F3FAFF",
                edgecolor="#0F4C5C",
                linewidth=2.0,
            )
        )
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=16, color="#111827")

    add_arrow(ax, (0.32, 0.50), (0.39, 0.50), color="#123B4A", lw=3.0, mutation=24)
    add_arrow(ax, (0.52, 0.65), (0.52, 0.58), color="#123B4A", lw=2.8, mutation=22)
    add_arrow(ax, (0.52, 0.49), (0.52, 0.42), color="#123B4A", lw=2.8, mutation=22)

    ax.text(0.515, 0.12, "resume-sensitive window", ha="center", va="center", fontsize=16, color="#111827")

    top_box = FancyBboxPatch(
        (0.765, 0.66),
        0.14,
        0.09,
        boxstyle="round,pad=0.010,rounding_size=0.02",
        facecolor="#EEE7F8",
        edgecolor="#6B3FA0",
        linewidth=2.0,
    )
    ax.add_patch(top_box)
    ax.text(0.835, 0.705, "tool call /\nreplanning", ha="center", va="center", fontsize=15, color="#111827")

    trusted_write = FancyBboxPatch(
        (0.745, 0.47),
        0.13,
        0.09,
        boxstyle="round,pad=0.010,rounding_size=0.02",
        facecolor="#EEE7F8",
        edgecolor="#6B3FA0",
        linewidth=2.0,
    )
    auth_action = FancyBboxPatch(
        (0.805, 0.32),
        0.12,
        0.11,
        boxstyle="round,pad=0.010,rounding_size=0.02",
        facecolor="#FFF3E6",
        edgecolor="#D97706",
        linewidth=2.0,
    )
    risk_box = FancyBboxPatch(
        (0.755, 0.14),
        0.16,
        0.10,
        boxstyle="round,pad=0.010,rounding_size=0.02",
        facecolor="#FEECEC",
        edgecolor="#D11A1A",
        linewidth=2.0,
    )
    for patch in (trusted_write, auth_action, risk_box):
        ax.add_patch(patch)

    ax.text(0.81, 0.515, "trusted write", ha="center", va="center", fontsize=16, color="#111827")
    ax.text(0.865, 0.375, "authorization-sensitive\naction", ha="center", va="center", fontsize=14.4, color="#111827")
    ax.text(0.835, 0.19, "possible\nboundary violation", ha="center", va="center", fontsize=16, color="#111827")

    add_arrow(ax, (0.64, 0.50), (0.72, 0.50), color="#123B4A", lw=3.0, mutation=24)
    add_arrow(ax, (0.835, 0.66), (0.81, 0.56), color="#123B4A", lw=2.6, mutation=21)
    add_arrow(ax, (0.835, 0.66), (0.865, 0.43), color="#123B4A", lw=2.6, mutation=21)
    add_arrow(ax, (0.81, 0.47), (0.835, 0.24), color="#123B4A", lw=2.6, mutation=21)
    add_arrow(ax, (0.865, 0.32), (0.84, 0.24), color="#123B4A", lw=2.6, mutation=21)

    fig.tight_layout(pad=0.25)
    save_figure(fig, *output_paths)
    plt.close(fig)


def draw_evidence_ladder(*output_paths: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Aptos", "Segoe UI", "DejaVu Sans"],
            "font.size": 12,
        }
    )
    fig, ax = plt.subplots(figsize=(13.8, 6.6), dpi=220)
    fig.patch.set_facecolor("#FCFDFE")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.add_patch(
        FancyBboxPatch(
            (0.06, 0.885),
            0.88,
            0.075,
            boxstyle="round,pad=0.010,rounding_size=0.020",
            facecolor="#F4F7FB",
            edgecolor="#D5DEEA",
            linewidth=1.2,
            zorder=1,
        )
    )
    ax.text(
        0.50,
        0.922,
        "Interpretation boundary: realism increases downstream, but headline quantitative claims stay anchored in Tier 1.",
        ha="center",
        va="center",
        fontsize=12.2,
        color="#334155",
        zorder=2,
    )

    add_arrow(
        ax,
        (0.18, 0.20),
        (0.86, 0.78),
        color="#D9E1EC",
        lw=18.0,
        mutation=26,
    )

    core = {"fill": "#EDF4FB", "edge": "#2F5D8C"}
    bridge = {"fill": "#FFF5E8", "edge": "#C5871E"}
    calib = {"fill": "#EEF6F0", "edge": "#547C5B"}
    note = {"fill": "#F6F8FA", "edge": "#73808C"}

    add_ladder_card(
        ax,
        (0.08, 0.16),
        0.35,
        0.24,
        accent=core["edge"],
        fill=core["fill"],
        tier="TIER 1",
        title="Controlled synthetic core",
        body="Experiments 1--3, S1--S7\nFrozen benchmark semantics\nMain support for C1--C3",
        footer="main evidence",
    )
    add_ladder_card(
        ax,
        (0.34, 0.40),
        0.33,
        0.23,
        accent=bridge["edge"],
        fill=bridge["fill"],
        tier="TIER 2",
        title="Near-positive bridge",
        body="S10--S12 bridge proper\nS8--S9 appendix support\nStrengthens realism linkage",
        footer="bridge only",
    )
    add_ladder_card(
        ax,
        (0.58, 0.62),
        0.31,
        0.23,
        accent=calib["edge"],
        fill=calib["fill"],
        tier="TIER 3",
        title="Real-trace calibration",
        body="S13--S23 audit packet\nBounds over-flagging and hidden misses\nNo prevalence claims",
        footer="calibration only",
    )

    add_arrow(ax, (0.43, 0.36), (0.48, 0.48), color=core["edge"], lw=2.8, mutation=21)
    add_arrow(ax, (0.67, 0.60), (0.72, 0.71), color=bridge["edge"], lw=2.8, mutation=21)

    ax.text(0.09, 0.10, "More controlled\nmore claim-carrying", fontsize=10.0, color=core["edge"], ha="left", va="top")
    ax.text(0.88, 0.58, "More real-grounded\nmore calibration-oriented", fontsize=10.0, color=calib["edge"], ha="right", va="center")

    add_ladder_card(
        ax,
        (0.68, 0.29),
        0.22,
        0.16,
        accent=note["edge"],
        fill=note["fill"],
        tier="S24",
        title="Prospective starter slice",
        body="Protocol-validating\nCurrently non-separating",
        footer="protocol disclosure",
        footer_color="#52606D",
        border="#C9D2DC",
        linestyle="--",
        title_size=15.2,
        body_size=10.2,
        footer_size=8.8,
    )
    add_arrow(ax, (0.67, 0.47), (0.69, 0.38), color="#8C98A5", lw=2.0, mutation=18, ls="--", rad=-0.14)

    fig.tight_layout(pad=0.25)
    save_figure(fig, *output_paths)
    plt.close(fig)


def draw_calibration_ladder(output_path: Path) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
        }
    )
    fig, ax = plt.subplots(figsize=(14, 7.8), dpi=220)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(
        0.5,
        0.955,
        "Calibration Ladder for Supplementary Real Grounding",
        ha="center",
        va="center",
        fontsize=28,
        fontweight="bold",
        color="#111827",
    )
    ax.text(
        0.5,
        0.913,
        "Retrospective packets tighten interpretation; the prospective slice checks whether the live protocol runs cleanly.",
        ha="center",
        va="center",
        fontsize=14.2,
        color="#475569",
    )

    blue = {"fill": "#E8F1FF", "edge": "#2563EB"}
    teal = {"fill": "#E8F8F5", "edge": "#0F766E"}
    amber = {"fill": "#FFF4E5", "edge": "#D97706"}
    rose = {"fill": "#FEF2F2", "edge": "#DC2626"}
    gray = {"fill": "#F8FAFC", "edge": "#64748B"}

    add_round_box(
        ax,
        (0.07, 0.20),
        0.24,
        0.22,
        fc=blue["fill"],
        ec=blue["edge"],
        text="Retrospective Base",
        title_size=21,
        body="S13 automatic stress checks\nS14--S15 manual calibration\nS16--S19 bounds / sensitivity checks\n\nQuestion: how unstable are the low-rate retrospective counts?",
        body_size=11.0,
    )
    add_round_box(
        ax,
        (0.36, 0.38),
        0.24,
        0.22,
        fc=teal["fill"],
        ec=teal["edge"],
        text="Negative-Side Tightening",
        title_size=20,
        body="S20--S21 targeted and blind audits\nS22 detector-decoupled boundary check\n\nQuestion: what hidden-miss risk remains?",
        body_size=12.0,
    )
    add_round_box(
        ax,
        (0.65, 0.56),
        0.21,
        0.20,
        fc=amber["fill"],
        ec=amber["edge"],
        text="Expanded External Packet",
        title_size=19,
        body="S23 single-external packet\nCombines flagged and audited negatives\n\nUse for calibrated interpretation only",
        body_size=11.5,
    )
    add_round_box(
        ax,
        (0.78, 0.21),
        0.16,
        0.16,
        fc=rose["fill"],
        ec=rose["edge"],
        text="Prospective S24",
        title_size=17.5,
        body="Live paired continuation probe\nExecution-validating; currently non-separating",
        body_size=10.8,
        linewidth=2.2,
    )

    add_arrow(ax, (0.31, 0.31), (0.36, 0.47), color=blue["edge"], lw=3.2, mutation=24)
    add_arrow(ax, (0.60, 0.49), (0.65, 0.65), color=teal["edge"], lw=3.2, mutation=24)
    add_arrow(ax, (0.74, 0.56), (0.84, 0.37), color="#7C3E00", lw=2.6, mutation=22, ls="--", rad=-0.2)

    ax.text(0.22, 0.16, "retrospective", fontsize=12.5, color=blue["edge"], fontweight="bold", ha="center")
    ax.text(0.48, 0.34, "tighter negative-side bounds", fontsize=12.5, color=teal["edge"], fontweight="bold", ha="center")
    ax.text(0.75, 0.81, "stronger external calibration", fontsize=12.5, color=amber["edge"], fontweight="bold", ha="center")
    ax.text(0.86, 0.18, "prospective probe", fontsize=11.8, color=rose["edge"], fontweight="bold", ha="center")

    add_round_box(
        ax,
        (0.08, 0.74),
        0.36,
        0.09,
        fc=gray["fill"],
        ec="#CBD5E1",
        text="Interpretation Boundary",
        title_size=16.5,
        body="These studies calibrate over-flagging / hidden-miss uncertainty and protocol viability; they are not prevalence estimates.",
        body_size=11.2,
        linewidth=1.8,
        rounding=0.02,
    )
    add_arrow(ax, (0.45, 0.785), (0.63, 0.785), color="#64748B", lw=2.0, mutation=18)

    ax.plot([0.09, 0.84], [0.11, 0.11], color="#94A3B8", linewidth=2.0)
    ax.text(0.09, 0.065, "Retrospective calibration ladder", fontsize=11.3, color="#334155", ha="left")
    ax.text(0.84, 0.065, "Prospective protocol probe", fontsize=11.3, color="#334155", ha="right")

    fig.tight_layout(pad=0.4)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    SUBMISSION_FIG_DIR.mkdir(parents=True, exist_ok=True)
    draw_persistent_state_pipeline(
        FIG_DIR / "figure1.png",
        SUBMISSION_FIG_DIR / "fig_pipeline.png",
        SUBMISSION_FIG_DIR / "fig_pipeline.pdf",
    )
    draw_evidence_ladder(
        FIG_DIR / "figure2.png",
        SUBMISSION_FIG_DIR / "fig_evidence_ladder.png",
        SUBMISSION_FIG_DIR / "fig_evidence_ladder.pdf",
    )
    draw_calibration_ladder(FIG_DIR / "figure6.png")


if __name__ == "__main__":
    main()
