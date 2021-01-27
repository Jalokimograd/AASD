import time
from spade import agent
import matplotlib.pyplot as plt
from matplotlib import animation

from EnvironmentManagerAgent import EnvironmentManagerAgent
from MobileAgent import MobileAgent
from Map import Map
import osmnx as ox
import random

PLACE_NAME = "Brwinow, Poland"
AGENTS_NUMBER = 4
GOALS = 10
GOALS_PER_CAPITA = 4
MAX_WAITING_TIME = 20

def make_random_goals(goals_set, n_goals, max_waiting_time):
    goal_nodes = random.sample(goals_set, n_goals)
    return {goal_node: random.randrange(1, max_waiting_time) for goal_node in goal_nodes}


def main():
    world_map = Map(PLACE_NAME)
    staring_points = world_map.get_random_nodes(AGENTS_NUMBER)
    goals_subset = world_map.get_random_nodes(GOALS)
    # ========== create agents ==========================================================================================================
    environment_manager_agent: EnvironmentManagerAgent = EnvironmentManagerAgent("environmentmanager@localhost", "environmentmanager")
    mobile_agents = [MobileAgent("mobileagent" + str(num) + "@localhost", "mobileagent" + str(num), world_map) for num in range(AGENTS_NUMBER)]

    # ========== start agents ===========================================================================================================
    environment_manager_agent.start()
    for i, agent in enumerate(mobile_agents):
        agent.set_starting_localization(agent.world_map.node_location(staring_points[i]))
        random_goals = make_random_goals(goals_subset, GOALS_PER_CAPITA, MAX_WAITING_TIME)
        agent.set_goals(random_goals)
        agent.start()

    rand_goals = make_random_goals(goals_subset, GOALS_PER_CAPITA, MAX_WAITING_TIME)
    print(rand_goals)
    print([goal for goal in rand_goals.keys()])

    environment_manager_agent.web.start(hostname="127.0.0.1", port="8888")

    fig, ax = ox.plot_graph(world_map.graph, show=False, close=False)
    sc = ax.scatter([], [], marker='.', c='r')
    for agent in mobile_agents:
        ax.plot(agent.current_path[:, 0], agent.current_path[:, 1])

    time.sleep(1)
    while environment_manager_agent.is_alive():
        try:
            x, y = environment_manager_agent.get_agent_points()
            ax.scatter(x, y, marker='+', c='r')
            # sc.set_data(x, y)
            plt.pause(0.01)
            # time.sleep(0.1)
        except KeyboardInterrupt:
        # except:
            environment_manager_agent.stop()
            for agent in mobile_agents: agent.stop()
            break
    print("FINISH")


if __name__ == "__main__":
    main()