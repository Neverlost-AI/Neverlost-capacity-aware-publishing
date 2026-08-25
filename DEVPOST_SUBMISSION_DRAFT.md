# Historical Devpost Submission Draft

> Archived Build Week artifact. This file preserves the competition-era submission copy and should not be read as the current repository status. For the portfolio-facing project description and quickstart, use [`README.md`](README.md). The exact submission-era repository state is preserved on `capacity-aware-publishing-2026-submission-final`.

## Project name

Neverlost Capacity-Aware Publishing Workflow

## Tagline

One approved idea becomes an accessible media package—without giving automation publication authority.

## Elevator pitch

Publishing one approved idea can require rebuilding it across scripts, slides, narration, captions, vertical video, metadata, and platform formats. For disabled and energy-limited creators, that repetitive production can become the barrier to publishing at all.

This prototype turns that multi-application process into one governed command. A human first approves the source and adaptation intent. A manifest then locks the source, narration audio, timing, optional brand assets, and review status. The runner verifies spoken excerpts and captions against the approved narration, creates vertical visuals, renders accessible media, and hashes the finished evidence package.

Recovery-Aware Mode adds a user-selected active-minute budget. It schedules the review work that fits, automates mechanical production, and preserves metadata, upload, and release decisions in a resume checkpoint. The Patient's Paradox Short and a separate logo-free synthetic case both pass the generalized runner. Together they produce sixteen source-bound caption cues, two capacity plans, two checkpoints, fifteen passing tests, and zero automated release decisions.

The workflow deliberately stops at `REVIEW_ONLY`. The author retains control over meaning, rights, final approval, and publication. Codex with GPT-5.6 Sol helped turn an exhausting manual process into a reusable, inspectable tool that reduces repetitive technical work and physical strain without replacing authorship.

## About the project

### Inspiration

The prototype came from producing Neverlost's first videos during Build Week. The creative work was only part of the burden. Each approved idea had to be repeatedly transferred across scripts, slides, narration files, captions, video renders, thumbnails, descriptions, and quality checks. That repeated handling consumed time and physical capacity that could have gone into the work itself.

The design question became: **Can AI reduce the mechanical burden of publishing while keeping the author's source, meaning, and release authority intact?**

### What it does

The workflow uses a controlled JSON manifest to define:

- the approved source and its SHA-256 hash;
- the exact narration excerpts authorized for use;
- scene timing and Neverlost branding;
- caption timing and accessible output;
- the machine-readable status of the result.

The creator can also select a recovery, standard, or full session profile—or provide a specific active-minute budget. The planner records what was completed, what fits now, what is deferred, and the exact next step. These values are user-directed workflow estimates, not medical or work-capacity determinations.

One command validates the controlled inputs, builds a vertical video, produces an SRT caption file, probes the finished media, creates a contact sheet, writes a hashed QA report, and preserves a recovery checkpoint. The pipeline refuses to continue if source, audio, or brand custody changes; narration or captions exceed the approved text; timings overlap; a path escapes the project; or automation attempts to label its own output `APPROVED`.

### How we built it

The prototype uses Python, Pillow, JSON manifests, FFmpeg, FFprobe, Kokoro, and standard-library tests. Codex with GPT-5.6 Sol helped generalize the runner, implement the recovery planner, create resume checkpoints, strengthen custody and caption validation, build two distinct cases, expand the suite to fifteen tests, and update the judge experience.

The human author selected the source and excerpts, controlled the manuscript and editorial direction, approved the established Neverlost visual language and narration profile, and retained the sole publication decision.

### Challenges

The hardest challenge was not rendering a video. It was preserving custody across transformations: ensuring that polished output did not silently rewrite the approved source or promote a generated draft into an approved publication. Caption placement also required iterative visual QA across light and dark scenes so accessibility did not compete with the designed message.

### What we learned

Governance can be executable. Source custody, timing, review status, and human authority do not have to remain informal promises; they can become testable build conditions. Capacity can also shape workflow without becoming a professional conclusion: the creator can bound a session, preserve deferred decisions, and resume without reconstructing the entire production state. The “last mile” of creative production is itself an accessibility problem worth designing for.

## Category

**Developer Tools** — a reusable, testable publishing runner with installation instructions and deliberate failure paths.

## Built with tags

`Codex` · `GPT-5.6 Sol` · `Python` · `FFmpeg` · `FFprobe` · `Pillow` · `JSON` · `Accessibility` · `Assistive Technology` · `YouTube`

## Try it out

### Published media

- **Primary judge demo:** [Capacity-Aware Publishing Workflow](https://youtu.be/nQpAkjY9roA)
- **Optional supporting output:** [The Patient's Paradox Short](https://youtube.com/shorts/tCoZlffA4Xc)

The primary video explains the project in 84.5 seconds. The 50.6-second Short is a concrete example of the governed output, included as optional supporting evidence.

```bash
python -m pip install -r requirements.txt
python build_short.py --validate-only
python build_short.py --capacity-profile recovery --capacity-budget 8
python build_short.py --manifest manifests/recovery_aware_synthetic_demo.json --capacity-profile recovery --capacity-budget 8
python -m unittest discover -s tests -v
```

Judges can also open the approved publication copies, reproducible case outputs, SRT files, build reports, capacity plans, resume checkpoints, and QA contact sheets in `output/` without rebuilding.

## Distinction from the first Neverlost submission

The first Neverlost project carries complex human evidence across healthcare, daily-life, benefits, education, and vocational decision systems. This project addresses a different user, task, implementation, and output: it carries **approved creative source material** into accessible media packages for disabled and energy-limited creators. It shares Neverlost's human-authority principle but does not run the Full Human Pathway evidence workflow.

## Historical remaining-submission fields

The list below is preserved exactly as competition-era planning context and is not a current task list:

- Repository URL
- `/feedback` Codex Session ID
- 3:2 gallery image selection
