import pandas as pd

# =========================================
# LOAD DATA (BLOOMBERG GC FIXED)
# =========================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(BASE_DIR, "GCcv1.csv")

df = pd.read_csv(file_path)

print("Columns in CSV:", df.columns.tolist())


# =========================================
# DATETIME
# =========================================

df['Date-Time'] = pd.to_datetime(df['Date-Time'])
df.set_index('Date-Time', inplace=True)

# Remove timezone (optional but cleaner)
df.index = df.index.tz_convert(None)


# =========================================
# RENAME COLUMNS
# =========================================

df.rename(columns={
    'Open': 'open',
    'High': 'high',
    'Low': 'low',
    'Last': 'close',
    'Volume': 'volume'
}, inplace=True)


# =========================================
# DROP UNUSED COLUMN
# =========================================

if '#RIC' in df.columns:
    df.drop(columns=['#RIC'], inplace=True)


# =========================================
# CLEAN DATA
# =========================================

df = df.sort_index()

for col in ['open', 'high', 'low', 'close']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(inplace=True)


# =========================================
# FINAL CHECK
# =========================================

print("\n--- DATA CHECK ---")
print(df.head())
print("\nColumns:", df.columns.tolist())
print("Timezone:", df.index.tz)
print("Total rows:", len(df))