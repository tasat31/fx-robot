import sys
import schedule
import time
from robots.trade_bot_alpha import TradeBotAlpha
import logging

logger = logging.getLogger('robots')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def job():
    bot = TradeBotAlpha()
    bot.entry()
    bot.shutdown()


if __name__ == "__main__":

    bot_scheduler = schedule.Scheduler()

    job()
    bot_scheduler.every(10).minutes.do(job)

    while True:
        bot_scheduler.run_pending()
        time.sleep(1)
