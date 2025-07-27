import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

import aiohttp


ASYNC_MARKUP = """placeholder for MT5 order execution"""


async def send_mt5(order: dict) -> bool:
    """Placeholder send to MT5, always succeeds."""
    await asyncio.sleep(0.1)
    return True


async def send_telegram(cfg: dict, text: str) -> bool:
    """Send a telegram message using the provided configuration."""
    if not cfg.get("enabled"):
        return False
    token = cfg.get("token")
    chat_id = cfg.get("chatid")
    if not token or not chat_id:
        logging.info("telegram config missing")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={"chat_id": chat_id, "text": text}) as resp:
                ok = resp.status == 200
                if not ok:
                    logging.warning("telegram send failed status %s", resp.status)
                return ok
    except Exception:
        logging.exception("telegram send error")
        return False

async def create_order(
    symbol: str,
    timeframe: str,
    logic_file: Path,
    lot_file: Path,
    directory: Path,
    timestamp: int,
    telegram_cfg: dict,
    account_name: str,
) -> Path:
    """Create order payload for MT5 and store to ``<symbol><timestamp>_order.json``."""
    logging.info("start create_order %s %s", symbol, timeframe)
    order_id = f"{symbol}{timeframe}{timestamp}"
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{order_id}_order.json"
        path = directory / filename
        if not path.exists():
            logging.info("creating order file %s", path)
            path.write_text("{}")

        logic_data = json.loads(logic_file.read_text() or "{}")
        lot_data = json.loads(lot_file.read_text() or "{}")

        entry = float(logic_data.get("entry", 0))
        tp = float(logic_data.get("tp", 0))
        sl = float(logic_data.get("sl", 0))
        pending = logic_data.get("pending_order_type", "skip")
        confidence = float(logic_data.get("confidence", 0))
        logic_trade = logic_data.get("logic_trade", "unknown")
        reason = logic_data.get("reason", "")

        lot = float(lot_data.get("lot", 0))
        risk_per_trade = lot_data.get("risk_per_trade", 0)

        rr = abs((tp - entry) / (entry - sl)) if entry != sl else 0

        order_payload = {
            "order_id": order_id,
            "symbol": symbol,
            "timeframe": timeframe,
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "pending_order_type": pending,
            "volume": lot,
            "comment": logic_trade,
        }
        path.write_text(json.dumps(order_payload))

        can_send = confidence > 50 and rr > 1.5
        success = False
        if can_send:
            success = await send_mt5(order_payload)
        else:
            reason = reason or "conditions not met"

        status = "success" if success else "failed"
        logging.info("send order %s", status)

        msg = (
            f"📅 {datetime.utcnow().isoformat()}\n"
            f"🏦 account:{account_name}\n"
            f"✅ Sending orders:{status}\n"
            f"⏰ order Timeframe: {timeframe}\n"
            f"⚙️ logic_trade: {logic_trade}\n"
            f"📌 order_id:{order_id}\n"
            f"💰 entry: {entry if entry else 'none'}\n"
            f"🛑 sl: {sl if sl else 'none'}\n"
            f"🎯 tp: {tp if tp else 'none'}\n"
            f"🟢⬆️ pending_order_type:{pending}\n"
            f"⭐️ confidence: {confidence}\n\n"
            f"⚖️ risk_per_trade:{risk_per_trade}%\n"
            f"💵 lot:{lot}\n"
            f"📈 rr:{rr}\n"
        )
        if not success:
            msg += f"⚠️ reason:{reason}\n"

        await send_telegram(telegram_cfg, msg)

        logging.info("completed create_order %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in create_order %s %s", symbol, timeframe)
        await send_telegram(telegram_cfg, f"send order for {order_id} failed")
        raise
