# gameconfig-tool

游戏策划配置表处理工具：将策划用 Excel 维护的配置表批量转换为程序可用的 JSON，并按配置规范做数据校验（重复 ID / 缺失字段 / 引用完整性 / 数值范围），输出可读的校验报告。

面向场景：游戏项目中策划用 Excel 维护数值配置，程序需要 JSON；手工转换与核对易错、低效。本工具把"转换 + 校验 + 报告"固化成一条命令，减少跨职能沟通成本。

## 功能

- **转换**：目录内所有 `*.xlsx` 配置表 → JSON（多 sheet 支持、类型推断、列名映射）
- **校验**：按 `schema.json` 规范校验（必填字段、唯一键、枚举、数值范围、跨表引用完整性）
- **报告**：控制台摘要 + `report.md` 明细（每条错误带 sheet / 行号 / 原因）
- **批处理**：一次处理整个配置目录，增量输出各表统计

## 快速开始

```bash
pip install openpyxl pytest
# 转换
python -m gameconfig convert examples/configs -o out/
# 校验
python -m gameconfig validate examples/configs --schema examples/schema.json
```

## 配置表规范（schema.json）

每个表一个条目，定义列名、类型、是否必填、唯一键、枚举值、数值范围与引用关系：

```json
{
  "items": {
    "columns": ["id", "name", "type", "value"],
    "types": {"id": "int", "value": "int"},
    "required": ["id", "name"],
    "unique": ["id"],
    "enums": {"type": ["consumable", "equipment", "material"]}
  }
}
```

详见 [docs/schema-spec.md](docs/schema-spec.md)。

## 校验规则

| 规则 | 说明 |
|---|---|
| 必填缺失 | required 列出现空值 |
| 唯一键重复 | unique 列存在重复值 |
| 类型错误 | 值与声明类型不符（int/float/str/bool） |
| 枚举越界 | 值不在枚举列表内 |
| 范围越界 | 数值超出 min/max |
| 引用悬空 | 外键引用的 ID 在目标表中不存在 |

## 项目结构

```
gameconfig-tool/
├── src/gameconfig/
│   ├── cli.py            # 命令行入口
│   ├── loader.py         # Excel 加载
│   ├── schema.py         # 规范解析与校验
│   ├── converter.py      # Excel → JSON
│   ├── validator.py      # 数据校验
│   └── report.py         # 报告生成
├── tests/                # pytest 单元测试
└── examples/             # 示例配置表与规范
```

## 常见问题（FAQ）

- **Excel 里有多余空行/合并单元格？** 加载器自动跳过空行；合并单元格按左上角取值。
- **列顺序变化怎么办？** 按列名读取，不依赖列顺序。
- **能否接入 CI？** 可以，`gameconfig validate` 校验失败时返回非零退出码，适合作为流水线检查步骤。

## 开源协议

MIT
