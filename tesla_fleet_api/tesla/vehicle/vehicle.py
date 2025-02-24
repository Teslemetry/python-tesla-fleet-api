from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla


class Vehicle:
    """Base class describing a Tesla vehicle."""

    vin: str

    def __init__(self, parent: Tesla, vin: str):
        self.vin = vin

    def pre2021(self, vin: str) -> bool:
        """Checks if a vehicle is a pre-2021 model S or X."""
        return vin[3] in ["S", "X"] and (vin[9] <= "L" or (vin[9] == "M" and vin[7] in ['1', '2', '3', '4']))
