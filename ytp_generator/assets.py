"""
Asset management: create and validate required asset directories.
"""
import os

ASSET_DIRS = [
    "adverts",
    "errors",
    "images",
    "memes",
    "memes_sounds",
    "overlays_videos",
    "sounds"
]

def ensure_asset_dirs(base_dir="assets"):
    base_dir = os.path.abspath(base_dir)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    for d in ASSET_DIRS:
        path = os.path.join(base_dir, d)
        if not os.path.exists(path):
            os.makedirs(path)
    return base_dir

def list_assets(base_dir="assets"):
    base_dir = os.path.abspath(base_dir)
    d = {}
    for name in ASSET_DIRS:
        p = os.path.join(base_dir, name)
        if os.path.isdir(p):
            d[name] = [os.path.join(p, f) for f in os.listdir(p)]
        else:
            d[name] = []
    return d