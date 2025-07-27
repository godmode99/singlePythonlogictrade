import logging
from pathlib import Path


async def calculate_indicator(
    symbol: str,
    timeframe: str,
    raw_file: Path,
    directory: Path,
    timestamp: int,
    enabled: dict,
) -> Path:
    """Calculate technical indicators and store to ``<symbol><timestamp>_indicators.csv``.

    Parameters
    ----------
    enabled : dict
        Mapping of indicator names to a boolean flag indicating if they should be
        calculated.
    """
    logging.info("start calculate_indicator %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_indicators.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating indicator file %s", path)
            indicators = [name for name, flag in enabled.items() if flag]
            header = ",".join(indicators) + "\n" if indicators else "\n"
            path.write_text(header)
        # placeholder for real indicator calculation using `enabled`
        logging.info("completed calculate_indicator %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in calculate_indicator %s %s", symbol, timeframe)
        raise
