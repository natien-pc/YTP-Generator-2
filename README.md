# YTP Deluxe Generator (Windows 8.1 + ffmpeg)

A Python-based YouTube Poop (YTP) deluxe generator scaffold and implementation for Windows 8.1 environments using ffmpeg. This project provides a CLI and a simple Tkinter GUI (Windows-compatible) plus modular effect functions (many implemented with ffmpeg filterchains). It is designed to be runnable on older Windows with a local ffmpeg binary (provide full path to ffmpeg.exe in the config if needed).

New: Added a simple Tkinter GUI for Windows 8.1 to make it easy to pick assets, toggle effects, tune probabilities/levels and run the generator.

Features (implemented or scaffolded):
- Random Sound overlay (audio overlay)
- Reverse Clip (video & audio)
- Speed Up / Slow Down
- Chorus Effect (aecho approximation)
- Vibrato / Pitch Bend (asetrate approximation)
- Stutter Loop
- Earrape Mode
- Auto-Tune Chaos (placeholder)
- Dance & Squidward Mode (scaffold)
- Invert Colors
- Rainbow Overlay (overlay PNG/GIF user-provided)
- Mirror Mode
- Sus Effect (random pitch/tempo)
- Explosion Spam (repetitive overlays scaffold)
- Frame Shuffle (simple implementation)
- Meme Injection (overlay image/audio)
- Sentence Mixing / Random Clip Shuffle / Random Cuts
- Effect toggles per-effect and per-effect probability and max level

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
- ffmpeg available on PATH or provide full path to ffmpeg.exe in the config (Windows)
- pip packages: pillow, numpy
- tkinter is part of the standard library (should be available on Windows); no extra install required for it.

Install:
1. Create virtualenv and activate it.
2. pip install -r requirements.txt
3. Put ffmpeg.exe in PATH or set path in config.json
4. Populate the assets folders with your overlays, sounds, memes etc.

Usage:
- CLI (as before):
  python main.py -i path\to\input.mp4 -o path\to\output.mp4

- Start the GUI:
  python main.py --gui

- Using config:
  python main.py -i input.mp4 -o out.mp4 -c config.json

- Dry run (print ffmpeg commands without running):
  python main.py -i input.mp4 -o out.mp4 --dry-run

Notes:
- The GUI is intentionally simple and built with Tkinter for broad Windows 8.1 compatibility.
- The GUI writes a temporary config from UI settings and runs the same processing pipeline as the CLI (so behavior should match).
- Long ffmpeg operations are executed in a background thread to keep the UI responsive.
- On Windows, if ffmpeg calls fail, try giving the full path to ffmpeg.exe in the GUI config.

What's next:
- Improve progress reporting by parsing ffmpeg stderr and streaming into the GUI log.
- Add a GUI-based asset previewer and drag & drop.
- Implement richer frame-shuffle (frame extraction + reorder) if you want a more chaotic effect.

```
