# Simple script to run bot
# Usage: python start.py

import subprocess
import sys
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Path to venv python
venv_python = os.path.join(script_dir, "venv", "Scripts", "python.exe")

if os.path.exists(venv_python):
    print("🚀 Starting TTS Bot with venv...")
    subprocess.run([venv_python, "tts_bot.py"])
else:
    print("❌ venv not found! Run: python -m venv venv")
    print("Then: .\\venv\\Scripts\\Activate.ps1")
    print("Then: pip install -r requirements.txt")
    sys.exit(1)
