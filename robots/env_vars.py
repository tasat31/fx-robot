import os
from pydantic import BaseSettings
import logging

logger = logging.getLogger(__name__)


class EnvVars(BaseSettings):

    # basic_auth(for /token)
    mt5_account: int = 0
    mt5_server: str = ""
    mt5_password: str = ""


if os.path.exists(".env"):
    env_vars = EnvVars(_env_file=".env", _env_file_encoding="utf-8")
else:
    try:
        env_vars = EnvVars()
    except Exception as e:
        logger.error("Env vars load error.")
        logger.error(e)
