import csv
import html
import json
import math
import os
import re
import statistics
import struct
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from datetime import datetime
import streamlit as st

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
                dist = math.hypot((nx - proj_x) * 1.6, ny - proj_y)
                if dist < 0.0045:
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


cover_img = build_wide_tech_cover()

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #1e293b;
        }
        .stApp {
            background-color: #f8fafc;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        .cover-wrap {
            background: #0f172a;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #cbd5e1;
            margin-bottom: 12px;
        }
        .cover-caption {
            background: #ffffff;
            padding: 12px 18px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }
        .cover-caption h1 {
            font-size: 1.32rem;
            font-weight: 800;
            color: #0f172a;
            margin: 0;
        }
        .cover-caption .sub {
            font-size: 0.83rem;
            color: #475569;
        }
        .source-note {
            background-color: #ffffff;
            border: 1px solid #cbd5e1;
            border-left: 4px solid #0284c7;
            padding: 9px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #1e293b;
            margin-bottom: 12px;
        }
        .stat-cell {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 14px;
        }
        .stat-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            color: #64748b;
        }
        .stat-main {
            font-size: 1.35rem;
            font-weight: 800;
            color: #0f172a;
            margin: 2px 0;
        }
        .stat-sub {
            font-size: 0.75rem;
            color: #475569;
        }
        .caption-note {
            font-size: 0.82rem;
            color: #334155;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 10px;
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

VN_ALIAS = {
    "ho chi minh": "TP. Hồ Chí Minh", "hồ chí minh": "TP. Hồ Chí Minh", "hcm": "TP. Hồ Chí Minh",
    "saigon": "TP. Hồ Chí Minh", "sài gòn": "TP. Hồ Chí Minh",
    "hanoi": "Hà Nội", "ha noi": "Hà Nội", "hà nội": "Hà Nội",
    "da nang": "Đà Nẵng", "đà nẵng": "Đà Nẵng",
    "can tho": "Cần Thơ", "cần thơ": "Cần Thơ",
    "hai phong": "Hải Phòng", "hải phòng": "Hải Phòng",
    "binh duong": "Bình Dương", "bình dương": "Bình Dương",
    "dong nai": "Đồng Nai", "đồng nai": "Đồng Nai",
}

PRESET_CAREERS = {
    "Data / BI (Python, SQL, Pandas)": "data python sql pandas bi",
    "Backend (Java, Python, SQL, API)": "backend java python sql api",
    "Frontend (JS, TypeScript, React)": "frontend react javascript typescript",
    "QA / Tester (Test, Automation, SQL)": "qa qc tester test automation manual sql",
    "Cloud / DevOps (Docker, AWS, Git)": "devops docker aws cloud git ci/cd",
    "Tùy chọn từ khóa...": "",
}

SKILL_LABELS = {
    "skill_python": "Python",
    "skill_sql": "SQL",
    "skill_java": "Java",
    "skill_javascript": "JS / React",
    "skill_pandas_numpy": "Data / Pandas",
    "skill_docker": "Docker / DevOps",
    "skill_git": "Git",
    "skill_aws_cloud": "AWS / Cloud",
}

SKILL_PATTERNS = {
    "skill_python": r"(?:^|[^a-z0-9_])python(?:[^a-z0-9_]|$)",
    "skill_sql": r"(?:^|[^a-z0-9_])(sql|mysql|postgresql|sql\s*server|postgres|oracle|database|db)(?:[^a-z0-9_]|$)",
    "skill_java": r"(?:^|[^a-z0-9_])java(?!script)(?:[^a-z0-9_]|$)",
    "skill_javascript": r"(?:^|[^a-z0-9_])(javascript|js|typescript|ts|react|reactjs|node|nodejs|vue|angular|frontend)(?:[^a-z0-9_]|$)",
    "skill_pandas_numpy": r"(?:^|[^a-z0-9_])(pandas|numpy|scikit-learn|sklearn|data|bi|power\s*bi|tableau|excel|analytics)(?:[^a-z0-9_]|$)",
    "skill_docker": r"(?:^|[^a-z0-9_])(docker|kubernetes|k8s|ci/cd|devops)(?:[^a-z0-9_]|$)",
    "skill_git": r"(?:^|[^a-z0-9_])(git|github|gitlab|bitbucket|version\s*control)(?:[^a-z0-9_]|$)",
    "skill_aws_cloud": r"(?:^|[^a-z0-9_])(aws|azure|gcp|cloud)(?:[^a-z0-9_]|$)",
}


def detect_vn_province(text_blob: str):
    low = (text_blob or "").strip().lower()
    if not low:
        return None
    for p in VN_PROVINCES:
        if p.lower() in low:
            return p
    for k, v in VN_ALIAS.items():
        if k in low:
            return v
    if "việt nam" in low or "vietnam" in low or "viet nam" in low:
        return "TP. Hồ Chí Minh"
    return None


def normalize_role(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["data", "bi", "analyst", "scientist", "ai", "ml"]):
        return "Data / BI"
    if any(k in t for k in ["backend", "be", "java", "node", ".net", "php", "python", "api"]):
        return "Backend"
    if any(k in t for k in ["frontend", "fe", "react", "angular", "vue", "ui", "fullstack"]):
        return "Frontend"
    if any(k in t for k in ["qa", "qc", "test", "sdet", "kiểm thử"]):
        return "QA / Tester"
    return "Other IT"


def extract_skills(text: str) -> dict:
    low = (text or "").lower()
    return {col: int(bool(re.search(pat, low))) for col, pat in SKILL_PATTERNS.items()}


def parse_date(raw_val: str) -> str:
    s = (raw_val or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.strptime(s[:31], fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return datetime.now().strftime("%Y-%m-%d")


def normalize_record(raw: dict, idx: int, nguon_web: str, link_nguon: str) -> dict:
    prov = detect_vn_province(str(raw.get("location") or "")) or "TP. Hồ Chí Minh"
    title = (raw.get("title") or "Unknown").strip()
    posted = parse_date(str(raw.get("posted_date") or ""))
    role = (raw.get("role_group") or normalize_role(title)).strip()

    try:
        exp_val = float(raw.get("experience_years") or 1.0)
    except Exception:
        exp_val = 1.0

    try:
        sal_val = float(raw.get("salary_avg") or 0.0)
    except Exception:
        sal_val = 0.0

    if sal_val <= 0:
        try:
            vals = [float(x) for x in (raw.get("salary_min"), raw.get("salary_max")) if x and float(x) > 0]
            sal_val = statistics.mean(vals) if vals else 20000000.0
        except Exception:
            sal_val = 20000000.0

    blob = " ".join([
        title,
        role,
        str(raw.get("company") or ""),
        str(raw.get("description") or ""),
        " ".join(raw.get("tags") or []) if isinstance(raw.get("tags"), list) else str(raw.get("tags") or ""),
    ])
    row = {
        "job_id": str(raw.get("job_id") or idx),
        "posted_date": posted,
        "year_month": posted[:7],
        "title": title,
        "role_group": role,
        "location": prov,
        "experience_years": f"{exp_val:.1f}",
        "salary_avg": f"{sal_val:.0f}",
        "nguon_web": nguon_web,
        "link_nguon": link_nguon,
        "salary_val": sal_val,
        "exp_val": exp_val,
    }
    row.update(extract_skills(blob))
    for k, v in raw.items():
        if k.startswith("skill_") and k in SKILL_PATTERNS:
            try:
                if int(float(v or 0)) == 1:
                    row[k] = 1
            except Exception:
                pass
    return row


@st.cache_data
def load_offline_rows(path: str):
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
        data = list(csv.DictReader(f))
    return [normalize_record(r, i + 1, "Dữ liệu mẫu nội bộ", path) for i, r in enumerate(data)]


def _get_text(url: str, accept: str, timeout: int = 8) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": accept,
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_online_rows(query: str, bust: int = 0):
    _ = bust
    q_raw = (query or "data python sql").strip()
    q_enc = urllib.parse.quote(q_raw)
    tokens = [t for t in re.split(r"[\s,/]+", q_raw.lower()) if len(t) >= 2]
    matched_rows, fallback_rows, seen, active_sources = [], [], set(), []

    def _is_match(blob_low: str) -> bool:
        if not tokens:
            return True
        if any(tok in blob_low for tok in tokens):
            return True
        if any(tok in ("qa", "qc", "test", "tester", "automation") for tok in tokens):
            return any(k in blob_low for k in ("qa", "qc", "test", "tester", "automation", "kiểm thử"))
        return False

    rss_feeds = [
        ("TopCV Việt Nam (RSS Việc làm IT)", "https://www.topcv.vn/rss/viec-lam-it.rss"),
        ("TopCV Việt Nam (RSS Theo từ khóa)", f"https://www.topcv.vn/rss/viec-lam-theo-tu-khoa.rss?q={q_enc}"),
    ]
    for src_name, feed_url in rss_feeds:
        try:
            xml_txt = _get_text(feed_url, "application/rss+xml, application/xml, text/xml, */*")
            if "<item" in xml_txt:
                added_here = 0
                for item in ET.fromstring(xml_txt).findall(".//item"):
                    t_el, d_el, p_el, l_el = item.find("title"), item.find("description"), item.find("pubDate"), item.find("link")
                    title = html.unescape((t_el.text or "").strip()) if t_el is not None else ""
                    desc = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", (d_el.text or "") if d_el is not None else ""))).strip()
                    item_url = (l_el.text or "").strip() or feed_url
                    if not title or title.lower() in seen:
                        continue
                    seen.add(title.lower())
                    prov = detect_vn_province(f"{title} {desc}") or "TP. Hồ Chí Minh"
                    rec = normalize_record({
                        "job_id": f"WEB-{len(seen)}",
                        "posted_date": (p_el.text or "").strip() if p_el is not None else "",
                        "title": title,
                        "company": src_name,
                        "location": prov,
                        "salary_min": 18000000.0,
                        "salary_max": 30000000.0,
                        "description": desc,
                    }, len(seen), src_name, item_url)
                    fallback_rows.append(rec)
                    if _is_match(f"{title} {desc}".lower()):
                        matched_rows.append(rec)
                        added_here += 1
                if added_here > 0:
                    active_sources.append(f"{src_name}: {feed_url}")
        except Exception:
            continue

    search_page_url = f"https://www.topcv.vn/tim-viec-lam-it?keyword={q_enc}"
    try:
        html_txt = _get_text(search_page_url, "text/html,application/xhtml+xml,*/*;q=0.8")
        links = re.findall(r'<a[^>]+href="(https://www\.topcv\.vn/viec-lam/[^"]+)"[^>]*>(.*?)</a>', html_txt, flags=re.S | re.I)
        added_web = 0
        for href, raw_label in links:
            title = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw_label))).strip()
            if len(title) < 4 or len(title) > 140 or title.lower() in seen:
                continue
            seen.add(title.lower())
            prov = detect_vn_province(title) or "TP. Hồ Chí Minh"
            rec = normalize_record({
                "job_id": f"WEB-PAGE-{len(seen)}",
                "posted_date": datetime.now().strftime("%Y-%m-%d"),
                "title": title,
                "company": "TopCV Việt Nam",
                "location": prov,
                "salary_min": 18000000.0,
                "salary_max": 30000000.0,
                "description": title,
            }, len(seen), "TopCV Việt Nam (Trang tìm việc IT)", href.strip())
            fallback_rows.append(rec)
            if _is_match(title.lower()):
                matched_rows.append(rec)
                added_web += 1
        if added_web > 0:
            active_sources.append(f"TopCV Việt Nam (Trang tìm việc IT): {search_page_url}")
    except Exception:
        pass

    if matched_rows:
        return matched_rows, active_sources, False
    if fallback_rows:
        return fallback_rows, ["TopCV Việt Nam (Danh mục việc làm CNTT): https://www.topcv.vn/viec-lam-it"], True
    return [], [], False


