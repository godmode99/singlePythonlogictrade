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


async def run_step(coro, name: str):
    """Run a pipeline step and log the outcome."""
    logging.info("starting %s", name)
    try:
        result = await coro
        logging.info("%s success", name)
        return result, True
    except Exception:
        logging.exception("%s failed", name)
        return None, False


async def pipeline(config: dict):
    main_cfg = config["main"]
    fetch_cfg = config["fetch"]
    lot_size = config["lot_size"]["risk_manage_timeframe"]

    symbol_market = fetch_cfg["symbol_market"].lower()
    symbol_save_file = fetch_cfg["symbol_save_file"].lower()
    timeframes = [tf for tf, enabled in fetch_cfg["timeframes"].items() if enabled]
    paths = {k: Path(v) for k, v in config["paths"].items()}

    balance = main_cfg.get("balance", 0)
    timestamp = int(time.time())

    for tf in timeframes:
        logging.info("processing timeframe %s", tf)
        ohclv_file, ok = await run_step(fetch_ohlcv(symbol_save_file, tf, paths["raw_ohlcv"], timestamp), f"fetch_ohlcv {tf}")
        if not ok:
            continue
        indicator_file, ok = await run_step(calculate_indicator(symbol_save_file, tf, ohclv_file, paths["indicators"], timestamp), f"calculate_indicator {tf}")
        if not ok:
            continue
        pattern_file, ok = await run_step(detect_price_pattern(symbol_save_file, tf, ohclv_file, paths["patterns"], timestamp), f"detect_price_pattern {tf}")
        if not ok:
            continue
        regime_file, ok = await run_step(identify_regime(symbol_save_file, tf, indicator_file, pattern_file, paths["regime"], timestamp), f"identify_regime {tf}")
        if not ok:
            continue
        confidence_file, ok = await run_step(confidence_scoring(symbol_save_file, tf, indicator_file, pattern_file, paths["confidence"], timestamp), f"confidence_scoring {tf}")
        if not ok:
            continue
        logic_file, ok = await run_step(select_logic_trade(symbol_save_file, tf, regime_file, paths["logic_trade"], timestamp), f"select_logic_trade {tf}")
        if not ok:
            continue
        lot_file, ok = await run_step(calculate_lot_size(symbol_save_file, tf, confidence_file, lot_size, balance, paths["lot_size"], timestamp), f"calculate_lot_size {tf}")
        if not ok:
            continue
        await run_step(create_order(symbol_save_file, tf, logic_file, lot_file, paths["orders"], timestamp), f"create_order {tf}")

    await run_step(fetch_trade_history(symbol_save_file, paths["trade_history"]), "fetch_trade_history")
    await run_step(update_win_rate(symbol_save_file, paths["win_rate"]), "update_win_rate")


async def main():
    config = load_config()
    main_cfg = config.get("main", {})
    interval = main_cfg.get("interval", 300)
    while True:
        try:
            await pipeline(config)
            logging.info("cycle completed")
        except Exception:
            logging.exception("error running pipeline")
        await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main())
