import pytz
import datetime
import MetaTrader5 as mt5
from robots.env_vars import env_vars
import logging

logger = logging.getLogger('robots.fx_robot_base')


class FxRobotBase:
    def __init__(self, symbol="AUDJPY"):
        self.mt5 = mt5
        self.logger = logging.getLogger('robots.fx_robot_base.FxRobotBase')
        # MetaTrader 5パッケージについてのデータを表示する
        self.logger.debug("MetaTrader5 package author: %s" % mt5.__author__)
        self.logger.debug("MetaTrader5 package version: %s" % mt5.__version__)
        # 指定された取引口座へのMetaTrader 5接続を確立する
        self.logger.debug(env_vars.mt5_account)

        if self.mt5.initialize(
            login=env_vars.mt5_account,
            server=env_vars.mt5_server,
            password=env_vars.mt5_password,
        ):
            logger.info("Connected to MT5 Version: %s, %s, %s" % mt5.version())
            # 接続状態、サーバ名、取引口座に関するデータを表示する
            self.logger.debug(mt5.terminal_info())
        else:
            self.logger.error("initialize() failed, error code = %s" %
                self.mt5.last_error()
            )
            quit()

        self.symbol = symbol
        self.position = ""
        self.rates_frame = None
        self.order_request = None

        self.timezone = pytz.timezone("Etc/UTC")

    def start(self):
        self.logger.info("Start FX Robot =======>")

    def shutdown(self):
        # MetaTrader 5ターミナルへの接続をシャットダウンする
        self.mt5.shutdown()

    def entry(self):
        pass

    def chekout(self):
        pass

    def get_mt5_copy_latest_rate_range(
        self, hours=1, timeframe=mt5.TIMEFRAME_M5, count=10
    ):
        utc_from = datetime.datetime.now() - datetime.timedelta(hours=hours)
        rates = self.mt5.copy_rates_from(
            self.symbol, timeframe, utc_from, count
        )
        return rates

    def order_summary(self):
        logger.info(self.rates_frame)
        logger.info(self.order_request)

if __name__ == "__main__":
    fxRobot = FxRobotBase()
    fxRobot.shutdown()
