import logging
from pathlib import Path


aSYNC_MARKUP = """placeholder for MT5 order execution"""

async def create_order(symbol: str, timeframe: str, logic_file: Path, lot_file: Path, directory: Path, timestamp: int) -> Path:
    """Create order payload for MT5 and store to ``<symbol><timestamp>_order.json``."""
    logging.info("start create_order %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_order.json"
        path = directory / filename
        if not path.exists():
            logging.info("creating order file %s", path)
            path.write_text("{}")
        # placeholder: send order to MT5
        logging.info("completed create_order %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in create_order %s %s", symbol, timeframe)
        raise
