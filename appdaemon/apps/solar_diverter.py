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
        if imported_power >= 0.0:
            filter_action = "turn_off_action"
            reverse = False
        elif imported_power < 0.0:
            filter_action = "turn_on_action"
            reverse = True
        attribute = "temperature"
        load_states = self._get_load_states(self._get_entity_state, self.entities)
        loads = self._get_filtered_loads(
            action=filter_action, attribute=attribute, reverse=reverse, load_states=load_states
        )
        if len(loads) == 0:
            self.log("No loads to switch available")
            return
        first_entity = loads[0]["entity_id"]
        switch_action = loads[0][filter_action]
        entity_power = loads[0]["power"]
        if (
            filter_action == "turn_on_action"
            and self._surplus_power_available(imported_power, entity_power) == False
        ):
            self.log(f"Not enough power to switch on {first_entity}")
            return
        self._switch_load(switch_action)

    def _get_imported_power(self) -> float:
        return float(self.get_state("sensor.power_import"))

    def _surplus_power_available(self, imported_power, entity_power):
        if abs(imported_power) < entity_power:
            return False
        return True

    def _switch_load(self, switch_action: dict):
        entity_id = switch_action["entity_id"]
        self.log(f"Switching: {entity_id} \n switch_action: {switch_action}")
        self.call_service(**switch_action)

    def _get_load_states(self, get_entity_state, entities: dict):
        return list(map(get_entity_state, entities))

    def _get_filtered_loads(
        self, action: str, attribute: str, reverse: str, load_states: dict
    ) -> list:
        filtered = list(
            filter(lambda x: x[attribute] != x[action][attribute], load_states)
        )
        self.log(filtered)
        ordered = sorted(filtered, key=lambda x: x.get("priority"), reverse=reverse)
        return ordered

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

