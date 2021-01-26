import asyncio
import random
from json import dumps, loads
from datetime import datetime, timedelta

from spade import agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message

from Map import Map, Planner
from Templates import BROADCAST
import numpy as np

AGENT_SPEED = 30

class MobileAgent(agent.Agent):
    agent_name: str
    localization = {}       # lokalizacja {"x": .., "y": ..}
    neighbors = {}          # sąsiedzi {"name": {"path": .., "time": .., "localization": ..}, ...}
    current_path = None     # ścieżka [[x, y, time], ... ]
    goals = {}              # cele {node_id: needed_time}
    schedule = {}           # harmonogram {node_id: [start_time, end_time]}
    clock = 0               # time of day


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
                              "schedule": self.agent.schedule})
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
                other_schedule = info["schedule"]

                print(f"[{self.agent.agent_name}] Broadcast receive from: {other_name}")

                self.agent.neighbors[other_name] = {}
                self.agent.neighbors[other_name]["time"] = 10
                self.agent.neighbors[other_name]["localization"] = other_localization
                self.agent.neighbors[other_name]["schedule"] = other_schedule

    class ExecuteSchedule(PeriodicBehaviour):
        async def run(self):
            if self.agent.current_path is not None:
                path = self.agent.current_path
                clock = self.agent.clock
                index = np.argmax(path[:, -1] > clock) - 1
                point = path[index:(index+2), :]
                stamp = point[:, -1]
                point = point[:, :-1]
                alpha = (clock - stamp[0]) / (stamp[-1] - stamp[0])
                location = point[0] * (1-alpha) + point[1] * alpha
                await self.agent.move_to(location[0], location[1])


    # wywalić po ogarnięciu globalnego zegara
    class ClockBehaviour(PeriodicBehaviour):
        async def run(self):
            self.agent.clock += self.period.microseconds * 1e-6

    async def move_to(self, x, y):
        self.localization['x'] = x
        self.localization['y'] = y

    async def move(self, x, y):
        self.localization['x'] += x
        self.localization['y'] += y

    async def plan(self):
        self.current_path = self.planer.get_full_path(AGENT_SPEED)

    async def numpy_localization(self):
        return np.array((self.localization['x'], self.localization['y']))

    async def setup(self):
        print(f"[{self.agent_name}] Agent created (setup)")
        start_at: datetime = datetime.now()

        self.add_behaviour(self.ActualizationInfoInEnvironment(period=1))
        self.add_behaviour(self.BroadcastSend(period=10, start_at = start_at + timedelta(seconds=5)))
        self.add_behaviour(self.BroadcastReceive(), template = BROADCAST)
        self.add_behaviour(self.ExecuteSchedule(period=0.25))
        self.add_behaviour(self.ClockBehaviour(period=0.1))

        await self.plan()

    def __init__(self, name, password, world_map: Map = None):
        super().__init__(name, password)
        self.agent_name = name
        self.world_map = world_map
        self.planer = Planner(world_map)
        self.localization = {"x":  random.randrange(100), "y":  random.randrange(100)}
        print(f"[{self.agent_name}] Agent created (init)")

    def set_starting_localization(self, localization):
        self.localization = localization

    def set_goals(self, goals):
        self.goals = [self.world_map.locate_nearset_node(self.localization)] + goals
        self.planer.set_goals(self.goals)

