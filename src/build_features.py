import csv
import os
import re
import statistics
from datetime import datetime

SKILL_PATTERNS = {
    "skill_python": r"\bpython\b",
    "skill_sql": r"\b(sql|mysql|postgresql|sql server)\b",
    "skill_java": r"\bjava\b(?!script)",
    "skill_javascript": r"\b(javascript|js|typescript|ts)\b",
    "skill_pandas_numpy": r"\b(pandas|numpy|scikit-learn|sklearn)\b",
    "skill_docker": r"\bdocker\b",
    "skill_git": r"\bgit\b",
    "skill_aws_cloud": r"\b(aws|azure|gcp|cloud)\b",
}

def normalize_role(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["data", "bi", "analyst", "scientist"]):
        return "Data / BI"
    if any(k in t for k in ["backend", "be", "java", "node", ".net", "php", "python"]):
        return "Backend"
    if any(k in t for k in ["frontend", "fe", "react", "angular", "vue"]):
        return "Frontend"
    if any(k in t for k in ["qa", "qc", "test"]):
        return "QA / Tester"
    return "Other IT"

def extract_skills(text: str) -> dict:
    content = (text or "").lower()
    return {
        col: int(bool(re.search(pattern, content)))
        for col, pattern in SKILL_PATTERNS.items()
    }

def parse_date(val: str):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val.strip(), fmt)
        except Exception:
            continue
    return None

def parse_salary(val: str):
    try:
        num = float(val)
        return num if num > 0 else None
    except Exception:
        return None

def build_feature_table(raw_csv_path: str, out_csv_path: str):
    with open(raw_csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    seen = set()
    cleaned = []
    for r in rows:
        title = (r.get("title") or "Unknown").strip()
        company = (r.get("company") or "").strip()
        posted_raw = (r.get("posted_date") or "").strip()
        desc = (r.get("description") or "").strip()

        dedup_key = (title, company, posted_raw, desc)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        dt = parse_date(posted_raw)
        if not dt:
            continue

        s_min = parse_salary(r.get("salary_min", ""))
        s_max = parse_salary(r.get("salary_max", ""))
        vals = [v for v in (s_min, s_max) if v is not None]
        s_avg = statistics.mean(vals) if vals else None

        role_group = normalize_role(title)
        location = (r.get("location") or "Khac").strip()
        skills = extract_skills(desc)

        cleaned.append({
            "job_id": (r.get("job_id") or "").strip(),
            "posted_date": dt.strftime("%Y-%m-%d"),
            "year_month": dt.strftime("%Y-%m"),
            "title": title,
            "role_group": role_group,
            "location": location,
            "experience_years": (r.get("experience_years") or "").strip(),
            "_salary_avg": s_avg,
            **skills,
        })

    global_salaries = [x["_salary_avg"] for x in cleaned if x["_salary_avg"] is not None]
    global_median = statistics.median(global_salaries) if global_salaries else 0.0

    role_medians = {}
    for role in set(x["role_group"] for x in cleaned):
        r_vals = [x["_salary_avg"] for x in cleaned if x["role_group"] == role and x["_salary_avg"] is not None]
        role_medians[role] = statistics.median(r_vals) if r_vals else global_median

    fieldnames = [
        "job_id", "posted_date", "year_month", "title", "role_group",
        "location", "experience_years", "salary_avg", *SKILL_PATTERNS.keys()
    ]

    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    with open(out_csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in cleaned:
            sal = item["_salary_avg"] if item["_salary_avg"] is not None else role_medians[item["role_group"]]
            out_row = {k: v for k, v in item.items() if k != "_salary_avg"}
            out_row["salary_avg"] = round(sal, 2)
            writer.writerow(out_row)

    print(f"[OK] Da tao bang dac trung: {out_csv_path} ({len(cleaned)} dong, {len(fieldnames)} cot)")

if __name__ == "__main__":
    build_feature_table("data/raw_jobs.csv", "data/jobs_features.csv")
