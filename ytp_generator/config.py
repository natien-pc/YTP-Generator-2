import json
import os

def default_config():
    """
    Return a default configuration dictionary.
    Edit probabilities, levels and ffmpeg path for Windows 8.1 environment.
    """
    here = os.path.abspath(os.getcwd())
    return {
        "ffmpeg_path": "ffmpeg",  # set to full path to ffmpeg.exe if needed
        "assets_dir": os.path.join(here, "assets"),
        "effect_chain": [
            {"name": "random_sound_overlay", "enabled": True, "probability": 0.9, "max_sounds": 2},
            {"name": "reverse", "enabled": True, "probability": 0.15},
            {"name": "speed_change", "enabled": True, "probability": 0.5, "min_factor": 0.25, "max_factor": 3.0},
            {"name": "chorus", "enabled": True, "probability": 0.25, "level": 0.8},
            {"name": "vibrato", "enabled": True, "probability": 0.2, "depth": 0.8},
            {"name": "stutter", "enabled": True, "probability": 0.3, "max_repeats": 6},
            {"name": "earrape", "enabled": True, "probability": 0.05, "gain_db": 20},
            {"name": "autotune_chaos", "enabled": False, "probability": 0.1},
            {"name": "dance_squidward", "enabled": True, "probability": 0.25},
            {"name": "invert_colors", "enabled": True, "probability": 0.15},
            {"name": "rainbow_overlay", "enabled": True, "probability": 0.25},
            {"name": "mirror", "enabled": True, "probability": 0.1},
            {"name": "sus_effect", "enabled": True, "probability": 0.2},
            {"name": "explosion_spam", "enabled": True, "probability": 0.12},
            {"name": "frame_shuffle", "enabled": True, "probability": 0.2},
            {"name": "meme_injection", "enabled": True, "probability": 0.4},
            {"name": "random_cuts", "enabled": True, "probability": 0.8, "min_cuts": 2, "max_cuts": 8}
        ]
    }