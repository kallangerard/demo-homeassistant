# pylint: disable=import-error
import hassapi as hass


class SolarDiverter(hass.Hass):
    def initialize(self):
        self.log("Initialising Solar Diverter")

        # Listen to Solar State
        self.listen_state(self.switch_heater, "input_number.solar_generation")

    # def solar_changed(self, )

    def switch_heater(self, entity, attribute, old, new, kwargs):
        self.log(f"{entity} changed from {old} watts to {new} watts")
        if float(new) > 2000:
            self.log("Turning on water heater")
            self.call_service(
                "input_boolean/turn_on", entity_id="input_boolean.heater_water"
            )
        elif float(new) <= 2000:
            self.log("Turning off water heater")
            self.call_service(
                "input_boolean/turn_off", entity_id="input_boolean.heater_water"
            )
