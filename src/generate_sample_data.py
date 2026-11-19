import csv
import os
import random
from datetime import date, timedelta

PROVINCES = [
    "TP. Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Bình Dương", "Cần Thơ", "Hải Phòng",
    "Bắc Ninh", "Đồng Nai", "Thừa Thiên Huế", "Khánh Hòa", "Bà Rịa - Vũng Tàu", "Long An",
    "Quảng Nam", "Quảng Ninh", "Thái Nguyên", "Nghệ An", "Thanh Hóa", "Lâm Đồng",
    "An Giang", "Bạc Liêu", "Bắc Giang", "Bến Tre", "Bình Định", "Bình Phước",
    "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên",
    "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hải Dương",
    "Hậu Giang", "Hòa Bình", "Hưng Yên", "Kiên Giang", "Kon Tum", "Lai Châu",
    "Lạng Sơn", "Lào Cai", "Nam Định", "Ninh Bình", "Ninh Thuận", "Phú Thọ",
    "Phú Yên", "Quảng Bình", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh",
    "Thái Bình", "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc",
    "Yên Bái", "Hà Nội (Khu CN)", "TP. Hồ Chí Minh (Khu vực 2)"
]

# Đảm bảo đủ 63 tỉnh/thành Việt Nam chuẩn
ALL_63_PROVINCES = [
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
    "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
]

ROLE_TEMPLATES = [
    ("Python Backend Developer", "Backend", 18000000, 32000000, 2, "Python, SQL, PostgreSQL, Docker, Git, REST API"),
    ("Java Software Engineer", "Backend", 20000000, 36000000, 3, "Java, Spring Boot, SQL, MySQL, Docker, AWS cloud, Git"),
    ("Data Analyst", "Data / BI", 14000000, 25000000, 1, "SQL, Python, Pandas, Numpy, BI dashboard, Excel"),
    ("Data Scientist", "Data / BI", 21000000, 38000000, 2, "Python, Pandas, Numpy, Scikit-learn, SQL, AWS cloud"),
    ("Data Engineer", "Data / BI", 22000000, 40000000, 3, "Python, SQL, Pandas, Docker, AWS cloud, Git"),
    ("Frontend React Developer", "Frontend", 14000000, 26000000, 2, "JavaScript, TypeScript, React, Git"),
    ("Fullstack JS Developer", "Frontend", 17000000, 30000000, 2, "JavaScript, TypeScript, SQL, Docker, Git"),
    ("QA Automation Engineer", "QA / Tester", 13000000, 24000000, 2, "Python, Java, SQL, Git, automation testing"),
    ("Manual QA / QC Tester", "QA / Tester", 11000000, 18000000, 1, "SQL, Git, API test, test case design"),
    ("Cloud / DevOps Engineer", "Other IT", 23000000, 42000000, 3, "Docker, AWS cloud, Linux, Python, Git, SQL"),
]

COMPANIES = [
    "TechViet", "FinData", "WebPro", "BankCore", "AIHub", "SoftTest",
    "CloudNet", "DataFlow", "AppStudio", "PayFast", "RetailPlus", "EnterpriseVN",
    "SmartAnalytics", "NextGen", "QualityFirst", "EduTech", "LogiTechVN", "HealthData",
    "DigiShop", "SkyCloud", "FinTechVN", "CoreAI", "VinaBank", "MarketInsight",
    "CreativeWeb", "FastDelivery", "VisionLab", "MekongSoft", "CentralTech", "DeltaDigital"
]

# Phân bổ số lượng tin theo từng tháng (2025-07 đến 2026-06), tháng 2026-02 (Tết) thấp hơn rõ rệt
MONTH_COUNTS = {
    (2025, 7): 18,
    (2025, 8): 20,
    (2025, 9): 22,
    (2025, 10): 24,
    (2025, 11): 23,
    (2025, 12): 19,
    (2026, 1): 21,
    (2026, 2): 9,
    (2026, 3): 25,
    (2026, 4): 24,
    (2026, 5): 26,
    (2026, 6): 25,
}

def generate_raw_jobs(out_path: str = "data/raw_jobs.csv", seed: int = 42):
    rng = random.Random(seed)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    rows = []
    job_id = 1

    # Gán mỗi tỉnh ít nhất 2 tin để phủ đủ 63 tỉnh/thành phố Việt Nam
    province_pool = []
    for p in ALL_63_PROVINCES:
        province_pool.extend([p, p])

    hub_weights = []
    for p in ALL_63_PROVINCES:
        if p in ("TP. Hồ Chí Minh", "Hà Nội"):
            hub_weights.append(12)
        elif p in ("Đà Nẵng", "Bình Dương", "Cần Thơ", "Hải Phòng", "Đồng Nai", "Bắc Ninh"):
            hub_weights.append(4)
        else:
            hub_weights.append(1)

    for (yr, mo), count in MONTH_COUNTS.items():
        days_in_month = 28 if mo == 2 else (30 if mo in (4, 6, 9, 11) else 31)
        for _ in range(count):
            day = rng.randint(1, days_in_month)
            posted = date(yr, mo, day).isoformat()
            title, _, s_min_base, s_max_base, exp_base, skills_txt = rng.choice(ROLE_TEMPLATES)

            if province_pool:
                loc = province_pool.pop()
            else:
                loc = rng.choices(ALL_63_PROVINCES, weights=hub_weights, k=1)[0]

            hub_bonus = 2000000 if loc in ("TP. Hồ Chí Minh", "Hà Nội") else 0
            s_min = (s_min_base + hub_bonus + rng.randint(-2, 3) * 1000000)
            s_max = max(s_min + 3000000, s_max_base + hub_bonus + rng.randint(-2, 4) * 1000000)
            exp = max(0, exp_base + rng.choice([-1, 0, 0, 1]))
            comp = rng.choice(COMPANIES)

            rows.append({
                "job_id": job_id,
                "posted_date": posted,
                "title": title,
                "company": comp,
                "location": loc,
                "experience_years": exp,
                "salary_min": s_min,
                "salary_max": s_max,
                "description": f"Position: {title} at {comp} ({loc}). Required skills: {skills_txt}. Experience: {exp} years.",
            })
            job_id += 1

    # Thêm một vài bản ghi trùng lặp có chủ đích để kiểm tra bước làm sạch dữ liệu
    for dup in rows[:3]:
        rows.append(dict(dup))

    fieldnames = [
        "job_id", "posted_date", "title", "company", "location",
        "experience_years", "salary_min", "salary_max", "description"
    ]
    with open(out_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Da sinh {len(rows)} dong du lieu tho (gom ca ban ghi trung lap test lam sach) tai {out_path}")

if __name__ == "__main__":
    generate_raw_jobs()
