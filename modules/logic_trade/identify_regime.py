import logging
from pathlib import Path


async def identify_regime(
    symbol: str,
    timeframe: str,
    indicator_file: Path,
    pattern_file: Path,
    directory: Path,
    timestamp: int,
    regime_cfg: dict,
) -> Path:
    """Identify market regime and store to ``<symbol><timestamp>_regime.csv``.

    Parameters
    ----------
    regime_cfg : dict
        Configuration specifying scoring for each regime type.
    """
    logging.info("start identify_regime %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_regime.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating regime file %s", path)
            path.write_text("regime,score\n")

        # very naive scoring just to demonstrate usage of `regime_cfg`
        scores = {
            name: sum(v for v in params.values())
            for name, params in regime_cfg.items()
        }
        regime = max(scores, key=scores.get)
        path.write_text(f"{regime},{scores[regime]}\n")

        logging.info("completed identify_regime %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in identify_regime %s %s", symbol, timeframe)
        raise
