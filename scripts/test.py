import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.build import run, validate_input, classify_risk
import pandas as pd

STANDARD_COLUMNS = [
    "trade_date", "build_id", "build_name", "target_id",
    "result_type", "result_value", "result_json",
    "data_version", "update_time",
]


def test_validate_input():
    try:
        validate_input({"start_date": "20250101", "end_date": "20250701"})
        print("PASS: valid input")
    except Exception as e:
        print(f"FAIL: {e}")

    try:
        validate_input({})
    except ValueError:
        print("PASS: empty input raises ValueError")
    except Exception as e:
        print(f"FAIL: expected ValueError, got {type(e).__name__}: {e}")

    try:
        validate_input("not a dict")
    except TypeError:
        print("PASS: non-dict input raises TypeError")
    except Exception as e:
        print(f"FAIL: expected TypeError, got {type(e).__name__}: {e}")


def test_classify_risk():
    row = pd.Series({"total_amount_ratio": 60.0, "excess_amount": 1000.0, "high_debt_ratio_amount": 500.0})
    level, flag = classify_risk(row)
    assert level == "high", f"Expected high, got {level}"
    print(f"PASS: high risk -> {level}/{flag}")

    row = pd.Series({"total_amount_ratio": 60.0, "excess_amount": 0.0, "high_debt_ratio_amount": 0.0})
    level, flag = classify_risk(row)
    assert level == "high", f"Expected high (50% net-asset red line), got {level}"
    assert "net_asset_red_line" in flag, f"Expected net_asset_red_line flag, got {flag}"
    print(f"PASS: 50% net-asset red line -> {level}/{flag}")

    row = pd.Series({"total_amount_ratio": 40.0, "excess_amount": 100.0, "high_debt_ratio_amount": 0.0})
    level, flag = classify_risk(row)
    assert level == "medium", f"Expected medium (excess only, below red line), got {level}"
    print(f"PASS: medium risk (excess, below red line) -> {level}/{flag}")

    row = pd.Series({"total_amount_ratio": 10.0, "excess_amount": 0.0, "high_debt_ratio_amount": 0.0})
    level, flag = classify_risk(row)
    assert level == "low", f"Expected low, got {level}"
    print(f"PASS: low risk -> {level}/{flag}")

    row = pd.Series({"total_amount_ratio": None, "excess_amount": None, "high_debt_ratio_amount": None})
    level, flag = classify_risk(row)
    assert level == "low", f"Expected low for None, got {level}"
    print(f"PASS: None values -> {level}/{flag}")


def test_run_real():
    result = run(
        {"symbols": ["000002.SZ"], "start_date": "20240101", "end_date": "20250701"},
        config={"ratio_threshold": 50.0},
    )
    assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
    assert len(result) > 0, "Expected at least 1 row"
    for col in STANDARD_COLUMNS:
        assert col in result.columns, f"Standard column {col} missing"
    assert result["result_value"].isin(["high", "medium", "low"]).all(), \
        "result_value must be valid risk level"
    print(f"PASS: real API call returned {len(result)} rows")
    print(f"     Columns: {list(result.columns)}")
    print(result.to_string())


def test_run_empty_symbols():
    result = run(
        {"start_date": "20240101", "end_date": "20240105"},
    )
    assert isinstance(result, pd.DataFrame), f"Expected DataFrame, got {type(result)}"
    for col in STANDARD_COLUMNS:
        assert col in result.columns, f"Standard column {col} missing"
    print(f"PASS: empty symbols returned {len(result)} rows")


if __name__ == "__main__":
    print("=== test_validate_input ===")
    test_validate_input()
    print("\n=== test_classify_risk ===")
    test_classify_risk()
    print("\n=== test_run_real ===")
    test_run_real()
    print("\n=== test_run_empty_symbols ===")
    test_run_empty_symbols()
