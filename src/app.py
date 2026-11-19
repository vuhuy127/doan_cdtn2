import csv
import statistics
import streamlit as st

st.set_page_config(
    page_title="Đồ án CTDN2 - Xu hướng tuyển dụng CNTT toàn quốc",
    layout="wide",
)

st.title("Phân tích & Dự báo Xu hướng Tuyển dụng Ngành CNTT (63 Tỉnh/Thành Việt Nam)")
st.caption("Chuyên đề tốt nghiệp 2 — Chuyên ngành Khoa học dữ liệu | Dự án: doan_cdtn2")


@st.cache_data
def load_features(path: str):
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try:
            r["salary_val"] = float(r.get("salary_avg") or 0.0)
        except Exception:
            r["salary_val"] = 0.0
        try:
            r["exp_val"] = float(r.get("experience_years") or 0.0)
        except Exception:
            r["exp_val"] = 0.0
    return rows


st.sidebar.header("Bộ lọc & Nguồn dữ liệu")
data_path = st.sidebar.text_input(
    "File dữ liệu đặc trưng (chạy độc lập)",
    value="data/jobs_features.csv",
)

try:
    rows = load_features(data_path)
except Exception as e:
    st.error(f"Không thể đọc file '{data_path}': {e}")
    st.stop()

if not rows:
    st.warning("File dữ liệu hiện đang trống.")
    st.stop()

skill_cols = [k for k in rows[0].keys() if k.startswith("skill_")]
skill_name_map = {col: col.replace("skill_", "").upper() for col in skill_cols}

roles = ["Tất cả"] + sorted({r.get("role_group", "Khác") for r in rows if r.get("role_group")})
locations = ["Tất cả"] + sorted({r.get("location", "Khác") for r in rows if r.get("location")})
skill_options = ["Tất cả"] + [skill_name_map[c] for c in skill_cols]

selected_role = st.sidebar.selectbox("Nhóm vị trí", roles)
selected_loc = st.sidebar.selectbox("Tỉnh / Thành phố (Việt Nam)", locations)
selected_skill = st.sidebar.selectbox("Kỹ năng yêu cầu (0/1)", skill_options)
keyword = st.sidebar.text_input("Tìm kiếm tên vị trí", value="").strip().lower()

filtered = []
for r in rows:
    if selected_role != "Tất cả" and r.get("role_group") != selected_role:
        continue
    if selected_loc != "Tất cả" and r.get("location") != selected_loc:
        continue
    if keyword and keyword not in (r.get("title") or "").lower():
        continue
    if selected_skill != "Tất cả":
        target_col = f"skill_{selected_skill.lower()}"
        try:
            if int(float(r.get(target_col) or 0)) != 1:
                continue
        except Exception:
            continue
    filtered.append(r)

skill_totals = {}
for col in skill_cols:
    total = 0
    for r in filtered:
        try:
            total += int(float(r.get(col) or 0))
        except Exception:
            pass
    skill_totals[skill_name_map[col]] = total

salaries = [r["salary_val"] for r in filtered if r["salary_val"] > 0]
median_sal = statistics.median(salaries) if salaries else 0.0
exps = [r["exp_val"] for r in filtered if r["exp_val"] > 0]
median_exp = statistics.median(exps) if exps else 0.0
distinct_provinces = len({r.get("location") for r in filtered if r.get("location")})

if skill_totals and any(v > 0 for v in skill_totals.values()):
    top_skill, top_count = max(skill_totals.items(), key=lambda x: x[1])
    top_pct = (top_count / len(filtered) * 100) if len(filtered) > 0 else 0.0
    top_skill_text = f"{top_skill} ({top_pct:.0f}%)"
else:
    top_skill_text = "Không có"

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Số tin tuyển dụng", f"{len(filtered):,}")
k2.metric("Số tỉnh/thành có tin", f"{distinct_provinces}")
k3.metric("Lương trung vị", f"{median_sal:,.0f} đ")
k4.metric("Kỹ năng đứng đầu", top_skill_text)
k5.metric("Kinh nghiệm trung vị", f"{median_exp:.1f} năm")

if not filtered:
    st.warning("Không có tin tuyển dụng phù hợp với bộ lọc hiện tại.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "1. EDA Kỹ năng & Mức lương",
    "2. Phân bố 63 Tỉnh/Thành Việt Nam",
    "3. Dự báo xu hướng & Phân tích lỗi",
    "4. Dữ liệu & Xuất CSV",
])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Số lượng tin theo kỹ năng / công nghệ (đặc trưng 0/1)")
        sorted_skills = dict(sorted(skill_totals.items(), key=lambda x: x[1], reverse=True))
        st.bar_chart(sorted_skills)

    with col_b:
        st.subheader("Mức lương trung vị theo nhóm vị trí (VNĐ)")
        role_sal_map = {}
        for role in sorted({r.get("role_group", "Khác") for r in filtered}):
            vals = [r["salary_val"] for r in filtered if r.get("role_group") == role and r["salary_val"] > 0]
            if vals:
                role_sal_map[role] = round(statistics.median(vals), 0)
        sorted_role_sal = dict(sorted(role_sal_map.items(), key=lambda x: x[1], reverse=True))
        st.bar_chart(sorted_role_sal)

