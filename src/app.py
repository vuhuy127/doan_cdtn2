import csv
import statistics
import streamlit as st

st.set_page_config(page_title="doan_cdtn2 - Xu huong tuyen dung CNTT", layout="wide")
st.title("Phan tich & du bao xu huong tuyen dung nganh CNTT")
st.caption("Chuyen de tot nghiep 2 - Khoa hoc du lieu | doan_cdtn2")

def load_features(path: str):
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try:
            r["salary_val"] = float(r.get("salary_avg") or 0.0)
        except Exception:
            r["salary_val"] = 0.0
    return rows

data_path = st.sidebar.text_input("File du lieu mau (doc lap)", value="data/jobs_features.csv")

try:
    rows = load_features(data_path)
except Exception as e:
    st.error(f"Khong doc duoc file: {e}")
    st.stop()

if not rows:
    st.warning("File du lieu chua co dong nao.")
    st.stop()

roles = ["Tat ca"] + sorted({r.get("role_group", "Other IT") for r in rows if r.get("role_group")})
locations = ["Tat ca"] + sorted({r.get("location", "Khac") for r in rows if r.get("location")})

selected_role = st.sidebar.selectbox("Nhom vi tri", roles)
selected_loc = st.sidebar.selectbox("Khu vuc", locations)

filtered = [
    r for r in rows
    if (selected_role == "Tat ca" or r.get("role_group") == selected_role)
    and (selected_loc == "Tat ca" or r.get("location") == selected_loc)
]

skill_cols = [k for k in rows[0].keys() if k.startswith("skill_")]

skill_totals = {}
for col in skill_cols:
    total = 0
    for r in filtered:
        try:
            total += int(float(r.get(col) or 0))
        except Exception:
            pass
    skill_totals[col.replace("skill_", "").upper()] = total

salaries = [r["salary_val"] for r in filtered if r["salary_val"] > 0]
median_sal = statistics.median(salaries) if salaries else 0.0
top_skill = max(skill_totals.items(), key=lambda x: x[1])[0] if (skill_totals and any(v > 0 for v in skill_totals.values())) else "N/A"

c1, c2, c3 = st.columns(3)
c1.metric("Tong so tin tuyen dung", f"{len(filtered):,}")
c2.metric("Muc luong trung vi (VND)", f"{median_sal:,.0f}")
c3.metric("Ky nang nhu cau cao nhat", top_skill)

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("1. So luong tin theo ky nang / cong nghe (0/1)")
    if skill_totals:
        st.bar_chart(skill_totals)

with col_right:
    st.subheader("2. Muc luong trung vi theo nhom vi tri")
    role_sal_map = {}
    for role in sorted({r.get("role_group", "Other IT") for r in filtered}):
        vals = [r["salary_val"] for r in filtered if r.get("role_group") == role and r["salary_val"] > 0]
        if vals:
            role_sal_map[role] = round(statistics.median(vals), 0)
    if role_sal_map:
        st.bar_chart(role_sal_map)

st.subheader("3. Xu huong so tin theo thang & danh gia Baseline (MAE)")
counts_by_month = {}
for r in filtered:
    ym = r.get("year_month", "")
    if ym:
        counts_by_month[ym] = counts_by_month.get(ym, 0) + 1

months = sorted(counts_by_month.keys())
actuals = [float(counts_by_month[m]) for m in months]
n = len(months)

if n >= 4:
    test_periods = 2
    split_idx = max(1, n - test_periods)
    ts_x = list(range(split_idx))
    ts_y = actuals[:split_idx]
    if len(ts_x) >= 2 and len(set(ts_x)) > 1:
        mx = statistics.mean(ts_x)
        my = statistics.mean(ts_y)
        den = sum((x - mx) ** 2 for x in ts_x)
        slope = sum((x - mx) * (y - my) for x, y in zip(ts_x, ts_y)) / den if den else 0.0
        intercept = my - slope * mx
    else:
        slope = 0.0
        intercept = statistics.mean(ts_y)

    preds = [max(0.0, round(intercept + slope * i)) for i in range(n)]
    baselines = [None] + [actuals[i - 1] for i in range(1, n)]

    eval_idx = [i for i in range(split_idx, n) if baselines[i] is not None]
    if eval_idx:
        mae_base = statistics.mean(abs(actuals[i] - baselines[i]) for i in eval_idx)
        mae_model = statistics.mean(abs(actuals[i] - preds[i]) for i in eval_idx)
        st.info(f"MAE Baseline (ky truoc): {mae_base:.2f} | MAE Mo hinh: {mae_model:.2f}")

    chart_rows = []
    for i, m in enumerate(months):
        chart_rows.append({
            "Thang": m,
            "Thuc_te": actuals[i],
            "Baseline_ky_truoc": baselines[i],
            "Du_bao_mo_hinh": preds[i],
        })
    st.dataframe(chart_rows, use_container_width=True)
    st.line_chart({
        "Thuc_te": {m: counts_by_month[m] for m in months},
        "Du_bao_mo_hinh": {months[i]: preds[i] for i in range(n)},
    })
else:
    st.warning("Can it nhat 4 thang de danh gia xu huong.")

with st.expander("Xem bang du lieu dac trung (jobs_features.csv)"):
    st.dataframe(filtered, use_container_width=True)
