"""
Model logic structure.
"""

from .parts.polimechs.consuming import *
from .parts.polimechs.publishing import *
from .parts.polimechs.optimizing import *
from .parts.polimechs.accounting import *


partial_state_update_block = [
    {
        'policies': {
            'consume_datasets': p_consume_datasets,
            'accounting': p_accounting,
        },
        'variables': {
            'agents': s_consume_datasets,
            'global_state': s_accounting
        }
    },
    {
        'policies': {
            'publish_datasets': p_publish_datasets,
        },
        'variables': {
            'agents': s_publish_datasets,
        }
    },
    {
        'policies': {
            'optimize': p_optimizing,
        },
        'variables': {
            'agents': s_optimizing,
        }
    },


]