with tab2:
    st.subheader("Top 15 Tỉnh/Thành phố có nhiều tin tuyển dụng nhất")
    loc_counts = {}
    loc_sal_lists = {}
    for r in filtered:
        loc = r.get("location") or "Khác"
        loc_counts[loc] = loc_counts.get(loc, 0) + 1
        if r["salary_val"] > 0:
            loc_sal_lists.setdefault(loc, []).append(r["salary_val"])

    sorted_locs = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)
    top15_dict = dict(sorted_locs[:15])
    st.bar_chart(top15_dict)

    st.subheader("Bảng thống kê chi tiết theo Tỉnh/Thành phố")
    prov_rows = []
    for loc, cnt in sorted_locs:
        med_s = statistics.median(loc_sal_lists[loc]) if loc in loc_sal_lists else 0.0
        prov_rows.append({
            "Tỉnh / Thành phố": loc,
            "Số tin đăng": cnt,
            "Tỷ trọng (%)": round(cnt / len(filtered) * 100, 2),
            "Lương trung vị (VNĐ)": int(round(med_s, 0)),
        })
    st.dataframe(prov_rows, use_container_width=True)

with tab3:
    st.subheader("Xu hướng số tin theo tháng & So sánh Baseline (MAE)")
    counts_by_month = {}
    for r in filtered:
        ym = r.get("year_month", "")
        if ym:
            counts_by_month[ym] = counts_by_month.get(ym, 0) + 1

    months = sorted(counts_by_month.keys())
    actuals = [float(counts_by_month[m]) for m in months]
    n = len(months)

    if n >= 4:
        test_periods = min(3, n - 2)
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
        abs_errors = [abs(actuals[i] - preds[i]) for i in range(n)]

        eval_idx = [i for i in range(split_idx, n) if baselines[i] is not None]
        if eval_idx:
            mae_base = statistics.mean(abs(actuals[i] - baselines[i]) for i in eval_idx)
            mae_model = statistics.mean(abs(actuals[i] - preds[i]) for i in eval_idx)
            rmse_model = (statistics.mean((actuals[i] - preds[i]) ** 2 for i in eval_idx)) ** 0.5
            m1, m2, m3 = st.columns(3)
            m1.metric("MAE Baseline (kỳ trước)", f"{mae_base:.2f}")
            m2.metric("MAE Mô hình tuyến tính", f"{mae_model:.2f}")
            m3.metric("RMSE Mô hình", f"{rmse_model:.2f}")

        st.line_chart({
            "Thực tế": {months[i]: actuals[i] for i in range(n)},
            "Dự báo mô hình": {months[i]: preds[i] for i in range(n)},
        })

        table_rows = []
        for i, m in enumerate(months):
            table_rows.append({
                "Tháng": m,
                "Thực tế (tin)": int(actuals[i]),
                "Baseline kỳ trước": int(baselines[i]) if baselines[i] is not None else None,
                "Dự báo mô hình": int(preds[i]),
                "Sai số tuyệt đối": int(abs_errors[i]),
            })
        st.dataframe(table_rows, use_container_width=True)

        worst_idx = max(range(n), key=lambda i: abs_errors[i])
        st.info(
            f"**Phân tích lỗi (Error Analysis):** Giai đoạn có sai số lớn nhất là **{months[worst_idx]}** "
            f"(sai số tuyệt đối **{int(abs_errors[worst_idx])}** tin). Mô hình xu hướng tuyến tính cơ bản "
            f"dễ sai lệch ở các giai đoạn biến động theo mùa vụ hoặc dịp lễ/Tết khi lượng tin thay đổi đột ngột; "
            f"đây được ghi nhận rõ là hạn chế đã biết của mô hình."
        )
    else:
        st.warning("Cần ít nhất 4 mốc tháng để tính xu hướng và đánh giá MAE.")

with tab4:
    st.subheader("Bảng đặc trưng (jobs_features.csv) sau khi lọc")
    display_cols = [
        "job_id", "posted_date", "year_month", "title", "role_group",
        "location", "experience_years", "salary_avg", *skill_cols,
    ]
    clean_table = [{k: r.get(k, "") for k in display_cols} for r in filtered]
    st.dataframe(clean_table, use_container_width=True)

    csv_buffer = ["\ufeff" + ",".join(display_cols)]
    for item in clean_table:
        escaped = []
        for col in display_cols:
            val = str(item.get(col, "")).replace('"', '""')
            escaped.append(f'"{val}"' if ("," in val or '"' in val or "\n" in val) else val)
        csv_buffer.append(",".join(escaped))

    st.download_button(
        label="Tải dữ liệu đã lọc (.csv)",
        data="\n".join(csv_buffer).encode("utf-8"),
        file_name="jobs_features_vietnam_filtered.csv",
        mime="text/csv",
    )
