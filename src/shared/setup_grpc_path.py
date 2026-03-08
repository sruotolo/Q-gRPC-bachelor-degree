import sys
from pathlib import Path

"""
This script setups the gRPC path to be sure that gRPC generated files will be found by Python.
Starting from the file executing, it climbs up until it finds the project root.
While going up throughout the directories, it searches for the 'generated' directory.
If 'generated' is found then it is added to the sys.path otherwise an exception will be thrown.
"""

current_file = Path(__file__).resolve()
project_root = current_file.parent

while not (project_root / 'generated').exists():
    if project_root == project_root.parent:
        raise RuntimeError("Cannot find project root directory!")
    project_root = project_root.parent

sys.path.append(str(project_root / 'generated'))