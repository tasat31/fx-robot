import MetaTrader5 as mt5
from robots.fx_robot_base import FxRobotBase
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger('robots.trade_bot_alpha')

class TradeBotAlpha(FxRobotBase):
    def __init__(self):
        super().__init__()
        self.coef_sell_or_buy = 0.0
        self.model_aic = 0.0
        self.predict_aic = 0.0

    def entry(self):
        self.rates = self.get_mt5_copy_latest_rate_range(
            hours=1, timeframe=mt5.TIMEFRAME_M1, count=10
        )
        self.rates_frame = pd.DataFrame(self.rates)

        self.rates_frame["median"] = self.rates_frame["high"] - (
            (self.rates_frame["high"] - self.rates_frame["low"]) / 2.0
        )
        rows = len(self.rates_frame)

        # SELL OR BUY
        lr_model = LinearRegression()
        lr_model.fit(
            self.rates_frame.index.values.reshape(rows, 1),
            self.rates_frame["open"].values.reshape(rows, 1),
        )
        self.coef_sell_or_buy = self.coef_sell_or_buy + lr_model.coef_[0][0]
        # print('coef: open' + str(lr_model.coef_[0][0]))

        lr_model.fit(
            self.rates_frame.index.values.reshape(rows, 1),
            self.rates_frame["high"].values.reshape(rows, 1),
        )
        self.coef_sell_or_buy = self.coef_sell_or_buy + lr_model.coef_[0][0]
        # print('coef: high' + str(lr_model.coef_[0][0]))

        lr_model.fit(
            self.rates_frame.index.values.reshape(rows, 1),
            self.rates_frame["low"].values.reshape(rows, 1),
        )
        self.coef_sell_or_buy = self.coef_sell_or_buy + lr_model.coef_[0][0]
        # print('coef: low' + str(lr_model.coef_[0][0]))

        lr_model.fit(
            self.rates_frame.index.values.reshape(rows, 1),
            self.rates_frame["close"].values
                .reshape(rows, 1),
        )
        self.coef_sell_or_buy = self.coef_sell_or_buy + lr_model.coef_[0][0]
        # print('coef: close' + str(lr_model.coef_[0][0]))

        lr_model.fit(
            self.rates_frame.index.values.reshape(rows, 1),
            self.rates_frame["median"].values.reshape(rows, 1),
        )
        self.coef_sell_or_buy = self.coef_sell_or_buy + lr_model.coef_[0][0]
        # print('coef: median' + str(lr_model.coef_[0][0]))

        glm_model = smf.glm(
            formula="median ~ time",
            data=self.rates_frame,
            family=sm.families.Gaussian(),
        )
        result = glm_model.fit()
        self.model_aic = result.aic

        if self.coef_sell_or_buy > 0:
            self.order_type = mt5.ORDER_TYPE_BUY
            price = self.mt5.symbol_info_tick(self.symbol).ask
            sl_price, tp_price = self._calc_price(self.order_type, price)
        else:
            self.order_type = mt5.ORDER_TYPE_SELL
            price = self.mt5.symbol_info_tick(self.symbol).bid
            sl_price, tp_price = self._calc_price(self.order_type, price)

        # add predict sample
        predict_sample = {
            "time": self.rates_frame.at[9, "time"] + 60,
            "open": self.rates_frame.at[9, "open"],
            "high": self.rates_frame.at[9, "high"],
            "low": self.rates_frame.at[9, "low"],
            "close": self.rates_frame.at[9, "close"],
            "tick_volume": self.rates_frame.at[9, "tick_volume"],
            "spread": self.rates_frame.at[9, "spread"],
            "real_volume": self.rates_frame.at[9, "real_volume"],
            "median": sl_price,
        }

        df_predict_sample = pd.DataFrame(predict_sample, index=[rows])
        self.rates_frame = pd.concat(
            [self.rates_frame, df_predict_sample], ignore_index=True
        )

        glm_model = smf.glm(
            formula="median ~ time",
            data=self.rates_frame,
            family=sm.families.Gaussian(),
        )
        result = glm_model.fit()
        self.predict_aic = result.aic

        if self.predict_aic < self.model_aic:
            if self.order_type == mt5.ORDER_TYPE_BUY:
                self.order_type = mt5.ORDER_TYPE_SELL
                price = self.mt5.symbol_info_tick(self.symbol).bid
                sl_price, tp_price = self._calc_price(self.order_type, price)
            else:
                self.order_type = mt5.ORDER_TYPE_BUY
                price = self.mt5.symbol_info_tick(self.symbol).ask
                sl_price, tp_price = self._calc_price(self.order_type, price)

        self.lot = 0.1
        self.deviation = 20
        self.order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot,
            "type": self.order_type,
            "price": price,
            "stoplimit": price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": self.deviation,
            "magic": 234000,
            "comment": "",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        self.order_summary()

        # 取引リクエストを送信する
        result = self.mt5.order_send(self.order_request)
        if result.retcode != self.mt5.TRADE_RETCODE_DONE:
            self.logger.info(
                (
                    "1. order_send(): "
                    "by {} {} lots "
                    "at {} with deviation={} points"
                ).format(
                    self.symbol, self.lot, price, self.deviation
                )
            )
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.info("2. order_send failed, retcode={}".format(result.retcode))
                # 結果をディクショナリとしてリクエストし、要素ごとに表示する
                result_dict = result._asdict()
                for field in result_dict.keys():
                    self.logger.info("   {}={}".format(field, result_dict[field]))
                    # これが取引リクエスト構造体の場合は要素ごとに表示する
                    if field == "request":
                        traderequest_dict = result_dict[field]._asdict()
                        for tradereq_filed in traderequest_dict:
                            self.logger.info(
                                "       traderequest: {}={}".format(
                                    tradereq_filed,
                                    traderequest_dict[tradereq_filed]
                                )
                            )

        self.mt5.shutdown()

    def order_summary(self):
        super().order_summary()
        logger.info("MODEL AIC=%f" % self.model_aic)
        logger.info("PREDICT AIC=%f" % self.predict_aic)

    def _calc_price(self, order_type, price):
        sl_price = 0
        tp_price = 0

        if order_type == mt5.ORDER_TYPE_BUY:
            sl_price = price - 0.3
            tp_price = price + 0.1
        else:
            sl_price = price + 0.3
            tp_price = price - 0.1

        return sl_price, tp_price
