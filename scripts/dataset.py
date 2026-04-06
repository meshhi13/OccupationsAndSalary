import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# Load the Excel file
input_path = DATA_DIR / "skills_original.xlsx"
df = pd.read_excel(input_path)

raw_required_cols = {"O*NET-SOC Code", "Title", "Element Name", "Scale ID", "Data Value"}
already_wide_cols = {"OCC_CODE", "Title"}

if raw_required_cols.issubset(df.columns):
    # Keep only the columns we need
    df = df[["O*NET-SOC Code", "Title", "Element Name", "Scale ID", "Data Value"]].copy()

    # Keep only IM and LV rows
    df = df[df["Scale ID"].isin(["IM", "LV"])].copy()

    # Standardize SOC code so 11-2011.00 becomes 11-2011
    df["OCC_CODE"] = df["O*NET-SOC Code"].astype(str).str.replace(r"\.00$", "", regex=True)

    # Make combined column names like "Speaking_IM" and "Speaking_LV"
    df["Skill_Scale"] = df["Element Name"] + "_" + df["Scale ID"]

    # Pivot so each skill/scale combo becomes its own column
    wide_df = df.pivot_table(
        index=["OCC_CODE", "Title"],
        columns="Skill_Scale",
        values="Data Value",
        aggfunc="first"   # change to "mean" if duplicates exist
    ).reset_index()

    # Remove pivot column name
    wide_df.columns.name = None
elif already_wide_cols.issubset(df.columns):
    # If the data is already in wide/refactored shape, pass it through.
    wide_df = df.copy()
else:
    raise ValueError(
        f"Unsupported input schema in {input_path.name}. "
        "Expected raw skills columns or an already-wide sheet with OCC_CODE and Title."
    )

# Save output
output_path = DATA_DIR / "skills_refactored.xlsx"
wide_df.to_excel(output_path, index=False)

print(f"Done. Output saved to {output_path}")
print(wide_df.head())