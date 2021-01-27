import networkx as nx
import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt
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
        node = ox.get_nearest_node(self.graph, (location['y'], location['x']), method='euclidean')
        return node

    def path_to_locations(self, node_path):
        points = self.nodes.loc[node_path]
        lengths = np.cumsum([0]+[self.graph[u][v][0]['length'] for u, v in zip(node_path, node_path[1:])])

        locations = {'x': points.geometry.values.x, 'y':points.geometry.values.y, 'd': lengths}
        return locations






# if __name__ == "__main__":
#     m = Map("Milanowek, Poland")
#     goals = m.get_random_nodes(6)
#
#     print(goals[0] in m.graph.nodes)
#
#     print(goals)
#
#     planer = Planner(m)
#     planer.set_goals(goals)
#     print(planer.goal_matrix)
#
#     node_path = nx.shortest_path(planer.world_map.graph, goals[0], goals[1])
#     path = planer.get_full_path()
#     goal_points = planer.world_map.nodes_locations(planer.goal_nodes)
#     print(path)
#
#     fig, ax = ox.plot_graph(graph, show=False, close=False)
#     ax.plot(path[:,0], path[:,1])
#     ax.scatter(goal_points['x'], goal_points['y'])
#     plt.show()



