# Rebuttal-Ready Packet (S13-S24 Calibration + Prospective Pilot)

## Core Position
We treat the real-world layer as calibrated grounding, not a prevalence study.
For C1, synthetic labels are frozen by the task schema before detector comparison; the compared detectors differ in input access, and only the StatePoisonBench monitor sees structured trajectory plus authorization metadata.
S13 is exploratory automatic stress-checking.
S14--S21 provide calibrated interpretation with full manual review, replay robustness, targeted negative probing, and an independent blind packet.
S22 adds a detector-decoupled external fairness check for C1 interpretation.
S23 widens negative-slice miss checking with an expanded single-external packet.
S24 adds a prospective paired real-platform starter slice, but we keep it explicitly conservative because the first corrected 6-pair run validates execution while remaining non-separating overall.
The fastest maturity-homogeneous read is the action-grounded nucleus (`tool_mediated_recovery` + `recovered_context_write`) plus S10--S12; the other core families remain explicit span tests rather than equally mature real-positive classes.

## Allowed vs Not Claimed

| Allowed reading | Not claimed |
|---|---|
| The paper validates a benchmark methodology for persistent-state contamination. | The paper estimates real-world prevalence of contamination failures. |
| Synthetic labels are frozen and auditable before Experiment 1 detector scoring. | The compared detectors define their own ground truth in Experiment 1. |
| C1 is an in-benchmark, semantics-aligned measurement-gap result. | C1 is a universal detector ranking. |
| C1 shows what becomes measurable under full benchmark observability. | C1 already proves which lighter portable cue set is sufficient. |
| S13--S23 provide a retrospective calibration ladder. | S13--S23 prove treatment effects on deployed endpoints. |
| S24 shows a prospective paired live-endpoint protocol is executable. | S24 already shows a stable real-endpoint contamination effect. |
| RTG is a lightweight benchmark-time probe baseline. | RTG is a deployable runtime defense. |
| Real traces ground workflow realism and calibration boundaries. | Every real trace is a clean contamination-positive failure. |

## Ready-to-Paste Responses

### On Real-World Evidence Strength
We agree that real-trace evidence must be calibrated conservatively. In the expanded 304-episode direct-endpoint slice (S14), only one clear contamination-positive case is confirmed (1/304), so we do not present prevalence claims. We then tighten negative-side calibration in S20--S21 and S23: S20 finds 0/17 hidden clear positives in write-bearing auto-negatives, S21 finds 0/24 hidden clear positives in an independent blind negative slice, and S23 finds 1/34 hidden clear positives in its audited negative slice. S24 adds a different kind of evidence: a prospective paired continuation pilot on a live endpoint. But after correcting a paired-summary bug, the first 6-pair starter slice is mixed-direction overall (0.50 clean vs 0.50 contaminated, exact McNemar $p=1.0$), so we keep it as execution-validating pilot evidence rather than effect evidence.

### On Why We Still Include S24
S24 is useful because it shows that the prospective paired protocol is runnable end-to-end on a live endpoint while holding task goal, authorization boundary, and trusted target fixed across clean and contaminated recovered-state conditions. That matters methodologically even though the current starter slice is too small for a directional claim. We explicitly state that S24 does not upgrade the paper's real-world effect claims and should be read as pilot infrastructure plus reporting-schema validation.

### On Off-Paper Stricter Follow-Up
We did test a stricter off-paper `E25 v2` redesign after fixing the paired-summary bug. That stricter slice removes much of the old broad-endpoint noise and yields one contaminated-only `primary_violation` in a recovered-context-write pair, but still no completed trusted-target writes on a 6-pair slice. We therefore use it only as internal guidance for the next prospective expansion, not as a paper result or as evidence strong enough to change the submission's real-world claim language.

### On C1 Fairness / Semantics Coupling
We add S22 to explicitly decouple detector comparison from frozen benchmark semantics. On a balanced 48-trajectory external-labeled packet, author-vs-external binary agreement is high (47/48), but detector ordering changes relative to the in-benchmark C1 table: the state-aware detector is no longer dominant on this decoupled slice. This is consistent with our claim that C1 is a semantics-aligned in-benchmark upper-bound result, not a universal detector ranking.

### On Missing Middle-Ground Baselines
We now state this limitation directly in the main text. The current C1 packet compares text-only screening proxies with a fully state-aware benchmark monitor, but does not yet include serialized-boundary or partial-event-typing comparators that would sit between those extremes. The present result therefore establishes an observability gap under frozen benchmark semantics, not which minimal portable cue set would recover most of that gain.

