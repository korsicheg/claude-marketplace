"""The car: its fuel, its tank, how much it burns at what speed, and the fuel brands its driver prefers.

The default is a typical compact petrol car. A car.json in the data folder overrides any field, e.g.
{"name": "Skoda Octavia 2.0 TDI (2020)", "fuel": "d", "tank_l": 45, "consumption": [[45, 5.2], [75, 4.1],
[100, 4.5], [999, 5.6]], "brands": ["SHELL", "AVIN"]}.
"""
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

CAR_FILE = "car.json"


@dataclass(frozen=True)
class Car:
    name: str = "a typical compact petrol car"
    fuel: str = "u95"  # a fuel code of the price feed: u95, u100, d, lpg…
    tank_l: float = 50.0
    reserve_l: float = 7.0  # never plan to drive below this, about where the low-fuel light comes on
    # Litres per 100 km by a stretch's average speed: [up to km/h, litres], fastest last.
    consumption: list[list[float]] = field(default_factory=lambda: [[45, 7.5], [75, 5.8], [100, 6.3], [999, 7.6]])
    brands: list[str] = field(default_factory=list)  # fuel brands by preference; none: every brand alike

    def litres_per_100km(self, kmh: float) -> float:
        for up_to_kmh, litres in self.consumption:
            if kmh <= up_to_kmh:
                return litres
        return self.consumption[-1][1]


def load_car(data_folder: Path) -> Car:
    path = data_folder / CAR_FILE
    if not path.exists():
        return Car()
    known = asdict(Car()).keys()
    overrides = {key: value for key, value in json.loads(path.read_text()).items() if key in known}
    return Car(**overrides)
