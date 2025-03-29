# SPDX-FileCopyrightText: 2025 Stefan Helmert <stefan@entroserv.de>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import subprocess

import pytest


def test_simple():
    rv = subprocess.run(
        ["python3", "-m", "stl2step", "tests/resources/simple_poly.stl"],
        stderr=subprocess.PIPE,
    )
    lines = rv.stderr.decode(errors="ignore").split("\n")
    assert len(lines) == 1
    assert len(lines[0]) == 0
