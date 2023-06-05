"""scheduler app"""
import asyncio
import signal
import os
import logging

from sendcloud.utils.scheduler import Scheduler

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def graceful_shutdown(loop):
    """Cleanup tasks tied to the service's shutdown."""
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    _LOGGER.info("[INFO] Scheduler shut down successfully")
    loop.stop()


def run():
    """Runs the feed refresher"""
    loop = asyncio.get_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for sig in signals:
        loop.add_signal_handler(sig, lambda: asyncio.create_task(graceful_shutdown(loop)))

    time_interval = int(os.environ.get("SCHEDULER_TIME_INTERVAL", 3000))
    loop.create_task(Scheduler(time_interval, loop).run())
    loop.run_forever()


if __name__ == '__main__':
    run()
