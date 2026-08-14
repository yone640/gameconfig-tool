# 配置表规范（schema.json）

`schema.json` 定义每个配置表的列、类型与校验规则。表名（顶层键）对应 Excel 中的 sheet 名。

## 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `columns` | string[] | 参与校验的列名；不填则所有列都参与 |
| `types` | object | 列 → 类型：`int` / `float` / `str` / `bool` |
| `required` | string[] | 必填列（空值报错） |
| `unique` | string \| string[] | 唯一键列；跨文件全局去重 |
| `enums` | object | 列 → 允许的取值列表 |
| `ranges` | object | 列 → `{"min": 0, "max": 9999}` 数值范围 |
| `refs` | array | 外键：`{"column": "weapon_id", "table": "items", "key": "id"}` |

## 示例

```json
{
  "items": {
    "columns": ["id", "name", "type", "value"],
    "types": {"id": "int", "value": "int"},
    "required": ["id", "name"],
    "unique": ["id"],
    "enums": {"type": ["consumable", "equipment", "material"]},
    "ranges": {"value": {"min": 0, "max": 9999}}
  },
  "heroes": {
    "unique": ["id"],
    "refs": [
      {"column": "starter_weapon", "table": "items", "key": "id"}
    ]
  }
}
```

## 说明

- **引用完整性是全局的**：`refs` 的目标表可以位于另一个 Excel 文件，工具会跨文件建立 ID 索引后校验，防止悬空引用。
- **唯一键跨文件去重**：同名 sheet 分布在多个文件时，唯一键全局唯一。
- **类型自动转换**：`convert` 命令会按 `types` 将字符串单元格转换为 int/float/bool，避免程序侧解析错误。
