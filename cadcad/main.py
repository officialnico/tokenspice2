# Dependences
from time import time
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Experiments
import run

start_time = time()
experiments = run.run()
end_time = time()
print("Execution in {:.1f}s".format(end_time - start_time))

# Get the ABM results
agent_ds = experiments.dataset[0].agents
site_ds = experiments.dataset[0].sites
timesteps = experiments.dataset[0].timestep


# N = 300

# timesteps = np.arange(1, N+1, 1)

# # make list of agents
# agents = list(person_data(1).keys())

# names = [str(agent) for agent in agents]
# names

# # make figure
# fig_dict = {
#     "data": [],
#     "layout": {},
#     "frames": []
# }

# # fill in most of layout
# fig_dict["layout"]["xaxis"] = {"range": [0, 200], "title": "Position X"}
# fig_dict["layout"]["yaxis"] = {"range": [0, 20], "title": "Position Y"}
# fig_dict["layout"]["hovermode"] = "closest"
# fig_dict["layout"]["updatemenus"] = [
#     {
#         "buttons": [
#             {
#                 "args": [None, {"frame": {"duration": 100, "redraw": False},
#                                 "fromcurrent": True, "transition": {"duration": 100,
#                                                                     "easing": "quadratic-in-out"}}],
#                 "label": "Play",
#                 "method": "animate"
#             },
#             {
#                 "args": [[None], {"frame": {"duration": 0, "redraw": False},
#                                   "mode": "immediate",
#                                   "transition": {"duration": 0}}],
#                 "label": "Pause",
#                 "method": "animate"
#             }
#         ],
#         "direction": "left",
#         "pad": {"r": 10, "t": 87},
#         "showactive": False,
#         "type": "buttons",
#         "x": 0.1,
#         "xanchor": "right",
#         "y": 0,
#         "yanchor": "top"
#     }
# ]

# sliders_dict = {
#     "active": 0,
#     "yanchor": "top",
#     "xanchor": "left",
#     "currentvalue": {
#         "font": {"size": 20},
#         "prefix": "Timestep:",
#         "visible": True,
#         "xanchor": "right"
#     },
#     "transition": {"duration": 100, "easing": "cubic-in-out"},
#     "pad": {"b": 10, "t": 50},
#     "len": 0.9,
#     "x": 0.1,
#     "y": 0,
#     "steps": []
# }

# # # # make data

# timestep = 1
# for attr in attraction_location(1).keys():
#     x,y = attraction_location(timestep).get(attr)
#     capacity = attraction_capacity(timestep).get(attr)
#     data_dict = {
#         "x" : [x],
#         "y" : [y],
#         "mode": "markers+text",
#         "text": [capacity],
#         "name": str(attr),
#         "marker_symbol": "square-open",
#         "marker_line_color": "midnightblue", 
#         "marker_color": "lightskyblue", 
#         "marker_line_width": 2, 
#         "marker_size": 15 
#     }
#     fig_dict["data"].append(data_dict)

# for proposal in proposal_location(1).keys():
#     x,y = proposal_location(timestep).get(proposal)
#     votes = proposal_votes(timestep).get(proposal)
#     money = proposal_money(timestep).get(proposal)
    
#     data_dict = {
#         "x" : [x],
#         "y" : [y],
#         "mode": "markers+text",
#         "text": [str(votes[0]) + " | " + str(votes[1]) + " --> € " + str(money)],
#         "name": str(proposal),
#         "marker_symbol": "square-open",
#         "marker_line_color": "red", 
#         "marker_color": "red", 
#         "marker_line_width": 2, 
#         "marker_size": 20 
#     }
#     fig_dict["data"].append(data_dict)

# timestep = 1
# for agent in agents:
#     x,y = person_data(timestep).get(agent)
#     data_dict = {
#         "x" : [x],
#         "y" : [y],
#         "mode": "markers",
#         "text": str(agent),
#         "name": str(agent)
#     }
#     fig_dict["data"].append(data_dict)

# start_time = time()

# # make frames
# for timestep in timesteps:
#     if timestep % 25 == 0:
#         print(timestep)
#     frame = {"data": [], "name": str(timestep)}
    
#     for attr in attraction_location(timestep).keys():
#         x,y = attraction_location(timestep).get(attr)
#         capacity = attraction_capacity(timestep).get(attr)
#         data_dict = {
#             "x" : [x],
#             "y" : [y],
#             "mode": "markers+text",
#             "text": [capacity],
#             "name": str(attr),
#             "marker_symbol": "square-open",
#             "marker_line_color": "midnightblue", 
#             "marker_color": "lightskyblue", 
#             "marker_line_width": 2, 
#             "marker_size": 17 
#         }
#         frame["data"].append(data_dict) 


#     for proposal in proposal_location(timestep).keys():
#         x,y = proposal_location(timestep).get(proposal)
#         votes = proposal_votes(timestep).get(proposal)
#         money = proposal_money(timestep).get(proposal)
#         data_dict = {
#             "x" : [x],
#             "y" : [y],
#             "mode": "markers+text",
#             "text": [str(votes[0]) + " | " + str(votes[1]) + " --> € " + str(money)],
#             "name": str(proposal),
#             "marker_symbol": "square-open",
#             "marker_line_color": "red", 
#             "marker_color": "red", 
#             "marker_line_width": 2, 
#             "marker_size": 20 
#         }
#         frame["data"].append(data_dict) 


#     agents = list(person_data(timestep).keys())
#     for agent in agents:
#         x,y = person_data(timestep).get(agent)
#         money = persons_money(timestep).get(agent)
#         data_dict = {
#             "x" : [x],
#             "y" : [y],
#             "mode": "markers+text",
#             "text": [],
#             "name": str(agent)
#         }
#         frame["data"].append(data_dict)


        
#     fig_dict["frames"].append(frame)
#     slider_step = {"args": [
#         [timestep],
#         {"frame": {"duration": 100, "redraw": False},
#          "mode": "immediate",
#          "transition": {"duration": 100}}
#     ],
#         "label": str(timestep),
#         "method": "animate"}
#     sliders_dict["steps"].append(slider_step)
    
# fig_dict["layout"]["sliders"] = [sliders_dict]

# fig = go.Figure(fig_dict)

# end_time = time()
# print("Execution in {:.1f}s".format(end_time - start_time))


# fig.show()