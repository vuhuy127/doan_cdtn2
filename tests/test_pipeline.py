from src.pipeline import (
    VN_34_UNITS,
    detect_vn_34_unit,
    evaluate_monthly_forecast,
    normalize_record,
    summarize_data_quality,
)


def test_34_administrative_units():
    assert len(VN_34_UNITS) == 34
    assert detect_vn_34_unit("Bình Dương") == "TP. Hồ Chí Minh"
    assert detect_vn_34_unit("Quảng Nam") == "TP. Đà Nẵng"
    assert detect_vn_34_unit("Khánh Hòa") == "Khánh Hòa"


def test_normalize_and_quality():
    r1 = normalize_record(
        {"title": "Data Analyst SQL Python", "location": "Hà Nội", "posted_date": "2026-01-10", "salary_avg": 25000000},
        1,
        "Nguồn test",
        "https://example.com",
    )
    assert r1["location"] == "TP. Hà Nội"
    assert r1["skill_python"] == 1
    assert r1["skill_sql"] == 1
    assert r1["has_valid_salary"] == 1
    q = summarize_data_quality([r1])
    assert q["total"] == 1 and q["salary_pct"] == 100.0


def test_forecast_metrics():
    rows = [
        {"year_month": f"2026-0{m}", "location": "TP. Hồ Chí Minh", "salary_val": 20000000.0, "has_valid_salary": 1, "has_any_skill": 1}
        for m in range(1, 7)
    ]
    res = evaluate_monthly_forecast(rows)
    assert res["enough_data"] is True
    assert res["mae_trend"] >= 0.0
    assert res["mae_ma3"] >= 0.0
