import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# =========================
# 1. LOAD FILES
# =========================
skills = pd.read_excel(DATA_DIR / "skills_refactored.xlsx")
salary = pd.read_excel(DATA_DIR / "national_occupations.xlsx", sheet_name="National Occupations")
education_raw = pd.read_excel(
    DATA_DIR / "education.xlsx",
    sheet_name="Education Requirements",
    keep_default_na=False
)

# =========================
# 2. CLEAN SKILLS
# =========================
skills = skills.copy()
skills["OCC_CODE"] = skills["OCC_CODE"].astype(str).str.strip()

# Keep only standard SOC codes like 11-2011
skills = skills[skills["OCC_CODE"].str.fullmatch(r"\d{2}-\d{4}")].copy()
skills = skills.drop_duplicates(subset="OCC_CODE")

skills_cols = [
    "OCC_CODE",
    "Active Learning_LV",
    "Active Listening_LV",
    "Coordination_LV",
    "Critical Thinking_LV",
    "Judgment and Decision Making_LV",
]
skills = skills[[c for c in skills_cols if c in skills.columns]].copy()

# =========================
# 3. CLEAN SALARY
# =========================
salary = salary.copy()
salary["OCC_CODE"] = salary["OCC_CODE"].astype(str).str.strip()

if "O_GROUP" in salary.columns:
    salary = salary[salary["O_GROUP"] == "detailed"].copy()

if "AREA_TITLE" in salary.columns:
    salary = salary[salary["AREA_TITLE"] == "U.S."].copy()

if "NAICS_TITLE" in salary.columns:
    salary = salary[salary["NAICS_TITLE"] == "Cross-industry"].copy()

salary_cols = [
    "OCC_CODE", "OCC_TITLE", "A_MEAN", "A_MEDIAN"
]

salary = salary[[c for c in salary_cols if c in salary.columns]].copy()

salary = salary.replace("#", pd.NA)

for col in salary.columns:
    if col not in ["OCC_CODE", "OCC_TITLE"]:
        salary[col] = pd.to_numeric(salary[col], errors="coerce")

salary = salary.drop_duplicates(subset="OCC_CODE")

# =========================
# 4. CLEAN EDUCATION
# =========================
education = education_raw.copy()

# First row contains actual headers
education.columns = education.iloc[0]
education = education.iloc[1:].copy()

education = education.rename(columns={
    "2024 National Employment Matrix title": "EDU_TITLE",
    "2024 National Employment Matrix code": "OCC_CODE",
    "Typical education needed for entry": "ENTRY_EDUCATION",
    "Work experience in a related occupation": "RELATED_WORK_EXPERIENCE",
    "Typical on-the-job training needed to attain competency in the occupation": "ON_THE_JOB_TRAINING",
    "Related Occupational Outlook Handbook (OOH) content": "OOH_CONTENT"
})

education["OCC_CODE"] = education["OCC_CODE"].astype(str).str.strip()

education = education[
    ["OCC_CODE", "ENTRY_EDUCATION", "RELATED_WORK_EXPERIENCE", "ON_THE_JOB_TRAINING"]
].copy()

education = education.drop_duplicates(subset="OCC_CODE")

# Convert to strings carefully so literal category values like "None" are preserved
qual_cols = ["ENTRY_EDUCATION", "RELATED_WORK_EXPERIENCE", "ON_THE_JOB_TRAINING"]

for col in qual_cols:
    education[col] = education[col].astype("string").str.strip()

# Only drop truly empty cells, not the literal string "None"
for col in qual_cols:
    education = education[
        education[col].notna() &
        (education[col] != "")
    ]

# Keep only occupations requiring Associate's degree or higher.
entry_education = education["ENTRY_EDUCATION"].str.lower()
education = education[
    entry_education.str.contains(
        r"associate|bachelor|master|doctoral|professional",
        regex=True,
        na=False,
    )
].copy()
# =========================
# 5. MERGE
# =========================
merged = salary.merge(skills, on="OCC_CODE", how="inner")
merged = merged.merge(education, on="OCC_CODE", how="inner")

# =========================
# 6. SAVE
# =========================
output_path = DATA_DIR / "data_merged.xlsx"
merged.to_excel(output_path, index=False)

print("Done.")
print("Merged rows with all 3 qualitative vars filled:", len(merged))