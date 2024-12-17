from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from loguru import logger


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    HEYGEN_API_KEY: SecretStr


class GenerateVideo:
    def __init__(self, config):
        self.config = config

    def retrieve_script(self):
        self.script = open(self.config["script"], "r").read()
        return

    def generate_avatar(self):
        return

    def retrieve_caption(self):
        return

    def generate_keywords(self):
        return

    def generate_text_video(self):
        return

    def generate_image(self):
        return


if __name__ == "__main__":
    config = {
        "dimensions": (1920, 1080),
        "avatar_offset": (900, 960),
        "avatar_size": (300, 500),
        "avatar_name": "georgia",
        "script": "data/template_script.txt",
    }

    timing_dict = {
        "systemic": ("00:03", "00:13"),
        "dysfunctional": ("00:07", "00:13"),
        "mailbox": ("00:16", "00:26"),
        "signals": ("00:23", "00:26"),
        "primary discomfort": ("00:28", "00:40"),
        "secondary manifestations": ("00:32", "00:40"),
        "tertiary effects": ("00:36", "00:40"),
        "percentage": ("00:42", "00:53"),
        "risk factors": ("00:49", "00:53"),
        "primary testing methods": ("00:55", "01:06"),
        "key indicators": ("00:59", "01:06"),
        "secondary evaluation methods": ("01:03", "01:06"),
    }

    logger.info(f"Starting video generation with config:\n {config}")
    logger.info(f"API key found: {Settings()}")
    video = GenerateVideo(config)
    video.retrieve_script()
    logger.info(f"Script retrieved: {video.script[:100]}")
