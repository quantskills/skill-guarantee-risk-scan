import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

BUILD_ID = "B01"
BUILD_NAME = "guarantee-risk-scan"
DATA_VERSION = "pandadata-guarantee-risk-scan-v1"

RISK_LEVEL_HIGH = "high"
RISK_LEVEL_MEDIUM = "medium"
RISK_LEVEL_LOW = "low"

RISK_FLAG_EXCESS_GUARANTEE = "excess_guarantee"
RISK_FLAG_HIGH_RATIO = "high_ratio"
RISK_FLAG_HIGH_DEBT_RATIO = "high_debt_ratio"
RISK_FLAG_NET_ASSET_RED_LINE = "net_asset_red_line"
RISK_FLAG_NORMAL = "normal"

# 《公司法》/上交所指引：对外担保累计总额占最近一期经审计净资产比例
# 达到 50% 触发章程/股东大会特别决议要求，视为净资产红线。
NET_ASSET_RED_LINE_RATIO = 50.0
DEFAULT_RATIO_THRESHOLD = 50.0
DEFAULT_EXCESS_THRESHOLD = 0.0
DEFAULT_HIGH_DEBT_THRESHOLD = 0.0


def get_panda_client():
    import panda_data
    username = os.environ.get("PANDA_DATA_USERNAME")
    password = os.environ.get("PANDA_DATA_PASSWORD")
    base_url = os.environ.get("PANDA_DATA_BASE_URL", "http://pandadata.pandaaiquant.com")
    if not username or not password:
        raise ValueError(
            "请设置环境变量 PANDA_DATA_USERNAME 和 PANDA_DATA_PASSWORD"
        )
    panda_data.init_token(username=username, password=password, base_url=base_url)
    return panda_data


def get_guarantee_data(
    symbols=None, start_date=None, end_date=None,
):
    """从 market_reference_reader 导入 get_cumu_guarantee 拉取累计担保数据。"""
    from panda_data.readers.market_reference_reader import get_cumu_guarantee
    return get_cumu_guarantee(
        symbol=symbols,
        start_date=start_date,
        end_date=end_date,
    )


def validate_input(input_data: dict):
    if not isinstance(input_data, dict):
        raise TypeError(f"input_data must be dict, got {type(input_data)}")
    if "start_date" not in input_data:
        raise ValueError("start_date is required")
    if "end_date" not in input_data:
        raise ValueError("end_date is required")
    for key in ("start_date", "end_date"):
        val = input_data[key]
        if not isinstance(val, str) or len(val) != 8 or not val.isdigit():
            raise ValueError(f"{key} must be an 8-digit YYYYMMDD string, got {val!r}")


def classify_risk(
    row: pd.Series,
    ratio_threshold: float = DEFAULT_RATIO_THRESHOLD,
    excess_threshold: float = DEFAULT_EXCESS_THRESHOLD,
    high_debt_threshold: float = DEFAULT_HIGH_DEBT_THRESHOLD,
) -> tuple:
    total_ratio = row.get("total_amount_ratio", 0) or 0
    excess_amount = row.get("excess_amount", 0) or 0
    high_debt_amount = row.get("high_debt_ratio_amount", 0) or 0

    flags = []

    if total_ratio >= ratio_threshold:
        flags.append(RISK_FLAG_HIGH_RATIO)
    if total_ratio >= NET_ASSET_RED_LINE_RATIO:
        flags.append(RISK_FLAG_NET_ASSET_RED_LINE)
    if excess_amount > excess_threshold:
        flags.append(RISK_FLAG_EXCESS_GUARANTEE)
    if high_debt_amount > high_debt_threshold:
        flags.append(RISK_FLAG_HIGH_DEBT_RATIO)

    if RISK_FLAG_NET_ASSET_RED_LINE in flags and (
        RISK_FLAG_EXCESS_GUARANTEE in flags or RISK_FLAG_HIGH_DEBT_RATIO in flags
    ):
        return RISK_LEVEL_HIGH, "+".join(flags)
    elif RISK_FLAG_NET_ASSET_RED_LINE in flags:
        return RISK_LEVEL_HIGH, RISK_FLAG_NET_ASSET_RED_LINE
    elif RISK_FLAG_HIGH_RATIO in flags and (
        RISK_FLAG_EXCESS_GUARANTEE in flags or RISK_FLAG_HIGH_DEBT_RATIO in flags
    ):
        return RISK_LEVEL_HIGH, "+".join(flags)
    elif RISK_FLAG_HIGH_RATIO in flags or RISK_FLAG_EXCESS_GUARANTEE in flags:
        return RISK_LEVEL_MEDIUM, flags[0]
    elif flags:
        return RISK_LEVEL_MEDIUM, flags[0]

    return RISK_LEVEL_LOW, RISK_FLAG_NORMAL


def run(
    input_data: dict,
    config: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    validate_input(input_data)

    panda = get_panda_client()

    symbols = input_data.get("symbols")
    start_date = input_data["start_date"]
    end_date = input_data["end_date"]
    cfg = config or {}
    ratio_threshold = cfg.get("ratio_threshold", DEFAULT_RATIO_THRESHOLD)
    excess_threshold = cfg.get("excess_threshold", DEFAULT_EXCESS_THRESHOLD)
    high_debt_threshold = cfg.get("high_debt_threshold", DEFAULT_HIGH_DEBT_THRESHOLD)

    df = get_guarantee_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
    )

    if df.empty:
        return pd.DataFrame(
            columns=[
                "trade_date", "build_id", "build_name", "target_id",
                "result_type", "result_value", "result_json",
                "data_version", "update_time",
            ]
        )

    rows = []
    for _, row in df.iterrows():
        level, flag = classify_risk(
            row, ratio_threshold, excess_threshold, high_debt_threshold
        )
        result_json = {
            "name": row.get("name"),
            "info_date": row.get("info_date"),
            "end_date": row.get("end_date"),
            "total_amount_ratio": row.get("total_amount_ratio"),
            "net_asset_red_line": bool(
                (row.get("total_amount_ratio") or 0) >= NET_ASSET_RED_LINE_RATIO
            ),
            "high_debt_ratio_amount": row.get("high_debt_ratio_amount"),
            "excess_amount": row.get("excess_amount"),
            "total_amount": row.get("total_amount"),
            "amount": row.get("amount"),
            "related_amount": row.get("related_amount"),
            "risk_flag": flag,
        }
        rows.append({
            "trade_date": row.get("info_date") or row.get("end_date"),
            "build_id": BUILD_ID,
            "build_name": BUILD_NAME,
            "target_id": row.get("symbol"),
            "result_type": "risk_flag",
            "result_value": level,
            "result_json": json.dumps(result_json, ensure_ascii=False),
            "data_version": DATA_VERSION,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    result = run(
        {"symbols": ["000002.SZ"], "start_date": "20240101", "end_date": "20250701"},
        config={"ratio_threshold": 50.0},
    )
    print(result.to_string())
    print(f"\nTotal: {len(result)} rows")
    print(f"High risk: {len(result[result['result_value'] == 'high'])}")
    print(f"Medium risk: {len(result[result['result_value'] == 'medium'])}")
    print(f"Low risk: {len(result[result['result_value'] == 'low'])}")
