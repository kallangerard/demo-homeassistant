import appdaemon.plugins.hass.hassapi as hass


class App(hass.Hass):
    def initialize(self):
        for args in self.args["thermostats"]:
            thermostat = self.args["thermostats"][args]
            self.log(thermostat.get("heat_gain"))
            self.log(thermostat.get("heat_loss"))
            self.log(thermostat.get("heater"))


class Thermostat:
    def __init__(self, app, thermostat):
        self.app = app
        self._heat_gain = thermostat.get("heat_gain")
        self._heat_loss = thermostat.get("heat_loss")
        self._heater = thermostat.get("heater")

    def set_target_temperature(self, target_temperature: float):
        pass

    def get_target_temperature(self) -> float:
        return self.app.get_state(self._heater, attribute="target_temperature")
