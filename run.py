import os, json, requests
import networkx as nx
import osmnx as ox
from shapely.geometry import mapping
from DataStructure import *


if __name__ == "__main__":

    with open('credentials.json', 'r') as fp:
        credentials = json.load(fp)

    api = SFBayAPI(api_key=credentials['api_key'])
    road_network = RoadNetwork(graphml_path='graph_full.graphml')

    real_time_data = dict()
    
    # Load events

    events_data = api.make_api_call(api.EVENTS_URL)
    real_time_data.update(dict(events=events_data['events']))

    # Load events

    toll_data = api.make_api_call(api.TOLL_URL)
    real_time_data.update(dict(toll_data=toll_data['toll-programs']))

    


