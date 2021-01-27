import time
from spade import agent
import matplotlib.pyplot as plt
from matplotlib import animation

from EnvironmentManagerAgent import EnvironmentManagerAgent
from MobileAgent import MobileAgent
from Map import Map
import osmnx as ox
import random

PLACE_NAME = "Milanowek, Poland"
AGENTS_NUMBER = 4
GOALS = 10
GOALS_PER_CAPITA = 4

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
        agent.set_goals(random.sample(goals_subset, GOALS_PER_CAPITA))
        agent.start()
        l = world_map.node_location(staring_points[i])
        print(staring_points[i])
        print(world_map.locate_nearset_node(l))
        print(l)


    # environment_manager_agent.web.start(hostname="127.0.0.1", port="10000")

    fig, ax = ox.plot_graph(world_map.graph, show=False, close=False)
    sc = ax.scatter([], [])

    time.sleep(1)
    while environment_manager_agent.is_alive():
        try:
            x, y = environment_manager_agent.get_agent_points()
            ax.scatter(x, y, marker='.', c='r')
            plt.pause(0.1)
            # time.sleep(0.1)
        # except KeyboardInterrupt:
        except:
            environment_manager_agent.stop()
            for agent in mobile_agents: agent.stop()
            break
    print("FINISH")


if __name__ == "__main__":
    main()