from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla

MODELS = {
    "S": "Model S",
    "X": "Model X",
    "3": "Model 3",
    "Y": "Model Y",
    "C": "Cybertruck",
    "R": "Roadster",
    "T": "Semi",
}

class Vehicle:
    """Base class describing a Tesla vehicle."""

    vin: str
    parent: Tesla

    def __init__(self, parent: Tesla, vin: str):
        self.vin = vin
        self.parent = parent

    @property
    def pre2021(self) -> bool:
        """Checks if a vehicle is a pre-2021 model S or X."""
        return self.vin[3] in ["S", "X"] and (self.vin[9] <= "L" or (self.vin[9] == "M" and self.vin[7] in ['1', '2', '3', '4']))

    @property
    def model(self) -> str:
        """Returns the model of the vehicle."""
        return MODELS.get(self.vin[3], "Unknown")
