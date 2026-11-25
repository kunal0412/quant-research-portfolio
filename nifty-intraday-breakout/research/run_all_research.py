import sys
import os

# Make project root visible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from strategy.signals import generate_intraday_signals
from backtest.engine import run_backtest

from research.mae_mfe_analysis import analyze_mae_mfe, print_summary
from research.sl_tp_optimizer import optimize_sl_tp, print_top_results
from research.regime_analysis import (
    classify_regime,
    tag_trades_with_regime,
    analyze_by_regime,
    print_regime_summary
)


# =========================================
# CONFIG
# =========================================

DATA_FILE = "NIFTY50_minute.csv"
DATA_FOLDER = "data"

INITIAL_CAPITAL = 1_000_000
RISK_PER_TRADE = 0.01


# =========================================
# PATH HANDLER
# =========================================

def get_data_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, DATA_FOLDER, DATA_FILE)


# =========================================
# LOAD DATA
# =========================================

def load_data(file_path):

    print(f"\n📂 Loading data: {file_path}\n")

    df = pd.read_csv(file_path)

    df.columns = [col.lower().strip() for col in df.columns]

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True)

    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    return df


# =========================================
# MAIN
# =========================================

def main():

    print("\n🧪 RUNNING FULL RESEARCH PIPELINE\n")

    # -------------------------
    # LOAD
    # -------------------------
    df = load_data(get_data_path())

    # -------------------------
    # SIGNALS
    # -------------------------
    df = generate_intraday_signals(df)

    print("Signals generated:", int(df['signal'].abs().sum()))

    # =========================
    # 1. MAE / MFE ANALYSIS
    # =========================
    print("\n🔍 Running MAE/MFE Analysis...")
    mae_mfe_df = analyze_mae_mfe(df)
    print_summary(mae_mfe_df)
    mae_mfe_df.to_excel("mae_mfe_analysis.xlsx", index=False)

    # =========================
    # 2. SL / TP OPTIMIZATION
    # =========================
    print("\n⚙️ Running SL/TP Optimization...")

    sl_values = [0.003, 0.005, 0.007, 0.01]
    tp_values = [0.008, 0.01, 0.015, 0.02]

    sltp_results = optimize_sl_tp(df, sl_values, tp_values)
    print_top_results(sltp_results)

    sltp_results.to_excel("sl_tp_optimization.xlsx", index=False)

    # =========================
    # 3. BACKTEST (for regime tagging)
    # =========================
    print("\n📈 Running Backtest for Regime Analysis...")

    df_bt, trades_df, _ = run_backtest(
        df,
        initial_capital=INITIAL_CAPITAL,
        risk_per_trade=RISK_PER_TRADE
    )

    # =========================
    # 4. REGIME ANALYSIS
    # =========================
    print("\n🌦️ Running Regime Analysis...")

    df_bt = classify_regime(df_bt)
    trades_df = tag_trades_with_regime(df_bt, trades_df)

    regime_results = analyze_by_regime(trades_df)
    print_regime_summary(regime_results)

    regime_results.to_excel("regime_analysis.xlsx", index=False)

    print("\n✅ ALL RESEARCH COMPLETED\n")


# =========================================
# ENTRY POINT
# =========================================

if __name__ == "__main__":
    main()