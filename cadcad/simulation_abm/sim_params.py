"""
Simulation parameters.
"""

from .model.parts.util.constants import S_PER_DAY, S_PER_HOUR, S_PER_YEAR

MAX_YEARS = 2
SIMULATION_TIME_STEPS = int(MAX_YEARS * S_PER_YEAR/S_PER_HOUR + 2)
