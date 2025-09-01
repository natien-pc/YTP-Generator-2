```markdown
# YTP Deluxe Generator (Windows 8.1 + ffmpeg)

A Python-based YouTube Poop (YTP) deluxe generator scaffold and implementation for Windows 8.1 environments using ffmpeg. This project provides a CLI and modular effect functions (many implemented with ffmpeg filterchains). It is designed to be safe to run on older Windows with a local ffmpeg binary (you may need to provide full path to ffmpeg.exe in the config).

Features included (implemented or scaffolded):
- Select own:
  - Add Random Sound (audio overlay)
  - Reverse Clip (video & audio)
  - Speed Up / Slow Down (chained atempo for large changes)
  - Chorus Effect (approx via aecho)
  - Vibrato / Pitch Bend (asetrate + atempo approximation)
  - Stutter Loop
  - Earrape Mode (large gain)
  - Auto-Tune Chaos (placeholder — requires external autotune tool)
  - Add Dance & Squidward Mode (video transforms: rotate/wobble scaffolds)
  - Invert Colors
  - Rainbow Overlay (overlay PNG/GIF, user-provided)
  - Mirror Mode
  - Sus Effect (random pitch/tempo)
  - Explosion Spam (repetitive overlays)
  - Frame Shuffle (placeholder; includes a simple implementation)
  - Meme Injection (overlay image/audio; user provides assets)
  - Sentence Mixing / Random Clip Shuffle / Random Cuts
  - Effect toggles per effect and per-effect probability and max level

Assets folder structure:
- assets/
  - adverts/
  - errors/
  - images/
  - memes/
  - memes_sounds/
  - overlays_videos/
  - sounds/

Requirements:
- Python 3.7+ (3.8+ recommended)
- ffmpeg available on PATH or provide full path in config (ffmpeg.exe for Windows)
- pip packages: pillow, numpy

Install:
1. Create virtualenv and activate it.
2. pip install -r requirements.txt
3. Put ffmpeg.exe in PATH or set path in config.json
4. Populate the assets folders with your overlays, sounds, memes etc.

Usage:
- Basic:
  python main.py -i path\to\input.mp4 -o path\to\output.mp4

- Using config:
  python main.py -i input.mp4 -o out.mp4 -c config.json

- Dry run (print ffmpeg commands without running):
  python main.py -i input.mp4 -o out.mp4 --dry-run

Notes and limitations:
- This project uses subprocess calls to ffmpeg. On Windows 8.1, provide the full path to ffmpeg.exe if not on PATH.
- Some filters (e.g., areverse, aresample) may vary with ffmpeg builds. If a filter is missing, check your ffmpeg build or adjust commands.
- Auto-Tune Chaos is a placeholder — hooking into a real autotune tool would require that tool's CLI and license.
- Frame shuffle and some complex video warps are scaffolded; simple implementations are included, and you can extend them.

What's next (developer notes):
- Populate assets to get great results quickly (images, gifs, short overlay videos and sounds).
- Test on a sample video and iterate on effect probabilities and levels in config.json.
- If you want a GUI, I can add a simple Tkinter interface compatible with Windows 8.1.

License: MIT
```