import logging
import time
from pathlib import Path


async def fetch_ohlcv(symbol: str, timeframe: str, directory: Path, timestamp: int) -> Path:
    """Fetch OHLCV data from MT5 and store to file if it does not exist."""
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{symbol}{timeframe}{timestamp}_ohlcv.csv"
    path = directory / filename
    if not path.exists():
        logging.info("creating raw ohlcv file %s", path)
        path.write_text("time,open,high,low,close,volume\n")
    # placeholder for fetching real data
    return path
