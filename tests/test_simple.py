import subprocess

import pytest


def test_simple():
    # rv = subprocess.run(["python3", "stl2step/stl2step.py", "simple_poly.stl"], stderr=subprocess.PIPE)
    rv = subprocess.run(
        ["python3", "-m", "stl2step", "simple_poly.stl"], stderr=subprocess.PIPE
    )
    lines = rv.stderr.decode(errors="ignore").split("\n")
    assert len(lines) == 1
    assert len(lines[0]) == 0