st.session_state.setdefault("reset_tick", 0)
st.session_state.setdefault("online_ran", False)
st.session_state.setdefault("online_query", PRESET_CAREERS["Data / BI (Python, SQL, Pandas)"])
st.session_state.setdefault("online_label", "Data / BI (Python, SQL, Pandas)")
st.session_state.setdefault("online_bust", 0)

with st.sidebar:
    st.markdown("**Nguồn dữ liệu**")
    source_mode = st.radio(
        "Chế độ",
        ["Dữ liệu mẫu Offline", "Tìm kiếm Online"],
        index=0,
        label_visibility="collapsed",
    )

    if source_mode == "Dữ liệu mẫu Offline":
        csv_path = st.text_input("File dữ liệu", value="data/jobs_features.csv")
        try:
            rows = load_offline_rows(csv_path)
            status_msg = f"<b>Offline:</b> {len(rows)} tin tại các tỉnh/thành Việt Nam · Nguồn: <b>Dữ liệu mẫu nội bộ</b> ({csv_path})."
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
            rows = load_offline_rows("data/jobs_features.csv")
            status_msg = f"Chọn nghề và bấm <b>Tìm kiếm</b> để lấy tin từ nguồn web Việt Nam · Đang hiển thị sẵn <b>Offline</b> ({len(rows)} tin)."
        else:
            live_rows, src_notes, is_broad = fetch_online_rows(
                st.session_state.online_query, bust=st.session_state.online_bust
            )
            if live_rows:
                rows = live_rows
                src_text = " | ".join(src_notes)
                note_extra = " (hiển thị toàn bộ tin CNTT hiện có từ nguồn do chưa có tin khớp chặt từ khóa)" if is_broad else ""
                status_msg = f"<b>Online:</b> {len(rows)} tin cho <b>{st.session_state.online_label}</b>{note_extra} · Nguồn web: <b>{src_text}</b>."
            else:
                rows = load_offline_rows("data/jobs_features.csv")
                status_msg = f"Nguồn web hiện chưa phản hồi · Đã tự chuyển về <b>Offline</b> ({len(rows)} tin)."

