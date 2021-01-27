from json import dumps, loads
import asyncio
from spade import agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message

from Templates import ACTUALIZE_INFORMATION, BROADCAST

range = 0.0001

class EnvironmentManagerAgent(agent.Agent):
    agent_name = "EnvironmentManagerAgent"
    agents_list = {}    # słownik wszystkich agentów {"name": localization, ...}

    # Odebranie informacji aktualizującej od agenta
    class ActualizationReceive(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                info = loads(msg.body)
                # zaktualizowanie czasu od ostatniego komunikatu od danego sąsiada i aktualizacja informacji o jego ścieżce
                agent_name = info["source_name"]
                agent_localization = info["localization"]

                self.agent.agents_list[agent_name] = {}
                self.agent.agents_list[agent_name]["localization"] = agent_localization

                print(f"[{self.agent.agent_name}] receive info from: {agent_name} {agent_localization}")

    # Odebranie informacji aktualizującej od agenta
    class TransmitBroadcast(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
            
                info = loads(msg.body)
                # zaktualizowanie czasu od ostatniego komunikatu od danego sąsiada i aktualizacja informacji o jego ścieżce
                agent_name = info["source_name"]
                agent_localization = info["localization"]

                print(f"[{self.agent.agent_name}] transmit broadcast info from: {agent_name}")
                for key, body in self.agent.agents_list.items():
                    if(key == agent_name): continue
                    xx = body["localization"]["x"] - agent_localization["x"]
                    yy = body["localization"]["y"] - agent_localization["y"]
                    distance = xx ** 2 + yy ** 2
                    print(f"distance: {distance}")
                    if distance < range ** 2:
                        msg = Message(
                            to = key,
                            metadata = dict(performative="broadcast"),
                            body = msg.body
                        )
                        print(f"to: {key}")
                        await self.send(msg)


    class PrintBeh(PeriodicBehaviour):
        async def run(self):
            print(f"[{self.agent.agent_name}] Actualize informations of environment Manager")

    def get_agent_points(self):
        x = []
        y = []
        for agent in self.agents_list.values():
            x.append(agent['localization']['x'])
            y.append(agent['localization']['y'])
        return x, y
                     
    async def setup(self):
        print("Environment Manager created")

        self.add_behaviour(self.ActualizationReceive(), template = ACTUALIZE_INFORMATION)
        self.add_behaviour(self.TransmitBroadcast(), template = BROADCAST)
        #self.add_behaviour(self.PrintBeh(period=(5)))