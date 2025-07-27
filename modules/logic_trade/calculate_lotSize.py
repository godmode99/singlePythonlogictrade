import json
import logging
from pathlib import Path


async def calculate_lot_size(
    symbol: str,
    timeframe: str,
    confidence_file: Path,
    risk_cfg: dict,
    balance: float,
    directory: Path,
    timestamp: int,
    max_confidence_score: int,
) -> Path:
    """Calculate lot size and store to ``<symbol><timestamp>_lotSize.json``."""
    logging.info("start calculate_lot_size %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_lotSize.json"
        path = directory / filename
        if not path.exists():
            logging.info("creating lot size file %s", path)
            path.write_text("{}")

        try:
            confidence = float(confidence_file.read_text().strip())
        except ValueError:
            confidence = 0.0

        risk = risk_cfg.get(timeframe, {}).get("max_risk_per_trade_free_margin", 0)
        lot = balance * (confidence / max_confidence_score) * (risk / 100)
        data = {"lot": lot, "risk_per_trade": risk}
        path.write_text(json.dumps(data))

        logging.info("completed calculate_lot_size %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in calculate_lot_size %s %s", symbol, timeframe)
        raise
