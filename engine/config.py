import yaml


class Config:

    def __init__(self):

        with open("config.yaml", "r") as f:
            self.data = yaml.safe_load(f)

    def plugin_enabled(self, name):

        return self.data["plugins"].get(name, False)