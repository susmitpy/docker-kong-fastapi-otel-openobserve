"""
Cleans Up / Resets environment by removing volume mapped data
"""

import os
import shutil

folders = ["./data/openobserve", "./data/postgres"]

for folder in folders:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"Removed {folder}")

    os.mkdir(folder)

print("Cleaned up environment and reset data folders")