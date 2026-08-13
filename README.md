# 担保风险扫描 Skill

**简体中文** | [English](README.en.md)

> 对 A 股上市公司担保数据进行风险扫描：担保比率过高、超额担保、高负债率担保 —— 三级预警，一目了然。

<p align="center">
  <img alt="risk levels" src="https://img.shields.io/badge/risk_levels-high%20%7C%20medium%20%7C%20low-red">
  <img alt="data source" src="https://img.shields.io/badge/data-Pandadata-ff69b4">
  <img alt="requires" src="https://img.shields.io/badge/requires-pandadata--api-7c3aed">
</p>

---

## 这是什么

`guarantee-risk-scan` 是一个 **BUILD 技能**：输入起止日期和股票代码清单，调用 PandaData 累计担保接口，按担保比率、超额担保金额、高负债率担保金额三维度进行风险分类，输出标准 BUILD 格式的风险扫描结果。

## 风险分类规则

| 等级 | 条件 |
|---|---|
| 🔴 **high** | 担保比率 ≥ 阈值且（超额担保 > 0 或高负债率担保 > 0） |
| 🟡 **medium** | 担保比率 ≥ 阈值，或超额担保 > 0 |
| 🟢 **low** | 所有指标正常 |

## 快速开始

```bash
# 设置凭据（首次）
export PANDA_DATA_USERNAME=your_phone
export PANDA_DATA_PASSWORD=your_password
export PANDA_DATA_BASE_URL=http://pandadata.pandaaiquant.com

# 运行扫描
python scripts/build.py
```

### 自定义参数

```python
from scripts.build import run

result = run(
    {"symbols": ["000002.SZ", "600519.SH"], "start_date": "20240101", "end_date": "20250701"},
    config={"ratio_threshold": 50.0},
)
print(result)
```

### 输出字段

| 字段 | 说明 |
|---|---|
| `trade_date` | 数据日期 |
| `build_id` | `B01` |
| `build_name` | `guarantee-risk-scan` |
| `target_id` | 股票代码 |
| `result_type` | `risk_flag` |
| `result_value` | `high`/`medium`/`low` |
| `result_json` | 原始担保明细 |

## 目录结构

```
guarantee-risk-scan/
├── SKILL.md                    # 技能入口
├── scripts/
│   ├── build.py                # BUILD 构建脚本
│   └── test.py                 # 单元测试
├── agents/
│   ├── openai.yaml
│   ├── cursor-rule.mdc
│   └── portable-loader.md
├── 生产产物/
│   ├── SKILL.md                # 生产版文档
│   └── 数据库.parquet          # 生产数据
└── skill.json                  # 技能元数据
```

## 免责声明

本技能输出为基于公开数据的统计分析结果，不构成任何投资建议。
