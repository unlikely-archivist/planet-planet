"""
Renders a typing-terminal animation as a PNG frame sequence.
Run: python3 make-terminal-frames.py
Then stitch with assemble-gif.sh (ffmpeg).
"""

from PIL import Image, ImageDraw, ImageFont

# ---- one-line config you can tweak ----
COLOR_SCHEME = "green"   # "green", "white", or "amber"
WIDTH, HEIGHT = 800, 420
FONT_SIZE = 20
LINE_SPACING = 30
FPS = 30
HOLD_SECONDS_AFTER_LINE = 0.5   # pause once a line finishes typing
FINAL_HOLD_SECONDS = 2.0        # pause on the last completed frame

SCHEMES = {
    "green":  {"bg": (10, 12, 10), "fg": (80, 255, 120), "dim": (40, 140, 65)},
    "white":  {"bg": (12, 12, 12), "fg": (235, 235, 235), "dim": (120, 120, 120)},
    "amber":  {"bg": (12, 10, 6), "fg": (255, 176, 60), "dim": (150, 100, 30)},
}
colors = SCHEMES[COLOR_SCHEME]

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
font = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=0)       # regular
font_bold = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=1)  # bold

# Each entry: (text, is_prompt_or_success, pause_after_typing_in_frames)
# is_prompt_or_success controls color emphasis (bold/bright vs dim log color)
LINES = [
    ("$ planet create --name=auto", "prompt"),
    ("[planet-engine] existence check... planet (+1)", "log"),
    ("[namegen] sampling from existence possibilities...", "log"),
    ("[namegen] -> terra-9, vek-null, orin-4, planet-planet", "log"),
    ("[namegen] selected: planet-planet", "log"),
    ("✓ created planet-planet.planet", "success"),
]

MARGIN_X = 24
MARGIN_Y = 24

def line_color(kind):
    if kind == "prompt":
        return colors["fg"]
    if kind == "success":
        return colors["fg"]
    return colors["dim"]

def render_frame(completed_lines, typing_line_text, cursor_visible):
    img = Image.new("RGB", (WIDTH, HEIGHT), colors["bg"])
    draw = ImageDraw.Draw(img)
    y = MARGIN_Y

    for text, kind in completed_lines:
        f = font_bold if kind in ("prompt", "success") else font
        draw.text((MARGIN_X, y), text, font=f, fill=line_color(kind))
        y += LINE_SPACING

    if typing_line_text is not None:
        text, kind = typing_line_text
        f = font_bold if kind in ("prompt", "success") else font
        draw.text((MARGIN_X, y), text, font=f, fill=line_color(kind))
        if cursor_visible:
            w = draw.textlength(text, font=f)
            cursor_h = FONT_SIZE + 4
            draw.rectangle(
                [MARGIN_X + w + 2, y - 2, MARGIN_X + w + 12, y - 2 + cursor_h],
                fill=colors["fg"],
            )

    return img

def main():
    frame_idx = 0
    completed = []

    def save(img):
        nonlocal frame_idx
        img.save(f"frames/frame_{frame_idx:04d}.png")
        frame_idx += 1

    for text, kind in LINES:
        # type out this line character by character
        for i in range(1, len(text) + 1):
            partial = text[:i]
            img = render_frame(completed, (partial, kind), cursor_visible=True)
            save(img)

        # hold with a blinking cursor once the line is fully typed
        hold_frames = int(FPS * HOLD_SECONDS_AFTER_LINE)
        for i in range(hold_frames):
            blink_on = (i // (FPS // 4 or 1)) % 2 == 0
            img = render_frame(completed, (text, kind), cursor_visible=blink_on)
            save(img)

        completed.append((text, kind))

    # final hold on the completed screen
    final_hold_frames = int(FPS * FINAL_HOLD_SECONDS)
    for i in range(final_hold_frames):
        blink_on = (i // (FPS // 4 or 1)) % 2 == 0
        img = render_frame(completed, None, cursor_visible=False)
        draw = ImageDraw.Draw(img)
        y = MARGIN_Y + LINE_SPACING * len(completed)
        if blink_on:
            draw.rectangle([MARGIN_X, y - 2, MARGIN_X + 10, y - 2 + FONT_SIZE + 4], fill=colors["fg"])
        save(img)

    print(f"wrote {frame_idx} frames to frames/ at {WIDTH}x{HEIGHT}, {FPS}fps")

if __name__ == "__main__":
    main()
