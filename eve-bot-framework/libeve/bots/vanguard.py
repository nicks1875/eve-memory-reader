from lib2to3.pgen2.token import OP
from libeve import KEYMAP
from libeve.bots import Bot
from libeve.interface import UITreeNode


import string
import random
import time
import traceback


class VanguardBot(Bot):
    def __init__(
        self,
        log_fn=print,
        pause_interrupt=None,
        pause_callback=None,
        stop_interrupt=None,
        stop_callback=None,
        stop_safely_interrupt=None,
        stop_safely_callback=None,
        deploy_drones_while_mining=False,
        station=None,
        number_of_miners=1,
        shields=None,
        asteroids_of_interest=[],
        accounts=[],
        fleet_commander=None,
    ):
        super().__init__(
            log_fn=log_fn,
            pause_interrupt=pause_interrupt,
            pause_callback=pause_callback,
            stop_interrupt=stop_interrupt,
            stop_callback=stop_callback,
            stop_safely_interrupt=stop_safely_interrupt,
            stop_safely_callback=stop_safely_callback,
        )
        self.visited_asteroid_belts = list()
        self.deploy_drones_while_mining = deploy_drones_while_mining
        self.station = station
        self.number_of_miners = number_of_miners
        self.shields = shields
        self.asteroids_of_interest = asteroids_of_interest
        self.accounts = accounts
        self.fleet_commander = fleet_commander
        self.trip_id = ""
        self.current_asteroid = None
        self.asteroids_mined = 0
        self.shields_enabled = False

    def mine_asteroids(self):
        self.wait_for({"_name": "target"}, type="TargetInBar", until=10)
        time.sleep(5)