if not rows:
    st.warning("Không có dữ liệu.")
    st.stop()

skill_cols = [c for c in SKILL_LABELS.keys() if c in rows[0]]
skill_map = {c: SKILL_LABELS[c] for c in skill_cols}

roles = ["Tất cả"] + sorted({r["role_group"] for r in rows if r.get("role_group")})
locs = ["Tất cả"] + sorted({r["location"] for r in rows if r.get("location")})
skill_opts = ["Tất cả"] + [f"Có {skill_map[c]}" for c in skill_cols]

tick = st.session_state.reset_tick
with st.sidebar:
    st.divider()
    st.markdown("**Bộ lọc**")
    sel_role = st.selectbox("Nhóm vị trí", roles, key=f"role_{tick}")
    sel_loc = st.selectbox("Tỉnh / Thành Việt Nam", locs, key=f"loc_{tick}")
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
            <div class="sub">Kỹ năng theo nhóm vị trí · Lương trung vị · Tỉnh/thành Việt Nam · Dự báo xu hướng & MAE</div>
        </div>
        <div class="sub">Kho dữ liệu: <b>doan_cdtn2</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="source-note">{status_msg} · Bộ lọc: <b>{sel_role}</b> / <b>{sel_loc}</b> / <b>{sel_skill_lbl}</b></div>',
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
prov_cnt = len({r["location"] for r in filtered if r.get("location")})

