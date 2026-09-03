#!/bin/sh
# Stitches frames/*.png into a small looping GIF for a landing page.
# Requires ffmpeg (brew install ffmpeg).
set -e

cd "$(dirname "$0")"

FPS=30

# palette gives a much cleaner/smaller GIF than a naive encode
ffmpeg -y -framerate "$FPS" -i frames/frame_%04d.png \
  -vf "fps=$FPS,split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer" \
  -loop 0 \
  terminal-intro.gif

echo "wrote terminal-intro.gif"
