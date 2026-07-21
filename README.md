# Neverlost Capacity-Aware Publishing Workflow

**Status:** working prototype · human-reviewed publication required

This software turns approved source into a governed, accessible media package while reducing repetitive editing and file-handling work. Recovery-Aware Mode lets the creator set an active-minute budget, schedules only the review work that fits, and preserves deferred decisions in a resume checkpoint.

## Watch the published proof

- **Primary judge demo:** [Capacity-Aware Publishing Workflow](https://youtu.be/nQpAkjY9roA) — the concise explanation of the problem, governed pipeline, Recovery-Aware Mode, and human-release boundary.
- **Optional supporting output:** [The Patient's Paradox Short](https://youtube.com/shorts/tCoZlffA4Xc) — a published example created from controlled source material.

The primary demo is the fastest judge route. The Short is supporting evidence, not a prerequisite for understanding or testing the repository.

## The problem

Publishing a single idea across video, captions, thumbnails, metadata, and short-form platforms requires many repetitive operations. That burden can become a barrier for creators living with pain, fatigue, cognitive variability, limited mobility, or constrained computer-task capacity.

The workflow separates creative authority from mechanical production:

1. A human approves the source and adaptation intent.
2. A manifest locks the source, narration audio, timing, optional brand assets, and output status.
3. The runner verifies that every spoken excerpt and caption exists in the declared narration.
4. The runner creates vertical visuals, concatenates approved narration, writes captions, renders the video, and emits a QA report.
5. The process hashes the finished outputs and stops at `REVIEW_ONLY`. A human decides whether to revise, approve, or publish.

## Recovery-Aware Mode

The creator selects a planning profile or active-minute budget. The runner estimates the active handling required for each remaining task, schedules the work that fits, and writes both a machine-readable capacity plan and a human-readable resume checkpoint.

```bash
python build_short.py --capacity-profile recovery --capacity-budget 8
```

The included eight-minute demonstration completes mechanical production, schedules visual and caption review, and safely defers metadata, upload, and publication decisions. These are declared workflow estimates for session planning—not medical, disability, or work-capacity conclusions.

## Working demonstration

The first demonstration converts two approved excerpts from *The Patient's Paradox* into a 36.93-second, 1080×1920 Short with:

- source-hash verification;
- verbatim narration custody;
- Neverlost navy/blue/white branding;
- blue-inlaid NVLT mark;
- burned-in captions plus an SRT sidecar;
- an automated media probe and contact sheet;
- an explicit human-release boundary.

A distinct second case uses a separate synthetic source, different audio, a logo-free brand profile, six caption cues, its own output directory, and an independent recovery checkpoint. Both cases pass the same generalized runner.

No medical, legal, benefits, vocational, or professional decision is automated.

## Run it

Supported platforms: Windows, macOS, and Linux with Python 3.10+, Pillow, and FFmpeg/FFprobe.

```bash
python -m pip install -r requirements.txt
python build_short.py --validate-only
python build_short.py --capacity-profile recovery --capacity-budget 8
python build_short.py --manifest manifests/recovery_aware_synthetic_demo.json --capacity-profile recovery --capacity-budget 8
python -m unittest discover -s tests -v
```

Outputs are written to `output/`.

### Build the narrated judge demo

The optional narration step uses a pinned local Kokoro runtime and the established `am_fenrir` voice at speed `0.83`. It downloads model/runtime packages from npm on first setup; Node.js, npm, and `tar` are required.

```bash
node setup_kokoro_runtime.mjs
node render_demo_audio.mjs
python build_demo.py
```

This creates seven concise WAV sections, timed captions, and the 84.5-second 1080p demo video. The pipeline labels the generated result `REVIEW_ONLY`; a human must listen, approve pronunciation and pacing, and make the publication decision. The linked publication was approved and released by the human author.

## Test the governance gates

- Change one character in the approved source: the build blocks on the SHA-256 mismatch.
- Replace narration text in the manifest with language absent from the approved source: the build blocks.
- Change `REVIEW_ONLY` to `APPROVED`: the automated build blocks.
- Change scene or caption timing beyond tolerance: the build blocks.
- Change a controlled audio or logo hash: the build blocks.
- Add overlapping, empty, or narration-unbound captions: the build blocks.
- Point an asset outside the project root: the build blocks.

The automated suite contains 15 positive, negative, distinct-case, and recovery-planning tests.

## How Codex and GPT-5.6 were used

Codex and GPT-5.6 helped generalize the runner, implement the Recovery-Aware planner and resume checkpoint, strengthen input and output custody, build a brand-optional second case, expand caption validation, create 15 automated tests, and update the judge-facing demonstration.

The human author retained authority over the manuscript, selected the excerpt, approved the established Kokoro voice profile and brand settings, and remains the only publication authority. AI-assisted narration and production reduced repetitive technical work; they did not replace authorship or release approval.

## Why this is assistive technology

The prototype converts a multi-application production process into one validated command and then protects the remaining human work with a bounded session plan. That reduces sustained computer time, repeated copying, manual timing, formatting, context switching, and the cost of reconstructing an interrupted session.

## Boundaries

- Synthetic or approved public materials only in demonstrations.
- No automatic publishing.
- No silent rewriting of source material.
- No implication that AI-generated polish equals human approval.
- Rights and platform checks remain a human gate.
- Capacity budgets are user-selected planning inputs, not professional conclusions.
- Workload estimates are model assumptions until measured with real users.
