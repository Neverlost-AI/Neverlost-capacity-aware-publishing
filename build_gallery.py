#!/usr/bin/env python3
"""Create the 3:2 Devpost gallery image from the validated Short frames."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
W, H = 1500, 1000
NAVY, BLUE, PAPER, INK, MUTED = "#0b243d", "#5aa6d1", "#f5f8fb", "#142b44", "#66788b"


def face(bold, size):
    name = "NimbusSans-Bold.otf" if bold else "NimbusSans-Regular.otf"
    return ImageFont.truetype(f"/usr/share/fonts/opentype/urw-base35/{name}", size=size)


def main():
    canvas = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 24, H), fill=BLUE)
    draw.text((70, 58), "ASSISTIVE CREATOR WORKFLOW", font=face(True, 25), fill=BLUE)
    draw.multiline_text((70, 135), "One approved idea.\nA complete governed\npublishing package.", font=face(True, 62), fill=INK, spacing=4)
    draw.text((70, 390), "Reduce repetition without losing authorship,", font=face(False, 29), fill=INK)
    draw.text((70, 430), "source custody, or human release authority.", font=face(False, 29), fill=INK)

    selected = [1, 3, 6]
    x_positions = [800, 1010, 1220]
    for x, index in zip(x_positions, selected):
        frame = Image.open(OUT / "frames" / f"scene-{index:02d}.png").convert("RGB")
        frame.thumbnail((190, 338), Image.Resampling.LANCZOS)
        canvas.paste(frame, (x, 100))

    draw.line((70, 560, 1430, 560), fill=BLUE, width=5)
    metrics = [("1", "validated command"), ("3 / 3", "governance tests"), ("36.93s", "vertical proof output"), ("0", "automated approvals")]
    for i, (value, label) in enumerate(metrics):
        x = 70 + i * 350
        draw.text((x, 625), value, font=face(True, 52), fill=BLUE)
        draw.text((x, 700), label, font=face(True, 24), fill=INK)

    draw.rounded_rectangle((70, 810, 1430, 930), 18, fill=NAVY)
    draw.text((105, 842), "PATIENT'S PARADOX SHORT", font=face(True, 25), fill=BLUE)
    draw.text((510, 837), "Source lock → video → captions → QA → human review", font=face(True, 31), fill=PAPER)

    logo = Image.open(ROOT / "assets/NVLT_Blue_Inlaid_Draft_v0_2.png").convert("RGBA")
    logo.thumbnail((80, 80), Image.Resampling.LANCZOS)
    canvas.paste(logo, (W - 115, 25), logo)
    target = OUT / "CAPACITY_AWARE_PUBLISHING_DEVPOST_GALLERY_3x2_v0_1.png"
    canvas.save(target)
    print(target)


if __name__ == "__main__":
    main()
