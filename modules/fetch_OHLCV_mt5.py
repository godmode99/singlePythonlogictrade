import logging
import time
from pathlib import Path


async def fetch_ohlcv(
    symbol: str,
    timeframe: str,
    directory: Path,
    timestamp: int,
    fetch_bars: int,
    tz_shift: int,
    balance: float,
) -> Path:
    """Fetch OHLCV data from MT5 and store to ``<symbol><timestamp>_ohlcv.csv``.

    Parameters
    ----------
    symbol : str
        Trading symbol used for the request.
    timeframe : str
        Timeframe to fetch.
    directory : Path
        Destination directory for the csv file.
    timestamp : int
        Unix timestamp used for naming the file.
    fetch_bars : int
        Number of bars to request from the data source.
    tz_shift : int
        Timezone shift applied when fetching data.
    balance : float
        Current account balance which may be logged together with the data.
    """
    logging.info(
        "start fetch_ohlcv %s %s bars=%s tz_shift=%s balance=%.2f",
        symbol,
        timeframe,
        fetch_bars,
        tz_shift,
        balance,
    )
    try:
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{symbol}{timestamp}_ohlcv.csv"
        path = directory / filename
        if not path.exists():
            logging.info("creating raw ohlcv file %s", path)
            header = "time,open,high,low,close,volume,fetch_bars,tz_shift,balance\n"
            path.write_text(header)
        # placeholder for fetching real data
        logging.info("completed fetch_ohlcv %s %s", symbol, timeframe)
        return path
    except Exception:
        logging.exception("error in fetch_ohlcv %s %s", symbol, timeframe)
        raise
