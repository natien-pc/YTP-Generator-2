"""
Processing pipeline moved out of the top-level script so the GUI can reuse it.
"""
import os
import tempfile
import shutil
import subprocess
import random

from . import assets, effects, config as cfg, utils

def ensure_ffmpeg(ffmpeg_path):
    # Accept either a bare executable name (on PATH) or a full path
    if shutil.which(ffmpeg_path) or os.path.isfile(ffmpeg_path):
        return ffmpeg_path
    raise FileNotFoundError(f"ffmpeg executable not found at '{ffmpeg_path}' and not on PATH.")

def process_video(input_path, output_path, config, dry_run=False, progress_callback=None):
    """
    Run the effect chain defined in config on input_path and write to output_path.

    progress_callback: optional callable(stage_index, total_stages, message) for UI updates.
    """
    ffmpeg_path = ensure_ffmpeg(config.get("ffmpeg_path", "ffmpeg"))
    tmpdir = tempfile.mkdtemp(prefix="ytp_tmp_")
    try:
        current = input_path
        stage = 0
        assets.ensure_asset_dirs(config.get("assets_dir", "assets"))
        chain = config.get("effect_chain", cfg.default_config()["effect_chain"])
        total = sum(1 for e in chain if e.get("enabled", True))
        for effect_conf in chain:
            name = effect_conf["name"]
            enabled = effect_conf.get("enabled", True)
            if not enabled:
                if progress_callback:
                    progress_callback(stage, total, f"Skipping {name} (disabled)")
                continue
            prob = effect_conf.get("probability", 1.0)
            roll = random.random()
            if roll > prob:
                if progress_callback:
                    progress_callback(stage, total, f"Skipping {name} (prob {prob:.2f} roll {roll:.2f})")
                continue
            stage += 1
            out_path = os.path.join(tmpdir, f"stage_{stage:02d}.mp4")
            if progress_callback:
                progress_callback(stage, total, f"Running {name} -> {os.path.basename(out_path)}")
            cmd = effects.build_effect_command(ffmpeg_path, current, out_path, effect_conf, config)
            # Some effect builders may return a ["copy", in, out] pseudo-command => do simple copy
            if isinstance(cmd, list) and len(cmd) == 3 and cmd[0] == "copy":
                # ensure directories
                shutil.copyfile(cmd[1], cmd[2])
            else:
                if dry_run:
                    # report full command as string
                    if progress_callback:
                        progress_callback(stage, total, "DRY RUN: " + " ".join(cmd if isinstance(cmd, list) else [str(cmd)]))
                else:
                    # Execute command list
                    subprocess.run(cmd, check=True)
            current = out_path
        # Final copy to requested output
        if dry_run:
            if progress_callback:
                progress_callback(stage, total, f"DRY RUN: final output would be: {output_path}")
        else:
            shutil.copyfile(current, output_path)
            if progress_callback:
                progress_callback(stage, total, f"Saved output: {output_path}")
    finally:
        # keep tmpdir when dry_run so user can inspect; otherwise remove
        if dry_run:
            if progress_callback:
                progress_callback(stage, total, f"Temporary files kept at: {tmpdir}")
        else:
            shutil.rmtree(tmpdir, ignore_errors=True)