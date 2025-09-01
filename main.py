#!/usr/bin/env python3
"""
Entry point CLI for YTP Deluxe Generator
"""
import argparse
import json
import os
import tempfile
import shutil
import subprocess
import sys
import random

from ytp_generator import assets, effects, config as cfg, utils

def ensure_ffmpeg(ffmpeg_path):
    if shutil.which(ffmpeg_path) or os.path.isfile(ffmpeg_path):
        return ffmpeg_path
    raise FileNotFoundError(f"ffmpeg executable not found at '{ffmpeg_path}' and not on PATH.")

def load_config(path=None):
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return cfg.default_config()

def process_video(input_path, output_path, config, dry_run=False):
    ffmpeg_path = ensure_ffmpeg(config.get("ffmpeg_path", "ffmpeg"))
    tmpdir = tempfile.mkdtemp(prefix="ytp_tmp_")
    try:
        current = input_path
        stage = 0
        # Ensure assets exist
        assets.ensure_asset_dirs(config.get("assets_dir", "assets"))
        # Compose list of chosen effects
        for effect_conf in config.get("effect_chain", cfg.default_config()["effect_chain"]):
            effect_name = effect_conf["name"]
            enabled = effect_conf.get("enabled", True)
            prob = effect_conf.get("probability", 1.0)
            if not enabled:
                print(f"[SKIP] {effect_name} (disabled)")
                continue
            roll = random.random()
            if roll > prob:
                print(f"[SKIP] {effect_name} (prob={prob:.2f}, roll={roll:.2f})")
                continue
            stage += 1
            out_path = os.path.join(tmpdir, f"stage_{stage:02d}.mp4")
            print(f"[RUN] {effect_name} -> {os.path.basename(out_path)}")
            cmd = effects.build_effect_command(ffmpeg_path, current, out_path, effect_conf, config)
            print(" ".join(cmd) if isinstance(cmd, list) else cmd)
            if not dry_run:
                # run
                res = subprocess.run(cmd, shell=False)
                if res.returncode != 0:
                    raise RuntimeError(f"ffmpeg failed for effect {effect_name} with exit {res.returncode}")
            current = out_path
        # Final copy to output
        if not dry_run:
            shutil.copyfile(current, output_path)
        else:
            print(f"[DRY RUN] final output would be: {output_path}")
    finally:
        if dry_run:
            print(f"[DRY RUN] temporary files kept at {tmpdir} for inspection")
        else:
            shutil.rmtree(tmpdir)

def main():
    parser = argparse.ArgumentParser(description="YTP Deluxe Generator CLI")
    parser.add_argument("-i", "--input", required=True, help="Input video file")
    parser.add_argument("-o", "--output", required=True, help="Output video file")
    parser.add_argument("-c", "--config", help="Path to JSON config")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg commands without running")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print("Input file not found:", args.input, file=sys.stderr)
        sys.exit(2)
    cfg_data = load_config(args.config)
    try:
        process_video(args.input, args.output, cfg_data, dry_run=args.dry_run)
        print("Done.")
    except Exception as e:
        print("Error during processing:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()