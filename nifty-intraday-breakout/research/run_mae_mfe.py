import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from strategy.signals import generate_intraday_signals
from research.mae_mfe_analysis import analyze_mae_mfe, print_summary


# =========================================
# CONFIG
# =========================================

DATA_FILE = "NIFTY50_minute.csv"
DATA_FOLDER = "data"


# =========================================
# PATH HANDLER
# =========================================

def get_data_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DATA_FOLDER, DATA_FILE)


# =========================================
# LOAD DATA (same logic as main)
# =========================================

def load_data(file_path):

    print(f"\n📂 Loading file from: {file_path}\n")

    df = pd.read_csv(file_path)

    df.columns = [col.lower().strip() for col in df.columns]

    if 'date' not in df.columns:
        raise ValueError("Expected 'date' column")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    return df


# =========================================
# MAIN
# =========================================

def main():

    print("\n🧪 Running MAE/MFE Research Module\n")

    df = load_data(get_data_path())

    # Generate signals
    df = generate_intraday_signals(df)

    print("Signals:", int(df['signal'].abs().sum()))

    # Run analysis
    mae_mfe_df = analyze_mae_mfe(df)

    # Print summary
    print_summary(mae_mfe_df)

    # Save output
    output_path = "mae_mfe_analysis.xlsx"
    mae_mfe_df.to_excel(output_path, index=False)

    print(f"\n📊 Saved results to: {output_path}")


if __name__ == "__main__":
    main()