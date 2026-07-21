#!/usr/bin/env python3
"""Build a governed vertical video from a locked source manifest.

The script refuses to render if the source hash changes, if narration text is
not present in the approved source, or if scene/caption timing is inconsistent.
Publication remains a separate human action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent


def fail(message: str) -> None:
    raise SystemExit(f"BUILD BLOCKED: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def audio_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as stream:
        return stream.getnframes() / stream.getframerate()


def resolve(rel: str) -> Path:
    path = (ROOT / rel).resolve()
    if ROOT not in path.parents and path != ROOT:
        fail(f"path escapes project root: {rel}")
    return path


def normalized_text(value: str) -> str:
    return " ".join(value.split())


def validate(manifest: dict, manifest_path: Path | None = None) -> dict:
    source = resolve(manifest["source"]["path"])
    if not source.exists():
        fail(f"missing approved source: {source}")
    actual_hash = sha256(source)
    if actual_hash != manifest["source"]["sha256"]:
        fail("approved source hash changed")

    source_text = " ".join(source.read_text(encoding="utf-8").split())
    audio_total = 0.0
    input_hashes = {"source": actual_hash}
    narration_text = []
    for segment in manifest["audio_segments"]:
        path = resolve(segment["path"])
        if not path.exists():
            fail(f"missing audio segment: {path}")
        actual_audio_hash = sha256(path)
        if actual_audio_hash != segment.get("sha256"):
            fail(f"controlled audio hash changed: {path.name}")
        input_hashes[f"audio:{path.name}"] = actual_audio_hash
        excerpt = normalized_text(segment["source_text"])
        if excerpt not in source_text:
            fail(f"narration is not verbatim approved source: {path.name}")
        narration_text.append(excerpt)
        audio_total += audio_duration(path)

    brand = manifest["brand"]
    logo_path = brand.get("logo")
    if logo_path:
        logo = resolve(logo_path)
        if not logo.exists():
            fail(f"missing brand logo: {logo}")
        actual_logo_hash = sha256(logo)
        if actual_logo_hash != brand.get("logo_sha256"):
            fail("controlled logo hash changed")
        input_hashes[f"logo:{logo.name}"] = actual_logo_hash

    scene_total = sum(float(scene["duration"]) for scene in manifest["scenes"])
    captions = manifest.get("captions", [])
    if not captions:
        fail("at least one caption cue is required")
    previous_end = 0.0
    authorized_narration = normalized_text(" ".join(narration_text))
    for index, cue in enumerate(captions, start=1):
        start = float(cue["start"])
        end = float(cue["end"])
        if start < 0 or end <= start:
            fail(f"caption {index} has invalid timing")
        if start < previous_end - 0.01:
            fail(f"caption {index} overlaps the previous cue")
        if end > audio_total + 0.08:
            fail(f"caption {index} extends beyond the controlled audio")
        caption_text = normalized_text(cue.get("text", ""))
        if not caption_text:
            fail(f"caption {index} is empty")
        if caption_text not in authorized_narration:
            fail(f"caption {index} is not bound to declared narration")
        previous_end = end
    caption_end = previous_end
    if abs(audio_total - scene_total) > 0.08:
        fail(f"scene total {scene_total:.3f}s does not match audio {audio_total:.3f}s")
    if abs(audio_total - caption_end) > 0.08:
        fail(f"caption end {caption_end:.3f}s does not match audio {audio_total:.3f}s")
    if manifest["status"] != "REVIEW_ONLY":
        fail("automated build may only produce REVIEW_ONLY output")

    manifest_hash = sha256(manifest_path) if manifest_path else None

    return {
        "manifest_sha256": manifest_hash,
        "source_sha256": actual_hash,
        "input_hashes": input_hashes,
        "audio_duration": round(audio_total, 3),
        "scene_duration": round(scene_total, 3),
        "caption_end": round(caption_end, 3),
        "source_checks": len(manifest["audio_segments"]),
        "caption_checks": len(captions),
        "status": "VALIDATED_FOR_REVIEW_BUILD",
    }


def font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    names = [
        "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf" if bold else "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size=size)
    return ImageFont.load_default()


def wrap(text: str, max_chars: int) -> str:
    return "\n".join(textwrap.wrap(text, width=max_chars, break_long_words=False))


def centered_multiline(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, face: ImageFont.FreeTypeFont, fill: str, spacing: int = 14) -> None:
    draw.multiline_text(xy, text, font=face, fill=fill, anchor="mm", align="center", spacing=spacing)


def render_scene(scene: dict, index: int, manifest: dict, out: Path) -> None:
    width = manifest["output"]["width"]
    height = manifest["output"]["height"]
    brand = manifest["brand"]
    theme = scene["theme"]
    background = {"navy": brand["navy"], "paper": brand["paper"], "blue": brand["blue"]}[theme]
    foreground = brand["paper"] if theme in {"navy", "blue"} else brand["ink"]
    accent = brand["blue"] if theme == "navy" else brand["navy"]

    image = Image.new("RGB", (width, height), background)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 28, height), fill=brand["blue"])
    draw.rectangle((82, 230, 235, 244), fill=accent)

    draw.text((84, 170), scene["eyebrow"], font=font(True, 42), fill=accent if theme == "paper" else brand["blue"])
    headline = wrap(scene["headline"], 22 if len(scene["headline"]) > 28 else 18)
    support = wrap(scene["support"], 28)
    centered_multiline(draw, (width // 2, 760), headline, font(True, 94 if len(scene["headline"]) < 30 else 76), foreground, 18)
    centered_multiline(draw, (width // 2, 1040), support, font(True if scene["support"].isupper() else False, 62), accent if theme == "paper" else brand["paper"], 14)

    draw.line((84, 1360, width - 84, 1360), fill=accent if theme == "paper" else brand["blue"], width=5)
    draw.text((84, 1410), "APPROVED SOURCE · GOVERNED ADAPTATION", font=font(True, 32), fill=accent if theme == "paper" else brand["blue"])
    draw.text((84, 1770), brand.get("footer", "GOVERNED PUBLISHING · REVIEW-ONLY"), font=font(True, 30), fill=foreground)

    if brand.get("logo"):
        logo = Image.open(resolve(brand["logo"])).convert("RGBA")
        logo.thumbnail((150, 150), Image.Resampling.LANCZOS)
        image.paste(logo, (width - 205, height - 220), logo)
    image.save(out / f"scene-{index:02d}.png", quality=95)


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_captions(manifest: dict, out: Path) -> Path:
    path = out / output_name(manifest, "captions_filename", "CAPTIONS.srt")
    blocks = []
    for index, cue in enumerate(manifest["captions"], start=1):
        blocks.append(f"{index}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}\n")
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


def artifact_stem(manifest: dict) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", manifest["artifact_id"].upper()).strip("_")


def output_name(manifest: dict, key: str, suffix: str) -> str:
    value = manifest["output"].get(key)
    if value:
        if Path(value).name != value:
            fail(f"output filename must be a basename: {value}")
        return value
    return f"{artifact_stem(manifest)}_{suffix}"


def output_directory(manifest: dict) -> Path:
    return resolve(manifest["output"].get("directory", "output"))


def run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if completed.returncode:
        print(completed.stdout)
        print(completed.stderr, file=sys.stderr)
        fail(f"command failed: {' '.join(command[:4])}")


DEFAULT_CAPACITY_TASKS = [
    {"id": "start_build", "label": "Start and verify the governed build", "kind": "human", "active_minutes": 1.0, "manual_baseline_minutes": 3.0, "manual_app_switches": 1},
    {"id": "render_media", "label": "Render scenes and assemble narration", "kind": "automation", "active_minutes": 0.2, "manual_baseline_minutes": 12.0, "manual_app_switches": 2},
    {"id": "build_captions", "label": "Write and render timed captions", "kind": "automation", "active_minutes": 0.2, "manual_baseline_minutes": 8.0, "manual_app_switches": 2},
    {"id": "build_qa", "label": "Probe media and generate QA evidence", "kind": "automation", "active_minutes": 0.2, "manual_baseline_minutes": 5.0, "manual_app_switches": 1},
    {"id": "visual_review", "label": "Review the visual contact sheet", "kind": "human", "active_minutes": 4.0, "manual_baseline_minutes": 4.0, "manual_app_switches": 1},
    {"id": "caption_review", "label": "Spot-check captions against narration", "kind": "human", "active_minutes": 2.0, "manual_baseline_minutes": 5.0, "manual_app_switches": 1},
    {"id": "metadata", "label": "Approve title, description, and platform copy", "kind": "human", "active_minutes": 3.0, "manual_baseline_minutes": 5.0, "manual_app_switches": 2},
    {"id": "upload", "label": "Upload the approved media package", "kind": "human", "active_minutes": 2.0, "manual_baseline_minutes": 2.0, "manual_app_switches": 1},
    {"id": "release_decision", "label": "Make the final publication decision", "kind": "human", "active_minutes": 1.0, "manual_baseline_minutes": 1.0, "manual_app_switches": 0},
]


CAPACITY_PROFILE_MINUTES = {"recovery": 8.0, "standard": 15.0, "full": 30.0}


def capacity_plan(manifest: dict, profile: str, budget: float | None, completed: set[str] | None = None) -> dict:
    if profile not in CAPACITY_PROFILE_MINUTES:
        fail(f"unknown capacity profile: {profile}")
    active_budget = float(budget if budget is not None else CAPACITY_PROFILE_MINUTES[profile])
    if active_budget <= 0:
        fail("capacity budget must be greater than zero")
    tasks = manifest.get("capacity_model", {}).get("tasks", DEFAULT_CAPACITY_TASKS)
    completed = completed or set()
    task_ids = {task["id"] for task in tasks}
    unknown = completed - task_ids
    if unknown:
        fail(f"unknown completed capacity task: {sorted(unknown)[0]}")

    completed_tasks = [task for task in tasks if task["id"] in completed]
    completed_minutes = sum(float(task["active_minutes"]) for task in completed_tasks)
    scheduled = []
    deferred = []
    used = completed_minutes
    for task in tasks:
        if task["id"] in completed:
            continue
        minutes = float(task["active_minutes"])
        if used + minutes <= active_budget + 1e-9:
            scheduled.append(task)
            used += minutes
        else:
            deferred.append(task)

    manual_baseline = sum(float(task["manual_baseline_minutes"]) for task in tasks if task["id"] not in completed)
    assisted_total = sum(float(task["active_minutes"]) for task in tasks if task["id"] not in completed)
    manual_switches = sum(int(task.get("manual_app_switches", 0)) for task in tasks if task["id"] not in completed)
    next_task = deferred[0] if deferred else None
    return {
        "artifact_id": manifest["artifact_id"],
        "status": "REVIEW_ONLY_CHECKPOINT_SAVED" if deferred else "READY_FOR_HUMAN_RELEASE_DECISION",
        "authority_boundary": "User-selected session-planning input only; not a medical or work-capacity determination.",
        "profile": profile,
        "active_minute_budget": active_budget,
        "completed_active_minutes": round(completed_minutes, 2),
        "active_minutes_used_or_scheduled": round(used, 2),
        "estimated_assisted_minutes_for_all_remaining_tasks": round(assisted_total, 2),
        "estimated_manual_baseline_minutes": round(manual_baseline, 2),
        "estimated_manual_app_switches": manual_switches,
        "estimate_boundary": "Workflow estimates for planning; not measured user outcomes.",
        "completed_task_ids": sorted(completed),
        "scheduled_now": scheduled,
        "deferred": deferred,
        "next_task": next_task,
    }


def write_capacity_outputs(manifest: dict, manifest_path: Path, out: Path, profile: str, budget: float | None, completed: set[str]) -> dict:
    plan = capacity_plan(manifest, profile, budget, completed)
    plan_path = out / output_name(manifest, "capacity_plan_filename", "CAPACITY_PLAN.json")
    checkpoint_path = out / output_name(manifest, "resume_checkpoint_filename", "RESUME_CHECKPOINT.md")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    scheduled = "\n".join(f"- {task['label']} ({task['active_minutes']} active min)" for task in plan["scheduled_now"]) or "- None"
    deferred = "\n".join(f"- {task['label']} ({task['active_minutes']} active min)" for task in plan["deferred"]) or "- None"
    completed_list = "\n".join(f"- `{task_id}`" for task_id in plan["completed_task_ids"]) or "- None"
    next_step = plan["next_task"]["label"] if plan["next_task"] else "Human release decision may proceed after the scheduled review tasks are completed."
    manifest_rel = manifest_path.relative_to(ROOT)
    checkpoint_path.write_text(
        f"# Recovery-Aware Resume Checkpoint\n\n"
        f"**Artifact:** `{manifest['artifact_id']}`  \n"
        f"**Status:** `{plan['status']}`  \n"
        f"**Profile:** `{profile}`  \n"
        f"**User-selected active-minute budget:** {plan['active_minute_budget']:.1f}\n\n"
        f"> This is session-planning information supplied by the creator. It is not a medical, disability, or work-capacity determination.\n\n"
        f"## Completed mechanical tasks\n\n{completed_list}\n\n"
        f"## Scheduled for this session\n\n{scheduled}\n\n"
        f"## Preserved for a later session\n\n{deferred}\n\n"
        f"## Exact next step\n\n{next_step}\n\n"
        f"To regenerate the plan without rebuilding media:\n\n"
        f"```bash\npython build_short.py --manifest {manifest_rel.as_posix()} --capacity-profile {profile} --capacity-budget {plan['active_minute_budget']:.1f} --plan-only\n```\n\n"
        f"## Estimate boundary\n\n{plan['estimate_boundary']} Publication remains a separate human action.\n",
        encoding="utf-8",
    )
    return {"capacity_plan": plan_path, "resume_checkpoint": checkpoint_path, "plan": plan}


def build(manifest_path: Path, capacity_profile: str, capacity_budget: float | None) -> Path:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        fail("ffmpeg and ffprobe are required")
    manifest = load_manifest(manifest_path)
    validation = validate(manifest, manifest_path)
    out = output_directory(manifest)
    out.mkdir(parents=True, exist_ok=True)
    frames = out / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    for old in frames.glob("scene-*.png"):
        old.unlink()

    for index, scene in enumerate(manifest["scenes"], start=1):
        render_scene(scene, index, manifest, frames)

    captions = write_captions(manifest, out)
    audio = out / output_name(manifest, "assembled_audio_filename", "NARRATION.wav")
    audio_inputs = []
    for segment in manifest["audio_segments"]:
        audio_inputs.extend(["-i", str(resolve(segment["path"]))])
    labels = "".join(f"[{i}:a]" for i in range(len(manifest["audio_segments"])))
    run(["ffmpeg", "-y", *audio_inputs, "-filter_complex", f"{labels}concat=n={len(manifest['audio_segments'])}:v=0:a=1,aresample=48000[a]", "-map", "[a]", "-ac", "1", str(audio)])

    concat = out / output_name(manifest, "scene_manifest_filename", "SCENES.ffconcat")
    lines = ["ffconcat version 1.0"]
    for index, scene in enumerate(manifest["scenes"], start=1):
        frame = (frames / f"scene-{index:02d}.png").resolve()
        lines.extend([f"file '{frame}'", f"duration {scene['duration']}"])
    lines.append(f"file '{(frames / f'scene-{len(manifest['scenes']):02d}.png').resolve()}'")
    concat.write_text("\n".join(lines) + "\n", encoding="utf-8")

    silent = out / output_name(manifest, "silent_video_filename", "VISUALS.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-vf", f"scale={manifest['output']['width']}:{manifest['output']['height']},format=yuv420p", "-r", str(manifest["output"]["fps"]), "-c:v", "libx264", "-crf", "18", "-preset", "medium", str(silent)])

    final = out / manifest["output"]["filename"]
    # libass scales font sizes from its script resolution; a compact value is
    # intentional for a 1080x1920 Short. MarginV keeps captions above platform
    # controls and below the designed headline field.
    style = "FontName=Nimbus Sans,FontSize=8,PrimaryColour=&H00FFFFFF,OutlineColour=&H003D240B,BackColour=&H00000000,BorderStyle=1,Outline=1.2,Shadow=0,Alignment=2,MarginV=95"
    run(["ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-vf", f"subtitles={captions.as_posix()}:force_style='{style}'", "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-t", f"{validation['audio_duration']:.3f}", "-movflags", "+faststart", str(final)])

    contact = out / output_name(manifest, "contact_sheet_filename", "QA_CONTACT_SHEET.jpg")
    run(["ffmpeg", "-y", "-i", str(final), "-vf", "fps=1/6,scale=270:-1,tile=3x2:padding=10:margin=10:color=white", "-frames:v", "1", str(contact)])

    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration", "-of", "json", str(final)], cwd=ROOT, text=True, capture_output=True, check=True)
    completed_mechanical = {"start_build", "render_media", "build_captions", "build_qa"}
    capacity = write_capacity_outputs(manifest, manifest_path, out, capacity_profile, capacity_budget, completed_mechanical)
    report = {
        "artifact_id": manifest["artifact_id"],
        "artifact": str(final.relative_to(ROOT)),
        "captions": str(captions.relative_to(ROOT)),
        "contact_sheet": str(contact.relative_to(ROOT)),
        "governance": validation,
        "output_hashes": {
            "video": sha256(final),
            "captions": sha256(captions),
            "contact_sheet": sha256(contact),
        },
        "media_probe": json.loads(probe.stdout),
        "capacity_plan": str(capacity["capacity_plan"].relative_to(ROOT)),
        "resume_checkpoint": str(capacity["resume_checkpoint"].relative_to(ROOT)),
        "capacity_status": capacity["plan"]["status"],
        "release_boundary": "Human review and upload required; pipeline does not publish.",
    }
    report_path = out / output_name(manifest, "report_filename", "BUILD_REPORT.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return final


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="manifests/patients_paradox_short.json")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--capacity-profile", choices=sorted(CAPACITY_PROFILE_MINUTES), default="recovery")
    parser.add_argument("--capacity-budget", type=float)
    parser.add_argument("--completed-tasks", default="", help="Comma-separated task IDs already completed by the user")
    args = parser.parse_args()
    manifest_path = resolve(args.manifest)
    manifest = load_manifest(manifest_path)
    if args.validate_only:
        print(json.dumps(validate(manifest, manifest_path), indent=2))
        return
    if args.plan_only:
        out = output_directory(manifest)
        out.mkdir(parents=True, exist_ok=True)
        completed = {item.strip() for item in args.completed_tasks.split(",") if item.strip()}
        result = write_capacity_outputs(manifest, manifest_path, out, args.capacity_profile, args.capacity_budget, completed)
        print(json.dumps(result["plan"], indent=2))
        return
    build(manifest_path, args.capacity_profile, args.capacity_budget)


if __name__ == "__main__":
    main()
