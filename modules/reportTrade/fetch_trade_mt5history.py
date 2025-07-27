import logging
from pathlib import Path


async def fetch_trade_history(symbol: str, directory: Path) -> Path:
    """Fetch trade history from MT5 account."""
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{symbol}_trade_history.csv"
    path = directory / filename
    if not path.exists():
        logging.info("creating trade history file %s", path)
        path.write_text("trade_history\n")
    # placeholder for fetching history
    return path
