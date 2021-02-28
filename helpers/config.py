import os
import configparser
from pathlib import Path


class Config:
    @staticmethod
    def load():
        base_directory_path = Path(os.path.dirname(__file__)).parent
        config_file_path = os.path.join(base_directory_path, 'config.conf')
        if not os.path.isfile(config_file_path):
            raise FileNotFoundError("Please copy and rename config.conf.example to config.conf")
        config = configparser.ConfigParser()
        config.read(config_file_path)
        return config
