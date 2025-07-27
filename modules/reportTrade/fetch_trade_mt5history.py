import logging
from pathlib import Path


async def fetch_trade_history(symbol: str, directory: Path) -> Path:
    """Fetch trade history from MT5 account and store to ``<symbol>_trade_history.csv``."""
    logging.info("start fetch_trade_history %s", symbol)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}_trade_history.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating trade history file %s", path)
            path.write_text("trade_history\n")
        # placeholder for fetching history
        logging.info("completed fetch_trade_history %s", symbol)
        return path
    except Exception:
        logging.exception("error in fetch_trade_history %s", symbol)
        raise
