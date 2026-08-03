"""Model detection from the VIN's 4th character (Vehicle.model)."""

from unittest import TestCase

from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle


class VehicleModelTests(TestCase):
    def _model_for(self, fourth_char: str) -> str:
        vin = f"5YJ{fourth_char}CAE43LF123456"
        vehicle = Vehicle(parent=None, vin=vin)
        return vehicle.model

    def test_model_s(self):
        self.assertEqual(self._model_for("S"), "Model S")

    def test_model_x(self):
        self.assertEqual(self._model_for("X"), "Model X")

    def test_model_3(self):
        self.assertEqual(self._model_for("3"), "Model 3")

    def test_model_y(self):
        self.assertEqual(self._model_for("Y"), "Model Y")

    def test_cybertruck(self):
        self.assertEqual(self._model_for("C"), "Cybertruck")

    def test_roadster(self):
        self.assertEqual(self._model_for("R"), "Roadster")

    def test_semi(self):
        self.assertEqual(self._model_for("T"), "Semi")

    def test_cybercab(self):
        self.assertEqual(self._model_for("A"), "Cybercab")

    def test_unknown(self):
        self.assertEqual(self._model_for("Z"), "Unknown")
