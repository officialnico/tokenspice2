"""
Model initial state.
"""

# Dependences

import random
import uuid
import numpy as np
from typing import Tuple, List, Dict
from itertools import cycle
from enum import Enum

import matplotlib.pyplot as plt
import matplotlib.animation as animation

### World size
N = 200
M = 20
INITIAL_CROWD = 1

### Initial agent count
PERSON_COUNT = 300
ATTRACTION_COUNT = 10
PROPOSAL_COUNT = 10

MAX_ATTRACTION_CAPACITY = 5
MAX_TIMESTEPS = 20
MAX_DURATION = 5


## yet to be implemented
agent_probabilities = [0.7,0.75,0.8,0.85,0.9,0.95]

class Person(Enum):
    parent = 1
    child = 2
    youngster = 3
    aged = 4
    single = 5
    groupie = 6

class Behaviour(Enum):
    clumper = 1
    conformist = 2
    bowler = 3
    maverick = 4
    wallhugger = 5

class Proposal(Enum):
    shop = 1
    service = 2
    art = 3
    sport = 4
    infrastructure = 5


## Helper functions

def select_agent_behaviour(person_id, behaviour_id) -> tuple:
    return (Person(person_id), Behaviour(behaviour_id))


def get_nearest_attraction_location(position: tuple, bucket_list: dict) -> tuple:
    distance_to_attraction = 1000
    nearest_location = (0,0)
    for label in bucket_list.keys():
        attraction_location = bucket_list[label]
        x = attraction_location[0]
        y = attraction_location[1]
        distance = np.abs(x - position[0]) + np.abs(y - position[1])
        if distance < distance_to_attraction:
            distance_to_attraction = distance
            nearest_location = attraction_location
        else:
            continue
    return nearest_location

def new_person_agent(agent_type: str, location: Tuple[int, int], person_type: Tuple[int, int], attractions: [str] = [''],
              nearest_attraction_location: Tuple[int, int] = (0,0), money: int=1000, queued: bool=False, locked: bool=False, stay: int=0) -> dict:
    agent = {'type': agent_type,
             'location': location,
             'person_type': person_type,
             'money': money,
             'bucket_list' : attractions,
             'proposal_preferences': [random.choice(range(1,6)), random.choice(range(1,6)), random.choice(range(1,6))],
             'nearest_attraction_location': nearest_attraction_location,
             'queued': queued,
             'locked': locked,
             'stay': stay,
             'probability': random.choice(agent_probabilities)}
    return agent

def new_attraction_agent(agent_type: str, location: Tuple[int, int],
               waiting_line: [str] = [''], money: int=0, capacity: int=MAX_ATTRACTION_CAPACITY) -> dict:
    agent = {'type': agent_type,
             'location': location,
             'money': money,
             'waiting_line': waiting_line,
             'capacity': capacity}
    return agent

def new_proposal_agent(agent_type: str, proposal_type: Proposal, location: Tuple[int, int],
               title: str = 'Proposal', money: int=0, votes_yes: int=0, votes_no: int=0, opened: bool = True) -> dict:
    agent = {'type': agent_type,
             'proposal_type': proposal_type,
             'location': location,
             'money': money,
             'title': title,
             'votes_yes': votes_yes,
             'votes_no': votes_no,
             'timesteps': 0,
             'open': opened,
             'passed': False
             }
    return agent

def select_attractions(attrs: dict, number: int) -> dict:
    selected = {}
    times = number
    while times > 0:
        try:
            k, v = random.choice(list(attrs.items()))
            selected[k] = v
            attrs.pop(k)
            times -= 1
        except IndexError:
            print('item is popped')
            break
    return selected


def generate_agents(available_locations: List[Tuple[int, int]],
                    n_attractions: int,
                    n_person: int, n_proposals) -> Dict[str, dict]:
    initial_agents = {}
    person_queue = ['person'] * n_person
    attraction_queue = ['attraction'] * n_attractions
    proposal_queue = ['proposal'] * n_proposals
    i = 0
    j = 0
#   attractions
    for agent_type in attraction_queue:
        i = i + 1
        if i > len(attraction_queue)/2:
            location = (20 + 30 * j, 15)
            j = j + 1
        else:
            location = (20 + 30 * i, 5)
        print(location)
        available_locations.remove(location)
        created_agent = new_attraction_agent(agent_type, location, {'test': (0,0)})
        initial_agents[uuid.uuid4()] = created_agent


#   people
    attraction_agents = initial_agents.copy()
    attractions = {k: v['location'] for k, v in attraction_agents.items()}
    for agent_type in person_queue:
        person_type = select_agent_behaviour(random.choice([e.value for e in Person]), random.choice([e.value for e in Behaviour]) )
        location = random.choice(available_locations)
        available_locations.remove(location)
#       select attractions (3 in total)

        selected_attractions = select_attractions(attractions.copy(), 7)
        nearest_attraction_location = get_nearest_attraction_location(location, selected_attractions)
        created_agent = new_person_agent(agent_type, location, person_type, selected_attractions.copy(), nearest_attraction_location)
        # print(created_agent)
        # print("\n")
        initial_agents[uuid.uuid4()] = created_agent


    # #proposals
    # i = 0
    # j = 0
    # for agent_type in proposal_queue:
    #     i = i + 1
    #     if i > len(proposal_queue)/2 - 1:
    #         location = (20 + 30 * j, 17)
    #         j = j + 1
    #     else:
    #         location = (20 + 30 * i, 7)
    #     created_agent = new_proposal_agent(agent_type, random.choice(range(1,6)), location)
    #     initial_agents[uuid.uuid4()] = created_agent


    return initial_agents


## Generate initial state

sites = np.zeros((N, M)) * INITIAL_CROWD
locations = [(n, m) for n in range(N) for m in range(M)]
initial_agents = generate_agents(locations, ATTRACTION_COUNT, PERSON_COUNT, PROPOSAL_COUNT)

persons = {k: v for k, v in initial_agents.items() if v['type'] == 'person' }
attrs = {k: v for k, v in initial_agents.items() if v['type'] == 'attraction' }
proposals = {k: v for k, v in initial_agents.items() if v['type'] == 'proposal' }
votes = {k: [] for k,v in initial_agents.items() if v['type'] == 'proposal' }

attr = list(attrs.values())[0]
person = list(persons.values())[0]
# proposal = list(proposals.values())[2]

# voted = list(votes.keys())
print(person)

# label = list(person['bucket_list'].keys())[0]
# person['bucket_list'].pop(label)
# print(list(person['bucket_list'].keys()))

genesis_states = {
    'agents': initial_agents,
    'sites': sites,
    'voted': votes
}
