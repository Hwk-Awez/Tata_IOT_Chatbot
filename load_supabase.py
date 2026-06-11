import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# ── CONNECTION ────────────────────────────────────────────────────────────────
DB_URL = os.getenv("SUPABASE_DB_URL")
engine = create_engine(DB_URL)

# ── CSV PATH ──────────────────────────────────────────────────────────────────
# Update this to the folder where your cleaned CSVs are saved
CSV_PATH = r"D:\SNTI\Filled_ds"

tables = [
    "machine_type",
    "machines",
    "deviation",
    "machine_derived",
    "periodic_data_interval2",
    "summarize_clad_details_info",
    "summarize_gascutting_machine",
    "summarize_nongascut_machine",
    "user",
]

for table in tables:
    filepath = os.path.join(CSV_PATH, f"{table}.csv")
    try:
        df = pd.read_csv(filepath, low_memory=False)
        df.to_sql(table, engine, if_exists="replace", index=False)
        print(f"✓ {table} — {len(df)} rows loaded")
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
    except Exception as e:
        print(f"✗ Error loading {table}: {e}")

print("\nDone. All tables loaded into Supabase.")