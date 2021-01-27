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
        self.waiting_times = []

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

    def set_goals(self, goals):
        self.goal_nodes = [goal_node for goal_node in goals.keys()]
        self.waiting_times = [goals[node] for node in self.goal_nodes]
        self._goals_matrix()

    def optimal_permutation(self):
        return solve_tsp_dynamic_programming(self.goal_matrix)

    def schedule(self, permutation, speed=1.0, current_location = None):
        start_time = 0
        schedule = []
        current_goal = permutation[0]
        if current_location is not None:
            start_node = self.world_map.locate_nearset_node(current_location)
            start_time += nx.shortest_path_length(self.world_map.graph, start_node, self.goal_nodes[current_goal]) / speed
        for p in permutation:
            start_time += self.goal_matrix[current_goal, p] / speed
            current_goal = p
            schedule.append([self.goal_nodes[current_goal], start_time, start_time + self.waiting_times[p]])
            start_time += self.waiting_times[p]
        return schedule


    def get_path(self,current_location, end_goal, speed=1.0):
        start_node = self.world_map.locate_nearset_node(current_location)
        path = self.path_between_nodes(start_node, self.goal_nodes[end_goal], speed)
        return path

    def generate_full_path(self, current_location, schedule, speed = 1.0):
        full_path = []
        current_goal = schedule[0][0]
        eta = schedule[0][1]
        start_node = self.world_map.locate_nearset_node(current_location)
        path = self.path_between_nodes(start_node, current_goal)
        full_path.append(path)
        start_time = schedule[0][-1]
        for appointment in schedule[1:]:
            target_goal = appointment[0]
            path = self.path_between_nodes(current_goal, target_goal, speed)
            path[:, -1] += start_time
            full_path.append(path)
            start_time = appointment[-1]
            current_goal = target_goal
        # print(full_path)
        return np.concatenate(full_path)




