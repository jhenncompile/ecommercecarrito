#!/usr/bin/env python
# mine.py - Shortcut for migrations
import sys
import os
import subprocess
from pathlib import Path

# Add current dir to path to find scripts_utiles
sys.path.append(str(Path(__file__).parent))

if __name__ == '__main__':
    script_path = os.path.join('scripts_utiles', 'migrations.py')
    args = sys.argv[1:] if len(sys.argv) > 1 else ['sync']
    
    # Use the same python that is running this script
    subprocess.run([sys.executable, script_path] + args)
