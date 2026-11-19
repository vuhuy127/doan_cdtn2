import csv
import html
import json
import re
import statistics
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

VN_CITIES_6 = [
    "TP. Hà Nội",
    "TP. Huế",
    "TP. Hải Phòng",
    "TP. Đà Nẵng",
    "TP. Hồ Chí Minh",
    "TP. Cần Thơ",
]

VN_PROVINCES_28 = [
    "Cao Bằng", "Lạng Sơn", "Lai Châu", "Điện Biên", "Sơn La",
    "Quảng Ninh", "Thanh Hóa", "Nghệ An", "Hà Tĩnh",
    "Tuyên Quang", "Lào Cai", "Thái Nguyên", "Phú Thọ", "Bắc Ninh",
    "Hưng Yên", "Ninh Bình", "Quảng Trị", "Quảng Ngãi", "Gia Lai",
    "Khánh Hòa", "Lâm Đồng", "Đắk Lắk", "Đồng Nai", "Tây Ninh",
    "Vĩnh Long", "Đồng Tháp", "Cà Mau", "An Giang",
]

VN_34_UNITS = VN_CITIES_6 + VN_PROVINCES_28

VN_ALIAS = {
    "ha noi": "TP. Hà Nội", "hà nội": "TP. Hà Nội", "hanoi": "TP. Hà Nội",
    "hue": "TP. Huế", "huế": "TP. Huế", "thua thien hue": "TP. Huế", "thừa thiên huế": "TP. Huế",
    "hai phong": "TP. Hải Phòng", "hải phòng": "TP. Hải Phòng", "hai duong": "TP. Hải Phòng", "hải dương": "TP. Hải Phòng",
    "da nang": "TP. Đà Nẵng", "đà nẵng": "TP. Đà Nẵng", "quang nam": "TP. Đà Nẵng", "quảng nam": "TP. Đà Nẵng",
    "ho chi minh": "TP. Hồ Chí Minh", "hồ chí minh": "TP. Hồ Chí Minh", "hcm": "TP. Hồ Chí Minh",
    "saigon": "TP. Hồ Chí Minh", "sài gòn": "TP. Hồ Chí Minh",
    "binh duong": "TP. Hồ Chí Minh", "bình dương": "TP. Hồ Chí Minh",
    "ba ria": "TP. Hồ Chí Minh", "bà rịa": "TP. Hồ Chí Minh", "vung tau": "TP. Hồ Chí Minh", "vũng tàu": "TP. Hồ Chí Minh",
    "can tho": "TP. Cần Thơ", "cần thơ": "TP. Cần Thơ", "soc trang": "TP. Cần Thơ", "sóc trăng": "TP. Cần Thơ",
    "hau giang": "TP. Cần Thơ", "hậu giang": "TP. Cần Thơ",
    "ha giang": "Tuyên Quang", "hà giang": "Tuyên Quang",
    "yen bai": "Lào Cai", "yên bái": "Lào Cai",
    "bac kan": "Thái Nguyên", "bắc kạn": "Thái Nguyên",
    "hoa binh": "Phú Thọ", "hòa bình": "Phú Thọ", "vinh phuc": "Phú Thọ", "vĩnh phúc": "Phú Thọ",
    "bac giang": "Bắc Ninh", "bắc giang": "Bắc Ninh",
    "thai binh": "Hưng Yên", "thái bình": "Hưng Yên",
    "ha nam": "Ninh Bình", "hà nam": "Ninh Bình", "nam dinh": "Ninh Bình", "nam định": "Ninh Bình",
    "quang binh": "Quảng Trị", "quảng bình": "Quảng Trị",
    "kon tum": "Quảng Ngãi",
    "binh dinh": "Gia Lai", "bình định": "Gia Lai",
    "ninh thuan": "Khánh Hòa", "ninh thuận": "Khánh Hòa",
    "dak nong": "Lâm Đồng", "đắk nông": "Lâm Đồng", "binh thuan": "Lâm Đồng", "bình thuận": "Lâm Đồng",
    "phu yen": "Đắk Lắk", "phú yên": "Đắk Lắk",
    "binh phuoc": "Đồng Nai", "bình phước": "Đồng Nai",
    "long an": "Tây Ninh",
    "ben tre": "Vĩnh Long", "bến tre": "Vĩnh Long", "tra vinh": "Vĩnh Long", "trà vinh": "Vĩnh Long",
    "tien giang": "Đồng Tháp", "tiền giang": "Đồng Tháp",
    "bac lieu": "Cà Mau", "bạc liêu": "Cà Mau",
    "kien giang": "An Giang", "kiên giang": "An Giang",
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


def detect_vn_34_unit(text_blob: str) -> str:
    low = (text_blob or "").strip().lower()
    if not low:
        return "TP. Hồ Chí Minh"
    for unit in VN_34_UNITS:
        clean_name = unit.replace("TP. ", "").lower()
        if clean_name in low:
            return unit
    for k, v in VN_ALIAS.items():
        if k in low:
            return v
    if "việt nam" in low or "vietnam" in low or "viet nam" in low:
        return "TP. Hồ Chí Minh"
    return "TP. Hồ Chí Minh"


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


def normalize_record(raw: dict, idx: int, nguon_web: str, link_nguon: str, pham_vi_nguon: str = "Việt Nam / Nội bộ") -> dict:
    unit_34 = detect_vn_34_unit(str(raw.get("location") or ""))
    title = (raw.get("title") or "Unknown").strip()
    posted = parse_date(str(raw.get("posted_date") or ""))
    role = (raw.get("role_group") or normalize_role(title)).strip()

    try:
        exp_val = float(raw.get("experience_years") or 1.0)
    except Exception:
        exp_val = 1.0

    has_valid_salary = False
    try:
        sal_val = float(raw.get("salary_avg") or 0.0)
        if sal_val > 0:
            has_valid_salary = True
    except Exception:
        sal_val = 0.0

    if not has_valid_salary:
        try:
            vals = [float(x) for x in (raw.get("salary_min"), raw.get("salary_max")) if x and float(x) > 0]
            if vals:
                sal_val = statistics.mean(vals)
                has_valid_salary = True
            else:
                sal_val = 20000000.0
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
        "location": unit_34,
        "experience_years": f"{exp_val:.1f}",
        "salary_avg": f"{sal_val:.0f}",
        "nguon_web": nguon_web,
        "link_nguon": link_nguon,
        "pham_vi_nguon": pham_vi_nguon,
        "has_valid_salary": int(has_valid_salary),
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
    row["has_any_skill"] = int(any(row.get(c, 0) == 1 for c in SKILL_PATTERNS))
    return row


def load_offline_rows(path: str) -> list:
    with open(path, mode="r", encoding="utf-8-sig", newline="") as f:
        data = list(csv.DictReader(f))
    return [normalize_record(r, i + 1, "Dữ liệu mẫu nội bộ", path, "Việt Nam / Nội bộ") for i, r in enumerate(data)]


def summarize_data_quality(rows: list) -> dict:
    total = len(rows)
    if total == 0:
        return {"total": 0, "salary_pct": 0.0, "skill_pct": 0.0, "distinct_units": 0}
    sal_ok = sum(int(r.get("has_valid_salary", 0)) for r in rows)
    sk_ok = sum(int(r.get("has_any_skill", 0)) for r in rows)
    units = len({r.get("location") for r in rows if r.get("location")})
    return {
        "total": total,
        "salary_pct": round(sal_ok / total * 100, 1),
        "skill_pct": round(sk_ok / total * 100, 1),
        "distinct_units": units,
    }


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


def fetch_online_rows(query: str):
    q_raw = (query or "data python sql").strip()
    q_enc = urllib.parse.quote(q_raw)
    tokens = [t for t in re.split(r"[\s,/]+", q_raw.lower()) if len(t) >= 2]
    matched_rows, broad_rows, seen, active_sources = [], [], set(), []

    def _is_match(blob_low: str) -> bool:
        if not tokens:
            return True
        if any(tok in blob_low for tok in tokens):
            return True
        if any(tok in ("qa", "qc", "test", "tester", "automation") for tok in tokens):
            return any(k in blob_low for k in ("qa", "qc", "test", "tester", "automation", "kiểm thử"))
        return False

    rss_feeds = [
        ("TopCV Việt Nam (RSS IT)", "https://www.topcv.vn/rss/viec-lam-it.rss"),
        ("TopCV Việt Nam (RSS Từ khóa)", f"https://www.topcv.vn/rss/viec-lam-theo-tu-khoa.rss?q={q_enc}"),
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
                    unit_34 = detect_vn_34_unit(f"{title} {desc}")
                    rec = normalize_record({
                        "job_id": f"WEB-{len(seen)}",
                        "posted_date": (p_el.text or "").strip() if p_el is not None else "",
                        "title": title,
                        "company": src_name,
                        "location": unit_34,
                        "description": desc,
                    }, len(seen), src_name, item_url, "Việt Nam")
                    broad_rows.append(rec)
                    if _is_match(f"{title} {desc}".lower()):
                        matched_rows.append(rec)
                        added_here += 1
                if added_here > 0:
                    active_sources.append(f"{src_name}: {feed_url}")
        except Exception:
            continue

    try:
        first_tok = tokens[0] if tokens else "software"
        remotive_url = f"https://remotive.com/api/remote-jobs?category=software-dev&search={urllib.parse.quote(first_tok)}"
        payload = json.loads(_get_text(remotive_url, "application/json"))
        jobs_list = payload.get("jobs") if isinstance(payload, dict) else []
        added_rem = 0
        for idx, item in enumerate(jobs_list or [], start=1):
            if not isinstance(item, dict) or not item.get("title"):
                continue
            title = str(item.get("title")).strip()
            if title.lower() in seen:
                continue
            seen.add(title.lower())
            desc_clean = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(item.get("description") or "")))).strip()
            unit_34 = detect_vn_34_unit(f"{item.get('candidate_required_location') or ''} {title}")
            job_link = str(item.get("url") or remotive_url)
            rec = normalize_record({
                "job_id": f"REM-{idx}",
                "posted_date": str(item.get("publication_date") or "")[:10],
                "title": title,
                "company": item.get("company_name") or "Doanh nghiệp CNTT",
                "location": unit_34,
                "description": desc_clean,
                "tags": item.get("tags") or [],
            }, len(seen), "Remotive API (Quốc tế / Từ xa)", job_link, "Quốc tế / API")
            broad_rows.append(rec)
            if _is_match(f"{title} {desc_clean}".lower()):
                matched_rows.append(rec)
                added_rem += 1
        if added_rem > 0:
            active_sources.append(f"Remotive API: {remotive_url}")
    except Exception:
        pass

    if matched_rows:
        return matched_rows, active_sources, False
    if broad_rows:
        fallback_srcs = active_sources if active_sources else ["Remotive API: https://remotive.com/api/remote-jobs"]
        return broad_rows, fallback_srcs, True
    return [], [], False


