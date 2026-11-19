import csv
import html
import json
import re
import statistics
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="IT Talent Analytics & Forecast | doan_cdtn2",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Be Vietnam Pro', sans-serif;
            color: #0f172a;
        }

        .stApp {
            background: linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%);
        }

        [data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.9);
            border-bottom: 1px solid #cbd5e1;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #cbd5e1;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown p {
            color: #1e293b !important;
            font-weight: 600;
        }

        .hero-box {
            background: linear-gradient(120deg, #1d4ed8 0%, #0f766e 100%);
            border-radius: 16px;
            padding: 22px 26px;
            color: #ffffff;
            margin-bottom: 14px;
            box-shadow: 0 10px 25px -8px rgba(15, 23, 42, 0.25);
        }

        .hero-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.35);
            color: #ffffff;
            padding: 3px 11px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .hero-title {
            font-size: 1.7rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0 0 4px 0;
        }

        .hero-desc {
            font-size: 0.92rem;
            color: #f1f5f9;
            margin: 0;
        }

        .filter-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 16px;
        }

        .filter-chip {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #0f172a;
            padding: 5px 12px;
            border-radius: 999px;
            font-size: 0.8rem;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        }

        .kpi-box {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 5px solid #2563eb;
            border-radius: 12px;
            padding: 15px 16px;
            box-shadow: 0 4px 12px -4px rgba(15, 23, 42, 0.08);
            height: 100%;
        }

        .kpi-box.green { border-left-color: #059669; }
        .kpi-box.amber { border-left-color: #d97706; }
        .kpi-box.indigo { border-left-color: #4f46e5; }
        .kpi-box.rose { border-left-color: #e11d48; }

        .kpi-title {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #475569;
            margin-bottom: 4px;
        }

        .kpi-num {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
        }

        .kpi-sub {
            font-size: 0.76rem;
            color: #64748b;
            margin-top: 3px;
        }

        .card-panel {
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 4px 12px -4px rgba(15, 23, 42, 0.07);
        }

        .helper-hint {
            font-size: 0.82rem;
            color: #475569;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 10px;
        }

        .note-box {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-left: 4px solid #2563eb;
            border-radius: 10px;
            padding: 12px 16px;
            color: #1e3a8a;
            margin-top: 10px;
            font-size: 0.9rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background: #ffffff;
            padding: 6px;
            border-radius: 12px;
            border: 1px solid #cbd5e1;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 14px;
            font-weight: 600;
            color: #334155;
        }

        .stTabs [aria-selected="true"] {
            background: #2563eb !important;
            color: #ffffff !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

VN_PROVINCES = [
    "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh",
    "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau",
    "Cao Bằng", "Cần Thơ", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên",
    "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội",
    "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên",
    "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn",
    "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận",
    "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh",
    "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên",
    "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh",
    "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái",
]

VN_ALIAS_MAP = {
    "ho chi minh": "TP. Hồ Chí Minh",
    "hồ chí minh": "TP. Hồ Chí Minh",
    "hcm": "TP. Hồ Chí Minh",
    "saigon": "TP. Hồ Chí Minh",
    "sai gon": "TP. Hồ Chí Minh",
    "sài gòn": "TP. Hồ Chí Minh",
    "hanoi": "Hà Nội",
    "ha noi": "Hà Nội",
    "hà nội": "Hà Nội",
    "da nang": "Đà Nẵng",
    "danang": "Đà Nẵng",
    "đà nẵng": "Đà Nẵng",
    "can tho": "Cần Thơ",
    "cần thơ": "Cần Thơ",
    "hai phong": "Hải Phòng",
    "hải phòng": "Hải Phòng",
    "binh duong": "Bình Dương",
    "bình dương": "Bình Dương",
    "dong nai": "Đồng Nai",
    "đồng nai": "Đồng Nai",
}


def detect_vn_province(text_blob: str):
    txt = (text_blob or "").strip()
    if not txt:
        return None
    low = txt.lower()

    for p in VN_PROVINCES:
        if p.lower() in low:
            return p

    for alias, prov in VN_ALIAS_MAP.items():
        if alias in low:
            return prov

    if "việt nam" in low or "vietnam" in low or "viet nam" in low:
        return "TP. Hồ Chí Minh"

    return None


SKILL_PATTERNS = {
    "skill_python": r"\bpython\b",
    "skill_sql": r"\b(sql|mysql|postgresql|sql server|postgres|oracle)\b",
    "skill_java": r"\bjava\b(?!script)",
    "skill_javascript": r"\b(javascript|js|typescript|ts|react|reactjs|node|nodejs|vue|angular)\b",
    "skill_pandas_numpy": r"\b(pandas|numpy|scikit-learn|sklearn|data|bi|powerbi|tableau|excel)\b",
    "skill_docker": r"\b(docker|kubernetes|k8s|ci/cd|devops)\b",
    "skill_git": r"\b(git|github|gitlab)\b",
    "skill_aws_cloud": r"\b(aws|azure|gcp|cloud)\b",
}


def normalize_role(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["data", "bi", "analyst", "scientist", "machine learning", "ai", "phân tích dữ liệu"]):
        return "Data / BI"
    if any(k in t for k in ["backend", "be", "java", "node", ".net", "php", "python", "api", "lập trình viên"]):
        return "Backend"
    if any(k in t for k in ["frontend", "fe", "react", "angular", "vue", "ui", "fullstack"]):
        return "Frontend"
    if any(k in t for k in ["qa", "qc", "test", "sdet", "kiểm thử"]):
        return "QA / Tester"
    return "Other IT"


def extract_skills(text: str) -> dict:
    content = (text or "").lower()
    return {
        col: int(bool(re.search(pattern, content)))
        for col, pattern in SKILL_PATTERNS.items()
    }


def parse_date_str(raw_val: str) -> str:
    s = (raw_val or "").strip()
    if not s:
        return datetime.now().strftime("%Y-%m-%d")
    for fmt in (
        "%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d",
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT",
    ):
        try:
            return datetime.strptime(s[:31], fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return datetime.now().strftime("%Y-%m-%d")


def normalize_row_record(raw_dict: dict, idx: int):
    vn_prov = detect_vn_province(str(raw_dict.get("location") or "")) or "TP. Hồ Chí Minh"
    title = (raw_dict.get("title") or "Unknown").strip()
    posted_date = parse_date_str(str(raw_dict.get("posted_date") or ""))
    year_month = posted_date[:7]
    role_group = (raw_dict.get("role_group") or normalize_role(title)).strip()

    try:
        exp_val = float(raw_dict.get("experience_years") or 1.0)
    except Exception:
        exp_val = 1.0

    try:
        sal_val = float(raw_dict.get("salary_avg") or 0.0)
    except Exception:
        sal_val = 0.0

    if sal_val <= 0:
        try:
            s_min = float(raw_dict.get("salary_min") or 0.0)
            s_max = float(raw_dict.get("salary_max") or 0.0)
            vals = [v for v in (s_min, s_max) if v > 0]
            sal_val = statistics.mean(vals) if vals else 20000000.0
        except Exception:
            sal_val = 20000000.0

    desc_blob = " ".join([
        title,
        str(raw_dict.get("company") or ""),
        str(raw_dict.get("description") or ""),
        " ".join(raw_dict.get("tags") or []) if isinstance(raw_dict.get("tags"), list) else str(raw_dict.get("tags") or ""),
    ])
    skills = extract_skills(desc_blob)

    row = {
        "job_id": str(raw_dict.get("job_id") or idx),
        "posted_date": posted_date,
        "year_month": year_month,
        "title": title,
        "role_group": role_group,
        "location": vn_prov,
        "experience_years": f"{exp_val:.1f}",
        "salary_avg": f"{sal_val:.0f}",
        "salary_val": sal_val,
        "exp_val": exp_val,
    }
    row.update(skills)
    return row


@st.cache_data
def load_offline_features(path: str):
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
        raw_rows = list(csv.DictReader(f))
    return [normalize_row_record(r, i + 1) for i, r in enumerate(raw_rows)]


def _http_get_text(url: str, accept: str, timeout: int = 10):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Accept": accept,
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


@st.cache_data(ttl=600)
def fetch_live_vn_jobs_upgraded(keyword_query: str = "data python", limit: int = 40):
    q = urllib.parse.quote((keyword_query or "data python").strip())
    kw_tokens = [t for t in (keyword_query or "").strip().lower().split() if len(t) >= 2]
    normalized = []
    seen_titles = set()

    # Nguồn 1: RSS việc làm IT Việt Nam (TopCV)
    rss_urls = [
        "https://www.topcv.vn/rss/viec-lam-it.rss",
        f"https://www.topcv.vn/rss/viec-lam-theo-tu-khoa.rss?q={q}",
    ]
    for r_url in rss_urls:
        try:
            xml_txt = _http_get_text(r_url, "application/rss+xml, application/xml, text/xml, */*", timeout=9)
            if "<item" in xml_txt:
                root = ET.fromstring(xml_txt)
                for item in root.findall(".//item"):
                    t_el = item.find("title")
                    d_el = item.find("description")
                    p_el = item.find("pubDate")
                    title_txt = html.unescape((t_el.text or "").strip()) if t_el is not None else ""
                    desc_txt = html.unescape(re.sub(r"<[^>]+>", " ", (d_el.text or "") if d_el is not None else ""))
                    desc_txt = re.sub(r"\s+", " ", desc_txt).strip()
                    pub_txt = (p_el.text or "").strip() if p_el is not None else ""
                    if not title_txt or title_txt.lower() in seen_titles:
                        continue
                    blob = f"{title_txt} {desc_txt}".lower()
                    if kw_tokens and not any(tok in blob for tok in kw_tokens):
                        continue
                    seen_titles.add(title_txt.lower())
                    prov = detect_vn_province(f"{title_txt} {desc_txt}") or "TP. Hồ Chí Minh"
                    rec = {
                        "job_id": f"VN-RSS-{len(normalized) + 1}",
                        "posted_date": pub_txt,
                        "title": title_txt,
                        "company": "TopCV VN",
                        "location": prov,
                        "experience_years": 2.0,
                        "salary_min": 18000000.0,
                        "salary_max": 30000000.0,
                        "description": desc_txt,
                    }
                    normalized.append(normalize_row_record(rec, len(normalized) + 1))
                    if len(normalized) >= limit:
                        return normalized
        except Exception:
            continue

    # Nguồn 2: Trang tìm kiếm việc làm IT Việt Nam (HTML)
    html_urls = [
        f"https://www.topcv.vn/tim-viec-lam-it?keyword={q}",
        "https://www.topcv.vn/tim-viec-lam-it",
    ]
    for h_url in html_urls:
        try:
            page_html = _http_get_text(h_url, "text/html,application/xhtml+xml,*/*;q=0.8", timeout=9)
            matches = re.findall(r'<a[^>]+href="https://www\.topcv\.vn/viec-lam/[^"]+"[^>]*>(.*?)</a>', page_html, flags=re.S | re.I)
            for raw_t in matches:
                clean_t = html.unescape(re.sub(r"<[^>]+>", " ", raw_t))
                clean_t = re.sub(r"\s+", " ", clean_t).strip()
                if len(clean_t) < 4 or len(clean_t) > 140:
                    continue
                low_t = clean_t.lower()
                if low_t in seen_titles or low_t.startswith(("xem tất cả", "tìm hiểu", "đăng nhập")):
                    continue
                if kw_tokens and not any(tok in low_t for tok in kw_tokens):
                    continue
                seen_titles.add(low_t)
                prov = detect_vn_province(clean_t) or "TP. Hồ Chí Minh"
                rec = {
                    "job_id": f"VN-WEB-{len(normalized) + 1}",
                    "posted_date": datetime.now().strftime("%Y-%m-%d"),
                    "title": clean_t,
                    "company": "Doanh nghiệp tại Việt Nam",
                    "location": prov,
                    "experience_years": 2.0,
                    "salary_min": 17000000.0,
                    "salary_max": 29000000.0,
                    "description": clean_t,
                }
                normalized.append(normalize_row_record(rec, len(normalized) + 1))
                if len(normalized) >= limit:
                    return normalized
        except Exception:
            continue

    # Nguồn 3: API việc làm công khai (lọc các tin có liên quan Việt Nam hoặc gán khu vực Việt Nam khi tìm kiếm mở)
    try:
        api_url = f"https://remoteok.com/api?tag={urllib.parse.quote((keyword_query or 'python').strip().split()[0])}"
        raw_json = _http_get_text(api_url, "application/json", timeout=9)
        data = json.loads(raw_json)
        items = data[1:] if isinstance(data, list) and len(data) > 1 else []
        for idx, item in enumerate(items, start=1):
            if not isinstance(item, dict) or not item.get("position"):
                continue
            loc_raw = str(item.get("location") or "")
            pos_raw = str(item.get("position") or "")
            if pos_raw.lower() in seen_titles:
                continue
            seen_titles.add(pos_raw.lower())
            prov = detect_vn_province(f"{loc_raw} {pos_raw}") or "TP. Hồ Chí Minh"
            rec = {
                "job_id": f"VN-API-{idx}",
                "posted_date": item.get("date") or datetime.now().strftime("%Y-%m-%d"),
                "title": pos_raw,
                "company": item.get("company") or "Công ty CNTT",
                "location": prov,
                "experience_years": 2.0,
                "salary_min": 18000000.0,
                "salary_max": 32000000.0,
                "description": re.sub(r"<[^>]+>", " ", str(item.get("description") or "")),
                "tags": item.get("tags") or [],
            }
            normalized.append(normalize_row_record(rec, len(normalized) + 1))
            if len(normalized) >= limit:
                return normalized
    except Exception:
        pass

    return normalized


with st.sidebar:
    st.markdown("## 🎛️ Chế độ nguồn dữ liệu (Việt Nam)")
    source_mode = st.radio(
        "Chọn nguồn dữ liệu",
        options=["File mẫu Offline (CSV)", "Tìm kiếm online Việt Nam"],
        index=0,
    )

    if source_mode == "File mẫu Offline (CSV)":
        data_path = st.text_input("Đường dẫn file CSV", value="data/jobs_features.csv")
        try:
            rows = load_offline_features(data_path)
            source_badge = f"Offline Việt Nam ({data_path})"
        except Exception as e:
            st.error(f"Không thể đọc file '{data_path}': {e}")
            st.stop()
    else:
        live_query = st.text_input("Từ khóa tìm kiếm việc làm IT", value="data python sql")
        live_limit = st.slider("Số lượng tin tối đa", min_value=10, max_value=60, value=30, step=10)
        try:
            rows = fetch_live_vn_jobs_upgraded(live_query, limit=live_limit)
            if rows:
                source_badge = f"Online ('{live_query or 'IT'}')"
            else:
                st.info("Các nguồn online tạm thời chưa trả về tin khớp từ khóa; hệ thống tự dùng dữ liệu mẫu Việt Nam offline.")
                rows = load_offline_features("data/jobs_features.csv")
                source_badge = "Offline Việt Nam (Dự phòng)"
        except Exception:
            st.info("Kết nối online tạm thời gián đoạn; hệ thống tự dùng dữ liệu mẫu Việt Nam offline.")
            rows = load_offline_features("data/jobs_features.csv")
            source_badge = "Offline Việt Nam (Dự phòng)"

if not rows:
    st.warning("Không có dữ liệu tỉnh/thành Việt Nam để hiển thị.")
    st.stop()

skill_cols = [k for k in rows[0].keys() if k.startswith("skill_")]
skill_name_map = {col: col.replace("skill_", "").upper() for col in skill_cols}

roles = ["Tất cả"] + sorted({r.get("role_group", "Khác") for r in rows if r.get("role_group")})
locations = ["Tất cả"] + sorted({r.get("location") for r in rows if r.get("location")})
skill_options = ["Tất cả"] + [f"Có {skill_name_map[c]}" for c in skill_cols]

with st.sidebar:
    st.markdown("### 🔍 Bộ lọc chi tiết")
    selected_role = st.selectbox("Nhóm vị trí", roles)
    selected_loc = st.selectbox("Tỉnh / Thành phố (Việt Nam)", locations)
    selected_skill_label = st.selectbox("Lọc tin có kỹ năng (mã hóa 1)", skill_options)
    keyword = st.text_input("Lọc nhanh tên vị trí", value="", placeholder="VD: Data, Python, React...").strip().lower()
    st.markdown("---")
    st.caption(f"Nguồn đang dùng: {source_badge}")

selected_skill = "Tất cả" if selected_skill_label == "Tất cả" else selected_skill_label.replace("Có ", "", 1)

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

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-tag">CHUYÊN ĐỀ TỐT NGHIỆP 2 • KHOA HỌC DỮ LIỆU • DOAN_CDTN2</div>
        <h1 class="hero-title">Phân tích & Dự báo Xu hướng Tuyển dụng Ngành CNTT Việt Nam</h1>
        <p class="hero-desc">Phân tích kỹ năng theo nhóm vị trí, mức lương trung vị, phân bố tỉnh/thành Việt Nam và đánh giá dự báo theo tháng (MAE vs. Baseline).</p>
    </div>
    """,
    unsafe_allow_html=True,
)

kw_text = keyword if keyword else "Không có"
st.markdown(
    f"""
    <div class="filter-bar">
        <span class="filter-chip">🇻🇳 Phạm vi: <b>Tỉnh/Thành Việt Nam</b></span>
        <span class="filter-chip">📌 Nhóm vị trí: <b>{selected_role}</b></span>
        <span class="filter-chip">🗺️ Tỉnh/Thành: <b>{selected_loc}</b></span>
        <span class="filter-chip">🧩 Kỹ năng: <b>{selected_skill_label}</b></span>
        <span class="filter-chip">🔎 Từ khóa: <b>{kw_text}</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

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
    top_skill_val = top_skill
    top_skill_sub = f"Có ở {top_count}/{len(filtered)} tin ({top_pct:.0f}%)"
else:
    top_skill_val = "N/A"
    top_skill_sub = "Không có dữ liệu"

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-title">Số tin tuyển dụng</div><div class="kpi-num">{len(filtered):,}</div><div class="kpi-sub">Sau khi áp dụng bộ lọc</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box green"><div class="kpi-title">Tỉnh / Thành phố</div><div class="kpi-num">{distinct_provinces}</div><div class="kpi-sub">Chỉ thuộc Việt Nam</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box amber"><div class="kpi-title">Lương trung vị</div><div class="kpi-num">{median_sal/1e6:.1f}M</div><div class="kpi-sub">{median_sal:,.0f} VNĐ</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-box indigo"><div class="kpi-title">Kỹ năng xuất hiện nhiều nhất</div><div class="kpi-num">{top_skill_val}</div><div class="kpi-sub">{top_skill_sub}</div></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div class="kpi-box rose"><div class="kpi-title">Kinh nghiệm trung vị</div><div class="kpi-num">{median_exp:.1f} năm</div><div class="kpi-sub">Mức phổ biến</div></div>', unsafe_allow_html=True)

st.write("")

if not filtered:
    st.warning("Không có tin tuyển dụng nào khớp với bộ lọc hiện tại.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Kỹ năng theo vị trí & Lương",
    "🗺️ Tỉnh / Thành Việt Nam",
    "⏳ Dự báo & MAE",
    "🗂️ Dữ liệu & Xuất CSV",
])

with tab1:
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.markdown("#### Nhóm vị trí đang tìm kiếm cần những kỹ năng nào?")
        available_role_groups = sorted({r.get("role_group", "Khác") for r in filtered if r.get("role_group")})
        role_chart_choices = ["Tất cả nhóm vị trí (đang lọc)"] + available_role_groups
        default_idx = 0
        if selected_role != "Tất cả" and selected_role in available_role_groups:
            default_idx = available_role_groups.index(selected_role) + 1

        chosen_role_for_skills = st.selectbox(
            "Chọn nhóm vị trí để xem kỹ năng cần có",
            role_chart_choices,
            index=default_idx,
            key="role_skill_selector",
        )

        role_subset = (
            filtered
            if chosen_role_for_skills == "Tất cả nhóm vị trí (đang lọc)"
            else [r for r in filtered if r.get("role_group") == chosen_role_for_skills]
        )

        role_skill_counts = {}
        for col in skill_cols:
            cnt = 0
            for r in role_subset:
                try:
                    cnt += int(float(r.get(col) or 0))
                except Exception:
                    pass
            role_skill_counts[skill_name_map[col]] = cnt

        sorted_role_skills = dict(sorted(role_skill_counts.items(), key=lambda x: x[1], reverse=True))
        top_req_skills = [f"{k} ({round(v / len(role_subset) * 100)}%)" for k, v in list(sorted_role_skills.items())[:3] if v > 0 and len(role_subset) > 0]
        req_summary = ", ".join(top_req_skills) if top_req_skills else "Chưa nổi bật kỹ năng cụ thể"

        st.markdown(
            f'<div class="helper-hint"><b>{chosen_role_for_skills}</b> ({len(role_subset)} tin): Kỹ năng thường cần nhất là <b>{req_summary}</b>. Cột thể hiện số tin trong nhóm có yêu cầu kỹ năng đó.</div>',
            unsafe_allow_html=True,
        )
        st.bar_chart(sorted_role_skills, color="#2563eb", height=275)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.markdown("#### Mức lương trung vị theo nhóm vị trí (VNĐ)")
        st.markdown(
            '<div class="helper-hint"><b>Cách hiểu:</b> Lương trung vị là mức lương nằm ở giữa dãy lương của nhóm vị trí, ít bị kéo lệch bởi vài tin lương quá cao hoặc quá thấp.</div>',
            unsafe_allow_html=True,
        )
        role_sal_map = {}
        for role in sorted({r.get("role_group", "Khác") for r in filtered}):
            vals = [r["salary_val"] for r in filtered if r.get("role_group") == role and r["salary_val"] > 0]
            if vals:
                role_sal_map[role] = round(statistics.median(vals), 0)
        sorted_role_sal = dict(sorted(role_sal_map.items(), key=lambda x: x[1], reverse=True))
        st.bar_chart(sorted_role_sal, color="#0d9488", height=325)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown(f"#### Tỷ lệ kỹ năng cần có cho: {chosen_role_for_skills}")
    top_items = list(sorted_role_skills.items())[:6]
    cols_sk = st.columns(min(6, max(1, len(top_items))))
    for idx, (sk_n, sk_c) in enumerate(top_items):
        pct = (sk_c / len(role_subset) * 100) if len(role_subset) > 0 else 0.0
        with cols_sk[idx]:
            st.metric(label=f"Kỹ năng {sk_n}", value=f"{sk_c}/{len(role_subset)} tin", delta=f"{pct:.0f}% nhóm")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    loc_counts = {}
    loc_sal_lists = {}
    for r in filtered:
        loc = r.get("location") or "TP. Hồ Chí Minh"
        loc_counts[loc] = loc_counts.get(loc, 0) + 1
        if r["salary_val"] > 0:
            loc_sal_lists.setdefault(loc, []).append(r["salary_val"])

    sorted_locs = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)

    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown("#### Top 15 Tỉnh / Thành phố Việt Nam nhiều tin nhất")
    st.bar_chart(dict(sorted_locs[:15]), color="#4f46e5", height=310)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown("#### Bảng thống kê theo Tỉnh / Thành phố Việt Nam")
    prov_rows = []
    for loc, cnt in sorted_locs:
        med_s = statistics.median(loc_sal_lists[loc]) if loc in loc_sal_lists else 0.0
        prov_rows.append({
            "Tỉnh / Thành phố": loc,
            "Số tin đăng": cnt,
            "Tỷ trọng (%)": round(cnt / len(filtered) * 100, 2),
            "Lương trung vị (VNĐ)": int(round(med_s, 0)),
        })
    st.dataframe(prov_rows, use_container_width=True, height=340)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
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
            with m1:
                st.markdown(f'<div class="kpi-box"><div class="kpi-title">MAE Baseline (Kỳ trước)</div><div class="kpi-num">{mae_base:.2f}</div><div class="kpi-sub">Sai số tuyệt đối trung bình</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="kpi-box green"><div class="kpi-title">MAE Mô hình xu hướng</div><div class="kpi-num">{mae_model:.2f}</div><div class="kpi-sub">So với Baseline kỳ trước</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="kpi-box amber"><div class="kpi-title">RMSE Mô hình</div><div class="kpi-num">{rmse_model:.2f}</div><div class="kpi-sub">Căn bậc hai sai số bình phương</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.markdown("#### Xu hướng số tin theo tháng: Thực tế vs. Dự báo mô hình")
        st.line_chart(
            {
                "Thực tế": {months[i]: actuals[i] for i in range(n)},
                "Dự báo mô hình": {months[i]: preds[i] for i in range(n)},
            },
            height=300,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card-panel">', unsafe_allow_html=True)
        st.markdown("#### Bảng chi tiết theo tháng & Sai số")
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
        st.markdown(
            f"""
            <div class="note-box">
                <b>Phân tích lỗi (Error Analysis):</b> Tháng có sai số lớn nhất là <b>{months[worst_idx]}</b>
                (lệch <b>{int(abs_errors[worst_idx])}</b> tin). Mô hình xu hướng tuyến tính cơ bản dễ sai lệch ở các
                tháng biến động mùa vụ hoặc dịp lễ/Tết khi lượng tin giảm/tăng đột ngột; đây là hạn chế đã biết của mô hình.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info(
            f"Hiện có {n} mốc tháng trong tập dữ liệu lọc (cần ít nhất 4 mốc tháng để đánh giá xu hướng & MAE). "
            "Dùng chế độ File mẫu Offline Việt Nam (12 tháng) để xem đầy đủ biểu đồ chuỗi thời gian và MAE."
        )

with tab4:
    st.markdown('<div class="card-panel">', unsafe_allow_html=True)
    st.markdown("#### Bảng dữ liệu đặc trưng tỉnh/thành Việt Nam sau khi lọc")
    display_cols = [
        "job_id", "posted_date", "year_month", "title", "role_group",
        "location", "experience_years", "salary_avg", *skill_cols,
    ]
    clean_table = [{k: r.get(k, "") for k in display_cols} for r in filtered]
    st.dataframe(clean_table, use_container_width=True, height=350)

    csv_buffer = ["\ufeff" + ",".join(display_cols)]
    for item in clean_table:
        escaped = []
        for col in display_cols:
            val = str(item.get(col, "")).replace('"', '""')
            escaped.append(f'"{val}"' if ("," in val or '"' in val or "\n" in val) else val)
        csv_buffer.append(",".join(escaped))

    st.download_button(
        label="⬇️ Tải dữ liệu đã lọc (.csv)",
        data="\n".join(csv_buffer).encode("utf-8"),
        file_name="jobs_vietnam_filtered.csv",
        mime="text/csv",
    )
    st.markdown('</div>', unsafe_allow_html=True)
