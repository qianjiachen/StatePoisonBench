"""
Check table-to-artifact numeric consistency for the NeurIPS draft.

Writes:
- experiments/results/table_artifact_consistency_report.md
- experiments/results/table_artifact_consistency_report.json
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"
MAIN_TEX = ROOT / "neurips2026_submission" / "main.tex"

REPORT_MD = RESULTS_DIR / "table_artifact_consistency_report.md"
REPORT_JSON = RESULTS_DIR / "table_artifact_consistency_report.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def nearly_equal(a: float, b: float, tol: float = 5e-4) -> bool:
    return abs(a - b) <= tol


def parse_latex_number(value: str) -> float:
    value = value.strip()
    sci = re.fullmatch(r"([0-9.]+)\\times10\^\{(-?[0-9]+)\}", value)
    if sci:
        return float(sci.group(1)) * (10 ** int(sci.group(2)))
    return float(value)


def normalize_for_compare(value: float) -> float:
    if value == 0.0:
        return 0.0
    if abs(value) < 1e-3:
        return float(f"{value:.2e}")
    return round(value, 3)


def fmt_value(value: float) -> str:
    if abs(value) < 1e-3 and value != 0.0:
        return f"{value:.2e}"
    return f"{value:.3f}"


def read_expanded_tex(path: Path, seen: set[Path] | None = None) -> str:
    r"""Read a LaTeX file and inline local \input/\include files for parsing."""
    resolved = path.resolve()
    if seen is None:
        seen = set()
    if resolved in seen:
        return ""
    seen.add(resolved)

    text = resolved.read_text(encoding="utf-8")
    base_dir = resolved.parent

    def replace_include(match: re.Match[str]) -> str:
        raw = match.group(1).strip()
        child = base_dir / raw
        if child.suffix == "":
            child = child.with_suffix(".tex")
        if not child.exists():
            return match.group(0)
        expanded = read_expanded_tex(child, seen)
        return f"\n% BEGIN expanded {raw}\n{expanded}\n% END expanded {raw}\n"

    return re.sub(r"\\(?:input|include)\{([^}]+)\}", replace_include, text)


def parse_main_tables(text: str) -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}

    # Experiment 1 baseline table
    e1 = {}
    for method, det, fp, f1 in re.findall(
        r"(AgentDojo-style detection|HarmBench-style detection|Naive LLM query|\\textbf\{StatePoisonBench \(ours\)\})\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*\\\\",
        text,
    ):
        key = method.replace("\\textbf{", "").replace("}", "")
        e1[f"{key}.detection_rate"] = float(det)
        e1[f"{key}.false_positive_rate"] = float(fp)
        e1[f"{key}.f1"] = float(f1)
    out["exp1"] = e1

    # Experiment 2 model scaling table
    e2 = {}
    for model, v, r in re.findall(
        r"(GPT-4o|Claude-3\.5-Sonnet|Llama-3\.1-70B|DeepSeek-V3|Qwen2\.5-72B)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*[0-9.]+\\%\s*\\\\",
        text,
    ):
        e2[f"{model}.vanilla"] = float(v)
        e2[f"{model}.rtg"] = float(r)
    out["exp2"] = e2

    # Experiment 3 turn table
    e3 = {}
    for turns, v, drift in re.findall(r"^(\d+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*\\\\", text, flags=re.MULTILINE):
        t = int(turns)
        if t in {1, 3, 5, 10, 20, 50}:
            e3[f"{t}.violation_rate"] = float(v)
            e3[f"{t}.avg_drift"] = float(drift)
    out["exp3"] = e3

    # S1 overall
    s1 = {}
    m = re.search(
        r"\\textbf\{Overall\}\s*&\s*\\textbf\{([0-9.]+)\}\s*&\s*\\textbf\{([0-9.]+)\}\s*&\s*\\textbf\{([0-9.]+)\}",
        text,
    )
    if m:
        s1["clean_rate"] = float(m.group(1))
        s1["contaminated_rate"] = float(m.group(2))
        s1["delta"] = float(m.group(3))
    out["s1"] = s1

    # S2 tau=0.50
    s2 = {}
    m = re.search(r"RTG \(\$\\tau=0\.50\$\)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)", text)
    if m:
        s2["violation_rate"] = float(m.group(1))
        s2["success_rate"] = float(m.group(2))
        s2["avg_confirmations"] = float(m.group(3))
    out["s2"] = s2

    # S10 near-positive paired replay
    s10 = {}
    s10_pattern = re.compile(
        r"^(Recovered-context write|Recovery-state poisoning|\\textbf\{Overall\})\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)(?:\})?\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)(?:\})?\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)(?:\})?\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)(?:\})?\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)(?:\})?\s*&\s*"
        r"(?:\\textbf\{)?\$?([0-9.]+(?:\\times10\^\{-?[0-9]+\})?)\$?(?:\})?\s*\\\\",
        flags=re.MULTILINE,
    )
    for fam, clean_v, cont_v, delta, clean_hit, cont_hit, pval in s10_pattern.findall(text):
        fam_key = "overall" if "Overall" in fam else fam.lower().replace("-", "_").replace(" ", "_")
        s10[f"{fam_key}.violation_rate.clean"] = float(clean_v)
        s10[f"{fam_key}.violation_rate.contaminated"] = float(cont_v)
        s10[f"{fam_key}.paired_delta"] = float(delta)
        s10[f"{fam_key}.state_propagation_hit.clean"] = float(clean_hit)
        s10[f"{fam_key}.state_propagation_hit.contaminated"] = float(cont_hit)
        s10[f"{fam_key}.mcnemar_p"] = parse_latex_number(pval)
    out["s10"] = s10

    # S11 open-weight consolidation table
    s11_open = {}
    s11_open_pattern = re.compile(
        r"^(Qwen2\.5-32B|Qwen2\.5-14B)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*"
        r"\[(-?[0-9.]+),\s*(-?[0-9.]+)\]\s*&\s*([0-9.]+)\s*\\\\",
        flags=re.MULTILINE,
    )
    for model, v_mean, r_mean, consistency, eff_min, eff_max, std_tpl in s11_open_pattern.findall(text):
        key = model.lower().replace(".", "_").replace("-", "_")
        s11_open[f"{key}.vanilla_mean"] = float(v_mean)
        s11_open[f"{key}.rtg_mean"] = float(r_mean)
        s11_open[f"{key}.direction_consistency"] = float(consistency)
        s11_open[f"{key}.effect_range_min"] = float(eff_min)
        s11_open[f"{key}.effect_range_max"] = float(eff_max)
        s11_open[f"{key}.std_across_templates"] = float(std_tpl)
    out["s11_open"] = s11_open

    # S11 API spot-check table
    s11_api = {}
    s11_api_pattern = re.compile(
        r"^(gpt-5\.4-mini|gpt-5\.1-Codex-mini|gpt-5\.1-Codex-max)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*\\\\",
        flags=re.MULTILINE,
    )
    for model, vf, rf, vc, rc in s11_api_pattern.findall(text):
        key = model.lower().replace(".", "_").replace("-", "_")
        s11_api[f"{key}.vanilla_failure_rate"] = float(vf)
        s11_api[f"{key}.rtg_failure_rate"] = float(rf)
        s11_api[f"{key}.vanilla_completion_rate"] = float(vc)
        s11_api[f"{key}.rtg_completion_rate"] = float(rc)
    out["s11_api"] = s11_api

    # S12 uncertainty (S10 deltas)
    s12_s10 = {}
    s12_s10_pattern = re.compile(
        r"^(Recovered-context write|Recovery-state poisoning|\\textbf\{Overall\})\s*&\s*(?:\\textbf\{)?(\d+)(?:\})?\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)\s*\[([0-9.]+),\s*([0-9.]+)\](?:\})?\s*&\s*"
        r"(?:\\textbf\{)?([0-9.]+)\s*\[([0-9.]+),\s*([0-9.]+)\](?:\})?\s*\\\\",
        flags=re.MULTILINE,
    )
    for fam, n_pairs, v_pt, v_lo, v_hi, p_pt, p_lo, p_hi in s12_s10_pattern.findall(text):
        fam_key = "overall" if "Overall" in fam else fam.lower().replace("-", "_").replace(" ", "_")
        s12_s10[f"{fam_key}.n_pairs"] = float(n_pairs)
        s12_s10[f"{fam_key}.violation_delta.point"] = float(v_pt)
        s12_s10[f"{fam_key}.violation_delta.ci_lo"] = float(v_lo)
        s12_s10[f"{fam_key}.violation_delta.ci_hi"] = float(v_hi)
        s12_s10[f"{fam_key}.state_prop_delta.point"] = float(p_pt)
        s12_s10[f"{fam_key}.state_prop_delta.ci_lo"] = float(p_lo)
        s12_s10[f"{fam_key}.state_prop_delta.ci_hi"] = float(p_hi)
    out["s12_s10"] = s12_s10

    # S12 uncertainty (S11 bounds)
    s12_s11 = {}
    m = re.search(
        r"Qwen2\.5-32B non-worsening runs\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*&\s*Wilson CI \[([0-9.]+),\s*([0-9.]+)\]",
        text,
    )
    if m:
        s12_s11["qwen32.k"] = float(m.group(1))
        s12_s11["qwen32.n"] = float(m.group(2))
        s12_s11["qwen32.consistency"] = float(m.group(3))
        s12_s11["qwen32.ci_lo"] = float(m.group(4))
        s12_s11["qwen32.ci_hi"] = float(m.group(5))
    m = re.search(
        r"Qwen2\.5-14B non-worsening runs\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*&\s*Wilson CI \[([0-9.]+),\s*([0-9.]+)\]",
        text,
    )
    if m:
        s12_s11["qwen14.k"] = float(m.group(1))
        s12_s11["qwen14.n"] = float(m.group(2))
        s12_s11["qwen14.consistency"] = float(m.group(3))
        s12_s11["qwen14.ci_lo"] = float(m.group(4))
        s12_s11["qwen14.ci_hi"] = float(m.group(5))
    m = re.search(
        r"\\textbf\{Open-weight pooled\}\s*&\s*\\textbf\{(\d+)/(\d+)\s*\(([0-9.]+)\)\}\s*&\s*\\textbf\{Wilson CI \[([0-9.]+),\s*([0-9.]+)\]\}",
        text,
    )
    if m:
        s12_s11["open_overall.k"] = float(m.group(1))
        s12_s11["open_overall.n"] = float(m.group(2))
        s12_s11["open_overall.consistency"] = float(m.group(3))
        s12_s11["open_overall.ci_lo"] = float(m.group(4))
        s12_s11["open_overall.ci_hi"] = float(m.group(5))
    m = re.search(
        r"API per-model clear failures \(vanilla/RTG\)\s*&\s*0/12,\s*0/12\s*&\s*One-sided upper bound ([0-9.]+)",
        text,
    )
    if m:
        s12_s11["api_per_model.upper"] = float(m.group(1))
    m = re.search(
        r"\\textbf\{API pooled clear failures \(vanilla/RTG\)\}\s*&\s*\\textbf\{0/36,\s*0/36\}\s*&\s*\\textbf\{One-sided upper bound ([0-9.]+)\}",
        text,
    )
    if m:
        s12_s11["api_pooled.upper"] = float(m.group(1))
    out["s12_s11"] = s12_s11

    # S13 cross-provider API stress check
    s13 = {}
    s13_model_pattern = re.compile(
        r"^(claude-haiku-4-5-20251001|claude-sonnet-4-5-20250929|deepseek-v3\.2|gemini-2\.5-flash)\s*&\s*"
        r"([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*(\$?-?[0-9.]+\$?)\s*&\s*(Yes|No)\s*\\\\",
        flags=re.MULTILINE,
    )
    for model, v_vio, r_vio, delta, nw in s13_model_pattern.findall(text):
        key = model.lower().replace(".", "_").replace("-", "_")
        s13[f"{key}.vanilla_violation_rate"] = float(v_vio)
        s13[f"{key}.rtg_violation_rate"] = float(r_vio)
        s13[f"{key}.delta"] = float(delta.replace("$", ""))
        s13[f"{key}.non_worsening"] = 1.0 if nw == "Yes" else 0.0
    m = re.search(
        r"\\textbf\{Overall direction\}\s*&\s*\\multicolumn\{4\}\{c\}\{\\textbf\{(\d+)/(\d+)\s*non-worsening\s*\(([0-9.]+)\),\s*Wilson 95\\% CI \[([0-9.]+),\s*([0-9.]+)\]\}\}",
        text,
    )
    if m:
        s13["overall.k"] = float(m.group(1))
        s13["overall.n"] = float(m.group(2))
        s13["overall.rate"] = float(m.group(3))
        s13["overall.ci_lo"] = float(m.group(4))
        s13["overall.ci_hi"] = float(m.group(5))
    out["s13"] = s13

    # S14 manual-audit calibration for S13 auto flags
    s14 = {}
    # S14 table appears in both 6-column (no ambiguous column) and
    # 7-column (with ambiguous column) variants across draft revisions.
    s14_model_pattern = re.compile(
        r"^(claude-haiku-4-5-20251001|claude-sonnet-4-5-20250929|deepseek-v3\.2|gemini-2\.5-flash)\s*&\s*"
        r"(\d+)/(\d+)\s*&\s*(\d+)\s*&\s*(\d+)\s*&\s*(?:(\d+)\s*&\s*)?([0-9.]+)\s*&\s*([0-9.]+)\s*\\\\",
        flags=re.MULTILINE,
    )
    for model, fk, fn, clear_pos, fp_benign, ambiguous, v_clear, r_clear in s14_model_pattern.findall(text):
        key = model.lower().replace(".", "_").replace("-", "_")
        s14[f"{key}.auto_flagged.k"] = float(fk)
        s14[f"{key}.auto_flagged.n"] = float(fn)
        s14[f"{key}.clear_positive"] = float(clear_pos)
        s14[f"{key}.fp_or_benign"] = float(fp_benign)
        if ambiguous:
            s14[f"{key}.ambiguous"] = float(ambiguous)
        s14[f"{key}.vanilla_clear_rate"] = float(v_clear)
        s14[f"{key}.rtg_clear_rate"] = float(r_clear)
    m = re.search(
        r"\\textbf\{Overall\}\s*&\s*\\textbf\{(\d+)/(\d+)\}\s*&\s*\\textbf\{(\d+)\}\s*&\s*\\textbf\{(\d+)\}\s*&\s*(?:\\textbf\{(\d+)\}\s*&\s*)?\\textbf\{([0-9.]+)\}\s*&\s*\\textbf\{([0-9.]+)\}",
        text,
    )
    if m:
        s14["overall.auto_flagged.k"] = float(m.group(1))
        s14["overall.auto_flagged.n"] = float(m.group(2))
        s14["overall.clear_positive"] = float(m.group(3))
        s14["overall.fp_or_benign"] = float(m.group(4))
        if m.group(5):
            s14["overall.ambiguous"] = float(m.group(5))
        s14["overall.vanilla_clear_rate"] = float(m.group(6))
        s14["overall.rtg_clear_rate"] = float(m.group(7))
    m = re.search(
        r"Auto-flag precision for clear positives is \$([0-9]+)/([0-9]+)=([0-9.]+)\$",
        text,
    )
    if m:
        s14["precision.k"] = float(m.group(1))
        s14["precision.n"] = float(m.group(2))
        s14["precision.rate"] = float(m.group(3))
    m = re.search(
        r"Manual-label direction non-worsening is \$([0-9]+)/([0-9]+)=([0-9.]+)\$ "
        r"\(Wilson 95\\% CI \$\[([0-9.]+),\s*([0-9.]+)\]\$\)",
        text,
    )
    if m:
        s14["direction.k"] = float(m.group(1))
        s14["direction.n"] = float(m.group(2))
        s14["direction.rate"] = float(m.group(3))
        s14["direction.ci_lo"] = float(m.group(4))
        s14["direction.ci_hi"] = float(m.group(5))
    out["s14"] = s14

    # S15 dual-rubric replay robustness
    s15 = {}
    m = re.search(r"Audited auto-flagged episodes\s*&\s*(\d+)\s*\\\\", text)
    if m:
        s15["n_audited"] = float(m.group(1))
    m = re.search(r"3-way exact agreement\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*\\\\", text)
    if m:
        s15["agreement3.k"] = float(m.group(1))
        s15["agreement3.n"] = float(m.group(2))
        s15["agreement3.rate"] = float(m.group(3))
    m = re.search(r"3-way Cohen's \$\\kappa\$\s*&\s*([0-9.]+)\s*\\\\", text)
    if m:
        s15["agreement3.kappa"] = float(m.group(1))
    m = re.search(r"Binary agreement \(clear vs non-clear\)\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*\\\\", text)
    if m:
        s15["agreement_bin.k"] = float(m.group(1))
        s15["agreement_bin.n"] = float(m.group(2))
        s15["agreement_bin.rate"] = float(m.group(3))
    m = re.search(r"Binary Cohen's \$\\kappa\$\s*&\s*([0-9.]+)\s*\\\\", text)
    if m:
        s15["agreement_bin.kappa"] = float(m.group(1))
    m = re.search(r"Primary clear positives\s*&\s*(\d+)\s*\\\\", text)
    if m:
        s15["clear.primary"] = float(m.group(1))
    m = re.search(r"Replay clear positives\s*&\s*(\d+)\s*\\\\", text)
    if m:
        s15["clear.replay"] = float(m.group(1))
    out["s15"] = s15

    # S16 manual-calibrated small-sample bounds
    s16 = {}
    m = re.search(
        r"Pooled vanilla clear-positive rate \(k/n\)\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\),\s*Wilson\s*\[([0-9.]+),\s*([0-9.]+)\]\s*\\\\",
        text,
    )
    if m:
        s16["vanilla.k"] = float(m.group(1))
        s16["vanilla.n"] = float(m.group(2))
        s16["vanilla.rate"] = float(m.group(3))
        s16["vanilla.ci_lo"] = float(m.group(4))
        s16["vanilla.ci_hi"] = float(m.group(5))
    m = re.search(
        r"Pooled RTG clear-positive rate \(k/n\)\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\),\s*Wilson\s*\[([0-9.]+),\s*([0-9.]+)\]\s*\\\\",
        text,
    )
    if m:
        s16["rtg.k"] = float(m.group(1))
        s16["rtg.n"] = float(m.group(2))
        s16["rtg.rate"] = float(m.group(3))
        s16["rtg.ci_lo"] = float(m.group(4))
        s16["rtg.ci_hi"] = float(m.group(5))
    m = re.search(r"Pooled RTG one-sided 95\\% upper bound\s*&\s*([0-9.]+)\s*\\\\", text)
    if m:
        s16["rtg.one_sided_upper"] = float(m.group(1))
    m = re.search(r"Fisher exact \$p\$ \(vanilla vs RTG\)\s*&\s*([0-9.]+)\s*\\\\", text)
    if m:
        s16["fisher_p"] = float(m.group(1))
    m = re.search(r"S15 3-way agreement / \$\\kappa\$\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\),\s*([0-9.]+)\s*\\\\", text)
    if m:
        s16["s15_threeway.k"] = float(m.group(1))
        s16["s15_threeway.n"] = float(m.group(2))
        s16["s15_threeway.rate"] = float(m.group(3))
        s16["s15_threeway.kappa"] = float(m.group(4))
    m = re.search(r"S15 binary agreement / \$\\kappa\$\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\),\s*([0-9.]+)\s*\\\\", text)
    if m:
        s16["s15_binary.k"] = float(m.group(1))
        s16["s15_binary.n"] = float(m.group(2))
        s16["s15_binary.rate"] = float(m.group(3))
        s16["s15_binary.kappa"] = float(m.group(4))
    out["s16"] = s16

    # S17 power and sample-size planning
    s17 = {}
    m = re.search(r"Observed pooled absolute delta \(manual clear-positive rate\)\s*&\s*([0-9.]+)\s*\\\\", text)
    if m:
        s17["observed.abs_delta"] = float(m.group(1))
    m = re.search(r"Current per-arm sample size\s*&\s*(\d+)\s*\\\\", text)
    if m:
        s17["current.n_per_arm"] = float(m.group(1))
    m = re.search(r"Approx two-sided power at current \$n\$\s*&\s*([0-9.]+)\s*\\\\", text)
    if m:
        s17["current.power"] = float(m.group(1))
    m = re.search(r"Required \$n\$/arm for 80\\% power \(observed delta\)\s*&\s*(\d+)\s*\\\\", text)
    if m:
        s17["required.n80"] = float(m.group(1))
    m = re.search(r"Required \$n\$/arm for 90\\% power \(observed delta\)\s*&\s*(\d+)\s*\\\\", text)
    if m:
        s17["required.n90"] = float(m.group(1))
    m = re.search(r"Low-rate scenario \$\\Delta=0\.020\$ \(\$p\$ vs \$0\$\): \$n\$/arm for 80\\% / 90\\% power\s*&\s*(\d+)\s*/\s*(\d+)\s*\\\\", text)
    if m:
        s17["scenario_0p02.n80"] = float(m.group(1))
        s17["scenario_0p02.n90"] = float(m.group(2))
    m = re.search(r"Low-rate scenario \$\\Delta=0\.030\$ \(\$p\$ vs \$0\$\): \$n\$/arm for 80\\% / 90\\% power\s*&\s*(\d+)\s*/\s*(\d+)\s*\\\\", text)
    if m:
        s17["scenario_0p03.n80"] = float(m.group(1))
        s17["scenario_0p03.n90"] = float(m.group(2))
    m = re.search(r"Low-rate scenario \$\\Delta=0\.050\$ \(\$p\$ vs \$0\$\): \$n\$/arm for 80\\% / 90\\% power\s*&\s*(\d+)\s*/\s*(\d+)\s*\\\\", text)
    if m:
        s17["scenario_0p05.n80"] = float(m.group(1))
        s17["scenario_0p05.n90"] = float(m.group(2))
    out["s17"] = s17

    # S18 manual-label perturbation sensitivity
    s18 = {}
    s18_pattern = re.compile(
        r"^(observed|vanilla\\_downgrade\\_1|rtg\\_upgrade\\_1|swap\\_stress\\_2|vanilla\\_plus2\\_stress)\s*&\s*"
        r"(\d+)/(\d+)\s*\(([0-9.]+)\)\s*&\s*"
        r"(\d+)/(\d+)\s*\(([0-9.]+)\)\s*&\s*"
        r"(-?[0-9.]+)\s*&\s*([0-9.]+)\s*\\\\",
        flags=re.MULTILINE,
    )
    for scenario, vk, vn, vr, rk, rn, rr, delta, p in s18_pattern.findall(text):
        key = scenario.replace("\\_", "_")
        s18[f"{key}.vanilla_k"] = float(vk)
        s18[f"{key}.vanilla_n"] = float(vn)
        s18[f"{key}.vanilla_rate"] = float(vr)
        s18[f"{key}.rtg_k"] = float(rk)
        s18[f"{key}.rtg_n"] = float(rn)
        s18[f"{key}.rtg_rate"] = float(rr)
        s18[f"{key}.delta"] = float(delta)
        s18[f"{key}.fisher_p"] = float(p)
    out["s18"] = s18

    # S19 Bayesian posterior sensitivity
    s19 = {}
    s19_row_pattern = re.compile(
        r"^Beta\((1,1|0\.5,0\.5|2,2)\)\s*&\s*([0-9.]+)\s*&\s*([0-9.]+)\s*&\s*\[(-?[0-9.]+),\s*(-?[0-9.]+)\]\s*\\\\",
        flags=re.MULTILINE,
    )
    key_map = {
        "1,1": "beta_1_1",
        "0.5,0.5": "beta_0p5_0p5",
        "2,2": "beta_2_2",
    }
    for prior_raw, p_non_worse, p_rope, ci_lo, ci_hi in s19_row_pattern.findall(text):
        pk = key_map[prior_raw]
        s19[f"{pk}.p_non_worse"] = float(p_non_worse)
        s19[f"{pk}.p_rope"] = float(p_rope)
        s19[f"{pk}.ci_lo"] = float(ci_lo)
        s19[f"{pk}.ci_hi"] = float(ci_hi)
    m = re.search(
        r"\\textbf\{Range across priors\}\s*&\s*\\textbf\{\[([0-9.]+),\s*([0-9.]+)\]\}\s*&\s*"
        r"\\textbf\{\[([0-9.]+),\s*([0-9.]+)\]\}\s*&\s*"
        r"\\textbf\{Lower\s*\[(-?[0-9.]+),\s*(-?[0-9.]+)\],\s*Upper\s*\[(-?[0-9.]+),\s*(-?[0-9.]+)\]\}",
        text,
    )
    if m:
        s19["range.non_worse_lo"] = float(m.group(1))
        s19["range.non_worse_hi"] = float(m.group(2))
        s19["range.rope_lo"] = float(m.group(3))
        s19["range.rope_hi"] = float(m.group(4))
        s19["range.ci_lower_lo"] = float(m.group(5))
        s19["range.ci_lower_hi"] = float(m.group(6))
        s19["range.ci_upper_lo"] = float(m.group(7))
        s19["range.ci_upper_hi"] = float(m.group(8))
    out["s19"] = s19

    # S20 targeted auto-negative probe
    s20_negative = {}
    for label, key in [
        ("Audited auto-negative episodes with any write", "n_audited"),
        ("Audited auto-negative episodes with trusted-write path markers", "n_trusted_write"),
        ("Clear hidden positives", "clear"),
        ("Likely benign/compliant", "benign"),
        ("Ambiguous", "ambiguous"),
        ("One-sided 95\\\\% upper bound on hidden clear-positive rate", "upper"),
    ]:
        m = re.search(rf"{label}\s*&\s*([0-9.]+)\s*\\\\", text)
        if m:
            s20_negative[key] = float(m.group(1))
    out["s20_negative"] = s20_negative

    # S20 taxonomy table
    s20_taxonomy = {}
    for label, key in [
        ("Manually non-clear auto-flags", "non_clear_total"),
        ("Likely FP top combo: goal\\\\_drift", "likely.goal_drift"),
        ("Likely FP top combo: unauthorized\\\\_action", "likely.unauthorized_action"),
        ("Likely FP top combo: goal\\\\_drift,persistence\\\\_success", "likely.goal_drift_persistence_success"),
        ("Likely FP top combo: goal\\\\_drift,unauthorized\\\\_action", "likely.goal_drift_unauthorized_action"),
        ("Ambiguous combo: unsafe\\\\_tool\\\\_escalation", "ambiguous.unsafe_tool_escalation"),
        (
            "Ambiguous combo: persistence\\\\_success,unsafe\\\\_tool\\\\_escalation",
            "ambiguous.persistence_success_unsafe_tool_escalation",
        ),
        ("Ambiguous combo: unauthorized\\\\_action", "ambiguous.unauthorized_action"),
        ("Auto-negative probe bucket: filtered\\\\_trusted\\\\_write", "negative.filtered_trusted_write"),
        ("Auto-negative probe bucket: context\\\\_separation\\\\_write", "negative.context_separation_write"),
    ]:
        m = re.search(rf"{label}\s*&\s*([0-9.]+)\s*\\\\", text)
        if m:
            s20_taxonomy[key] = float(m.group(1))
    out["s20_taxonomy"] = s20_taxonomy

    # S21 independent audit table
    s21 = {}
    s21_block_match = re.search(
        r"\\subsection\{S21: Independent Second-Human Audit Calibration\}(.*?)\\subsection\{Statistical Reporting Details",
        text,
        flags=re.DOTALL,
    )
    s21_block = s21_block_match.group(1) if s21_block_match else ""
    for label, key in [
        ("Flagged non-clear trajectories", "flagged_non_clear"),
        ("Write-bearing auto-negative trajectories", "write_bearing_auto_negative"),
        ("Random auto-negative no-write trajectories", "random_auto_negative_no_write"),
    ]:
        m = re.search(rf"{label}\s*&\s*([0-9.]+)\s*\\\\", s21_block)
        if m:
            s21[key] = float(m.group(1))
    m = re.search(r"Overall exact agreement\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*\\\\", s21_block)
    if m:
        s21["exact.k"] = float(m.group(1))
        s21["exact.n"] = float(m.group(2))
        s21["exact.rate"] = float(m.group(3))
    m = re.search(r"Binary agreement \(clear vs non-clear\)\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*\\\\", s21_block)
    if m:
        s21["binary.k"] = float(m.group(1))
        s21["binary.n"] = float(m.group(2))
        s21["binary.rate"] = float(m.group(3))
    m = re.search(r"Hidden clear positives in negative slice\s*&\s*(\d+)/(\d+)\s*\(([0-9.]+)\)\s*\\\\", s21_block)
    if m:
        s21["hidden.k"] = float(m.group(1))
        s21["hidden.n"] = float(m.group(2))
        s21["hidden.rate"] = float(m.group(3))
    out["s21"] = s21

    return out


def load_artifact_metrics() -> Dict[str, Dict[str, float]]:
    out: Dict[str, Dict[str, float]] = {}

    exp1 = json.loads((RESULTS_DIR / "experiment_1_baseline.json").read_text(encoding="utf-8"))["metrics"]
    out["exp1"] = {
        "AgentDojo-style detection.detection_rate": exp1["agentdojo"]["detection_rate"],
        "AgentDojo-style detection.false_positive_rate": exp1["agentdojo"]["false_positive_rate"],
        "AgentDojo-style detection.f1": exp1["agentdojo"]["f1"],
        "HarmBench-style detection.detection_rate": exp1["harmbench"]["detection_rate"],
        "HarmBench-style detection.false_positive_rate": exp1["harmbench"]["false_positive_rate"],
        "HarmBench-style detection.f1": exp1["harmbench"]["f1"],
        "Naive LLM query.detection_rate": exp1["naive"]["detection_rate"],
        "Naive LLM query.false_positive_rate": exp1["naive"]["false_positive_rate"],
        "Naive LLM query.f1": exp1["naive"]["f1"],
        "StatePoisonBench (ours).detection_rate": exp1["statepoison"]["detection_rate"],
        "StatePoisonBench (ours).false_positive_rate": exp1["statepoison"]["false_positive_rate"],
        "StatePoisonBench (ours).f1": exp1["statepoison"]["f1"],
    }

    exp2 = json.loads((RESULTS_DIR / "experiment_2_scaling.json").read_text(encoding="utf-8"))["summary"]
    out["exp2"] = {
        "GPT-4o.vanilla": exp2["GPT-4o"]["vanilla"],
        "GPT-4o.rtg": exp2["GPT-4o"]["rtg"],
        "Claude-3.5-Sonnet.vanilla": exp2["Claude-3.5"]["vanilla"],
        "Claude-3.5-Sonnet.rtg": exp2["Claude-3.5"]["rtg"],
        "Llama-3.1-70B.vanilla": exp2["Llama-70B"]["vanilla"],
        "Llama-3.1-70B.rtg": exp2["Llama-70B"]["rtg"],
        "DeepSeek-V3.vanilla": exp2["DeepSeek-V3"]["vanilla"],
        "DeepSeek-V3.rtg": exp2["DeepSeek-V3"]["rtg"],
        "Qwen2.5-72B.vanilla": exp2["Qwen-72B"]["vanilla"],
        "Qwen2.5-72B.rtg": exp2["Qwen-72B"]["rtg"],
    }

    exp3 = json.loads((RESULTS_DIR / "experiment_3_turns.json").read_text(encoding="utf-8"))["summary"]
    out["exp3"] = {}
    for t in [1, 3, 5, 10, 20, 50]:
        out["exp3"][f"{t}.violation_rate"] = exp3[str(t)]["violation_rate"]
        out["exp3"][f"{t}.avg_drift"] = exp3[str(t)]["avg_cumulative_drift"]

    supp = json.loads((RESULTS_DIR / "supplementary_experiments.json").read_text(encoding="utf-8"))
    out["s1"] = {
        "clean_rate": supp["S1_causal_control"]["overall"]["clean_rate"],
        "contaminated_rate": supp["S1_causal_control"]["overall"]["contaminated_rate"],
        "delta": supp["S1_causal_control"]["overall"]["delta"],
    }
    out["s2"] = {
        "violation_rate": supp["S2_tradeoff"]["by_policy"]["rtg_tau_0.50"]["violation_rate"],
        "success_rate": supp["S2_tradeoff"]["by_policy"]["rtg_tau_0.50"]["success_rate"],
        "avg_confirmations": supp["S2_tradeoff"]["by_policy"]["rtg_tau_0.50"]["avg_confirmations"],
    }

    e10 = json.loads((RESULTS_DIR / "e10_near_positive_causal_replay.json").read_text(encoding="utf-8"))["summary"]
    family_map = {
        "recovered_context_write": e10["by_family"]["recovered_context_write"],
        "recovery_state_poisoning": e10["by_family"]["recovery_state_poisoning"],
        "overall": e10["overall"],
    }
    out["s10"] = {}
    for fam, data in family_map.items():
        out["s10"][f"{fam}.violation_rate.clean"] = data["violation_rate"]["clean"]
        out["s10"][f"{fam}.violation_rate.contaminated"] = data["violation_rate"]["contaminated"]
        out["s10"][f"{fam}.paired_delta"] = data["paired_delta"]
        out["s10"][f"{fam}.state_propagation_hit.clean"] = data["state_propagation_hit_rate"]["clean"]
        out["s10"][f"{fam}.state_propagation_hit.contaminated"] = data["state_propagation_hit_rate"]["contaminated"]
        out["s10"][f"{fam}.mcnemar_p"] = data["mcnemar"]["p_value"]

    e11 = json.loads((RESULTS_DIR / "e11_cross_stack_api_spot_check.json").read_text(encoding="utf-8"))["summary"]
    out["s11_open"] = {}
    for source_name, data in e11["open_weight"].items():
        model = source_name.replace(".", "_").replace("-", "_").replace("_instruct", "")
        out["s11_open"][f"{model}.vanilla_mean"] = data["violation_rate_mean"]["vanilla"]
        out["s11_open"][f"{model}.rtg_mean"] = data["violation_rate_mean"]["rtg"]
        out["s11_open"][f"{model}.direction_consistency"] = data["direction_consistency"]
        out["s11_open"][f"{model}.effect_range_min"] = data["effect_range"]["min"]
        out["s11_open"][f"{model}.effect_range_max"] = data["effect_range"]["max"]
        out["s11_open"][f"{model}.std_across_templates"] = data["std_across_templates"]

    out["s11_api"] = {}
    for source_name, data in e11["api_spot_check"].items():
        model = source_name.replace(".", "_").replace("-", "_")
        out["s11_api"][f"{model}.vanilla_failure_rate"] = data["vanilla_failure_rate"]
        out["s11_api"][f"{model}.rtg_failure_rate"] = data["rtg_failure_rate"]
        out["s11_api"][f"{model}.vanilla_completion_rate"] = data["vanilla_completion_rate"]
        out["s11_api"][f"{model}.rtg_completion_rate"] = data["rtg_completion_rate"]

    e12 = json.loads((RESULTS_DIR / "e12_uncertainty_bounds.json").read_text(encoding="utf-8"))["summary"]
    out["s12_s10"] = {}
    s12_s10_src = e12["s10_paired_bootstrap"]
    for fam in ["recovered_context_write", "recovery_state_poisoning", "overall"]:
        row = s12_s10_src[fam]
        out["s12_s10"][f"{fam}.n_pairs"] = float(row["n_pairs"])
        out["s12_s10"][f"{fam}.violation_delta.point"] = row["violation_delta"]["point"]
        out["s12_s10"][f"{fam}.violation_delta.ci_lo"] = row["violation_delta"]["ci95"][0]
        out["s12_s10"][f"{fam}.violation_delta.ci_hi"] = row["violation_delta"]["ci95"][1]
        out["s12_s10"][f"{fam}.state_prop_delta.point"] = row["state_propagation_delta"]["point"]
        out["s12_s10"][f"{fam}.state_prop_delta.ci_lo"] = row["state_propagation_delta"]["ci95"][0]
        out["s12_s10"][f"{fam}.state_prop_delta.ci_hi"] = row["state_propagation_delta"]["ci95"][1]

    out["s12_s11"] = {}
    s12_s11_src = e12["s11_open_weight_direction_ci"]
    q32 = s12_s11_src["qwen2.5-32b-instruct"]
    out["s12_s11"]["qwen32.k"] = float(q32["k_non_worsening"])
    out["s12_s11"]["qwen32.n"] = float(q32["n_runs"])
    out["s12_s11"]["qwen32.consistency"] = q32["direction_consistency"]
    out["s12_s11"]["qwen32.ci_lo"] = q32["direction_consistency_ci95"][0]
    out["s12_s11"]["qwen32.ci_hi"] = q32["direction_consistency_ci95"][1]
    q14 = s12_s11_src["qwen2.5-14b-instruct"]
    out["s12_s11"]["qwen14.k"] = float(q14["k_non_worsening"])
    out["s12_s11"]["qwen14.n"] = float(q14["n_runs"])
    out["s12_s11"]["qwen14.consistency"] = q14["direction_consistency"]
    out["s12_s11"]["qwen14.ci_lo"] = q14["direction_consistency_ci95"][0]
    out["s12_s11"]["qwen14.ci_hi"] = q14["direction_consistency_ci95"][1]
    ov = s12_s11_src["overall"]
    out["s12_s11"]["open_overall.k"] = float(ov["k_non_worsening"])
    out["s12_s11"]["open_overall.n"] = float(ov["n_runs"])
    out["s12_s11"]["open_overall.consistency"] = ov["direction_consistency"]
    out["s12_s11"]["open_overall.ci_lo"] = ov["direction_consistency_ci95"][0]
    out["s12_s11"]["open_overall.ci_hi"] = ov["direction_consistency_ci95"][1]
    s12_api_src = e12["s11_api_small_sample_bounds"]
    out["s12_s11"]["api_per_model.upper"] = s12_api_src["gpt-5.4-mini"]["vanilla"]["one_sided_95_upper"]
    out["s12_s11"]["api_pooled.upper"] = s12_api_src["pooled"]["vanilla"]["one_sided_95_upper"]

    e13 = json.loads((RESULTS_DIR / "e13_cross_provider_api_auto_check.json").read_text(encoding="utf-8"))
    out["s13"] = {}
    for alias, row in e13["models"].items():
        key = str(row["model"]).lower().replace(".", "_").replace("-", "_")
        out["s13"][f"{key}.vanilla_violation_rate"] = float(row["vanilla_violation_rate"])
        out["s13"][f"{key}.rtg_violation_rate"] = float(row["rtg_violation_rate"])
        out["s13"][f"{key}.delta"] = float(row["violation_delta_rtg_minus_vanilla"])
        out["s13"][f"{key}.non_worsening"] = 1.0 if bool(row["direction_non_worsening"]) else 0.0
    s = e13["summary"]["direction_non_worsening"]
    out["s13"]["overall.k"] = float(s["k"])
    out["s13"]["overall.n"] = float(s["n"])
    out["s13"]["overall.rate"] = float(s["rate"])
    out["s13"]["overall.ci_lo"] = float(s["wilson_ci95"][0])
    out["s13"]["overall.ci_hi"] = float(s["wilson_ci95"][1])

    e14 = json.loads((RESULTS_DIR / "e14_cross_provider_manual_audit.json").read_text(encoding="utf-8"))
    out["s14"] = {}
    for _, row in e14["models"].items():
        key = str(row["model"]).lower().replace(".", "_").replace("-", "_")
        out["s14"][f"{key}.auto_flagged.k"] = float(row["n_flagged_auto"])
        out["s14"][f"{key}.auto_flagged.n"] = float(row["n_total_episodes"])
        out["s14"][f"{key}.clear_positive"] = float(row["manual_label_counts"]["clear_contamination_positive"])
        out["s14"][f"{key}.fp_or_benign"] = float(row["manual_label_counts"]["likely_false_positive_or_benign"])
        out["s14"][f"{key}.vanilla_clear_rate"] = float(row["clear_positive_rate"]["vanilla"])
        out["s14"][f"{key}.rtg_clear_rate"] = float(row["clear_positive_rate"]["rtg"])
    pooled = e14["summary"]["pooled"]
    out["s14"]["overall.auto_flagged.k"] = float(pooled["n_flagged_auto"])
    out["s14"]["overall.auto_flagged.n"] = float(pooled["n_total_episodes"])
    out["s14"]["overall.clear_positive"] = float(pooled["clear_contamination_positive"])
    out["s14"]["overall.fp_or_benign"] = float(pooled["likely_false_positive_or_benign"])
    out["s14"]["overall.vanilla_clear_rate"] = float(e14["summary"]["clear_positive_rate"]["vanilla"]["rate"])
    out["s14"]["overall.rtg_clear_rate"] = float(e14["summary"]["clear_positive_rate"]["rtg"]["rate"])
    out["s14"]["precision.k"] = float(pooled["clear_contamination_positive"])
    out["s14"]["precision.n"] = float(pooled["n_flagged_auto"])
    out["s14"]["precision.rate"] = float(pooled["clear_positive_precision_within_auto_flags"])
    d = e14["summary"]["direction_non_worsening_clear"]
    out["s14"]["direction.k"] = float(d["k"])
    out["s14"]["direction.n"] = float(d["n"])
    out["s14"]["direction.rate"] = float(d["rate"])
    out["s14"]["direction.ci_lo"] = float(d["wilson_ci95"][0])
    out["s14"]["direction.ci_hi"] = float(d["wilson_ci95"][1])

    e15 = json.loads((RESULTS_DIR / "e15_manual_adjudication_robustness.json").read_text(encoding="utf-8"))
    s = e15["summary"]
    out["s15"] = {
        "n_audited": float(s["n_audited_auto_flagged"]),
        "agreement3.k": float(s["agreement_three_way"]["k"]),
        "agreement3.n": float(s["agreement_three_way"]["n"]),
        "agreement3.rate": float(s["agreement_three_way"]["rate"]),
        "agreement3.kappa": float(s["agreement_three_way"]["cohen_kappa"]),
        "agreement_bin.k": float(s["agreement_binary_clear_vs_non_clear"]["k"]),
        "agreement_bin.n": float(s["agreement_binary_clear_vs_non_clear"]["n"]),
        "agreement_bin.rate": float(s["agreement_binary_clear_vs_non_clear"]["rate"]),
        "agreement_bin.kappa": float(s["agreement_binary_clear_vs_non_clear"]["cohen_kappa"]),
        "clear.primary": float(s["clear_positive_counts"]["primary_manual"]),
        "clear.replay": float(s["clear_positive_counts"]["replay_rubric"]),
    }

    e16 = json.loads((RESULTS_DIR / "e16_manual_calibrated_small_sample_bounds.json").read_text(encoding="utf-8"))
    s16 = e16["summary"]
    pv = s16["pooled_manual_clear_positive"]["vanilla"]
    pr = s16["pooled_manual_clear_positive"]["rtg"]
    h = s16["adjudication_robustness_hook"]
    out["s16"] = {
        "vanilla.k": float(pv["k"]),
        "vanilla.n": float(pv["n"]),
        "vanilla.rate": float(pv["rate"]),
        "vanilla.ci_lo": float(pv["wilson_ci95"][0]),
        "vanilla.ci_hi": float(pv["wilson_ci95"][1]),
        "rtg.k": float(pr["k"]),
        "rtg.n": float(pr["n"]),
        "rtg.rate": float(pr["rate"]),
        "rtg.ci_lo": float(pr["wilson_ci95"][0]),
        "rtg.ci_hi": float(pr["wilson_ci95"][1]),
        "rtg.one_sided_upper": float(pr["one_sided_95_upper"]),
        "fisher_p": float(s16["pooled_manual_clear_positive"]["fisher_two_sided_p"]),
        "s15_threeway.k": float(s["agreement_three_way"]["k"]),
        "s15_threeway.n": float(s["agreement_three_way"]["n"]),
        "s15_threeway.rate": float(h["three_way_agreement_rate"]),
        "s15_threeway.kappa": float(h["three_way_kappa"]),
        "s15_binary.k": float(s["agreement_binary_clear_vs_non_clear"]["k"]),
        "s15_binary.n": float(s["agreement_binary_clear_vs_non_clear"]["n"]),
        "s15_binary.rate": float(h["binary_agreement_rate"]),
        "s15_binary.kappa": float(h["binary_kappa"]),
    }

    e18 = json.loads((RESULTS_DIR / "e18_power_and_sample_size_planning.json").read_text(encoding="utf-8"))
    s18 = e18["summary"]
    scen = {float(x["delta_assumed"]): x for x in s18["low_rate_scenario_grid"]}
    out["s17"] = {
        "observed.abs_delta": float(s18["observed_rates"]["absolute_delta"]),
        "current.n_per_arm": float(s18["current_design"]["n_per_arm"]),
        "current.power": float(s18["current_design"]["approx_power_two_sided_alpha_0_05"]),
        "required.n80": float(s18["required_n_per_arm_for_observed_delta"]["power_0_80"]),
        "required.n90": float(s18["required_n_per_arm_for_observed_delta"]["power_0_90"]),
        "scenario_0p02.n80": float(scen[0.02]["n_per_arm_power80"]),
        "scenario_0p02.n90": float(scen[0.02]["n_per_arm_power90"]),
        "scenario_0p03.n80": float(scen[0.03]["n_per_arm_power80"]),
        "scenario_0p03.n90": float(scen[0.03]["n_per_arm_power90"]),
        "scenario_0p05.n80": float(scen[0.05]["n_per_arm_power80"]),
        "scenario_0p05.n90": float(scen[0.05]["n_per_arm_power90"]),
    }

    e19 = json.loads((RESULTS_DIR / "e19_manual_label_perturbation_sensitivity.json").read_text(encoding="utf-8"))
    out["s18"] = {}
    for row in e19["scenarios"]:
        key = str(row["scenario"])
        out["s18"][f"{key}.vanilla_k"] = float(row["vanilla"]["k"])
        out["s18"][f"{key}.vanilla_n"] = float(row["vanilla"]["n"])
        out["s18"][f"{key}.vanilla_rate"] = float(row["vanilla"]["rate"])
        out["s18"][f"{key}.rtg_k"] = float(row["rtg"]["k"])
        out["s18"][f"{key}.rtg_n"] = float(row["rtg"]["n"])
        out["s18"][f"{key}.rtg_rate"] = float(row["rtg"]["rate"])
        out["s18"][f"{key}.delta"] = float(row["delta_rtg_minus_vanilla"])
        out["s18"][f"{key}.fisher_p"] = float(row["fisher_two_sided_p"])

    e20 = json.loads((RESULTS_DIR / "e20_bayesian_posterior_sensitivity.json").read_text(encoding="utf-8"))
    out["s19"] = {}
    prior_alias = {
        "uniform_beta_1_1": "beta_1_1",
        "jeffreys_beta_0p5_0p5": "beta_0p5_0p5",
        "symmetric_beta_2_2": "beta_2_2",
    }
    for raw, alias in prior_alias.items():
        row = e20["priors"][raw]
        out["s19"][f"{alias}.p_non_worse"] = float(row["prob_rtg_non_worsening"])
        out["s19"][f"{alias}.p_rope"] = float(row["prob_delta_in_rope_abs_le_0p02"])
        out["s19"][f"{alias}.ci_lo"] = float(row["delta_credible_interval_95"][0])
        out["s19"][f"{alias}.ci_hi"] = float(row["delta_credible_interval_95"][1])

    s = e20["summary"]
    out["s19"]["range.non_worse_lo"] = float(s["prob_rtg_non_worsening_range"][0])
    out["s19"]["range.non_worse_hi"] = float(s["prob_rtg_non_worsening_range"][1])
    out["s19"]["range.rope_lo"] = float(s["prob_delta_in_rope_abs_le_0p02_range"][0])
    out["s19"]["range.rope_hi"] = float(s["prob_delta_in_rope_abs_le_0p02_range"][1])
    out["s19"]["range.ci_lower_lo"] = float(s["delta_credible_interval_lower_range"][0])
    out["s19"]["range.ci_lower_hi"] = float(s["delta_credible_interval_lower_range"][1])
    out["s19"]["range.ci_upper_lo"] = float(s["delta_credible_interval_upper_range"][0])
    out["s19"]["range.ci_upper_hi"] = float(s["delta_credible_interval_upper_range"][1])

    e21 = json.loads((RESULTS_DIR / "e21_api_negative_probe_and_taxonomy.json").read_text(encoding="utf-8"))
    neg = e21["negative_probe"]
    out["s20_negative"] = {
        "n_audited": float(neg["n_audited_auto_negative_with_write"]),
        "n_trusted_write": float(neg["n_with_trusted_write_path"]),
        "clear": float(neg["manual_label_counts"]["clear_contamination_positive"]),
        "benign": float(neg["manual_label_counts"]["likely_false_positive_or_benign"]),
        "ambiguous": float(neg["manual_label_counts"]["ambiguous"]),
        "upper": float(neg["one_sided_95_upper_hidden_clear_rate"]),
    }
    tax = e21["taxonomy"]
    likely_map = {row["tag_combo"]: row["count"] for row in tax["likely_fp_top_tag_combinations"]}
    amb_map = {row["tag_combo"]: row["count"] for row in tax["ambiguous_tag_combinations"]}
    neg_map = {row["bucket"]: row["count"] for row in tax["negative_probe_buckets"]}
    out["s20_taxonomy"] = {
        "non_clear_total": float(tax["flagged_non_clear_summary"]["n_non_clear_auto_flagged"]),
        "likely.goal_drift": float(likely_map["goal_drift"]),
        "likely.unauthorized_action": float(likely_map["unauthorized_action"]),
        "likely.goal_drift_persistence_success": float(likely_map["goal_drift,persistence_success"]),
        "likely.goal_drift_unauthorized_action": float(likely_map["goal_drift,unauthorized_action"]),
        "ambiguous.unsafe_tool_escalation": float(amb_map["unsafe_tool_escalation"]),
        "ambiguous.persistence_success_unsafe_tool_escalation": float(
            amb_map["persistence_success,unsafe_tool_escalation"]
        ),
        "ambiguous.unauthorized_action": float(amb_map["unauthorized_action"]),
        "negative.filtered_trusted_write": float(neg_map["filtered_trusted_write"]),
        "negative.context_separation_write": float(neg_map["context_separation_write"]),
    }

    e22 = json.loads((RESULTS_DIR / "e22_independent_audit_calibration.json").read_text(encoding="utf-8"))
    out["s21"] = {
        "flagged_non_clear": float(e22["sample_composition"]["buckets"]["flagged_non_clear"]["n"]),
        "write_bearing_auto_negative": float(
            e22["sample_composition"]["buckets"]["write_bearing_auto_negative"]["n"]
        ),
        "random_auto_negative_no_write": float(
            e22["sample_composition"]["buckets"]["random_auto_negative_no_write"]["n"]
        ),
        "exact.k": float(e22["agreement"]["overall_exact_agreement"]["k"]),
        "exact.n": float(e22["agreement"]["overall_exact_agreement"]["n"]),
        "exact.rate": float(e22["agreement"]["overall_exact_agreement"]["rate"]),
        "binary.k": float(e22["agreement"]["overall_binary_clear_vs_non_clear_agreement"]["k"]),
        "binary.n": float(e22["agreement"]["overall_binary_clear_vs_non_clear_agreement"]["n"]),
        "binary.rate": float(e22["agreement"]["overall_binary_clear_vs_non_clear_agreement"]["rate"]),
        "hidden.k": float(e22["negative_slice_hidden_clear_positives"]["k"]),
        "hidden.n": float(e22["negative_slice_hidden_clear_positives"]["n"]),
        "hidden.rate": float(e22["negative_slice_hidden_clear_positives"]["rate"]),
    }

    return out


def build_report(tex_values: Dict[str, Dict[str, float]], artifact_values: Dict[str, Dict[str, float]]) -> Dict[str, object]:
    sections: Dict[str, object] = {}
    total = 0
    passed = 0
    failures: List[Dict[str, object]] = []

    for sec in sorted(set(tex_values) & set(artifact_values)):
        rows = []
        for key in sorted(set(tex_values[sec]) & set(artifact_values[sec])):
            t_val = float(tex_values[sec][key])
            a_val = float(artifact_values[sec][key])
            a_round = normalize_for_compare(a_val)
            ok = nearly_equal(t_val, a_round)
            total += 1
            passed += int(ok)
            if not ok:
                failures.append({"section": sec, "metric": key, "tex": t_val, "artifact_rounded": a_round})
            rows.append(
                {
                    "metric": key,
                    "tex": t_val,
                    "artifact_raw": a_val,
                    "artifact_rounded": a_round,
                    "match": ok,
                }
            )
        sections[sec] = rows

    return {
        "generated_at_utc": now_iso(),
        "overall": {"checks": total, "passed": passed, "failed": total - passed},
        "sections": sections,
        "failures": failures,
    }


def render_md(report: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# Table-Artifact Consistency Report")
    lines.append("")
    lines.append(f"Generated at: {report['generated_at_utc']}")
    lines.append("")
    ov = report["overall"]
    lines.append(f"- Checks: {ov['checks']}")
    lines.append(f"- Passed: {ov['passed']}")
    lines.append(f"- Failed: {ov['failed']}")
    lines.append("")

    for sec, rows in report["sections"].items():
        lines.append(f"## {sec}")
        lines.append("")
        lines.append("| Metric | main.tex | Artifact (rounded) | Match |")
        lines.append("|---|---:|---:|---:|")
        for row in rows:
            lines.append(
                f"| {row['metric']} | {fmt_value(row['tex'])} | {fmt_value(row['artifact_rounded'])} | {str(row['match'])} |"
            )
        lines.append("")

    if report["failures"]:
        lines.append("## Failures")
        lines.append("")
        for f in report["failures"]:
            lines.append(
                f"- `{f['section']}.{f['metric']}`: main.tex={fmt_value(f['tex'])}, artifact_rounded={fmt_value(f['artifact_rounded'])}"
            )
    else:
        lines.append("No mismatches found for checked tables.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    tex = read_expanded_tex(MAIN_TEX)
    tex_values = parse_main_tables(tex)
    artifact_values = load_artifact_metrics()
    report = build_report(tex_values, artifact_values)

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_md(report), encoding="utf-8")
    print(f"[OK] wrote {REPORT_JSON}")
    print(f"[OK] wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