def evaluate_monthly_forecast(rows: list) -> dict:
    by_m = {}
    for r in rows:
        if r.get("year_month"):
            by_m[r["year_month"]] = by_m.get(r["year_month"], 0) + 1
    months = sorted(by_m.keys())
    actuals = [float(by_m[m]) for m in months]
    n = len(months)
    if n < 4:
        return {"enough_data": False, "months": months, "actuals": actuals}

    split = max(1, n - min(3, n - 2))
    xs, ys = list(range(split)), actuals[:split]
    if len(xs) >= 2 and len(set(xs)) > 1:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        den = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0.0
        intercept = my - slope * mx
    else:
        slope, intercept = 0.0, statistics.mean(ys)

    trend_preds = [max(0.0, round(intercept + slope * i)) for i in range(n)]
    baselines = [None] + [actuals[i - 1] for i in range(1, n)]
    ma3_preds = [
        None if i < 2 else round(statistics.mean(actuals[i - 2:i + 1]), 1)
        for i in range(n)
    ]
    errs = [abs(actuals[i] - trend_preds[i]) for i in range(n)]

    ev_base = [i for i in range(split, n) if baselines[i] is not None]
    ev_ma3 = [i for i in range(split, n) if ma3_preds[i] is not None]

    mae_base = statistics.mean(abs(actuals[i] - baselines[i]) for i in ev_base) if ev_base else 0.0
    mae_trend = statistics.mean(abs(actuals[i] - trend_preds[i]) for i in ev_base) if ev_base else 0.0
    mae_ma3 = statistics.mean(abs(actuals[i] - ma3_preds[i]) for i in ev_ma3) if ev_ma3 else 0.0
    rmse_trend = (statistics.mean((actuals[i] - trend_preds[i]) ** 2 for i in ev_base)) ** 0.5 if ev_base else 0.0

    worst_idx = max(range(n), key=lambda i: errs[i])
    return {
        "enough_data": True,
        "months": months,
        "actuals": actuals,
        "baselines": baselines,
        "trend_preds": trend_preds,
        "ma3_preds": ma3_preds,
        "errs": errs,
        "mae_base": mae_base,
        "mae_trend": mae_trend,
        "mae_ma3": mae_ma3,
        "rmse_trend": rmse_trend,
        "worst_month": months[worst_idx],
        "worst_err": int(errs[worst_idx]),
    }
