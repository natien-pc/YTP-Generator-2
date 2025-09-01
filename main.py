#!/usr/bin/env python3
"""
Entry point CLI for YTP Deluxe Generator
Supports a simple Tkinter GUI via --gui
"""
import argparse
import os
import sys

from ytp_generator import config as cfg

def main_cli():
    import json
    import subprocess
    import tempfile
    import shutil
    import random
    import argparse
    from ytp_generator import processor

    parser = argparse.ArgumentParser(description="YTP Deluxe Generator CLI")
    parser.add_argument("-i", "--input", required=True, help="Input video file")
    parser.add_argument("-o", "--output", required=True, help="Output video file")
    parser.add_argument("-c", "--config", help="Path to JSON config")
    parser.add_argument("--dry-run", action="store_true", help="Print ffmpeg commands without running")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print("Input file not found:", args.input, file=sys.stderr)
        sys.exit(2)
    cfg_data = cfg.default_config()
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                cfg_data = json.load(f)
        except Exception as e:
            print("Failed to load config:", e, file=sys.stderr)
            sys.exit(2)
    try:
        processor.process_video(args.input, args.output, cfg_data, dry_run=args.dry_run)
        print("Done.")
    except Exception as e:
        print("Error during processing:", e, file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--gui", action="store_true", help="Open Tkinter GUI")
    parser.add_argument("-h", "--help", action="store_true", help="Show help")
    args, rest = parser.parse_known_args()
    if args.gui:
        # Launch GUI
        from ytp_generator.gui import YTPGui
        YTPGui().run()
        return
    # Otherwise fallback to CLI behavior
    main_cli()

if __name__ == "__main__":
    main()