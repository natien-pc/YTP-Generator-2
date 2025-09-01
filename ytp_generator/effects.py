"""
High level effect orchestration: choose ffmpeg command builders and implement operations
that require multi-step file ops (random cuts, stutter, etc.).
"""
import os
import random
import shutil
import tempfile
import subprocess

from . import ffmpeg_cmds, assets, utils

def build_effect_command(ffmpeg_path, input_path, output_path, effect_conf, global_config):
    name = effect_conf["name"]
    if name == "reverse":
        return ffmpeg_cmds.build_reverse_cmd(ffmpeg_path, input_path, output_path)
    if name == "speed_change":
        factor = random.uniform(effect_conf.get("min_factor", 0.5), effect_conf.get("max_factor", 2.0))
        return ffmpeg_cmds.build_speed_cmd(ffmpeg_path, input_path, output_path, factor)
    if name == "invert_colors":
        return ffmpeg_cmds.build_invert_cmd(ffmpeg_path, input_path, output_path)
    if name == "mirror":
        return ffmpeg_cmds.build_mirror_cmd(ffmpeg_path, input_path, output_path)
    if name == "earrape":
        gain = effect_conf.get("gain_db", 20)
        return ffmpeg_cmds.build_earrape_cmd(ffmpeg_path, input_path, output_path, gain)
    if name == "chorus":
        level = effect_conf.get("level", 0.7)
        return ffmpeg_cmds.build_chorus_cmd(ffmpeg_path, input_path, output_path, level)
    if name == "vibrato":
        depth = effect_conf.get("depth", 0.5)
        return ffmpeg_cmds.build_vibrato_cmd(ffmpeg_path, input_path, output_path, depth)
    if name == "random_sound_overlay":
        # find some sounds
        base_assets = assets.list_assets(global_config.get("assets_dir", "assets"))
        candidates = base_assets.get("sounds", []) + base_assets.get("memes_sounds", [])
        picks = utils.pick_random_files(candidates, max_count=effect_conf.get("max_sounds", 1))
        if not picks:
            # fallback: copy input to output (no change)
            return ["copy", input_path, output_path]
        return ffmpeg_cmds.build_overlay_audio_cmd(ffmpeg_path, input_path, output_path, picks)
    if name == "rainbow_overlay":
        base_assets = assets.list_assets(global_config.get("assets_dir", "assets"))
        overlays = base_assets.get("images", []) + base_assets.get("memes", [])
        if not overlays:
            return ["copy", input_path, output_path]
        pick = random.choice(overlays)
        return ffmpeg_cmds.build_overlay_image_cmd(ffmpeg_path, input_path, output_path, pick)
    if name == "explosion_spam":
        base_assets = assets.list_assets(global_config.get("assets_dir", "assets"))
        vids = base_assets.get("overlays_videos", [])
        if not vids:
            return ["copy", input_path, output_path]
        pick = random.choice(vids)
        repeats = random.randint(2, effect_conf.get("max_repeats", 6))
        return ffmpeg_cmds.build_explosion_spam_cmd(ffmpeg_path, input_path, output_path, pick, repeats=repeats)
    if name == "frame_shuffle":
        # simple scaffold that reduces fps; real shuffle would extract frames + reorder + re-encode
        sample_rate = effect_conf.get("sample_rate", 15)
        return ffmpeg_cmds.build_frame_shuffle_cmd(ffmpeg_path, input_path, output_path, sample_rate=sample_rate)
    if name == "meme_injection":
        base_assets = assets.list_assets(global_config.get("assets_dir", "assets"))
        imgs = base_assets.get("memes", []) + base_assets.get("images", [])
        sounds = base_assets.get("memes_sounds", []) + base_assets.get("sounds", [])
        if not imgs and not sounds:
            return ["copy", input_path, output_path]
        # If both present: overlay image then overlay audio (two-step)
        tmp = tempfile.mktemp(suffix=".mp4")
        if imgs:
            img = random.choice(imgs)
            cmd1 = ffmpeg_cmds.build_overlay_image_cmd(ffmpeg_path, input_path, tmp, img, position="10:10")
            return cmd1 if not sounds else ffmpeg_cmds.build_overlay_audio_cmd(ffmpeg_path, tmp, output_path, [random.choice(sounds)])
        else:
            # only sound overlay
            return ffmpeg_cmds.build_overlay_audio_cmd(ffmpeg_path, input_path, output_path, [random.choice(sounds)])
    if name == "stutter":
        # Stutter loop: pick a short segment and repeat it several times
        repeats = random.randint(2, effect_conf.get("max_repeats", 5))
        return _build_stutter_cmd(ffmpeg_path, input_path, output_path, repeats=repeats)
    if name == "random_cuts":
        return _build_random_cuts_cmd(ffmpeg_path, input_path, output_path, effect_conf)
    # placeholder/disabled features: return copy
    return ["copy", input_path, output_path]

