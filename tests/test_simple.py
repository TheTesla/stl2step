# SPDX-FileCopyrightText: 2025 Stefan Helmert <stefan@entroserv.de>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess

import pytest


def test_simple():
    stl_names = ["simple_poly", "hole_poly", "multi_poly", "multi_hole_multi_poly"]
    for name in stl_names:
        rv = subprocess.run(
            ["python3", "-m", "stl2step", f"tests/resources/{name}.stl"],
            stderr=subprocess.PIPE,
        )
        lines = rv.stderr.decode(errors="ignore").split("\n")
        assert len(lines) == 1
        assert len(lines[0]) == 0