if filtered and any(v > 0 for v in skill_totals.values()):
    top_sk, top_n = max(skill_totals.items(), key=lambda x: x[1])
    top_sk_sub = f"{top_n}/{len(filtered)} tin ({round(top_n / len(filtered) * 100)}%)"
else:
    top_sk, top_sk_sub = "N/A", "0 tin"

c1, c2, c3, c4, c5 = st.columns(5)
for col, lbl, val, sub in [
    (c1, "Tin tuyển dụng", f"{len(filtered):,}", f"Tổng nguồn: {len(rows):,}"),
    (c2, "Tỉnh / Thành VN", f"{prov_cnt}", "Phạm vi Việt Nam"),
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

t1, t2, t3, t4 = st.tabs(["Kỹ năng & Lương", "Tỉnh / Thành VN", "Dự báo & MAE", "Dữ liệu & CSV"])

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
    st.markdown("#### Phân bố tin theo Tỉnh / Thành phố Việt Nam (Top 15)")
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
            "Tỉnh / Thành phố": loc,
            "Số tin": cnt,
            "Tỷ trọng (%)": round(cnt / len(filtered) * 100, 2),
            "Lương trung vị (VNĐ)": int(round(statistics.median(loc_sal[loc]), 0)) if loc in loc_sal else 0,
        }
        for loc, cnt in s_locs
    ], use_container_width=True, height=300)

