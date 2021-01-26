import networkx as nx
import osmnx as ox
import numpy as np
# from shapely.geometry import LineString, mapping
# from ipyleaflet import *
import matplotlib.pyplot as plt
from python_tsp.heuristics import solve_tsp_simulated_annealing
import random

class Map:
    def __init__(self, place_name):
        self.graph = ox.graph_from_place(place_name)
        self.nodes, self.edges = ox.graph_to_gdfs(self.graph)

    def get_random_nodes(self, k):
        return random.sample(self.graph.nodes, k)

    def node_location(self, node_id):
        location = self.nodes.loc[node_id]
        return {'x': location.x, 'y': location.y}

    def nodes_locations(self, nodes):
        points = self.nodes.loc[nodes]
        locations = {'x': points.geometry.values.x, 'y': points.geometry.values.y}
        return locations

    def locate_nearset_node(self, location):
        node = ox.get_nearest_node(graph, (location['x'], location['y']))
        return node

    def path_to_locations(self, node_path):
        points = self.nodes.loc[node_path]
        lengths = np.cumsum([0]+[self.graph[u][v][0]['length'] for u, v in zip(node_path, node_path[1:])])

        locations = {'x': points.geometry.values.x, 'y':points.geometry.values.y, 'd': lengths}
        return locations



class Planner:
    goal_nodes = []
    goal_matrix = []
    def __init__(self, world_map: Map):
        self.world_map = world_map

    def path_between_nodes(self, start_node, target_node, speed=1.0):
        path = nx.shortest_path(self.world_map.graph, start_node, target_node, weight='length')
        locations = self.world_map.path_to_locations(path)
        path = np.stack([locations['x'], locations['y'], locations['d']]).T
        path[:, -1] /= speed
        return path

    def _goals_matrix(self):
        N = len(self.goal_nodes)
        self.goal_matrix = np.zeros((N,N))
        for i in range(N):
            for j in range(i):
                self.goal_matrix[j, i] = nx.shortest_path_length(self.world_map.graph, self.goal_nodes[i], self.goal_nodes[j], weight='length')
                self.goal_matrix[i, j] = self.goal_matrix[j, i]

    def set_goals(self, goal_nodes):
        self.goal_nodes = goal_nodes
        self._goals_matrix()

    def get_full_path(self, speed=1.0):
        permutation, distance = solve_tsp_simulated_annealing(self.goal_matrix)
        full_path = []
        finish_time = 0
        for u, v in zip(permutation, permutation[1:]):
            path = self.path_between_nodes(self.goal_nodes[u], self.goal_nodes[v], speed)
            path[:, -1] += finish_time
            finish_time = path[-1, -1]
            full_path.append(path)
        return np.concatenate(full_path, axis=0)





place_name = "Milanowek, Poland"
graph = ox.graph_from_place(place_name)


localization = (60.16607, 24.93116)
target = (60.16607, 30.93116)

nearest_node = ox.get_nearest_node(graph, localization)
target_node = ox.get_nearest_node(graph, target)
print(nearest_node)

length, shortest_path = nx.single_source_dijkstra(graph, nearest_node, target_node, weight='length')

nodes, edges = ox.graph_to_gdfs(graph)
points = nodes.loc[shortest_path]
lengths = edges


if __name__ == "__main__":
    m = Map("Milanowek, Poland")
    goals = m.get_random_nodes(6)

    print(goals[0] in m.graph.nodes)

    print(goals)

    planer = Planner(m)
    planer.set_goals(goals)
    print(planer.goal_matrix)

    node_path = nx.shortest_path(planer.world_map.graph, goals[0], goals[1])
    path = planer.get_full_path()
    goal_points = planer.world_map.nodes_locations(planer.goal_nodes)
    print(path)

    fig, ax = ox.plot_graph(graph, show=False, close=False)
    ax.plot(path[:,0], path[:,1])
    ax.scatter(goal_points['x'], goal_points['y'])
    plt.show()



