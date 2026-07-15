"""
Wrapper: delegates to the real Semira Fashion Flask app at the workspace root.
Uses runpy so __file__ is set correctly and Flask finds its templates/static dirs.
"""
import os, sys, runpy

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(root)
sys.path.insert(0, root)

runpy.run_path(os.path.join(root, "app.py"), run_name="__main__")