def _build_stutter_cmd(ffmpeg_path, input_path, output_path, repeats=4):
    # This implementation uses ffmpeg to trim a 0.2s sample and concat it repeated times,
    # then concatenate with original.
    tmpdir = tempfile.mkdtemp(prefix="stutter_")
    try:
        # produce a small clip
        sample = os.path.join(tmpdir, "sample.mp4")
        # take first 0.2s (could be random)
        cmd_trim = [ffmpeg_path, "-y", "-loglevel", "warning", "-i", input_path, "-ss", "0", "-t", "0.2", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", sample]
        subprocess.run(cmd_trim, check=True)
        list_file = os.path.join(tmpdir, "list.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for i in range(repeats):
                f.write(f"file '{sample}'\n")
        repeated = os.path.join(tmpdir, "repeated.mp4")
        cmd_concat = [ffmpeg_path, "-y", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", repeated]
        subprocess.run(cmd_concat, check=True)
        # now concat repeated with original
        concat_list = os.path.join(tmpdir, "concat.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            f.write(f"file '{repeated}'\n")
            f.write(f"file '{input_path}'\n")
        cmd_final = [ffmpeg_path, "-y", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", output_path]
        return cmd_final
    finally:
        # don't delete immediately; ffmpeg may still read files when returning command list
        shutil.rmtree(tmpdir, ignore_errors=True)

def _get_duration_with_ffprobe(ffprobe_path, input_path):
    """Return duration in seconds using ffprobe. Raises subprocess.CalledProcessError on failure."""
    cmd = [ffprobe_path, "-v", "error", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_path]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    out = proc.stdout.strip()
    try:
        return float(out)
    except Exception:
        # As a fallback try parsing stderr for duration-like strings
        raise ValueError(f"Could not parse duration from ffprobe output: {out!r}")

def _find_ffprobe(ffmpeg_path):
    """Try to locate ffprobe. Prefer same directory as ffmpeg_path, then system PATH 'ffprobe'."""
    # If ffmpeg_path is full path, check same dir for ffprobe
    try:
        ffmpeg_dir = os.path.dirname(os.path.abspath(ffmpeg_path))
        candidate = os.path.join(ffmpeg_dir, "ffprobe")
        candidate_exe = candidate + (".exe" if os.name == "nt" else "")
        if os.path.isfile(candidate_exe):
            return candidate_exe
        # try 'ffprobe' on PATH
        from shutil import which
        wp = which("ffprobe")
        if wp:
            return wp
    except Exception:
        pass
    # fallback to 'ffprobe' (may fail later if not installed)
    return "ffprobe"

def _build_random_cuts_cmd(ffmpeg_path, input_path, output_path, effect_conf):
    """
    Split file into N cuts and re-order randomly then concat.
    This implementation uses ffprobe (preferred) to get duration instead of moviepy so
    it works when moviepy is not installed.
    """
    tmpdir = tempfile.mkdtemp(prefix="cuts_")
    try:
        # find ffprobe
        ffprobe = _find_ffprobe(ffmpeg_path)
        # get duration
        try:
            duration = _get_duration_with_ffprobe(ffprobe, input_path)
        except Exception as e:
            # If ffprobe fails, raise informative error
            raise RuntimeError(f"Unable to determine input duration (ffprobe error): {e}")
        if duration <= 0:
            raise RuntimeError("Input duration is zero or could not be determined.")

        cuts = random.randint(effect_conf.get("min_cuts", 2), effect_conf.get("max_cuts", 6))
        # create unique random cut points (exclude 0 and duration)
        points = sorted({round(random.uniform(0.0, duration), 6) for _ in range(cuts - 1)})
        times = [0.0] + points + [duration]
        pieces = []
        for i in range(len(times)-1):
            start = max(0.0, times[i])
            end = min(duration, times[i+1])
            # ensure minimal length
            if end - start < 0.05:
                # skip extremely short pieces
                continue
            out_piece = os.path.join(tmpdir, f"piece_{i:03d}.mp4")
            # Use -ss ... -to ... -i ... -c copy for faster cutting where possible.
            cmd = [ffmpeg_path, "-y", "-loglevel", "warning", "-ss", str(start), "-to", str(end), "-i", input_path, "-c", "copy", out_piece]
            subprocess.run(cmd, check=True)
            pieces.append(out_piece)
        if not pieces:
            raise RuntimeError("No pieces were created for random cuts.")
        random.shuffle(pieces)
        list_file = os.path.join(tmpdir, "concat_list.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for p in pieces:
                f.write(f"file '{p}'\n")
        final_cmd = [ffmpeg_path, "-y", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_path]
        return final_cmd
    finally:
        # cleanup; if ffmpeg still reading files this will be ignored/raise but we ignore errors
        shutil.rmtree(tmpdir, ignore_errors=True)