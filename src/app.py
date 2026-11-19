import math
import os
import statistics
import struct
import zlib
import streamlit as st

from pipeline import (
    PRESET_CAREERS,
    SKILL_LABELS,
    VN_34_UNITS,
    VN_CITIES_6,
    evaluate_monthly_forecast,
    fetch_online_rows,
    load_offline_rows,
    summarize_data_quality,
)

st.set_page_config(
    page_title="Phân tích & Dự báo Tuyển dụng CNTT Việt Nam",
    page_icon="🌐",
    layout="wide",
)


def _write_png(filepath: str, width: int, height: int, pixel_fn):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            r, g, b, a = pixel_fn(x, y, width, height)
            raw.extend((
                max(0, min(255, int(r))),
                max(0, min(255, int(g))),
                max(0, min(255, int(b))),
                max(0, min(255, int(a))),
            ))

    def _chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", crc)

    ihdr = struct.pack("!IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=6)
    png_bytes = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")
    with open(filepath, "wb") as f:
        f.write(png_bytes)


def build_wide_tech_cover(path: str = "assets/tech_wide_cover.png") -> str:
    nodes = [
        (0.14, 0.34, 0.022, (56, 189, 248, 255)),
        (0.28, 0.66, 0.026, (45, 212, 191, 255)),
        (0.46, 0.30, 0.024, (251, 146, 60, 255)),
        (0.62, 0.62, 0.028, (96, 165, 250, 255)),
        (0.78, 0.36, 0.025, (45, 212, 191, 255)),
        (0.89, 0.64, 0.020, (251, 146, 60, 255)),
    ]
    edges = [
        ((0.14, 0.34), (0.28, 0.66)),
        ((0.28, 0.66), (0.46, 0.30)),
        ((0.46, 0.30), (0.62, 0.62)),
        ((0.62, 0.62), (0.78, 0.36)),
        ((0.78, 0.36), (0.89, 0.64)),
        ((0.14, 0.34), (0.46, 0.30)),
        ((0.46, 0.30), (0.78, 0.36)),
    ]

    def px(x, y, w, h):
        nx, ny = x / max(1, w - 1), y / max(1, h - 1)
        r = 15 + 14 * nx + 8 * ny
        g = 23 + 48 * nx + 24 * ny
        b = 42 + 68 * nx - 12 * ny
        glow = math.exp(-(((nx - 0.52) / 0.34) ** 2 + ((ny - 0.48) / 0.36) ** 2))
        r += 24 * glow
        g += 46 * glow
        b += 58 * glow
        for (x0, y0), (x1, y1) in edges:
            dx, dy = x1 - x0, y1 - y0
            denom = dx * dx + dy * dy
            if denom > 0:
                t = max(0.0, min(1.0, ((nx - x0) * dx + (ny - y0) * dy) / denom))
                proj_x, proj_y = x0 + t * dx, y0 + t * dy
                if math.hypot((nx - proj_x) * 1.6, ny - proj_y) < 0.0045:
                    return (125, 211, 252, 235)
        wave_a = 0.78 + 0.07 * math.sin(nx * 14.0) - 0.06 * nx
        wave_b = 0.80 + 0.05 * math.cos(nx * 10.0 + 0.8) - 0.05 * nx
        if abs(ny - wave_a) < 0.0055:
            return (251, 146, 60, 255)
        if abs(ny - wave_b) < 0.0045:
            return (45, 212, 191, 240)
        for cx, cy, rad, col in nodes:
            d = math.hypot((nx - cx) * 1.55, ny - cy)
            if d <= rad * 1.45 and d > rad:
                return (col[0], col[1], col[2], 95)
            if d <= rad:
                return col
        return (r, g, b, 255)

    _write_png(path, 1280, 270, px)
    return path


@st.cache_data
def get_offline_cached(path: str):
    return load_offline_rows(path)


@st.cache_data(ttl=300, show_spinner=False)
def get_online_cached(query: str, bust: int = 0):
    _ = bust
    return fetch_online_rows(query)


cover_img = build_wide_tech_cover()

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #1e293b;
        }
        .stApp { background-color: #f8fafc; }
        [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
        .cover-wrap {
            background: #0f172a; border-radius: 12px; overflow: hidden;
            border: 1px solid #cbd5e1; margin-bottom: 12px;
        }
        .cover-caption {
            background: #ffffff; padding: 12px 18px; border-top: 1px solid #e2e8f0;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
        }
        .cover-caption h1 { font-size: 1.32rem; font-weight: 800; color: #0f172a; margin: 0; }
        .cover-caption .sub { font-size: 0.83rem; color: #475569; }
        .source-note {
            background-color: #ffffff; border: 1px solid #cbd5e1; border-left: 4px solid #0284c7;
            padding: 9px 14px; border-radius: 8px; font-size: 0.85rem; color: #1e293b; margin-bottom: 12px;
        }
        .stat-cell {
            background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;
        }
        .stat-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #64748b; }
        .stat-main { font-size: 1.35rem; font-weight: 800; color: #0f172a; margin: 2px 0; }
        .stat-sub { font-size: 0.75rem; color: #475569; }
        .caption-note {
            font-size: 0.82rem; color: #334155; background-color: #ffffff;
            border: 1px solid #e2e8f0; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("reset_tick", 0)
st.session_state.setdefault("online_ran", False)
st.session_state.setdefault("online_query", PRESET_CAREERS["Data / BI (Python, SQL, Pandas)"])
st.session_state.setdefault("online_label", "Data / BI (Python, SQL, Pandas)")
st.session_state.setdefault("online_bust", 0)

with st.sidebar:
    st.markdown("**Nguồn dữ liệu**")
    source_mode = st.radio("Chế độ", ["Dữ liệu mẫu Offline", "Tìm kiếm Online"], index=0, label_visibility="collapsed")

    if source_mode == "Dữ liệu mẫu Offline":
        csv_path = st.text_input("File dữ liệu", value="data/jobs_features.csv")
        try:
            rows = get_offline_cached(csv_path)
            status_msg = f"<b>Offline:</b> {len(rows)} tin (chuẩn 34 ĐVHC cấp tỉnh VN) · Nguồn: <b>Dữ liệu mẫu nội bộ</b> ({csv_path})."
        except Exception as e:
            st.error(f"Không đọc được '{csv_path}': {e}")
            st.stop()
    else:
        career_choice = st.selectbox("Nghề cần tìm", list(PRESET_CAREERS.keys()), index=0)
        if career_choice == "Tùy chọn từ khóa...":
            q_val = st.text_input("Từ khóa", value="qa tester sql").strip()
        else:
            q_val = PRESET_CAREERS[career_choice]
            st.caption(f"Từ khóa: {q_val}")

        if st.button("Tìm kiếm", type="primary", use_container_width=True):
            st.session_state.online_ran = True
            st.session_state.online_query = q_val or "data python sql"
            st.session_state.online_label = career_choice
            st.session_state.online_bust += 1

        if not st.session_state.online_ran:
            rows = get_offline_cached("data/jobs_features.csv")
            status_msg = f"Chọn nghề và bấm <b>Tìm kiếm</b> để lấy tin online · Đang hiển thị sẵn <b>Offline</b> ({len(rows)} tin)."
        else:
            live_rows, src_notes, is_broad = get_online_cached(
                st.session_state.online_query, bust=st.session_state.online_bust
            )
            if live_rows:
                rows = live_rows
                src_text = " | ".join(src_notes)
                extra_txt = " (mở rộng danh sách CNTT hiện có khi chưa có tin khớp chặt)" if is_broad else ""
                status_msg = f"<b>Online:</b> {len(rows)} tin cho <b>{st.session_state.online_label}</b>{extra_txt} · Nguồn: <b>{src_text}</b>."
            else:
                rows = get_offline_cached("data/jobs_features.csv")
                status_msg = f"Nguồn online tạm gián đoạn · Đã tự chuyển về <b>Offline</b> ({len(rows)} tin)."

if not rows:
    st.warning("Không có dữ liệu.")
    st.stop()

skill_cols = [c for c in SKILL_LABELS.keys() if c in rows[0]]
skill_map = {c: SKILL_LABELS[c] for c in skill_cols}

roles = ["Tất cả"] + sorted({r["role_group"] for r in rows if r.get("role_group")})
locs = ["Tất cả"] + VN_34_UNITS
skill_opts = ["Tất cả"] + [f"Có {skill_map[c]}" for c in skill_cols]

tick = st.session_state.reset_tick
with st.sidebar:
    st.divider()
    st.markdown("**Bộ lọc**")
    sel_role = st.selectbox("Nhóm vị trí", roles, key=f"role_{tick}")
    sel_loc = st.selectbox("Tỉnh / Thành (34 ĐVHC VN)", locs, key=f"loc_{tick}")
    sel_skill_lbl = st.selectbox("Kỹ năng (mã hóa 1)", skill_opts, key=f"skill_{tick}")
    kw = st.text_input("Tên vị trí", placeholder="VD: Data, Python, QA...", key=f"kw_{tick}").strip().lower()
    if st.button("Đặt lại bộ lọc", use_container_width=True):
        st.session_state.reset_tick += 1
        st.rerun()

sel_skill = "Tất cả" if sel_skill_lbl == "Tất cả" else sel_skill_lbl.replace("Có ", "", 1)
label_to_col = {v: k for k, v in skill_map.items()}
sel_skill_col = label_to_col.get(sel_skill)

filtered = [
    r for r in rows
    if (sel_role == "Tất cả" or r["role_group"] == sel_role)
    and (sel_loc == "Tất cả" or r["location"] == sel_loc)
    and (not kw or kw in r["title"].lower())
    and (not sel_skill_col or int(float(r.get(sel_skill_col, 0) or 0)) == 1)
]

st.markdown('<div class="cover-wrap">', unsafe_allow_html=True)
st.image(cover_img, use_container_width=True)
st.markdown(
    """
    <div class="cover-caption">
        <div>
            <h1>Phân tích & Dự báo Tuyển dụng CNTT Việt Nam</h1>
            <div class="sub">34 đơn vị hành chính cấp tỉnh (6 TP trực thuộc TW & 28 tỉnh) · Kỹ năng · Lương trung vị · Dự báo & MAE</div>
        </div>
        <div class="sub">Kho dữ liệu: <b>doan_cdtn2</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

dq = summarize_data_quality(filtered)
st.markdown(
    f'<div class="source-note">{status_msg} · Bộ lọc: <b>{sel_role}</b> / <b>{sel_loc}</b> / <b>{sel_skill_lbl}</b> · Chất lượng dữ liệu: lương thực <b>{dq["salary_pct"]}%</b>, có kỹ năng <b>{dq["skill_pct"]}%</b>.</div>',
    unsafe_allow_html=True,
)

skill_totals = {
    skill_map[c]: sum(int(float(r.get(c, 0) or 0)) for r in filtered)
    for c in skill_cols
}
salaries = [r["salary_val"] for r in filtered if r["salary_val"] > 0]
med_sal = statistics.median(salaries) if salaries else 0.0
exps = [r["exp_val"] for r in filtered if r["exp_val"] > 0]
med_exp = statistics.median(exps) if exps else 0.0

if filtered and any(v > 0 for v in skill_totals.values()):
    top_sk, top_n = max(skill_totals.items(), key=lambda x: x[1])
    top_sk_sub = f"{top_n}/{len(filtered)} tin ({round(top_n / len(filtered) * 100)}%)"
else:
    top_sk, top_sk_sub = "N/A", "0 tin"

c1, c2, c3, c4, c5 = st.columns(5)
for col, lbl, val, sub in [
    (c1, "Tin tuyển dụng", f"{len(filtered):,}", f"Tổng nguồn: {len(rows):,}"),
    (c2, "Địa bàn (34 ĐVHC)", f"{dq['distinct_units']}/34", "6 TP TW & 28 tỉnh"),
    (c3, "Lương trung vị", f"{med_sal/1e6:.1f}M", f"{med_sal:,.0f} đ"),
    (c4, "Kỹ năng dẫn đầu", top_sk, top_sk_sub),
    (c5, "Kinh nghiệm", f"{med_exp:.1f} năm", "Trung vị"),
]:
    col.markdown(
        f'<div class="stat-cell"><div class="stat-label">{lbl}</div><div class="stat-main">{val}</div><div class="stat-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
if not filtered:
    st.warning("Không có tin nào khớp với bộ lọc hiện tại.")
    st.stop()

t1, t2, t3, t4 = st.tabs(["Kỹ năng & Lương", "34 Tỉnh / Thành VN", "Dự báo & MAE", "Dữ liệu & CSV"])

with t1:
    l_col, r_col = st.columns(2)
    with l_col:
        st.markdown("#### Nhóm vị trí tìm kiếm cần những kỹ năng nào?")
        avail_roles = sorted({r["role_group"] for r in filtered})
        role_choices = ["Tất cả nhóm vị trí"] + avail_roles
        def_idx = (avail_roles.index(sel_role) + 1) if sel_role in avail_roles else 0
        chosen_role = st.selectbox("Chọn nhóm vị trí", role_choices, index=def_idx)

        subset = filtered if chosen_role == "Tất cả nhóm vị trí" else [r for r in filtered if r["role_group"] == chosen_role]
        r_skills = {
            skill_map[c]: sum(int(float(r.get(c, 0) or 0)) for r in subset)
            for c in skill_cols
        }
        r_skills = dict(sorted(r_skills.items(), key=lambda x: x[1], reverse=True))
        top3 = [f"{k} ({round(v/len(subset)*100)}%)" for k, v in list(r_skills.items())[:3] if v > 0 and subset]
        st.markdown(
            f'<div class="caption-note"><b>{chosen_role}</b> ({len(subset)} tin): nổi bật <b>{", ".join(top3) if top3 else "chưa rõ"}</b> · mã hóa 1 = có nhắc kỹ năng, 0 = không.</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(r_skills, color="#0284c7", height=275)

    with r_col:
        st.markdown("#### Mức lương trung vị theo nhóm vị trí")
        st.markdown(
            '<div class="caption-note">Dùng trung vị thay cho trung bình để hạn chế ảnh hưởng của các tin lương ngoại lai.</div>',
            unsafe_allow_html=True,
        )
        sal_by_role = {}
        for rg in sorted({r["role_group"] for r in filtered}):
            vals = [r["salary_val"] for r in filtered if r["role_group"] == rg and r["salary_val"] > 0]
            if vals:
                sal_by_role[rg] = round(statistics.median(vals), 0)
        st.bar_chart(dict(sorted(sal_by_role.items(), key=lambda x: x[1], reverse=True)), color="#0f766e", height=325)

with t2:
    st.markdown("#### Phân bố tin theo 34 đơn vị hành chính cấp tỉnh Việt Nam (Top 15)")
    loc_cnt = {}
    loc_sal = {}
    for r in filtered:
        loc_cnt[r["location"]] = loc_cnt.get(r["location"], 0) + 1
        if r["salary_val"] > 0:
            loc_sal.setdefault(r["location"], []).append(r["salary_val"])
    s_locs = sorted(loc_cnt.items(), key=lambda x: x[1], reverse=True)
    st.bar_chart(dict(s_locs[:15]), color="#1d4ed8", height=280)
    st.dataframe([
        {
            "Tỉnh / Thành phố (34 ĐVHC)": loc,
            "Loại": "TP trực thuộc TW" if loc in VN_CITIES_6 else "Tỉnh",
            "Số tin": cnt,
            "Tỷ trọng (%)": round(cnt / len(filtered) * 100, 2),
            "Lương trung vị (VNĐ)": int(round(statistics.median(loc_sal[loc]), 0)) if loc in loc_sal else 0,
        }
        for loc, cnt in s_locs
    ], use_container_width=True, height=300)

with t3:
    fc = evaluate_monthly_forecast(filtered)
    if fc["enough_data"]:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("MAE Baseline (kỳ trước)", f"{fc['mae_base']:.2f}")
        m2.metric("MAE Trung bình trượt (3 kỳ)", f"{fc['mae_ma3']:.2f}")
        m3.metric("MAE Mô hình xu hướng", f"{fc['mae_trend']:.2f}")
        m4.metric("RMSE Mô hình xu hướng", f"{fc['rmse_trend']:.2f}")

        months = fc["months"]
        st.line_chart({
            "Thực tế": {months[i]: fc["actuals"][i] for i in range(len(months))},
            "Xu hướng": {months[i]: fc["trend_preds"][i] for i in range(len(months))},
        }, height=280)

        st.dataframe([
            {
                "Tháng": months[i],
                "Thực tế": int(fc["actuals"][i]),
                "Baseline kỳ trước": int(fc["baselines"][i]) if fc["baselines"][i] is not None else None,
                "MA-3": fc["ma3_preds"][i],
                "Dự báo xu hướng": int(fc["trend_preds"][i]),
                "Sai số tuyệt đối": int(fc["errs"][i]),
            }
            for i in range(len(months))
        ], use_container_width=True)

        st.markdown(
            f'<div class="caption-note"><b>Phân tích lỗi:</b> Tháng lệch lớn nhất là <b>{fc["worst_month"]}</b> ({fc["worst_err"]} tin) do biến động mùa vụ/lễ Tết; đối chiếu đồng thời Baseline kỳ trước, Trung bình trượt 3 kỳ và xu hướng tuyến tính giúp nhận diện rõ giới hạn của mô hình cơ bản.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"Có {len(fc['months'])} mốc tháng (cần tối thiểu 4 tháng để đánh giá MAE). Hãy dùng chế độ Dữ liệu mẫu Offline để xem đầy đủ.")

with t4:
    cols = ["job_id", "posted_date", "year_month", "title", "role_group", "location", "experience_years", "salary_avg", "nguon_web", "link_nguon", "pham_vi_nguon", *skill_cols]
    tbl = [{k: r.get(k, "") for k in cols} for r in filtered]
    st.dataframe(tbl, use_container_width=True, height=320)

    csv_lines = ["\ufeff" + ",".join(cols)]
    for item in tbl:
        csv_lines.append(",".join(
            f'"{str(item.get(c, "")).replace(chr(34), chr(34)*2)}"'
            if ("," in str(item.get(c, "")) or '"' in str(item.get(c, "")))
            else str(item.get(c, ""))
            for c in cols
        ))
    st.download_button("Tải CSV", data="\n".join(csv_lines).encode("utf-8"), file_name="jobs_vn_34dvhc.csv", mime="text/csv")
