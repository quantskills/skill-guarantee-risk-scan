---
name: guarantee-risk-scan
description: A-share cumulative guarantee risk scanning skill for Pandadata-based monitoring of stock guarantee ratios, excess guarantee amounts, and high-debt-ratio guarantee exposure. Use when the user asks to scan A-share holdings for guarantee risks, monitor cumulative guarantee ratios, flag excess guarantee events, generate guarantee risk reports, or schedule recurring guarantee risk scans.
license: GPL-3.0-only
metadata:
  organization: QuantSkills
  organization_url: https://github.com/quantskills
  repository: skill-guarantee-risk-scan
  repository_url: https://github.com/quantskills/skill-guarantee-risk-scan
  project_type: skill
  collection: guarantee-risk-scan
  creator: fuzijun
  maintainer: fuzijun
quantSkills:
  project_type: skill
  category: monitor
  tags:
    - a-share
    - guarantee-risk
    - monitoring
    - pandadata
  platforms:
    - claude-code
    - codex
    - openclaw
    - cursor
  status: draft
  requires:
    - skill-pandadata-api
  validation_level: listed
  maintainer_type: community
  summary_zh: "A 股累计担保风险扫描：担保比率、超额担保、高负债率担保占比监控与预警报告。"
  summary_en: "A-share cumulative guarantee risk scanning: guarantee ratio, excess guarantee, and high-debt-ratio guarantee monitoring and alerting."
---

# Guarantee Risk Scan

Use this skill to scan A-share stocks for cumulative guarantee risk. This BUILD monitors guarantee ratios, flags excess guarantee events, and generates structured risk reports.

## Tool Positioning
- Tool type: 监控预警型 (Monitoring & Alerting BUILD)
- Problem solved: 定期扫描持股/自选股的累计担保风险，输出结构化预警报告
- User: agent / 人工分析

## Applicable Scenarios
- When the user needs to scan holdings for guarantee risks
- When the user needs to monitor guarantee ratio changes over time
- When scheduled guarantee risk scanning is required
- When excess guarantee events need to be flagged

## Authentication

Set environment variables before calling `run()`:

```bash
set PANDA_DATA_USERNAME=your_phone
set PANDA_DATA_PASSWORD=your_password
set PANDA_DATA_BASE_URL=http://pandadata.pandaaiquant.com
```

## Input
| Field | Type | Description |
|---|---|---|
| symbols | List[str] | Stock codes to scan (optional, scans all if empty) |
| start_date | str | Scan start date, format "YYYYMMDD" |
| end_date | str | Scan end date, format "YYYYMMDD" |
| config | dict | Optional config: ratio_threshold, excess_threshold, high_debt_threshold |

## Standard BUILD Output
| Field | Type | Description |
|---|---|---|
| trade_date | str | Data date (from info_date or end_date) |
| build_id | str | BUILD identifier (B01) |
| build_name | str | BUILD name (guarantee-risk-scan) |
| target_id | str | Stock code (symbol) |
| result_type | str | Always "risk_flag" |
| result_value | str | Risk level: high / medium / low |
| result_json | str | JSON-encoded detail (all raw fields + risk_flag) |
| data_version | str | Data version identifier |
| update_time | str | Timestamp of generation |

## Usage
```python
from scripts.build import run, validate_input

# 输入校验：缺字段、空数据、类型错误会抛出明确异常
validate_input({
    "symbols": ["000002.SZ"],
    "start_date": "20250101",
    "end_date": "20250712"
})

result = run({
    "symbols": ["000002.SZ", "600519.SH"],
    "start_date": "20250101",
    "end_date": "20250712"
})
```

## Data Source
- 数据来源：PandaAI data 数据拉取库（panda_data）
- 额定接口：`panda_data.readers.market_reference_reader.get_cumu_guarantee`
- 输入必须来自 PandaAI data、调用方传入的标准结构化数据或项目指定数据源

## Can Be Called by Alpha
- Yes
- Call method: `run(input_data, config)` + `validate_input(input_data)`
- Dependency: panda_data（PandaAI data），`get_cumu_guarantee`

## Production Result
- Generates `生产产物/数据库.parquet` with daily guarantee risk snapshot
- Update frequency: daily after market close
- See `生产产物/SKILL.md` for production usage details

## Dependencies
- panda_data >= 0.0.12
- numpy
- pandas
