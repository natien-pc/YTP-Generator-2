"""
Utility helpers
"""
import random
import os
import math
import shutil

def pick_random_files(file_list, max_count=1):
    file_list = [f for f in file_list if os.path.isfile(f)]
    if not file_list:
        return []
    k = min(max_count, len(file_list))
    return random.sample(file_list, k)

def clamp(v, a, b):
    return max(a, min(b, v))

def make_temp_path(tmpdir, base_name, ext=".mp4"):
    return os.path.join(tmpdir, base_name + ext)

def chain_atempo_factors(target):
    """
    ffmpeg's atempo supports between 0.5 and 2.0. To achieve arbitrary speed change,
    chain multiple atempo filters.
    Returns a list of float factors that multiply to 'target'.
    """
    factors = []
    t = target
    # Decompose into multiples within [0.5, 2.0]
    while t < 0.5:
        factors.append(0.5)
        t /= 0.5
    while t > 2.0:
        factors.append(2.0)
        t /= 2.0
    factors.append(t)
    # Clean tiny rounding issues
    factors = [round(f, 5) for f in factors if f > 0]
    return factors