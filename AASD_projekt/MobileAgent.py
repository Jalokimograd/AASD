import asyncio
import random
from json import dumps, loads
from datetime import datetime, timedelta

from spade import agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message

from Templates import BROADCAST


class MobileAgent(agent.Agent):
    agent_name: str
    localization = {}       # lokalizacja {"x": .., "y": ..}
    neighbors = {}          # sąsiedzi {"name": {"path": .., "time": .., "localization": ..}, ...}
    path = []               # ścieżka [[x, y, time], ... ]


    # Informacja o położeniu do EnvironmentManager'a
    class ActualizationInfoInEnvironment(PeriodicBehaviour):
        async def run(self):
            msg = Message(
                to = "environmentmanager@localhost",
                metadata = dict(performative="environment_actualize"),
                body = dumps({"source_name": self.agent.agent_name,
                              "localization": self.agent.localization})
            )
            print(f"[{self.agent.agent_name}] Send informations actualization to Environment manager")
            await self.send(msg)

    # Informacja Broadcast jest wysyłana do EnvironmentManager'a, który wyśle ją do wszystkich urządzeń w pobliżu
    class BroadcastSend(PeriodicBehaviour):
        async def run(self):
            msg = Message(
                to = "environmentmanager@localhost",
                metadata = dict(performative="broadcast"),
                body = dumps({"source_name": self.agent.agent_name,
                              "localization": self.agent.localization,
                              "path": self.agent.path})
            )
            print(f"[{self.agent.agent_name}] Send Broadcast")
            await self.send(msg)


    # Odebranie informacji o Broadcast od urządzenia w pobliżu za pośrednictwem EnvironmentManager'a
    class BroadcastReceive(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                info = loads(msg.body)
                # zaktualizowanie czasu od ostatniego komunikatu od danego sąsiada i aktualizacja informacji o jego ścieżce
                other_name = info["source_name"]
                other_localization = info["localization"]
                other_path = info["path"]

                print(f"[{self.agent.agent_name}] Broadcast receive from: {other_name}")

                self.agent.neighbors[other_name] = {}
                self.agent.neighbors[other_name]["time"] = 10
                self.agent.neighbors[other_name]["localization"] = other_localization
                self.agent.neighbors[other_name]["path"] = other_path

    async def setup(self):
        print(f"[{self.agent_name}] Agent created (setup)")
        start_at: datetime = datetime.now()


        self.add_behaviour(self.ActualizationInfoInEnvironment(period=(7)))
        self.add_behaviour(self.BroadcastSend(period=(10), start_at = start_at + timedelta(seconds=5)))
        self.add_behaviour(self.BroadcastReceive(), template = BROADCAST)

    def __init__(self, name, password):
        super().__init__(name, password)
        self.agent_name = name
        self.localization = {"x":  random.randrange(100), "y":  random.randrange(100)}
        print(f"[{self.agent_name}] Agent created (init)")