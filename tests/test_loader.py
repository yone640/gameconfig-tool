# -*- coding: utf-8 -*-
"""Tests for the Excel loader."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gameconfig.loader import load_excel, load_directory

from helpers import make_xlsx


def test_load_basic():
    path = make_xlsx({"items": [
        ["id", "name", "value"],
        [1, "sword", 100],
        [2, "shield", 50],
    ]})
    wb = load_excel(path)
    assert len(wb.sheets) == 1
    sheet = wb.sheet("items")
    assert sheet.columns == ["id", "name", "value"]
    assert len(sheet.rows) == 2
    assert sheet.rows[0] == {"id": 1, "name": "sword", "value": 100}


def test_load_skips_blank_rows():
    path = make_xlsx({"items": [
        ["id", "name"],
        [1, "a"],
        [None, None],
        [2, "b"],
    ]})
    wb = load_excel(path)
    assert len(wb.sheet("items").rows) == 2


def test_load_directory_filters_ext():
    d = tempfile.mkdtemp()
    make_xlsx({"a": [["id"], [1]]}, dirpath=d, filename="a.xlsx")
    make_xlsx({"b": [["id"], [2]]}, dirpath=d, filename="b.xlsx")
    with open(os.path.join(d, "notes.txt"), "w") as f:
        f.write("ignore me")
    wbs = load_directory(d)
    assert len(wbs) == 2
