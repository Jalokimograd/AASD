import asyncio
import random
from json import dumps, loads
from datetime import datetime, timedelta

from spade import agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from Map import Map
from Planner import Planner
from Templates import BROADCAST
import numpy as np

AGENT_SPEED = 80

class MobileAgent(agent.Agent):
    agent_name: str

    # Informacja o położeniu do EnvironmentManager'a
    class ActualizationInfoInEnvironment(PeriodicBehaviour):
        async def run(self):
            msg = Message(
                to = "environmentmanager@localhost",
                metadata = dict(performative="environment_actualize"),
                body = dumps({"source_name": self.agent.agent_name,
                              "localization": self.agent.localization})
            )
            # print(f"[{self.agent.agent_name}] Send informations actualization to Environment manager")
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
            # print(f"[{self.agent.agent_name}] Send Broadcast")
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
                if point.shape[0] == 0:
                    return
                stamp = point[:, -1]
                point = point[:, :-1]
                time_dist = (stamp[-1] - stamp[0])
                if time_dist <= 0.0:
                    return
                alpha = (clock - stamp[0]) / time_dist
                location = point[0] * (1-alpha) + point[-1] * alpha
                await self.agent.move_to(location[0], location[1])


    # wywalić po ogarnięciu globalnego zegara
    class ClockUpdate(PeriodicBehaviour):
        async def run(self):
            self.agent.clock += (self.period.microseconds * 1e-6)

    class PlanPathBehaviour(OneShotBehaviour):
        permutation = []
        async def run(self):
            self.permutation, distance = self.agent.planer.optimal_permutation()
            print(f'Planning started... {self.permutation}')

            schedule = self.agent.planer.schedule(self.permutation, AGENT_SPEED)
            self.agent.schedule = {str(appointment[0]): (float(appointment[1]), float(appointment[2])) for appointment in schedule}
            path = self.agent.planer.generate_full_path(self.agent.localization, schedule, AGENT_SPEED)
            # path = self.agent.planer.get_path(self.agent.localization, self.permutation[0], AGENT_SPEED)
            print('Path created!')
            await self.agent.set_path(path)

    async def move_to(self, x, y):
        self.localization['x'] = x
        self.localization['y'] = y

    async def move(self, x, y):
        self.localization['x'] += x
        self.localization['y'] += y

    async def set_path(self, path):
        self.current_path = path



    async def numpy_localization(self):
        return np.array((self.localization['x'], self.localization['y']))

    async def setup(self):
        print(f"[{self.agent_name}] Agent created (setup)")
        start_at: datetime = datetime.now()

        self.add_behaviour(self.ActualizationInfoInEnvironment(period=1))
        self.add_behaviour(self.BroadcastSend(period=10, start_at = start_at + timedelta(seconds=5)))
        self.add_behaviour(self.BroadcastReceive(), template=BROADCAST)
        self.add_behaviour(self.ExecuteSchedule(period=0.25))
        self.add_behaviour(self.ClockUpdate(period=0.05))

        self.add_behaviour(self.PlanPathBehaviour())

    def __init__(self, name, password, world_map: Map = None):
        super().__init__(name, password)
        self.agent_name = name
        self.world_map = world_map
        self.planer = Planner(world_map)
        self.localization = {"x":  random.randrange(100), "y":  random.randrange(100)} # lokalizacja {"x": .., "y": ..}
        self.current_path = None  # ścieżka [[x, y, time], ... ]
        self.schedule = {}  # harmonogram {node_id: [start_time, end_time]}
        self.neighbors = {}  # sąsiedzi {"name": {"path": .., "time": .., "localization": ..}, ...}
        self.goals = {}  # cele {node_id: needed_time}
        self.clock = 0  # time of day
        print(f"[{self.agent_name}] Agent created (init)")

    def set_starting_localization(self, localization):
        self.localization = localization

    def set_goals(self, goals):
        current_node = self.world_map.locate_nearset_node(self.localization)
        new_goals = {current_node: 0, **goals}
        self.goals = new_goals
        self.planer.set_goals(self.goals)

