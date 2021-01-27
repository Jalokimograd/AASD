import numpy as np
import networkx as nx
from python_tsp.heuristics import solve_tsp_simulated_annealing
from python_tsp.exact import solve_tsp_dynamic_programming

from Map import Map


class Planner:
    def __init__(self, world_map: Map):
        self.world_map = world_map
        self.goal_nodes = []
        self.goal_matrix = []

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

    def optimal_permutation(self):
        return solve_tsp_dynamic_programming(self.goal_matrix)

    def evaluate_permutation(self, permutation):
        pass


    def get_path(self,current_location,end_goal, speed=1.0):
        # finish_time = 0
        strart_node = self.world_map.locate_nearset_node(current_location)
        path = self.path_between_nodes(strart_node, self.goal_nodes[end_goal], speed)
        # path[:, -1] += finish_time
        # finish_time = path[-1, -1]
        return path