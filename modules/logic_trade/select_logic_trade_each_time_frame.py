import json
import logging
from pathlib import Path


async def select_logic_trade(symbol: str, timeframe: str, regime_file: Path, directory: Path, timestamp: int) -> Path:
    """Select trade logic and store to ``<symbol><timestamp>_logicTrade.json``."""
    logging.info("start select_logic_trade %s %s", symbol, timeframe)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_logicTrade.json"
        path = directory / filename
        if not path.exists():
            logging.info("creating logic trade file %s", path)
            path.write_text("{}")

        trade = {
            "logic_trade": f"trend_follow_{timeframe}",
            "entry": 100.0,
            "tp": 102.0,
            "sl": 99.0,
            "pending_order_type": "buy_stop",
            "confidence": 60,
            "reason": "",
        }

        path.write_text(json.dumps(trade))

        logging.info("completed select_logic_trade %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in select_logic_trade %s %s", symbol, timeframe)
        raise
