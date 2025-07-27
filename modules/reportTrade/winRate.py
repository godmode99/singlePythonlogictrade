import logging
from pathlib import Path

from modules.create_pending_order_sendMt5 import send_telegram


async def update_win_rate(symbol: str, directory: Path, telegram_cfg: dict | None = None) -> Path:
    """Update win rate statistics and store to ``<symbol>_win_rate.csv``.

    Parameters
    ----------
    symbol : str
        Trading symbol used for the report.
    directory : Path
        Directory where the win rate csv will be stored.
    telegram_cfg : dict, optional
        Telegram configuration for sending notifications.
    """
    logging.info("start update_win_rate %s", symbol)
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}_win_rate.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating win rate file %s", path)
            path.write_text("win_rate\n")
        # placeholder for win rate calculation
        logging.info("completed update_win_rate %s", symbol)
        if telegram_cfg is not None:
            await send_telegram(telegram_cfg, f"update win rate completed for {symbol}")
        return path
    except Exception:
        logging.exception("error in update_win_rate %s", symbol)
        if telegram_cfg is not None:
            await send_telegram(telegram_cfg, f"update win rate failed for {symbol}")
        raise
