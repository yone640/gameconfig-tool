# -*- coding: utf-8 -*-
"""Tests for the validator."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gameconfig.loader import load_directory
from gameconfig.schema import load_schema
from gameconfig.validator import validate_all

from helpers import make_xlsx


def _schema(tmpdir, cfg):
    path = os.path.join(tmpdir, "schema.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)
    return load_schema(path)


def _run(dirpath, cfg):
    specs = _schema(dirpath, cfg)
    wbs = load_directory(dirpath)
    results = validate_all(wbs, specs)
    issues = [i for res in results.values() for i in res.issues]
    return issues


def test_duplicate_unique_key():
    d = tempfile.mkdtemp()
    make_xlsx({"items": [
        ["id", "name"],
        [1, "a"],
        [1, "b"],
    ]}, dirpath=d, filename="items.xlsx")
    issues = _run(d, {"items": {"unique": ["id"], "types": {"id": "int"}}})
    assert any(i.rule == "unique" for i in issues)


def test_duplicate_across_files():
    d = tempfile.mkdtemp()
    make_xlsx({"items": [["id", "name"], [1, "a"]]}, dirpath=d, filename="a_items.xlsx")
    make_xlsx({"items": [["id", "name"], [1, "b"]]}, dirpath=d, filename="b_items.xlsx")
    issues = _run(d, {"items": {"unique": ["id"]}})
    assert any(i.rule == "unique" for i in issues)


def test_required_missing():
    d = tempfile.mkdtemp()
    make_xlsx({"items": [
        ["id", "name"],
        [1, ""],
    ]}, dirpath=d, filename="items.xlsx")
    issues = _run(d, {"items": {"required": ["name"]}})
    assert any(i.rule == "required" for i in issues)


def test_type_and_enum_and_range():
    d = tempfile.mkdtemp()
    make_xlsx({"items": [
        ["id", "type", "value"],
        [1, "weapon", 999],
    ]}, dirpath=d, filename="items.xlsx")
    issues = _run(d, {
        "items": {
            "types": {"id": "int", "value": "int"},
            "enums": {"type": ["consumable", "equipment", "material"]},
            "ranges": {"value": {"min": 0, "max": 100}},
        }
    })
    rules = {i.rule for i in issues}
    assert "enum" in rules
    assert "range" in rules


def test_dangling_reference_cross_file():
    d = tempfile.mkdtemp()
    # items table in a separate file: id 1001 exists
    make_xlsx({"items": [["id", "name"], [1001, "sword"]]}, dirpath=d, filename="items.xlsx")
    # heroes references item 9999 which does not exist anywhere -> dangling
    make_xlsx({"heroes": [
        ["id", "name", "weapon_id"],
        [1, "alice", 9999],
    ]}, dirpath=d, filename="heroes.xlsx")
    issues = _run(d, {
        "items": {"unique": ["id"], "types": {"id": "int"}},
        "heroes": {"refs": [{"column": "weapon_id", "table": "items", "key": "id"}]},
    })
    assert any(i.rule == "ref" and i.level == "error" for i in issues)


def test_valid_reference_cross_file():
    d = tempfile.mkdtemp()
    make_xlsx({"items": [["id", "name"], [1001, "sword"]]}, dirpath=d, filename="items.xlsx")
    make_xlsx({"heroes": [
        ["id", "name", "weapon_id"],
        [1, "alice", 1001],
    ]}, dirpath=d, filename="heroes.xlsx")
    issues = _run(d, {
        "items": {"unique": ["id"], "types": {"id": "int"}},
        "heroes": {"refs": [{"column": "weapon_id", "table": "items", "key": "id"}]},
    })
    assert not any(i.rule == "ref" for i in issues)


def test_clean_table_passes():
    d = tempfile.mkdtemp()
    make_xlsx({"items": [
        ["id", "name", "type", "value"],
        [1, "sword", "equipment", 10],
        [2, "potion", "consumable", 5],
    ]}, dirpath=d, filename="items.xlsx")
    issues = _run(d, {
        "items": {
            "required": ["id", "name"],
            "unique": ["id"],
            "types": {"id": "int", "value": "int"},
            "enums": {"type": ["consumable", "equipment", "material"]},
            "ranges": {"value": {"min": 0, "max": 9999}},
        }
    })
    assert issues == [], issues
