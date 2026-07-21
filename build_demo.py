#!/usr/bin/env python3
"""Build the under-three-minute judge demo for the publishing workflow."""

from __future__ import annotations

import json
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
WIDTH, HEIGHT = 1920, 1080
NAVY, BLUE, PAPER, INK, MUTED = "#0b243d", "#5aa6d1", "#f5f8fb", "#142b44", "#66788b"


def face(bold: bool, size: int):
    path = "/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf" if bold else "/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf"
    return ImageFont.truetype(path, size=size)


def duration(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes() / handle.getframerate()


def base(dark=False):
    image = Image.new("RGB", (WIDTH, HEIGHT), NAVY if dark else PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 28, HEIGHT), fill=BLUE)
    return image, draw


def header(draw, eyebrow, title, dark=False):
    fg = PAPER if dark else INK
    draw.text((90, 70), eyebrow, font=face(True, 30), fill=BLUE)
    draw.multiline_text((90, 135), title, font=face(True, 62), fill=fg, spacing=8)
    draw.rectangle((90, 285, 260, 291), fill=BLUE)


def footer(image, draw, number, dark=False):
    fg = PAPER if dark else INK
    draw.text((90, 1015), "CAPACITY-AWARE PUBLISHING · REVIEW-ONLY DEMO", font=face(True, 22), fill=fg)
    draw.text((1690, 1015), f"{number:02d} / 07", font=face(True, 22), fill=fg)
    logo = Image.open(ROOT / "assets/NVLT_Blue_Inlaid_Draft_v0_2.png").convert("RGBA")
    logo.thumbnail((82, 82), Image.Resampling.LANCZOS)
    image.paste(logo, (WIDTH - 120, HEIGHT - 105), logo)


def write_slide(index, image):
    path = OUT / "demo-frames" / f"slide-{index:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path


