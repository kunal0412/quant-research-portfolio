import pandas as pd


def load_kaggle_data(filepath, symbol="S&P500"):
    """
    Load and clean Kaggle global financial markets dataset.

    Parameters:
    - filepath: path to CSV file
    - symbol: asset_name to filter (e.g., 'S&P500', 'DAX', etc.)

    Returns:
    - Clean pandas DataFrame with OHLCV data indexed by datetime
    """

    # =========================
    # LOAD DATA
    # =========================
    df = pd.read_csv(filepath)

    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]

    # =========================
    # DATE HANDLING
    # =========================
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    # =========================
    # FILTER SYMBOL
    # =========================
    df = df[df['asset_name'] == symbol]

    if df.empty:
        raise ValueError(f"No data found for asset: {symbol}")

    # =========================
    # SORT + INDEX
    # =========================
    df = df.sort_values('date')
    df.set_index('date', inplace=True)

    # =========================
    # KEEP REQUIRED COLUMNS
    # =========================
    required_cols = ['open', 'high', 'low', 'close', 'volume']

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")

    df = df[required_cols]

    # =========================
    # CLEANING
    # =========================
    df = df[~df.index.duplicated(keep='first')]

    # Ensure numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    # Drop NaNs
    df = df.dropna()

    # Remove zero/negative prices (data sanity)
    df = df[(df['close'] > 0) & (df['high'] > 0) & (df['low'] > 0)]

    return df