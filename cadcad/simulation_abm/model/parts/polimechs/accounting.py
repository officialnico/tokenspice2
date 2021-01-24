import random

from ....model.SimState import SimState

def p_accounting(params, substep, state_history, prev_state):
    """
    Update the KPIs.
    """
    step = prev_state['timestep']
    print(f'p_accounting, {step} - {substep}')

    global_state = prev_state['global_state']

    global_state.takeStep()
    # print(f'State: {global_state.OCEANprice()}')
    stats_delta = global_state

    return {'stats_delta': stats_delta }

def s_accounting(params, substep, state_history, prev_state, policy_input):
    updated_stats = policy_input['stats_delta']
    return ('global_state', updated_stats)


