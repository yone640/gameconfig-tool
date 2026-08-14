# -*- coding: utf-8 -*-
"""Tests for the converter."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gameconfig.converter import convert_workbook, write_json
from gameconfig.loader import load_excel
from gameconfig.schema import load_schema

from helpers import make_xlsx


def test_convert_coerces_types():
    d = tempfile.mkdtemp()
    path = make_xlsx({"items": [
        ["id", "name", "value"],
        ["1", "sword", "100"],
    ]}, dirpath=d)
    schema_path = os.path.join(d, "schema.json")
    with open(schema_path, "w", encoding="utf-8") as f:
        json.dump({"items": {"types": {"id": "int", "value": "int"}}}, f)
    specs = load_schema(schema_path)
    data = convert_workbook(load_excel(path), specs)
    row = data["items"]["rows"][0]
    assert row["id"] == 1 and isinstance(row["id"], int)
    assert row["value"] == 100 and isinstance(row["value"], int)
    assert row["name"] == "sword"


def test_write_json():
    d = tempfile.mkdtemp()
    out = os.path.join(d, "out")
    p = write_json({"a": {"rows": [{"x": 1}]}}, out, "a.json")
    assert os.path.exists(p)
    with open(p, "r", encoding="utf-8") as f:
        assert json.load(f)["a"]["rows"][0]["x"] == 1
