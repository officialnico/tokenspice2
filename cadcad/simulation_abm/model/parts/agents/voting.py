from ..utils import votes_for_money, vote
from ..location import is_neighbor

def p_voting(params, substep, state_history, prev_state):
    """
    Vote if agents are nearby proposal location.
    """
    print('p_voting')
    agents = prev_state['agents']
    voted = prev_state['voted']
    voting_persons = {k: v for k, v in agents.items() 
            if v['type'] == 'person' and v['locked'] == False and v['money'] > 10}
    proposals = {k: v for k, v in agents.items() 
            if v['type'] == 'proposal' and v['open'] == True }
    updated_proposal_open = {}
    updated_proposal_timesteps = {}
    updated_proposal_passed = {}
    updated_proposal_vote = {}
    updated_agent_money = {}
    updated_voted = {}

    # for proposal_label, proposal_properties in proposals.items():
    #     timestep = proposal_properties['timesteps']
    #     proposal_money = proposal_properties['money']
    #     timestep += 1
    #     if timestep > params['max_timesteps']:
    #         print(proposal_properties)
    #         updated_proposal_open[proposal_label] = False
    #         updated_proposal_timesteps[proposal_label] = 0
    #         updated_proposal_passed[proposal_label] = (True, False)[proposal_properties['votes_yes'] - proposal_properties['votes_no'] > 0]
    #     else:
    #         updated_proposal_timesteps[proposal_label] = timestep
    #         voting_done = voted[proposal_label]
    #         eligible_voting_persons = {k: v for k, v in voting_persons.items() if k not in voting_done}
    #         for label, properties in eligible_voting_persons.items():
    #             probability = properties['probability']
    #             proposal_preferences = properties['proposal_preferences']
    #             location = properties['location']
    #             voting_money = properties['money']
    #             if is_neighbor(location, proposal_properties['location'], 3):
    #                 money, vote_yes, vote_no = vote(proposal_properties['proposal_type'], proposal_preferences, voting_money)
    #                 updated_proposal_vote[proposal_label] = (vote_yes, vote_no)
    #                 print("Vote: (Yes,No): ", updated_proposal_vote[proposal_label])
    #                 updated_agent_money[proposal_label] = proposal_money + money
    #                 updated_agent_money[label] = voting_money - money
    #                 updated_voted[proposal_label] = voting_done.append(label)
    #                 print("Voting at " + str(proposal_label) + " done for: " + str(voting_done))
    #             else:
    #                 continue

    return {'update_agent_proposal_timesteps': updated_proposal_timesteps,
            'update_agent_proposal_open': updated_proposal_open,
            'update_agent_proposal_passed': updated_proposal_passed,
            'update_agent_proposal_vote': updated_proposal_vote,
            'update_agent_money': updated_agent_money,
            'update_agent_voted': updated_voted}

def s_voting(params, substep, state_history, prev_state, policy_input):
    updated_agents = prev_state['agents'].copy()
    updated_voted = prev_state['voted'].copy()
    for label, timesteps in policy_input['update_agent_proposal_timesteps'].items():
        updated_agents[label]['timesteps'] = timesteps
    for label, opened in policy_input['update_agent_proposal_open'].items():
        updated_agents[label]['open'] = opened
    for label, passed in policy_input['update_agent_proposal_passed'].items():
        updated_agents[label]['passed'] = passed
    for label, vote in policy_input['update_agent_proposal_vote'].items():
        updated_agents[label]['votes_yes'] = vote[0]
        updated_agents[label]['votes_no'] = vote[1]
    for label, money in policy_input['update_agent_money'].items():
        updated_agents[label]['money'] = money   
    for label, voted in policy_input['update_agent_voted'].items():
        updated_voted[label] = voted   
    return ('agents', updated_agents)
