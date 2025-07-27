import logging
from pathlib import Path


async def detect_price_pattern(
    symbol: str,
    timeframe: str,
    raw_file: Path,
    directory: Path,
    timestamp: int,
    enabled: dict,
) -> Path:
    """Detect price patterns and store to ``<symbol><timestamp>_pattern.csv``.

    Parameters
    ----------
    enabled : dict
        Mapping of pattern names to a boolean flag indicating if they should be
        detected.
    """
    logging.info("start detect_price_pattern %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_pattern.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating price pattern file %s", path)
            patterns = [name for name, flag in enabled.items() if flag]
            header = ",".join(patterns) + "\n" if patterns else "\n"
            path.write_text(header)
        # placeholder for pattern detection using `enabled`
        logging.info("completed detect_price_pattern %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in detect_price_pattern %s %s", symbol, timeframe)
        raise
