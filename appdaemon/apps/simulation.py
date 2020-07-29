import time

import appdaemon.plugins.hass.hassapi as hass
from thermostat import Thermostat
from solar_diverter import Loads
from mock import dryer
from mock import pv
from mock import washing_machine

DRYER = dryer.DRYER
PV = pv.PV
WASHING_MACHINE = washing_machine.WASHING_MACHINE


class Simulation(hass.Hass):
    def initialize(self):
        self.log("Running Simulation")
        self.loads = Loads(self, self.args["heaters"])
        self.set_state("input_number.tick", state=0)
        self.set_state("input_number.tick", state=0)
        self.run_every(self.hourly, "now", 1)

    def hourly(self, *args):
        tick = int(float(self.get_state("input_number.tick")))
        tick = tick + 1
        if tick > 72:
            self.log("Finished Simulation")
            self.stop_app("simulation")
        # self.log(f"Setting Tick to {type(tick)}")
        self.set_value("input_number.tick", tick)
        self.set_value("input_number.solar_generation", PV[tick])
        self._switch_load("input_boolean.dryer", state_string=DRYER[tick], tick=tick)
        self._switch_load(
            "input_boolean.washing_machine",
            state_string=WASHING_MACHINE[tick],
            tick=tick,
        )
        self.loads.control_loads()

    def _switch_load(self, entity_id: str, state_string: str, tick: int):
        self.log(state_string)
        if state_string == "on":
            self.turn_on(entity_id)
        elif state_string == "off":
            self.turn_off(entity_id)
