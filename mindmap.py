#!/usr/bin/env python3
"""
Mindmap Generator - Entry Point
A simple wrapper to run the mindmap generator from the root directory.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run main
from main import main

if __name__ == "__main__":
    main()