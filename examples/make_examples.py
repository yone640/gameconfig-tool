# -*- coding: utf-8 -*-
"""Generate example config xlsx files (with a few intentional errors for demo)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from openpyxl import Workbook

HERE = os.path.dirname(os.path.abspath(__file__))


def save(sheets, name):
    wb = Workbook()
    wb.remove(wb.active)
    for title, rows in sheets.items():
        ws = wb.create_sheet(title=title)
        for r in rows:
            ws.append(r)
    path = os.path.join(HERE, "configs", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wb.save(path)
    print("wrote", path)


# items: 2 good rows + 1 duplicate id (1002) + 1 bad enum type
save({
    "items": [
        ["id", "name", "type", "value", "sell_price"],
        [1001, "小治疗药水", "consumable", 30, 5],
        [1002, "铁剑", "equipment", 120, 20],
        [1002, "重复ID演示", "material", 1, 1],   # duplicate unique key
        [1003, "错误类型演示", "weapon", 10, 2],   # weapon not in enum
    ],
}, "items.xlsx")

# heroes: 1 good row + 1 dangling reference to a non-existent item id
save({
    "heroes": [
        ["id", "name", "hp", "atk", "starter_weapon"],
        [1, "阿瑞斯", 1000, 150, 1001],
        [2, "悬空引用演示", 900, 120, 9999],   # item 9999 does not exist
    ],
}, "heroes.xlsx")
