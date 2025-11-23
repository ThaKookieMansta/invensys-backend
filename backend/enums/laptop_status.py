from enum import Enum

class LaptopStatus(str, Enum):
    available = "Available"
    allocated = "Allocated"
    under_repair = "Under Repair"
    retired = "Retired"
    lost = "Lost"