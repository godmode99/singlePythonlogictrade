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
    main_cfg = config["main"]
    fetch_cfg = config["fetch"]
    lot_size_cfg = config["lot_size"]["risk_manage_timeframe"]
    max_conf_score = config["lot_size"].get("max_confidence_score", 100)

    symbol_save_file = fetch_cfg["symbol_save_file"].lower()
    timeframes = [tf for tf, enabled in fetch_cfg["timeframes"].items() if enabled]
    paths = {k: Path(v) for k, v in config["paths"].items()}

    balance = main_cfg.get("balance", 0)
    fetch_bars = fetch_cfg.get("fetch_bars", 0)
    tz_shift = fetch_cfg.get("tz_shift", 0)
    timestamp = int(time.time())

    for tf in timeframes:
        logging.info("processing timeframe %s", tf)

        try:
            logging.info("Fetching OHLCV...")
            ohclv_file = await fetch_ohlcv(
                symbol_save_file,
                tf,
                paths["raw_ohlcv"],
                timestamp,
                fetch_bars,
                tz_shift,
                balance,
            )
            logging.info("Fetching OHLCV complete")
        except Exception:
            logging.exception("Fetching OHLCV failed")
            continue

        try:
            logging.info("Calculating indicators...")
            indicator_file = await calculate_indicator(
                symbol_save_file,
                tf,
                ohclv_file,
                paths["indicators"],
                timestamp,
                config["indicators"]["enabled"],
            )
            logging.info("Calculating indicators complete")
        except Exception:
            logging.exception("Calculating indicators failed")
            continue

        try:
            logging.info("Detecting patterns...")
            pattern_file = await detect_price_pattern(
                symbol_save_file,
                tf,
                ohclv_file,
                paths["patterns"],
                timestamp,
                config["patterns"]["enabled"],
            )
            logging.info("Detecting patterns complete")
        except Exception:
            logging.exception("Detecting patterns failed")
            continue

        try:
            logging.info("Identifying regime...")
            regime_file = await identify_regime(
                symbol_save_file,
                tf,
                indicator_file,
                pattern_file,
                paths["regime"],
                timestamp,
                config["regime"],
            )
            logging.info("Identifying regime complete")
        except Exception:
            logging.exception("Identifying regime failed")
            continue

        try:
            logging.info("Scoring confidence...")
            confidence_file = await confidence_scoring(
                symbol_save_file,
                tf,
                indicator_file,
                pattern_file,
                paths["confidence"],
                timestamp,
                config["confidence"],
            )
            logging.info("Scoring confidence complete")
        except Exception:
            logging.exception("Scoring confidence failed")
            continue

        try:
            logging.info("Selecting logic trade...")
            logic_file = await select_logic_trade(symbol_save_file, tf, regime_file, paths["logic_trade"], timestamp)
            logging.info("Selecting logic trade complete")
        except Exception:
            logging.exception("Selecting logic trade failed")
            continue

        try:
            logging.info("Calculating lot size...")
            lot_file = await calculate_lot_size(
                symbol_save_file,
                tf,
                confidence_file,
                lot_size_cfg,
                balance,
                paths["lot_size"],
                timestamp,
                max_conf_score,
            )
            logging.info("Calculating lot size complete")
        except Exception:
            logging.exception("Calculating lot size failed")
            continue

        try:
            logging.info("Creating order...")
            await create_order(symbol_save_file, tf, logic_file, lot_file, paths["orders"], timestamp)
            logging.info("Creating order complete")
        except Exception:
            logging.exception("Creating order failed")

    try:
        logging.info("Fetching trade history...")
        await fetch_trade_history(symbol_save_file, paths["trade_history"])
        logging.info("Fetching trade history complete")
    except Exception:
        logging.exception("Fetching trade history failed")

    try:
        logging.info("Updating win rate...")
        await update_win_rate(symbol_save_file, paths["win_rate"])
        logging.info("Updating win rate complete")
    except Exception:
        logging.exception("Updating win rate failed")


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
