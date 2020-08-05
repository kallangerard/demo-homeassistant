import json
import time
import appdaemon.plugins.hass.hassapi as hass
from mock import dryer
from mock import pv
from mock import washing_machine

DRYER = dryer.DRYER
PV = pv.PV
WASHING_MACHINE = washing_machine.WASHING_MACHINE


class Simulation(hass.Hass):
    def initialize(self):

        self.thermostats = self._get_loads(self.args["loads"].items())
        self.set_state("input_number.tick", state=0)
        # self.log(test_state)
        setup_loads = self.args["loads"].items()
        for load in setup_loads:
            start_temperature = float(load[1]["start_temperature"])
            temperature = load[1]["temperature"]
            thermostat = load[1]["thermostat"]
            self.log(f"Setting {temperature} to {start_temperature}")
            self.set_value(temperature, start_temperature)
            self.log(f"Setting {thermostat} to {start_temperature}")
            self.call_service(
                "climate/set_temperature",
                entity_id=thermostat,
                temperature=start_temperature,
            )
        self.run_every(self.hourly, "now", 1)

    def _get_loads(self, loads: dict):
        thermostats = list(map(lambda x: x[1].get("thermostat"), loads))
        return thermostats

    def hourly(self, *args):
        solar_diverter = self.get_app("solar_diverter")
        tick = int(float(self.get_state("input_number.tick")))
        if tick == 72:
            self.log("Finished Simulation")
            self.turn_off("input_boolean.run_simulation")
            return
        self.set_value("input_number.tick", tick + 1)
        self.set_value("input_number.solar_generation", PV[tick - 1])
        self._switch_load(
            "input_boolean.dryer", state_string=DRYER[tick - 1], tick=tick
        )
        self._switch_load(
            "input_boolean.washing_machine",
            state_string=WASHING_MACHINE[tick - 1],
            tick=tick,
        )
        self._run_thermostat()
        if self.args["control_loads"] == True:
            for _ in range(4):
                solar_diverter.control_loads()

    def _switch_load(self, entity_id: str, state_string: str, tick: int):
        if state_string == "on":
            self.turn_on(entity_id)
        elif state_string == "off":
            self.turn_off(entity_id)

    def _run_thermostat(self, *args):
        current_temperatures = self.get_state("input_number")
        input_booleans = self.get_state("input_boolean")
        heater_states = {k: v.get("state") for (k, v) in input_booleans.items()}

        for load in self.args["loads"].items():
            heater = load[1]["heater"]
            if heater_states[heater] == "off":
                heat_gain = 0.0
            else:
                heat_gain = float(load[1]["heat_gain"])

            heat_loss = float(load[1]["heat_loss"])
            thermal_mass = float(load[1]["thermal_mass"])
            target_temperature = load[1]["temperature"]
            current_temp = float(current_temperatures[target_temperature]["state"])
            new_temp = (
                current_temp + (heat_gain / thermal_mass) - (heat_loss / thermal_mass)
            )
            self.set_value(target_temperature, new_temp)