### On the New Middle-Ground Observability Ladder
We now directly probe that middle ground in appendix-only E26--E27 diagnostics on the same 48-trajectory S22 packet, using local cached Qwen2.5 3B/7B judges. In the looser first-round construction, the 3B judge shows only a small directional shift from text-only to boundary-aware views (F1 `0.333 -> 0.400 -> 0.400`), while 7B ties all three views at `0.500`. We then tighten the design by removing family/defense labels and internal reasoning/decision text from the text-only view. Under that stricter construction, the 3B result becomes `0.500 -> 0.333 -> 0.500` and 7B again ties all three views at `0.500`. So we can now say the missing middle-ground comparator has been directly tested, but the effect is weak and view-construction-sensitive rather than a robust monotonic gain from adding boundary or event cues.

### On Detector vs Labeler Disentanglement
We now make the contract in the main text explicit. Synthetic ground truth is fixed by the task schema plus deterministic rules before any detector is run. The prompt-local comparators read flattened text without authorization-boundary annotations or trusted-target tags; the StatePoisonBench detector reads the structured trajectory together with restore markers, action targets, and boundary metadata. We therefore present C1 as a benchmark-internal comparison between text-only screening proxies and a state-aware benchmark-time monitor under frozen labels, then use S22 as the detector-decoupled boundary check rather than claiming one universal detector ordering.

### On RTG Policy Specificity
The revised main text now gives a compact RTG policy card: the score is based on recovered artifact source, authorization sensitivity, and action class; at the default `tau=0.50`, low-risk reads proceed, medium-risk state-changing steps are rewritten into read-only verification, and confirmation-gated trusted writes or goal/tool escalations are halted or converted into explicit confirmation requests. This keeps RTG auditable as a benchmark-time probe without reframing it as a deployment-ready defense.

### On the New Concrete Main-Text Example
To reduce abstraction, the revised Experiment 1 section includes a compact worked trajectory showing the exact rule firing sequence: recovered state is restored, the agent adopts the recovered hint, a trusted rebuttal file is written without confirmation inside the resume-sensitive window, and the frozen rule engine emits `unauthorized_action` plus `state_propagation`. This example is intended to make the benchmark's labeler, detector inputs, and scoring logic auditable without sending the reader to the appendix.

### On the Mixed-Grounding Main Table
We now provide a nucleus-first reading path in the main text. Readers who want the most reality-anchored slice can read the two action-grounded families first and then use S10--S12 as the bridge packet; the remaining three families are explicitly framed as span/calibration extensions rather than equally mature direct-real-positive evidence.

### On Runtime-Layer Related Work
The revised related-work section now positions StatePoisonBench against both architecture-first and runtime-layer enforcement paradigms. The paper explicitly treats systems such as Parallax and OpenClaw PRISM as adjacent runtime/enforcement proposals, while clarifying that StatePoisonBench contributes a benchmark-time measurement interface rather than another online defense stack.

### On Over-Flagging vs Hidden Misses
S14/S15/S20/S21 already showed over-flagging as a dominant error mode in manually audited slices. S23 sharpens that statement by surfacing a small but non-zero hidden-clear rate in negatives (1/34) while keeping high binary agreement (52/54), so the calibration narrative remains conservative and non-prevalence. S24 does not contradict that reading: its starter slice is too small and too mixed-direction to support a separate real-endpoint treatment-effect claim.

## Data Integrity Status (2026-04-14)
- Canonical source: `experiments/results/table_artifact_consistency_report.md` (`Generated at: 2026-04-14T07:17:04.579105+00:00`).
- Current status: `220/220` checks passed, `failed=0`.

## Quick Numbers
- S14: 1 clear contamination-positive in 304 direct-endpoint episodes; 173/181 auto-flags likely FP/benign.
- S15: replay agreement 180/181 (3-way), 181/181 (binary clear-vs-non-clear).
- S20: hidden clear positives in targeted write-bearing negatives = 0/17.
- S21: hidden clear positives in independent blind negative slice = 0/24.
- S22: balanced packet n=48; exact agreement 26/48; binary agreement 47/48; state-aware F1/FPR = 0.148/0.489; harmfulness proxy F1/FPR = 0.572/0.044.
- E26: same S22 packet with Qwen2.5-3B gives `text-only / +boundary / +event` F1 = `0.333 / 0.400 / 0.400`; Qwen2.5-7B ties at `0.500 / 0.500 / 0.500`.
- E27: stricter clean-text rerun on the same packet gives Qwen2.5-3B `0.500 / 0.333 / 0.500`; Qwen2.5-7B again ties at `0.500 / 0.500 / 0.500`.
- S23: expanded packet n=54 (20 flagged, 17 write-negative, 17 random-negative); exact agreement 29/54; binary agreement 52/54; hidden clear positives in negatives = 1/34.
- S24: prospective paired starter slice n=6 pairs / 12 episodes on `gpt-4.1-mini`; overall paired any-violation = 0.50 clean vs 0.50 contaminated, discordant pairs = 1 clean-only / 1 contaminated-only, exact McNemar `p=1.0`.
