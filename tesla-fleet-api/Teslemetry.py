from . import TeslaFleetApi


class Teslemetry(TeslaFleetApi):
    def __init__(self, access_token: str):
        self.server = "https://teslemetry.com"
        pass
