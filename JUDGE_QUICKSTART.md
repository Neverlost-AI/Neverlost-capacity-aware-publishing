# Historical Build Week Judge Quickstart

> Archived competition artifact. This file preserves the original judge-oriented walkthrough. For the current portfolio quickstart and repository status, use [`README.md`](README.md). The exact submission-era repository state is preserved on `capacity-aware-publishing-2026-submission-final`.

## See the result

Start with the **84.5-second primary judge demo**:

- [Capacity-Aware Publishing Workflow](https://youtu.be/nQpAkjY9roA)

Then, if useful, view the **50.6-second supporting output**:

- [The Patient's Paradox Short](https://youtube.com/shorts/tCoZlffA4Xc)

Approved local copies and timed captions are included in `output/published/` for inspection without YouTube.

The reproducible Patient's Paradox runner case remains at `output/patients-paradox-short/PATIENTS_PARADOX_SHORT_REVIEW_ONLY_v0_2.mp4`.

Then open the distinct logo-free case at `output/recovery-aware-demo/RECOVERY_AWARE_SYNTHETIC_DEMO_REVIEW_ONLY_v0_1.mp4`.

The final pre-publication render of the narrated overview remains at `output/CAPACITY_AWARE_PUBLISHING_WORKFLOW_DEMO_REVIEW_ONLY_v0_4.mp4`.

## Reproduce it

```bash
python -m pip install -r requirements.txt
python build_short.py --validate-only
python build_short.py --capacity-profile recovery --capacity-budget 8
python build_short.py --manifest manifests/recovery_aware_synthetic_demo.json --capacity-profile recovery --capacity-budget 8
python -m unittest discover -s tests -v
```

Optional narrated-demo rebuild:

```bash
node setup_kokoro_runtime.mjs
node render_demo_audio.mjs
python build_demo.py
```

## Inspect the proof

- `manifests/patients_paradox_short.json` — controlled data contract
- `source/PATIENTS_PARADOX_APPROVED_v1_1.txt` — locked source
- `output/patients-paradox-short/PATIENTS_PARADOX_SHORT_CAPTIONS_v0_2.srt` — source-bound accessible captions
- `output/patients-paradox-short/PATIENTS_PARADOX_SHORT_BUILD_REPORT_v0_2.json` — input, output, timing, and media checks
- `output/patients-paradox-short/PATIENTS_PARADOX_SHORT_QA_CONTACT_SHEET_v0_2.jpg` — visual overview
- `output/patients-paradox-short/PATIENTS_PARADOX_SHORT_CAPACITY_PLAN_v0_2.json` — machine-readable eight-minute plan
- `output/patients-paradox-short/PATIENTS_PARADOX_SHORT_RESUME_CHECKPOINT_v0_2.md` — deferred decisions and exact next step

## Try a deliberate failure

Change the manifest status from `REVIEW_ONLY` to `APPROVED`, then run the validator. The build will refuse to let automation grant publication authority.

The automated suite performs this and the other custody failures without modifying the controlled examples.