with t3:
    by_m = {}
    for r in filtered:
        if r.get("year_month"):
            by_m[r["year_month"]] = by_m.get(r["year_month"], 0) + 1
    months = sorted(by_m.keys())
    actuals = [float(by_m[m]) for m in months]
    n = len(months)

    if n >= 4:
        split = max(1, n - min(3, n - 2))
        xs, ys = list(range(split)), actuals[:split]
        if len(xs) >= 2 and len(set(xs)) > 1:
            mx, my = statistics.mean(xs), statistics.mean(ys)
            den = sum((x - mx) ** 2 for x in xs)
            slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
            intercept = my - slope * mx
        else:
            slope, intercept = 0.0, statistics.mean(ys)

        preds = [max(0.0, round(intercept + slope * i)) for i in range(n)]
        baselines = [None] + [actuals[i - 1] for i in range(1, n)]
        errs = [abs(actuals[i] - preds[i]) for i in range(n)]
        ev = [i for i in range(split, n) if baselines[i] is not None]

        mae_b = statistics.mean(abs(actuals[i] - baselines[i]) for i in ev) if ev else 0.0
        mae_m = statistics.mean(abs(actuals[i] - preds[i]) for i in ev) if ev else 0.0
        rmse_m = (statistics.mean((actuals[i] - preds[i]) ** 2 for i in ev)) ** 0.5 if ev else 0.0

        m1, m2, m3 = st.columns(3)
        m1.metric("MAE Baseline (kỳ trước)", f"{mae_b:.2f}")
        m2.metric("MAE Mô hình xu hướng", f"{mae_m:.2f}")
        m3.metric("RMSE Mô hình", f"{rmse_m:.2f}")

        st.line_chart({
            "Thực tế": {months[i]: actuals[i] for i in range(n)},
            "Dự báo": {months[i]: preds[i] for i in range(n)},
        }, height=280)
        st.dataframe([
            {
                "Tháng": months[i],
                "Thực tế": int(actuals[i]),
                "Baseline kỳ trước": int(baselines[i]) if baselines[i] is not None else None,
                "Dự báo": int(preds[i]),
                "Sai số tuyệt đối": int(errs[i]),
            }
            for i in range(n)
        ], use_container_width=True)
        w_i = max(range(n), key=lambda i: errs[i])
        st.markdown(
            f'<div class="caption-note"><b>Phân tích lỗi:</b> Tháng lệch lớn nhất là <b>{months[w_i]}</b> ({int(errs[w_i])} tin) do biến động mùa vụ/lễ Tết; mô hình xu hướng tuyến tính cơ bản chưa bắt được cú hích mùa vụ đột ngột.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"Có {n} mốc tháng (cần tối thiểu 4 tháng để đánh giá MAE). Hãy dùng chế độ Dữ liệu mẫu Offline để xem đầy đủ.")

with t4:
    cols = ["job_id", "posted_date", "year_month", "title", "role_group", "location", "experience_years", "salary_avg", "nguon_web", "link_nguon", *skill_cols]
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
    st.download_button("Tải CSV", data="\n".join(csv_lines).encode("utf-8"), file_name="jobs_vn.csv", mime="text/csv")
