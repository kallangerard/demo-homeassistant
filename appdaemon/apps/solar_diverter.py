import json
import appdaemon.plugins.hass.hassapi as hass


class App(hass.Hass):
    def initialize(self):
        self.log("Initialising Solar Diverter")
        self.entities = self.args["loads"]
        self.log("initialized Loads")

    def control_loads(self):
        imported_power = self._get_imported_power()
        self.log(f"Imported Power: {imported_power}")

        # def blah(self):
        if imported_power >= 0.0:
            loads = self._get_filtered_loads(
                filter_state=self._get_on_state, reverse=False, entities=self.entities
            )
            if len(loads) > 0:
                first_entity = loads[0]["entity_id"]
                self.log(f"Turning off {first_entity}")
                turn_off_action = loads[0]["turn_off_action"]
                self.log(turn_off_action)
                response = self.call_service(**turn_off_action)
                self.log(response)
            else:
                self.log("No loads to switch available")

        elif imported_power < 0.0:
            loads = self._get_filtered_loads(
                filter_state=self._get_off_state, reverse=True, entities=self.entities
            )
            self.log(f"Length of loads to control is {len(loads)}")
            if len(loads) > 0:
                first_entity = loads[0]["entity_id"]
                entity_power = loads[0]["power"]
                if abs(imported_power) > entity_power:
                    self.log(f"Turning on {first_entity}")
                    turn_on_action = loads[0]["turn_on_action"]
                    self.log(turn_on_action)
                    response = self.call_service(**turn_on_action)
                    self.log(response)
            else:
                self.log("No loads to switch available")

    def _get_load_priority(self, state):
        return state.get("priority")

    def _get_entity_state(self, entity: str) -> dict:
        state = self.get_state(entity, attribute="all")
        return {
            "entity_id": state["entity_id"],
            "state": state["state"],
            "power": float(state["attributes"]["power"]),
            "priority": int(state["attributes"]["priority"]),
            "turn_on_action": json.loads(state["attributes"]["turn_on_action"])[0],
            "turn_off_action": json.loads(state["attributes"]["turn_off_action"])[0],
            "temperature": state["attributes"]["temperature"],
        }

    def _get_off_state(self, state: dict) -> str:
        if state["temperature"] == state["turn_off_action"]["temperature"]:
            return True
        else:
            return False

    def _get_on_state(self, state: dict) -> str:
        if state["temperature"] == state["turn_on_action"]["temperature"]:
            return True
        else:
            return False

    def _get_filtered_loads(self, filter_state, reverse: str, entities: list) -> list:
        load_states = list(map(self._get_entity_state, self.entities))
        filtered = list(filter(filter_state, load_states))
        ordered = sorted(filtered, key=self._get_load_priority, reverse=reverse,)
        return list(ordered)

    def _get_imported_power(self) -> float:
        return float(self.get_state("sensor.power_import"))
