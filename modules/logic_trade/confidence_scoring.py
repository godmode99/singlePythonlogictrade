import logging
from pathlib import Path


async def confidence_scoring(
    symbol: str,
    timeframe: str,
    indicator_file: Path,
    pattern_file: Path,
    directory: Path,
    timestamp: int,
    confidence_cfg: dict,
) -> Path:
    """Score trade confidence and store to ``<symbol><timestamp>_confidence.csv``.

    Parameters
    ----------
    confidence_cfg : dict
        Configuration weights used for scoring the trade setup.
    """
    logging.info("start confidence_scoring %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_confidence.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating confidence file %s", path)
            path.write_text("confidence\n")

        score = sum(confidence_cfg.values())
        path.write_text(f"{score}\n")

        logging.info("completed confidence_scoring %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in confidence_scoring %s %s", symbol, timeframe)
        raise
