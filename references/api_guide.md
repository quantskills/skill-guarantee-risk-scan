# Guarantee Risk Scan API Guide

## Data Source
- **API**: panda_data.readers.market_reference_reader.get_cumu_guarantee()
- **Base URL**: http://pandadata.pandaaiquant.com (overridable via `PANDA_DATA_BASE_URL`)

## Authentication

### Environment Variables (Recommended)
```bash
set PANDA_DATA_USERNAME=your_phone
set PANDA_DATA_PASSWORD=your_password
set PANDA_DATA_BASE_URL=http://pandadata.pandaaiquant.com
```

The BUILD uses `panda_data.init_token(username, password, base_url)` internally.

### Direct init_token
```python
import panda_data
panda_data.init_token(phone, password, base_url)
```

## Method Signature
```python
get_cumu_guarantee(
    symbol: Optional[Union[str, List[str]]] = None,
    start_date: str = None,
    end_date: str = None,
    fields: Optional[Union[str, List[str]]] = None,
) -> pd.DataFrame
```

## Raw API Returned Fields
| Field | Type | Description |
|---|---|---|
| symbol | str | Stock code |
| info_date | str | Announcement date |
| end_date | str | Reporting period end date |
| name | str | Company name |
| currency | str | Currency (CNY) |
| amount | float | Total guarantee balance |
| ex_amount | float | Guarantees to subsidiaries |
| sub_amount | float | Guarantees to third parties |
| occur_amount | float | Occurred guarantee amount |
| ex_occur_amount | float | Subsidiary guarantee occurred |
| sub_occur_amount | float | Third-party guarantee occurred |
| total_amount | float | Total guarantees |
| ex_balance | float | Subsidiary guarantee balance |
| sub_balance | float | Third-party guarantee balance |
| total_amount_ratio | float | Guarantee to net asset ratio (%) |
| high_debt_ratio_amount | float | High-debt-ratio guarantee |
| related_amount | float | Related party guarantee |
| excess_amount | float | Excess guarantee amount |

## Standard BUILD Output Fields

The `run()` function returns a DataFrame with these standard columns:

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

## Risk Classification Logic (与 build.py classify_risk 保持一致)
- **High**: `total_amount_ratio >= 50%`（净资产红线，单独触发即 High）
- **High (with flags)**: `total_amount_ratio >= 50%` 且超额担保/高负债率担保 > 0（同样 High）
- **Medium**: `total_amount_ratio < 50%` 但超额担保 > 0 或高负债率担保 > 0
- **Low**: 无任何阈值触发

## Configuration Parameters
| Parameter | Default | Description |
|---|---|---|
| ratio_threshold | 50.0 | Guarantee ratio threshold (%) |
| excess_threshold | 0.0 | Excess guarantee threshold |
| high_debt_threshold | 0.0 | High-debt guarantee threshold |
