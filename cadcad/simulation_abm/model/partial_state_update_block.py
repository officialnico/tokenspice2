"""
Model logic structure.
"""


# from .parts.environment.food_regeneration import *
from .parts.agents.consuming import *


partial_state_update_block = [
    {
        'policies': {
            'consume_datasets': p_consume_datasets,
        },
        'variables': {
            'agents': s_agent_location,

        }
    },
    {
        'policies': {
            'vote_agent': p_voting,
        },
        'variables': {
            'agents': s_voting,
        }
    },
]
