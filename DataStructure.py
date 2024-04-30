import os, json, requests
import networkx as nx
import osmnx as ox
from shapely.geometry import mapping


def create_graph(north, south, east, west):
    try:
        G = ox.graph_from_bbox(north=north, south=south, east=east, west=west, network_type='all')
        if G is None or G.number_of_nodes() == 0:
            return None
        return G
    except Exception as e:
        print(f"Failed to fetch data for box with bounds ({north}, {south}, {east}, {west}): {e}")
        return None


# Generate bounding boxes (assuming this function is already defined)
def generate_sub_boxes(north, south, east, west, num_lat_splits, num_lon_splits):
    lat_step = (north - south) / num_lat_splits
    lon_step = (east - west) / num_lon_splits
    sub_boxes = []
    for i in range(num_lat_splits):
        for j in range(num_lon_splits):
            sub_north = north - i * lat_step
            sub_south = north - (i + 1) * lat_step
            sub_west = west + j * lon_step
            sub_east = west + (j + 1) * lon_step
            sub_boxes.append((sub_north, sub_south, sub_east, sub_west))
    return sub_boxes



class Event:
    
    def __init__(self, id, status, event_type, geography, *ignore_args, **ignore_kwargs):

        self.id = id
        self.status = status
        self.event_type = event_type
        self.coordinates = geography.get('coordinates', [None, None])


class RoadNetwork:

    BAY_AREA_COORDINATES = [39.517, 36.031, -119.163, -125.546]
    
    def __init__(self, use_graphml = True, graphml_path = None):

        if use_graphml is False:
            sub_boxes = generate_sub_boxes(north, south, east, west, 20, 20)
            results = []

            for box in tqdm(sub_boxes):
                graph = create_graph(*box)
                if graph is not None:
                    results.append(graph)

            self.graph = nx.compose_all(results)
            ox.io.save_graphml(self.graph, 'graph_save.graphml')
        
        elif use_graphml is True:
            assert graphml_path is not None
            self.graph = ox.io.load_graphml(graphml_path)
        
    
    def update_graph_with_events(self, real_time_data:dict):
        
        closures = set()

        for event in real_time_data['events']:

            road_name = event['roads'][0]['from']
            degree = 1 if event['roads'][0]['state'] == "SOME_LANES_CLOSED" else 2
            closures.update({
                'name':road_name, 
                'degree':degree
                })
                
        tolls = None
        closure_weight = None
        toll_weight = None

        for start_point, endpoint, key, road_info in self.graph.edges(keys=True, data=True):

            road_name = road_info.get('name', None)

            if road_name in closures and closures[road_name]:
                road_info['weight'] = closure_weight*closure_degrees
            
            if road_name in tolls:
                road_info['weight'] += toll_weight*tolls['avg_rate']
            

    def calculate_k_best_routes(self, start, end, k):
        return ox.routing.k_shortest_paths(self.graph, start, end, weight='weight')        


    def show_results():
        pass

class SFBayAPI:

    EVENTS_URL = "http://api.511.org/traffic/events"
    TOLL_URL = "http://api.511.org/toll/programs"
    WORK_ZONE_URL = "http://api.511.org/traffic/wzdx"

    def __init__(self, api_key, limit=20):

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

        data = None

        if response.status_code == 200:
            json_string = response.content.decode('utf-8-sig')
            data = json.loads(json_string)
        
        
        return data