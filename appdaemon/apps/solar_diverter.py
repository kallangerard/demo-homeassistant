import appdaemon.plugins.hass.hassapi as hass

class App(hass.Hass):
    def initialize(self):
        self.log("Initialising Solar Diverter")
        app = self
        self.loads = Loads(app, self.args["heaters"])
        self.run_every(self.loads.control_loads, "now", 1)

class Loads:
    def __init__(self, app, entities):
        self.app = app
        self.entities = entities

    def control_loads(self, *args):
        imported_power = self._get_imported_power()
        self.app.log(f"Imported Power: {imported_power}")

        if imported_power >= 0.0:
            loads = self._get_filtered_loads(
                filter_state=self._get_on_state, reverse=False
            )
            if len(loads) > 0:
                first_entity = loads[0]["entity_id"]
                self.app.log(f"Turning off {first_entity}")
                self.app.call_service(
                    "input_boolean/turn_off", entity_id=first_entity,
                )

        elif imported_power < 0.0:
            loads = self._get_filtered_loads(
                filter_state=self._get_off_state, reverse=True
            )
            if len(loads) > 0:
                first_entity = loads[0]["entity_id"]
                entity_power = loads[0]["power"]
                if abs(imported_power) > entity_power:
                    self.app.log(f"Turning on {first_entity}")
                    self.app.call_service(
                        "input_boolean/turn_on", entity_id=first_entity,
                    )

    def _get_load_priority(self, state):
        return state.get("priority")

    def _get_entity_state(self, entity: str) -> dict:
        state = self.app.get_state(entity, attribute="all")
        return {
            "entity_id": state["entity_id"],
            "state": state["state"],
            "power": float(state["attributes"]["power"]),
            "priority": int(state["attributes"]["priority"]),
        }

    def _get_off_state(self, state: dict) -> str:
        if state.get("state") == "off":
            return True
        else:
            return False

    def _get_on_state(self, state: dict) -> str:
        if state.get("state") == "on":
            return True
        else:
            return False

    def _get_filtered_loads(self, filter_state, reverse: str) -> list:
        states = list(map(self._get_entity_state, self.entities))
        filtered = list(filter(filter_state, states))
        ordered = sorted(filtered, key=self._get_load_priority, reverse=reverse,)
        return list(ordered)

    def _get_imported_power(self) -> float:
        return float(self.app.get_state("sensor.power_import"))
