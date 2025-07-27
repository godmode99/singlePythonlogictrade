import asyncio
import json
import logging
import time
from pathlib import Path

from modules.fetch_OHLCV_mt5 import fetch_ohlcv
from modules.process.calculate_indicator import calculate_indicator
from modules.process.detect_price_pattern import detect_price_pattern
from modules.logic_trade.identify_regime import identify_regime
from modules.logic_trade.confidence_scoring import confidence_scoring
from modules.logic_trade.select_logic_trade_each_time_frame import select_logic_trade
from modules.logic_trade.calculate_lotSize import calculate_lot_size
from modules.create_pending_order_sendMt5 import create_order
from modules.reportTrade.fetch_trade_mt5history import fetch_trade_history
from modules.reportTrade.winRate import update_win_rate

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def load_config(path: str = "config.json") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def pipeline(config: dict):
    symbol = config["symbol"].lower()
    timeframes = config["timeframes"]
    paths = {k: Path(v) for k, v in config["paths"].items()}
    risk = config["risk_management"]

    balance = config.get("balance", 0)
    timestamp = int(time.time())

    for tf in timeframes:
        ohclv_file = await fetch_ohlcv(symbol, tf, paths["raw_ohlcv"], timestamp)
        indicator_file = await calculate_indicator(symbol, tf, ohclv_file, paths["indicators"], timestamp)
        pattern_file = await detect_price_pattern(symbol, tf, ohclv_file, paths["patterns"], timestamp)
        regime_file = await identify_regime(symbol, tf, indicator_file, pattern_file, paths["regime"], timestamp)
        confidence_file = await confidence_scoring(symbol, tf, indicator_file, pattern_file, paths["confidence"], timestamp)
        logic_file = await select_logic_trade(symbol, tf, regime_file, paths["logic_trade"], timestamp)
        lot_file = await calculate_lot_size(symbol, tf, confidence_file, risk, balance, paths["lot_size"], timestamp)
        order_file = await create_order(symbol, tf, logic_file, lot_file, paths["orders"], timestamp)
        await fetch_trade_history(symbol, paths["trade_history"])
        await update_win_rate(symbol, paths["win_rate"])


async def main():
    config = load_config()
    interval = config.get("interval", 300)
    while True:
        try:
            await pipeline(config)
            logging.info("cycle completed")
        except Exception:
            logging.exception("error running pipeline")
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
