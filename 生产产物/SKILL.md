---
name: guarantee-risk-scan-production
description: 生产环境的累计担保风险数据读取和使用。从标准Parquet文件中读取担保风险扫描结果，支持实盘风险监控和预警报告生成。
tags: [quant, build, production, monitoring, guarantee-risk]
---

# 累计担保风险扫描（生产）

## 数据读取

生产担保风险数据存储在：`生产产物/数据库.parquet`

**数据格式**：标准Parquet格式，包含BUILD标准字段

## 主键

- `trade_date`
- `build_id`
- `target_id`
- `result_type`

```python
import pandas as pd

# 读取生产数据
df = pd.read_parquet("生产产物/数据库.parquet")

# 筛选高风险记录
high_risk = df[df['result_value'] == 'high'].copy()
```

## 生产监控

### 风险质量监控

**每日监控指标**：
- 高风险记录数量（应>=0，大幅增加需关注）
- 中风险记录数量
- 数据更新及时性（check update_time）
- 覆盖股票数量变化

### 异常告警

**告警条件**：
- 高风险记录数量突然激增（超过前日2倍）
- 数据更新延迟超过预期
- 目标股票长时间无数据更新

## 数据使用

### 获取最新风险扫描

```python
import pandas as pd
from datetime import datetime

# 读取担保风险数据
df = pd.read_parquet("生产产物/数据库.parquet")

# 获取最新交易日的高风险股票
latest_date = df['trade_date'].max()
today_high_risk = df[
    (df['trade_date'] == latest_date) &
    (df['result_value'] == 'high')
].copy()
```

### 字段说明

| 字段 | 用途 | 说明 |
|---|---|---|
| trade_date | 数据日期 | 公告日期 |
| build_id | BUILD标识 | B01 |
| build_name | BUILD名称 | guarantee-risk-scan |
| target_id | 目标股票 | 股票代码 |
| result_type | 结果类型 | risk_flag |
| result_value | 风险等级 | high/medium/low |
| result_json | 详细信息 | JSON格式包含担保指标 |
| data_version | 数据版本 | 用于追溯 |
| update_time | 更新时间 | 数据生成时间戳 |

## 生产注意事项

1. **更新时机**：担保风险数据在市场收盘后更新
2. **读取时机**：收盘后读取，次日开盘前使用
3. **数据验证**：使用前检查data_version和update_time
4. **阈值配置**：可根据需要在build.py中调整ratio_threshold/excess_threshold/high_debt_threshold
5. **禁止重算**：生产环境禁止重新扫描全量数据

## 风险边界

### 数据延迟

- 担保公告数据依赖上市公司披露
- 非交易日无新数据产生
- 季报/年报披露期数据集中更新

### 覆盖范围

- 仅覆盖A股上市公司
- 数据来源为公开担保公告
- 可能遗漏非标准披露的担保信息

## 维护说明

### 更新机制

- **更新频率**：每日收盘后自动更新
- **数据保留**：保留最近1年数据
- **备份策略**：每日备份，保留7天

### 版本管理

- **data_version**: 标识数据版本
- **update_time**: 记录更新时间
- **版本追踪**: 支持历史版本回溯

## 故障处理

### 常见问题

1. **数据缺失**
   - 检查文件是否存在
   - 检查数据版本标识
   - 确认PandaData账号权限和余额

2. **风险结果异常**
   - 检查更新时间
   - 验证数据版本
   - 查看result_json中的详细担保指标

3. **性能下降**
   - 检查扫描范围是否过大
   - 确认PandaData API响应正常
   - 联系开发团队

### 恢复策略

- **自动重试**：读取失败自动重试
- **降级处理**：主数据源失败时使用前日数据
- **人工介入**：严重问题时人工处理

## 联系支持

如有生产问题，请联系：
- 技术支持：量化研究团队
- 数据支持：PandaData技术支持
- 项目负责人：担保风险扫描负责人

## 数据来源说明

**真实PandaData数据**：
- 数据API：panda_data.get_cumu_guarantee()
- 账号格式：86+手机号（需自行申请PandaData权限）
- 数据版本：pandadata-guarantee-risk-scan-v1
- 认证方式：环境变量 PANDA_DATA_USERNAME / PANDA_DATA_PASSWORD

**风险分类规则**（与 build.py classify_risk 一致）：
- High: 担保比例 >= 50%（净资产红线）或担保比例 >= 50% 且（超额担保 > 0 或 高负债率担保 > 0）
- Medium: 担保比例 < 50% 且（超额担保 > 0 或 高负债率担保 > 0）
- Low: 未触发任何阈值
