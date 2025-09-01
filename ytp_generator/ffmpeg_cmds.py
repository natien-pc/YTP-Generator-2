"""
Helpers for building ffmpeg command lines.
We construct explicit command lists (no shell). This helps on Windows.
"""
import os
from . import utils

def base_ffmpeg_cmd(ffmpeg_path):
    return [ffmpeg_path, "-y", "-loglevel", "warning"]

def build_reverse_cmd(ffmpeg_path, input_path, output_path):
    # Reverse video and audio (may be slower on large files)
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-vf", "reverse", "-af", "areverse", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", output_path]
    return cmd

def build_speed_cmd(ffmpeg_path, input_path, output_path, factor):
    # Video: setpts=PTS/factor
    # Audio: chain atempo factors
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    vf = f"setpts={1.0/float(factor)}*PTS"
    atempo_factors = utils.chain_atempo_factors(factor)
    atempo_str = ",".join(f"atempo={f}" for f in atempo_factors)
    cmd += ["-i", input_path, "-vf", vf, "-af", atempo_str, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", output_path]
    return cmd

def build_invert_cmd(ffmpeg_path, input_path, output_path):
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-vf", "negate", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "copy", output_path]
    return cmd

def build_mirror_cmd(ffmpeg_path, input_path, output_path):
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    # Horizontal mirror (hflip) and overlay copy to have both sides (simple)
    cmd += ["-i", input_path, "-vf", "hflip", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "copy", output_path]
    return cmd

def build_earrape_cmd(ffmpeg_path, input_path, output_path, gain_db=20):
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-af", f"volume={gain_db}dB", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", output_path]
    return cmd

def build_chorus_cmd(ffmpeg_path, input_path, output_path, level=0.7):
    # approximate chorus with multiple aecho calls; aecho params: in_gain:out_gain:delays:decays
    in_gain = 0.8 + 0.2 * level
    out_gain = 0.9
    delays = "60|90"
    decays = f"{0.4*level}|{0.3*level}"
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-af", f"aecho={in_gain}:{out_gain}:{delays}:{decays}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", output_path]
    return cmd

def build_vibrato_cmd(ffmpeg_path, input_path, output_path, depth=0.5):
    # Approx vibrato by varying sample rate slightly and then adjusting tempo back.
    # This is approximate: asetrate=sample_rate*(1+delta), atempo for correction
    # We'll apply a static pitch shift here (approximation)
    pitch_ratio = 1.0 + (depth - 0.5) * 0.3  # small pitch shift
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-af", f"asetrate=44100*{pitch_ratio},aresample=44100", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", output_path]
    return cmd

def build_overlay_audio_cmd(ffmpeg_path, input_path, output_path, overlays, volumes=None):
    """
    overlays: list of file paths to audio to overlay (mix)
    volumes: optional list of volumes for each overlay relative (0..1)
    """
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path]
    for o in overlays:
        cmd += ["-i", o]
    # build amix filter: inputs = 1 + len(overlays)
    ninputs = 1 + len(overlays)
    if volumes is None:
        volumes = [1.0] * len(overlays)
    # For simplicity, use amerge + pan or amix; amix normalizes
    amix = f"amix=inputs={ninputs}:normalize=0"
    cmd += ["-filter_complex", amix, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", output_path]
    return cmd

def build_overlay_image_cmd(ffmpeg_path, input_path, output_path, image_path, position="10:10"):
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-i", image_path, "-filter_complex", f"[0:v][1:v] overlay={position}:enable='between(t,0,99999)'", "-c:a", "copy", "-c:v", "libx264", "-preset", "veryfast", output_path]
    return cmd

def build_explosion_spam_cmd(ffmpeg_path, input_path, output_path, overlay_video, repeats=5):
    # Simple repeated overlay at random positions/times (scaffold)
    # Create filter_complex that overlays the same clip at different start times.
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-stream_loop", str(repeats-1), "-i", overlay_video]
    # naive overlay: overlay video on top-left always (scaffold)
    cmd += ["-filter_complex", "[0:v][1:v] overlay=10:10:enable='gte(t,0)'", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "copy", output_path]
    return cmd

def build_frame_shuffle_cmd(ffmpeg_path, input_path, output_path, seed=None, sample_rate=10):
    # Simple placeholder: extract frames, shuffle a subset, re-encode.
    # We'll rely on ffmpeg's fps filter to reduce frames, then concat - this is a scaffold.
    cmd = base_ffmpeg_cmd(ffmpeg_path)
    cmd += ["-i", input_path, "-vf", f"fps={sample_rate}", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "copy", output_path]
    return cmd

def build_random_cuts_cmd(ffmpeg_path, input_path, output_path, min_cuts=2, max_cuts=6):
    # Simple sample: cut into N pieces and concat in random order.
    # Implementation is in effects.py because requires file operations; this is a placeholder.
    raise NotImplementedError("Use effects.random_cuts for this operation.")