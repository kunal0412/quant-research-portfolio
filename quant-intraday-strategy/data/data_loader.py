import pandas as pd


def load_kaggle_data(filepath, symbol="S&P500"):
    """
    Load and clean Kaggle global financial markets dataset.

    Parameters:
    - filepath: path to CSV file
    - symbol: asset_name to filter (e.g., 'S&P500', 'DAX', etc.)

    Returns:
    - Clean pandas DataFrame with OHLCV data
    """

    # Load CSV
    df = pd.read_csv(filepath)

    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]

    # Convert date column
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=['date'])

    # Filter for selected asset
    df = df[df['asset_name'] == symbol]

    if df.empty:
        raise ValueError(f"No data found for asset: {symbol}")

    # Sort by date
    df = df.sort_values('date')

    # Set datetime index
    df.set_index('date', inplace=True)

    # Keep only required columns
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    df = df[[col for col in required_cols if col in df.columns]]

    # Drop duplicates
    df = df[~df.index.duplicated(keep='first')]

    # Final sanity check
    df = df.dropna()

    return df