def slides():
    paths = []
    image, draw = base(True)
    draw.text((90, 80), "ASSISTIVE CREATOR TOOL", font=face(True, 30), fill=BLUE)
    draw.multiline_text((90, 220), "One approved idea.\nA complete governed\npublishing package.", font=face(True, 76), fill=PAPER, spacing=8)
    draw.text((90, 610), "Reduce repetition · preserve authorship · keep release human", font=face(False, 34), fill=PAPER)
    draw.line((90, 730, 1730, 730), fill=BLUE, width=5)
    draw.text((90, 780), "FIRST END-TO-END TEST", font=face(True, 27), fill=BLUE)
    draw.text((90, 830), "The Patient's Paradox Short", font=face(True, 43), fill=PAPER)
    footer(image, draw, 1, True); paths.append(write_slide(1, image))

    image, draw = base(); header(draw, "RECOVERY-AWARE MODE", "The creator sets the active-minute budget first.")
    items = [("8.0", "user-selected minutes"), ("7.6", "used or scheduled"), ("3", "tasks safely deferred"), ("1", "resume checkpoint")]
    for i, (num, label) in enumerate(items):
        x = 90 + (i % 2) * 860; y = 390 + (i // 2) * 220
        draw.rounded_rectangle((x, y, x + 760, y + 150), 18, fill="#ffffff", outline="#d6e2ec", width=3)
        draw.text((x + 35, y + 25), num, font=face(True, 55), fill=BLUE)
        draw.text((x + 210, y + 38), label, font=face(True, 34), fill=INK)
        draw.text((x + 210, y + 90), "Bounded session planning", font=face(False, 24), fill=MUTED)
    draw.text((90, 870), "User-provided planning input · not a medical or work-capacity determination", font=face(True, 26), fill=MUTED)
    footer(image, draw, 2); paths.append(write_slide(2, image))

    image, draw = base(); header(draw, "THE GOVERNED WORKFLOW", "Creative authority stays separate from mechanical production.")
    stages = [("1", "Approve", "Source + intent"), ("2", "Lock", "Manifest + hash"), ("3", "Build", "Media package"), ("4", "Validate", "Tests + QA"), ("5", "Review", "Human release")]
    for i, (num, label, sub) in enumerate(stages):
        x = 80 + i * 360
        draw.ellipse((x, 430, x + 78, 508), fill=BLUE)
        draw.text((x + 39, 469), num, font=face(True, 32), fill=PAPER, anchor="mm")
        draw.text((x, 545), label, font=face(True, 34), fill=INK)
        draw.text((x, 595), sub, font=face(False, 25), fill=MUTED)
        if i < 4: draw.line((x + 95, 469, x + 330, 469), fill="#b8cfdf", width=5)
    draw.rounded_rectangle((90, 750, 1830, 890), 18, fill=NAVY)
    draw.text((130, 785), "ONE COMMAND", font=face(True, 30), fill=BLUE)
    draw.text((400, 785), "Source checks → branded video → SRT → QA evidence", font=face(True, 38), fill=PAPER)
    footer(image, draw, 3); paths.append(write_slide(3, image))

    image, draw = base(True); header(draw, "BOUNDARIES ENFORCED IN CODE", "The runner refuses unsafe transformations.", True)
    checks = ["Changed controlled input", "Caption absent from narration", "Timing overlap or unsafe path", "Automation claims APPROVED"]
    for i, label in enumerate(checks):
        y = 370 + i * 125
        draw.rounded_rectangle((90, y, 980, y + 88), 14, fill="#132f4c")
        draw.text((125, y + 23), "BLOCK", font=face(True, 26), fill="#ffcc66")
        draw.text((280, y + 20), label, font=face(True, 34), fill=PAPER)
    draw.text((1120, 390), "15 / 15", font=face(True, 100), fill=BLUE)
    draw.text((1120, 505), "governance tests pass", font=face(True, 34), fill=PAPER)
    draw.text((1120, 615), "0", font=face(True, 100), fill=BLUE)
    draw.text((1120, 730), "automated release decisions", font=face(True, 34), fill=PAPER)
    footer(image, draw, 4, True); paths.append(write_slide(4, image))

    image, draw = base(); header(draw, "WORKING OUTPUT", "The Patient's Paradox Short · 36.93 seconds · vertical video")
    sheet = Image.open(OUT / "PATIENTS_PARADOX_SHORT_QA_CONTACT_SHEET_v0_1.jpg").convert("RGB")
    sheet.thumbnail((970, 650), Image.Resampling.LANCZOS)
    image.paste(sheet, (90, 340))
    stats = [("1080 × 1920", "vertical output"), ("10", "timed caption cues"), ("2", "source-bound excerpts"), ("1", "visual QA sheet")]
    for i, (value, label) in enumerate(stats):
        y = 370 + i * 140
        draw.text((1170, y), value, font=face(True, 54), fill=BLUE)
        draw.text((1170, y + 65), label, font=face(True, 27), fill=INK)
    footer(image, draw, 5); paths.append(write_slide(5, image))

    image, draw = base(); header(draw, "CODEX + GPT-5.6 SOL", "AI reduced technical repetition without taking authorship.")
    left = ["Generic manifest runner", "Recovery-aware planner", "Brand-optional renderer", "Caption and media pipeline"]
    right = ["Two distinct cases", "15 governance tests", "Resume checkpoints", "Hashed QA package"]
    for col, items in enumerate((left, right)):
        x = 110 + col * 870
        for i, label in enumerate(items):
            y = 380 + i * 125
            draw.text((x, y), "✓", font=face(True, 38), fill=BLUE)
            draw.text((x + 60, y), label, font=face(True, 35), fill=INK)
    draw.rounded_rectangle((90, 870, 1830, 955), 16, fill=NAVY)
    draw.text((130, 890), "Human: source, meaning, editorial direction, brand, and release authority", font=face(True, 31), fill=PAPER)
    footer(image, draw, 6); paths.append(write_slide(6, image))

    image, draw = base(True)
    draw.text((90, 80), "HUMAN AUTHORITY PRESERVED", font=face(True, 30), fill=BLUE)
    draw.multiline_text((90, 230), "AI creates leverage.\nThe author remains\nin command.", font=face(True, 82), fill=PAPER, spacing=12)
    draw.line((90, 650, 1700, 650), fill=BLUE, width=5)
    draw.text((90, 710), "Meaning · rights · approval · publication", font=face(True, 40), fill=PAPER)
    draw.text((90, 805), "The pipeline stops at REVIEW_ONLY.", font=face(True, 44), fill=BLUE)
    footer(image, draw, 7, True); paths.append(write_slide(7, image))
    return paths


def timecode(value):
    ms = round(value * 1000); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    narration = json.loads((ROOT / "demo_narration.json").read_text())
    frames = slides()
    audio = [OUT / "demo-audio" / f"section-{i:02d}.wav" for i in range(1, 8)]
    missing = [str(path) for path in audio if not path.exists()]
    if missing: raise SystemExit("Missing demo audio; run: node render_demo_audio.mjs")
    durations = [duration(path) for path in audio]

    concat_images = OUT / "demo-images.ffconcat"
    image_lines = ["ffconcat version 1.0"]
    for frame, seconds in zip(frames, durations):
        image_lines.extend([f"file '{frame.resolve()}'", f"duration {seconds:.3f}"])
    image_lines.append(f"file '{frames[-1].resolve()}'")
    concat_images.write_text("\n".join(image_lines) + "\n")

    audio_inputs = []
    for path in audio: audio_inputs.extend(["-i", str(path)])
    labels = "".join(f"[{i}:a]" for i in range(len(audio)))
    master = OUT / "demo-narration.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *audio_inputs, "-filter_complex", f"{labels}concat=n=7:v=0:a=1,aresample=48000[a]", "-map", "[a]", "-ac", "1", str(master)], check=True)

    captions = OUT / "PUBLISHING_WORKFLOW_DEMO_CAPTIONS_v0_4.srt"
    cursor = 0.0; blocks = []
    lead_silence = 0.22
    trail_silence = 0.43
    for i, (text, seconds) in enumerate(zip(narration, durations), 1):
        blocks.append(
            f"{i}\n{timecode(cursor + lead_silence)} --> "
            f"{timecode(cursor + seconds - trail_silence)}\n{text}\n"
        )
        cursor += seconds
    captions.write_text("\n".join(blocks))

    silent = OUT / "demo-visuals.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_images), "-vf", "scale=1920:1080,format=yuv420p", "-r", "30", "-c:v", "libx264", "-crf", "18", str(silent)], check=True)
    final = OUT / "CAPACITY_AWARE_PUBLISHING_WORKFLOW_DEMO_REVIEW_ONLY_v0_4.mp4"
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y",
        "-i", str(silent), "-i", str(master),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-crf", "18",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", str(final)
    ], check=True)
    print(final)


if __name__ == "__main__":
    main()
