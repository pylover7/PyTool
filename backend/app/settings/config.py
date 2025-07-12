import configparser
from pathlib import Path

from app.settings import settings

pay_path = Path(settings.CONFIG_PATH).joinpath("pay.ini")


class Config:
    def __init__(self, path: Path):
        self.config = configparser.ConfigParser()
        self.path = path
        self.config.read(self.path, encoding='utf-8')

    def get_config(self, section, option):
        return self.config.get(section, option)

    def set_config(self, section, option, value):
        self.config.set(section, option, value)
        with open(self.path, 'w', encoding='utf-8') as f:
            self.config.write(f)


pay_config = Config(pay_path)
base_config = Config(Path(settings.CONFIG_PATH).joinpath("base.ini"))

if __name__ == '__main__':
    pay_config = Config(pay_path)
    print(pay_config.get_config('mysql', 'host'))
