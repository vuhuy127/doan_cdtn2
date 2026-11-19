import csv
import statistics

def evaluate_trend_forecast(feature_csv_path: str = "data/jobs_features.csv", test_periods: int = 2):
    with open(feature_csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    counts_by_month = {}
    for r in rows:
        ym = r["year_month"]
        counts_by_month[ym] = counts_by_month.get(ym, 0) + 1

    months = sorted(counts_by_month.keys())
    actuals = [float(counts_by_month[m]) for m in months]
    n = len(months)

    split_idx = max(1, n - test_periods)
    ts_x = list(range(split_idx))
    ts_y = actuals[:split_idx]

    if len(ts_x) >= 2 and len(set(ts_x)) > 1:
        mean_x = statistics.mean(ts_x)
        mean_y = statistics.mean(ts_y)
        denom = sum((x - mean_x) ** 2 for x in ts_x)
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(ts_x, ts_y)) / denom if denom else 0.0
        intercept = mean_y - slope * mean_x
    else:
        slope = 0.0
        intercept = statistics.mean(ts_y) if ts_y else 0.0

    preds = [max(0.0, round(intercept + slope * i)) for i in range(n)]
    baselines = [None] + [actuals[i - 1] for i in range(1, n)]

    eval_indices = [i for i in range(split_idx, n) if baselines[i] is not None]
    mae_base = statistics.mean(abs(actuals[i] - baselines[i]) for i in eval_indices)
    mae_model = statistics.mean(abs(actuals[i] - preds[i]) for i in eval_indices)
    rmse_model = (statistics.mean((actuals[i] - preds[i]) ** 2 for i in eval_indices)) ** 0.5

    abs_errors = [abs(actuals[i] - preds[i]) for i in range(n)]
    worst_idx = max(range(n), key=lambda i: abs_errors[i])

    print("=== KET QUA DANH GIA MO HINH DU BAO XU HUONG ===")
    print(f"{'year_month':<12} {'job_count':<10} {'baseline':<10} {'model_pred':<11} {'abs_err'}")
    for i in range(n):
        b_str = f"{baselines[i]:.0f}" if baselines[i] is not None else "N/A"
        print(f"{months[i]:<12} {actuals[i]:<10.0f} {b_str:<10} {preds[i]:<11.0f} {abs_errors[i]:.0f}")

    print(f"\nMAE Baseline (giu nguyen gia tri ky truoc): {mae_base:.2f}")
    print(f"MAE Mo hinh (Linear Trend):                {mae_model:.2f}")
    print(f"RMSE Mo hinh (Linear Trend):               {rmse_model:.2f}")
    print("\n=== PHAN TICH LOI (ERROR ANALYSIS) ===")
    print(f"Giai doan sai lech lon nhat: {months[worst_idx]} (sai so tuyet doi = {abs_errors[worst_idx]:.0f} tin)")
    print("Nhan xet: Mo hinh tuyen tinh sai nhieu o cac ky bien dong dot ngot (vi du mua vu/le Tet).")

if __name__ == "__main__":
    evaluate_trend_forecast()
