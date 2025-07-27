import logging
from pathlib import Path


aSYNC_MARKUP = """placeholder for MT5 order execution"""

async def create_order(symbol: str, timeframe: str, logic_file: Path, lot_file: Path, directory: Path, timestamp: int) -> Path:
    """Create order payload for MT5 and store to file."""
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{symbol}{timeframe}{timestamp}_order.json"
    path = directory / filename
    if not path.exists():
        logging.info("creating order file %s", path)
        path.write_text("{}")
    # placeholder: send order to MT5
    return path
