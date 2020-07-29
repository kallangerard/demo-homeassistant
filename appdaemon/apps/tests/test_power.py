from solar_diverter import Loads


# class TestPower:
#     def test_surplus_importing(self):
#         power = Power(power_demand=1200, power_generation=1000, power_import=200)
#         assert power.surplus == 0

#     def test_shortfall_positive(self):
#         power = Power(power_demand=0, power_generation=1000, power_import=0)
#         assert power.shortfall == 0


class TestLoads:
    def test_loads_app(self):
        loads = Loads("app", "entities")
        assert loads.app == "app"

    def test_loads_entities(self):
        loads = Loads("app", "entities")
        assert loads.entities == "entities"

