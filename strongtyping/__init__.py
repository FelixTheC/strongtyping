#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 04.06.20
@author: felix
"""
import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
