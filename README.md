# Neverlost Capacity-Aware Publishing

**A governed, recovery-aware publishing compiler that turns approved source into accessible media packages while preserving human release authority.**

[![Status: Working prototype](https://img.shields.io/badge/Status-Working%20prototype-1769AA)](#validated-prototype)
[![Tests: 15 passing](https://img.shields.io/badge/Tests-15%20passing-1B7F4B)](#governance-gates)
[![Release: Human only](https://img.shields.io/badge/Release-Human%20only-6B4EFF)](#human-authority-boundary)

Capacity-Aware Publishing reduces the repetitive work between an approved idea and a publication-ready media package. A controlled manifest locks source material, narration, timing, optional brand assets, captions, and review status. The runner validates those inputs, renders media, produces accessibility artifacts and QA evidence, records hashes, and stops at `REVIEW_ONLY`.

**Recovery-Aware Mode** adds a user-selected active-minute budget. It schedules the remaining human review work that fits, defers what does not, and writes an exact resume checkpoint so an interrupted production session can continue without reconstructing state.

## Portfolio status

This project was created for **OpenAI Build Week 2026** in the Developer Tools category. Judging is complete and `main` now serves as the portfolio and continued-development branch.

The exact competition-era repository state is preserved on [`capacity-aware-publishing-2026-submission-final`](https://github.com/Neverlost-AI/Neverlost-capacity-aware-publishing/tree/capacity-aware-publishing-2026-submission-final). Later commits on `main` are post-competition documentation, security, portability, or development changes and should not be represented as part of the original judged submission.

## Watch the working proof

- **Workflow demo:** [Capacity-Aware Publishing Workflow](https://youtu.be/nQpAkjY9roA) — 84.5-second overview of the governed pipeline, Recovery-Aware Mode, validation gates, and human-release boundary.
- **Published output:** [The Patient's Paradox Short](https://youtube.com/shorts/tCoZlffA4Xc) — a concrete media artifact produced from controlled source material.

The repository also contains reproducible outputs, timed captions, build reports, capacity plans, resume checkpoints, and QA contact sheets for inspection without rebuilding.

## The problem

Publishing one approved idea across scripts, narration, captions, video, thumbnails, metadata, and platform formats can require repeated copying, timing, formatting, app switching, and file handling. The creative decision may already be finished while the mechanical production burden remains.

Capacity-Aware Publishing separates **creative authority** from **mechanical production**:

1. A human approves the source and adaptation intent.
2. A manifest locks the controlled source, narration audio, timing, optional brand assets, and review status.
3. The runner verifies source custody, narration binding, caption validity, timing, and safe project paths.
4. The system renders accessible media and creates QA evidence.
5. Finished artifacts are hashed and recorded.
6. Automation stops at `REVIEW_ONLY`; publication remains a human decision.

## Recovery-Aware Mode

The creator selects a planning profile or an active-minute budget:

```bash
python build_short.py --capacity-profile recovery --capacity-budget 8
```

The included eight-minute example records completed mechanical work, schedules visual and caption review, and defers metadata, upload, and final release decisions. It produces both a machine-readable capacity plan and a human-readable resume checkpoint with the exact next action.

These values are **workflow-planning estimates supplied to the tool**, not medical, disability, employment, or work-capacity determinations.

## Validated prototype

The primary case converts approved excerpts from *The Patient's Paradox* into a **36.93-second 1080×1920 vertical video** with:

- SHA-256 source custody;
- controlled narration audio;
- source-bound captions;
- SRT accessibility output;
- optional Neverlost branding;
- FFprobe media validation;
- visual QA contact sheet;
- output hashes;
- recovery-aware session plan; and
- resume checkpoint.

A distinct second case uses a separate synthetic source, different audio, a logo-free visual profile, six caption cues, its own output directory, and an independent recovery checkpoint. Both cases run through the same generalized pipeline.

## Quickstart

### Requirements

- Python 3.10+
- Pillow
- FFmpeg and FFprobe available on `PATH`

No API key or platform credential is required for the core runner.

```bash
git clone https://github.com/Neverlost-AI/Neverlost-capacity-aware-publishing.git
cd Neverlost-capacity-aware-publishing
python -m pip install -r requirements.txt
python build_short.py --validate-only
python build_short.py --capacity-profile recovery --capacity-budget 8
python build_short.py --manifest manifests/recovery_aware_synthetic_demo.json --capacity-profile recovery --capacity-budget 8
python -m unittest discover -s tests -v
```

Generated artifacts are written beneath `output/`.

### Optional local narration build

The narrated workflow demo uses a local Kokoro runtime and the `am_fenrir` voice profile. This optional path requires Node.js, npm, and `tar` and downloads the pinned runtime/model packages on first setup.

```bash
node setup_kokoro_runtime.mjs
node render_demo_audio.mjs
python build_demo.py
```

Generated narration remains review-only until a human listens to it and makes the publication decision.

## Governance gates

The automated suite contains **15 positive, negative, distinct-case, and recovery-planning tests**.

The build blocks when:

- an approved source hash changes;
- narration is not bound to the approved source;
- a controlled audio or logo hash changes;
- captions are empty, overlapping, invalid, or unbound from narration;
- scene or caption timing exceeds tolerance;
- an asset path escapes the project root; or
- automation attempts to promote its own status from `REVIEW_ONLY` to `APPROVED`.

This makes governance executable rather than relying only on documentation or operator intent.

## Human-authority boundary

The system can build, validate, schedule, hash, and preserve state. It cannot grant itself publication authority.

The creator retains control over:

- source selection and meaning;
- rights and platform checks;
- editorial direction;
- final visual and caption review;
- approval; and
- publication.

The included published videos were explicitly reviewed and approved by the human author after the automated pipeline produced review-only artifacts.

## How Codex and GPT-5.6 Sol were used

During Build Week, Codex with GPT-5.6 Sol helped generalize the runner, implement Recovery-Aware Mode and resume checkpoints, strengthen custody validation, create the brand-optional second case, expand caption and path-safety checks, build the automated test suite, and assemble the technical demonstration.

Human decisions remained separate: the creator selected the source and excerpts, controlled the editorial direction, approved the visual language and narration profile, reviewed the outputs, and retained release authority.

## Repository map

| Location | Purpose |
| --- | --- |
| `build_short.py` | Generalized governed media runner and Recovery-Aware planner |
| `manifests/` | Controlled inputs for the primary and synthetic cases |
| `source/` | Approved source material used by the primary demonstration |
| `fixtures/` | Independent synthetic source/audio case |
| `tests/` | Positive, negative, governance, and recovery-planning tests |
| `build_demo.py` | 16:9 narrated workflow demonstration builder |
| `render_demo_audio.mjs` | Optional local Kokoro narration generation |
| `output/` | Preserved proof artifacts, reports, captions, checkpoints, and published copies |
| `BUILD_WEEK_COMPLIANCE_CHECKLIST.md` | Historical submission checklist |
| `DEVPOST_SUBMISSION_DRAFT.md` | Historical Build Week submission material |

## Security and privacy

The repository is designed so the core demonstration does not require OAuth credentials, API tokens, account secrets, or private records. Local credentials, environment files, tokens, private keys, and upload receipts are explicitly excluded by `.gitignore`.

Platform upload and publication remain outside the governed build runner and require a separate human-authorized action.

## Boundaries and limitations

This is a working prototype, not a production publishing platform or clinical tool.

- Demonstrations use synthetic material or creator-controlled approved source.
- No automatic publication occurs.
- The runner does not silently rewrite controlled source material.
- AI-generated polish is never treated as human approval.
- Capacity budgets are user-selected planning inputs, not professional conclusions.
- Workload estimates are model assumptions until tested with broader real-user measurements.
- Narration hashes protect file custody but do not semantically transcribe and verify spoken audio.
- Caption semantic timing still benefits from human review.
- Build reports are hashed but not cryptographically signed.

The governing design principle is simple: **automation may reduce the work required to publish, but it does not inherit the authority to decide what should be published.**
