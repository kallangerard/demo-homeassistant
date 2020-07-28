import hassapi as hass  # pylint: disable=import-error


class Thermostat:
    def __init__(self, entity_id):
        self._entity_id = entity_id

    def set_target_temperature(self, target_temperature: float):
        pass

    def get_target_temperature(self) -> float:
        pass
