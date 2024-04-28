import os, json, requests
import networkx as nx
import osmnx as ox
from shapely.geometry import mapping

class EventsAPI:

    def __init__(self, api_key, limit=None):

        self.api_key = api_key
        self.limit = limit
    
    def make_api_call(self, base_url):

        params = dict(
            api_key= self.api_key,
            limit= self.limit,
            format='json')

        response = requests.get(
            url = base_url,
            params = params
        )
        