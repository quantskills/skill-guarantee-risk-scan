# Guarantee Risk Scan Skill

[简体中文](README.md) | **English**

> Scan A-share listed companies' guarantee data for risk: excessive guarantee ratios, excess guarantee amounts, high-debt-ratio guarantees — 3-tier alerting at a glance.

<p align="center">
  <img alt="risk levels" src="https://img.shields.io/badge/risk_levels-high%20%7C%20medium%20%7C%20low-red">
  <img alt="data source" src="https://img.shields.io/badge/data-Pandadata-ff69b4">
  <img alt="requires" src="https://img.shields.io/badge/requires-pandadata--api-7c3aed">
</p>

---

## What is this

`guarantee-risk-scan` is a **BUILD skill**: input a date range and stock symbol list, call the PandaData cumulative guarantee API, classify risk by guarantee ratio, excess guarantee amount, and high-debt-ratio guarantee amount, and output standard BUILD-format risk scan results.

## Risk Classification Rules

| Level | Condition |
|---|---|
| 🔴 **high** | ratio ≥ threshold AND (excess > 0 OR high-debt > 0) |
| 🟡 **medium** | ratio ≥ threshold, OR excess > 0 |
| 🟢 **low** | All indicators normal |

## Quick Start

```bash
# Set credentials (first time)
export PANDA_DATA_USERNAME=your_phone
export PANDA_DATA_PASSWORD=your_password
export PANDA_DATA_BASE_URL=http://pandadata.pandaaiquant.com

# Run scan
python scripts/build.py
```

### Custom Parameters

```python
from scripts.build import run

result = run(
    {"symbols": ["000002.SZ", "600519.SH"], "start_date": "20240101", "end_date": "20250701"},
    config={"ratio_threshold": 50.0},
)
print(result)
```

### Output Fields

| Field | Description |
|---|---|
| `trade_date` | Data date |
| `build_id` | `B01` |
| `build_name` | `guarantee-risk-scan` |
| `target_id` | Stock symbol |
| `result_type` | `risk_flag` |
| `result_value` | `high`/`medium`/`low` |
| `result_json` | Raw guarantee details |

## Directory Layout

```
guarantee-risk-scan/
├── SKILL.md                    # Skill entry
├── scripts/
│   ├── build.py                # BUILD script
│   └── test.py                 # Unit tests
├── agents/
│   ├── openai.yaml
│   ├── cursor-rule.mdc
│   └── portable-loader.md
├── 生产产物/
│   ├── SKILL.md                # Production doc
│   └── 数据库.parquet          # Production data
└── skill.json                  # Skill metadata
```

## Disclaimer

This skill produces statistical analysis based on public data. Nothing here constitutes investment advice.
