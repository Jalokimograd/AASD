import time
from spade import agent

from EnvironmentManagerAgent import EnvironmentManagerAgent
from MobileAgent import MobileAgent


AGENTS_NUMBER = 3

def main():
    # ========== create agents ==========================================================================================================
    environment_manager_agent: EnvironmentManagerAgent = EnvironmentManagerAgent("environmentmanager@localhost", "environmentmanager")
    mobile_agents = [MobileAgent("mobileagent" + str(num) + "@localhost", "mobileagent" + str(num)) for num in range(AGENTS_NUMBER)]

    # ========== start agents ===========================================================================================================
    environment_manager_agent.start()
    for agent in mobile_agents: agent.start()

    time.sleep(1)
    while environment_manager_agent.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            environment_manager_agent.stop()
            for agent in mobile_agents: agent.stop()
            break
    print("FINISH")


if __name__ == "__main__":
    main()