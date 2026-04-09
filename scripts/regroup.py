import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Load the file
df = pd.read_excel(DATA_DIR / "data_merged.xlsx")

# Clean OCC_CODE
df["OCC_CODE"] = df["OCC_CODE"].astype(str).str.strip()

def map_group(code):
    prefix = code[:2]

    # Exclude outlier categories
    if prefix in ["23", "27", "33", "45"]:
        return None

    # Main 4-group mapping
    if prefix in ["11", "13", "41", "43"]:
        return "Business, Management & Admin"
    elif prefix in ["15", "17", "19"]:
        return "STEM & Technical"
    elif prefix in ["21", "25", "29", "31"]:
        return "Healthcare, Education & Social"
    elif prefix in ["35", "37", "39", "47", "49", "51", "53"]:
        return "Operations, Trades & Labor"
    else:
        return None

# Add the new grouping column
df["GROUP"] = df["OCC_CODE"].apply(map_group)

# Optional: drop rows that do not fall into one of the 4 groups
df = df[df["GROUP"].notna()].copy()

# Save the output
df.to_excel(DATA_DIR / "data_grouped.xlsx", index=False)

print("Done.")
print(df["GROUP"].value_counts())
print(df[["OCC_CODE", "GROUP"]].head(20))