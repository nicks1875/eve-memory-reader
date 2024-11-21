from lib2to3.pgen2.token import OP
from libeve import KEYMAP
from libeve.bots import Bot
from libeve.interface import UITreeNode
import pyautogui as gui

import string
import random
import time
import traceback


class AbyssalFilamentBot(Bot):
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
        self.fleet_commander = fleet_commander
        self.trip_id = ""
        self.current_asteroid = None
        self.asteroids_mined = 0
        self.shields_enabled = False

    def use_filament(self):
        print("in use_filament")
        #self.wait_for({"_name": "aaaaaaaaaa"}, type="MenuEntryView")
        
        # test = self.wait_for({"_name": "shieldGauge"}, type="HealthGauge")
        # test_node_id = test.children[-1]
        # drone_shield_damage_node = self.tree.nodes[test_node_id]
        # #print(f"drone armor damage node id: {drone_armor_damage_node}")
        # current_drone_shield_hp_percent  = drone_shield_damage_node.attrs['_displayX'] / (drone_shield_damage_node.attrs['_displayX'] + drone_shield_damage_node.attrs['_displayWidth'])
        # self.say(f"current drone shield: {current_drone_shield_hp_percent}")

        
        #filament_type = "Chaotic Gamma Filament"
        filament_type = "Fierce Gamma Filament"
        inventorySearchArea = self.tree.find_node({"_name": "hintTextLabel", "_setText": "Search"}, type="LabelOverride")
        if inventorySearchArea:
            self.click_node(inventorySearchArea)
            gui.typewrite(filament_type)
        else:
            self.say("Could not find inventory search window")

        time.sleep(5) # sleep to give extra time to refresh json for inventory window

        filamentItem = self.tree.find_node({"_name": "itemNameLabel", "_setText": filament_type}, type="Label", contains=True)
        if filamentItem:
            self.click_node(filamentItem, right_click=True)

            time.sleep(0.5)

            useFilamentText = self.wait_for({"_name": "context_menu_Use " + filament_type}, type="MenuEntryView", until=5, contains=True)
            if useFilamentText:
                self.click_node(useFilamentText)

            time.sleep(0.5)

            activateFilamentButton = self.wait_for({"_setText": "Activate"}, type="EveLabelMedium")

            self.click_node(activateFilamentButton)

        else:
            self.say(f"no {filament_type} found in inventory. Need to return to station to get more")

    def ensure_active_modules_on(self):
        print("in ensure_active_modules_on")
        # Check if multispectrum shield hardener II is active and use if it isnt
        check_shield_hardener_active = self.wait_for({"_name": "ModuleButton_2281", "ramp_active": True}, type="ModuleButton", until=0.005)
        if not check_shield_hardener_active:
            click_shield_hardener = self.tree.find_node({"_name": "ModuleButton_2281"}, type="ModuleButton")
            self.click_node(click_shield_hardener)
        
        time.sleep(0.5)

        # Check if 10MN Afterburner II is active and use if it isnt
        check_afterburner_active = self.wait_for({"_name": "ModuleButton_12058", "ramp_active": True}, type="ModuleButton", until=0.005)
        if not check_afterburner_active:
            click_afterburner = self.tree.find_node({"_name": "ModuleButton_12058"}, type="ModuleButton")
            self.click_node(click_afterburner)

        time.sleep(0.5)        

    def start_room(self):
        print("in start_room")
        # wait for bioadaptive cache to appear on overview to tell when you're in the filament room
        self.wait_for({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel", contains=True)

        time.sleep(5)

        self.ensure_active_modules_on()

        loot_cache =  self.wait_for({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel", contains=True)
        if loot_cache:
            self.click_node(loot_cache)
        
        time.sleep(0.5)

        orbit_loot_cache =  self.tree.find_node({"_name": "selectedItemOrbit"}, type="SelectedItemButton")
        if orbit_loot_cache:
            self.click_node(orbit_loot_cache)

    def count_enemies(self):
        print("in count_enemies")
        overview_enemies = self.tree.find_node({"_name": "scrollentry"}, type="OverviewScrollEntry", select_many=True, contains=True)

        enemy_count = 0
        for enemy in overview_enemies:
            enemy_name_field = enemy.attrs.get("_name", None)
            # Filter out Triglavian Extraction Node / Triglavian Bioadaptive Cache to count number of enemies in room. Also exclude Vila Swarmer
            if enemy_name_field != "scrollentry_49662" and enemy_name_field != "scrollentry_47951" and enemy_name_field != "scrollentry_49661" and enemy_name_field != "scrollentry_48253" and enemy_name_field != None:
                enemy_count = enemy_count + 1

        print(f"number of enemies: {enemy_count}")
        return enemy_count

    def check_room_type(self):
        print("in check_room_type")
        target_priority_list = ["Any"] # Default target priority list if room type cannot be determined

        trig_frigate = self.wait_for({"_text": "Damavik"}, type="OverviewLabel", until=0.005, contains=True)
        trig_destroyer = self.wait_for({"_text": "Kikimora"}, type="OverviewLabel", until=0.005, contains=True)
        trig_cruiser1 = self.wait_for({"_text": "Vedmak"}, type="OverviewLabel", until=0.005, contains=True)
        trig_cruiser2 = self.wait_for({"_text": "Rodiva"}, type="OverviewLabel", until=0.005, contains=True)
        trig_battlecruiser = self.wait_for({"_text": "Drekavac"}, type="OverviewLabel", until=0.005, contains=True)
        trig_battleship = self.wait_for({"_text": "Leshak"}, type="OverviewLabel", until=0.005, contains=True)

        if trig_frigate or trig_destroyer or trig_cruiser1 or trig_cruiser2 or trig_battlecruiser or trig_battleship:
            room_type = "Triglavian"
            print(f"Room type is {room_type}")
            target_priority_list = ["Starving Damavik", "Starving Vedmak", "Starving Leshak", "Renewing", "Striking", "Ghosting", "Any"]

        edencom_ship = self.wait_for({"_text": "Disparu Troop"}, type="OverviewLabel", until=0.005, contains=True)

        if edencom_ship:
            room_type = "Edencom"
            print(f"Room type is {room_type}")
            target_priority_list = ["Drainer Marshal Disparu Troop", "Drainer Enforcer Disparu Troop", "Drainer Pacifier Disparu Troop", "Marshal Disparu Troop", "Any"]
        
        angel_ship = self.wait_for({"_text": "Lucifer"}, type="OverviewLabel", until=0.005, contains=True)

        if angel_ship:
            room_type = "Angel"
            print(f"Room type is {room_type}")
            target_priority_list = ["Lucifer Fury", "Lucifer Cynabal", "Elite Lucifer Cynabal", "Lucifer Echo", "Any"]
        
        drifter_ship1 = self.wait_for({"_text": "Lucid"}, type="OverviewLabel", until=0.005, contains=True)
        drifter_ship2 = self.wait_for({"_text": "Ephialtes"}, type="OverviewLabel", until=0.005, contains=True)
        drifter_ship3 = self.wait_for({"_text": "Scylla"}, type="OverviewLabel", until=0.005, contains=True)
        drifter_ship4 = self.wait_for({"_text": "Karybdis Tyrannos"}, type="OverviewLabel", until=0.005, contains=True)

        if drifter_ship1 or drifter_ship2 or drifter_ship3 or drifter_ship4:
            room_type = "Sleeper"
            print(f"Room type is {room_type}")
            target_priority_list = ["Lucid Firewatcher", "Ephialtes Dissipator", "Scylla Tyrannos", "Lucid Sentinel", "Karybdis Tyrannos", "Lucid Deepwatcher", "Any"]

        sansha_ship = self.wait_for({"_text": "Devoted"}, type="OverviewLabel", until=0.005, contains=True)
        if sansha_ship:
            room_type = "Sansha"
            print(f"Room type is {room_type}")
            target_priority_list = ["Devoted Smith", "Devoted Knight", "Any"]
        
        rogue_drone_ship1 = self.wait_for({"_text": "Tessella"}, type="OverviewLabel", until=0.005, contains=True)
        rogue_drone_ship2 = self.wait_for({"_text": "Tessera"}, type="OverviewLabel", until=0.005, contains=True)
        rogue_drone_ship3 = self.wait_for({"_text": "Overmind"}, type="OverviewLabel", until=0.005, contains=True)

        if rogue_drone_ship1 or rogue_drone_ship2 or rogue_drone_ship3:
            room_type = "Rogue Drone"
            print(f"Room type is {room_type}")
            target_priority_list = ["Plateforger Tessella", "Fieldweaver Tessella", "Overmind", "Fogcaster Tessella", "Any"]
        
        return target_priority_list

    #def get_targets(self):
    def get_targets(self, target_priority_list):
        print("in get_targets")
        max_targets = 7
        # there exists at least 1 enemy on overview so room is not done
        #target_priority_list = ["Starving Damavik", "Starving Vedmak", "Starving Leshak", "Renewing", "Striking", "Ghosting", "Any"]

        targets_clicked = 0

        for target in target_priority_list:

            if targets_clicked >= max_targets:
                break
            if target == "Any": # Lock any enemy present. Have to find a different UI element to search for them instead
                overview_enemies = self.tree.find_node({"_name": "scrollentry"}, type="OverviewScrollEntry", select_many=True, contains=True)
                for enemy in overview_enemies:
                    enemy_name = enemy.attrs.get("_name", None)
                    if enemy_name != "scrollentry_49662" and enemy_name != "scrollentry_47951" and enemy_name != "scrollentry_49661"  and enemy_name != "scrollentry_49661" and enemy_name != "scrollentry_48253" and enemy_name != None:
                        print(f"Clicking target {enemy_name}")
                        gui.keyDown('ctrl')
                        time.sleep(0.050)
                        self.click_node(enemy)
                        targets_clicked = targets_clicked + 1
                        time.sleep(0.050)
                        gui.keyUp('ctrl')
            else:
                overview_enemies = self.tree.find_node({"_text": target}, type="OverviewLabel", select_many=True, contains=True)
                for enemy in overview_enemies:
                    print(f"Clicking target {target}")
                    gui.keyDown('ctrl')
                    time.sleep(0.050)
                    self.click_node(enemy)
                    targets_clicked = targets_clicked + 1
                    time.sleep(0.050)
                    gui.keyUp('ctrl')

        #time.sleep(0.5)

    def ensure_drones_deployed(self):
        print("in ensure_drones_deployed")
        drones_deployed = self.wait_for({"_name": "entry_"}, type="DroneInSpaceEntry", contains=True, select_many=True, until=0.05)
        num_drones_deployed = len(drones_deployed)
        if num_drones_deployed < 2:
            gui.keyDown('shift')
            time.sleep(0.05)
            gui.press('f')
            time.sleep(0.05)
            gui.keyUp('shift')

    def ensure_drones_attacking(self, target_priority_list):
        print("in ensure_drones_attacking")
        drones_attacking = self.wait_for({"_hint": "Drones Republic Fleet Valkyrie: 2"}, type="Sprite", until=0.005)
        if not drones_attacking: # find suitable target for drones to attack

            for target in target_priority_list:

                if target == "Any": # Lock any enemy present. Have to find a different UI element to search for them instead
                    overview_enemies = self.tree.find_node({"_name": "scrollentry"}, type="OverviewScrollEntry", select_many=True, contains=True)
                    random_enemy = random.choice(overview_enemies)
                    random_enemy_name = random_enemy.attrs.get("_name", None)
                    if random_enemy_name != "scrollentry_49662" and random_enemy_name != "scrollentry_47951" and random_enemy_name != "scrollentry_49661" and random_enemy_name != None:
                        print(f"Clicking target {random_enemy}")
                        self.click_node(random_enemy)
                        time.sleep(0.050)
                        gui.press('f')
                        break
                else:
                    enemy_present = self.tree.find_node({"_text": target}, type="OverviewLabel", contains=True)
                    if enemy_present:
                        print(f"Clicking target {target}")
                        self.click_node(enemy_present)
                        time.sleep(0.050)
                        gui.press('f')
                        break         
            

    def find_target_of_drones(self):
        print("in find_target_of_drones")
        drone_attacking_target = self.tree.find_node({"_hint": "Drones Republic Fleet Valkyrie:"}, type="Sprite", contains=True)
        if drone_attacking_target:
            self.click_node(drone_attacking_target, y_offset=-150) # Click target above drone attacking target icon. Should be around target lock portrait
            return True
        else:
            return False

    def ensure_missile_launchers_active(self):
        print("in ensure_missile_launchers_active")
        missile_launcher_active = self.tree.find_node({"_name": "ModuleButton_1877", "ramp_active": True}, type="ModuleButton")
        if not missile_launcher_active:
            drones_have_target = self.find_target_of_drones()
            print(f"drones have target: {drones_have_target}")
            if drones_have_target:
                time.sleep(0.05)
                gui.press('f1')

    def check_drone_hp(self):
        shield_gauge_nodes = self.tree.find_node({"_name": "shieldGauge"}, type="HealthGauge", select_many=True)
        test_node_id = shield_gauge_nodes.children[-1]
        drone_shield_damage_node = self.tree.nodes[test_node_id]
        #print(f"drone armor damage node id: {drone_armor_damage_node}")
        current_drone_shield_hp_percent  = drone_shield_damage_node.attrs['_displayX'] / (drone_shield_damage_node.attrs['_displayX'] + drone_shield_damage_node.attrs['_displayWidth'])
        self.say(f"current drone shield: {current_drone_shield_hp_percent}")    

    def loot_cache(self, loot_collected):

        loot_wreck_button = self.tree.find_node({"_setText": "Loot All"}, type="EveLabelMedium")
        if loot_wreck_button:
            self.say("Clicked loot wreck button")
            self.click_node(loot_wreck_button)
            loot_collected = True
            return loot_collected
        
        # Loot cache already destroyed. just need to loot
        loot_cache_wreck = self.tree.find_node({"_text": "Triglavian Bioadaptive Cache Wreck"}, type="OverviewLabel", contains=True)
        if loot_cache_wreck:
            self.say("Clicked loot cache wreck")
            gui.keyDown('q')
            time.sleep(0.050)
            self.click_node(loot_cache_wreck)
            time.sleep(0.050)
            gui.keyUp('q')
            time.sleep(0.25)
            # self.click_node(loot_cache_wreck, right_click=True)
            # time.sleep(0.25)
            # open_cargo_option = self.wait_for({"_setText": "Open Cargo"}, type="TextBody")
            # if open_cargo_option:
            #     self.click_node(open_cargo_option)

        open_cargo = self.tree.find_node({"_name": "selectedItemOpenCargo"}, type="SelectedItemButton")
        if open_cargo:
            self.say("Clicked loot cargo")
            self.click_node(open_cargo)

        loot_cache_overview = self.tree.find_node({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel")
        if loot_cache_overview:
            self.say("Clicking loot cache target")
            gui.keyDown('ctrl')
            time.sleep(0.050)
            self.click_node(loot_cache_overview)
            time.sleep(0.050)
            gui.keyUp('ctrl')
            time.sleep(3)
            gui.press('f1')
            time.sleep(2)

        return loot_collected

    def approach_and_take_gate(self):
        print("in approach and take gate")

        # recall drones
        gui.keyDown('shift')
        time.sleep(0.05)
        gui.press('r')
        time.sleep(0.05)
        gui.keyUp('shift')

        transfer_gate = self.tree.find_node({"_text": "Transfer Conduit (Triglavian)", "_hint": "Transfer Conduit (Triglavian)"}, type="OverviewLabel")
        if transfer_gate:
            self.click_node(transfer_gate)

        in_new_room = self.wait_for({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel", until=0.005)

        while not in_new_room:
            
            approach_transfer_gate = self.tree.find_node({"_name": "selectedItemActivateGate"}, type="SelectedItemButton")
            if approach_transfer_gate:
                self.click_node(approach_transfer_gate)
            
            time.sleep(1)

            in_new_room = self.wait_for({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel", until=0.005)

    def main(self):

        #self.wait_for({"_name": "aaaaaaaaaa"}, type="MenuEntryView")     

        self.use_filament()

        room_number = 1
        print(f"in room #{room_number}")

        while room_number < 4: # all filaments have 3 rooms except the special T5 / T6 single room
            self.start_room()
            loot_collected = False
            # Wait a few seconds while overview targets settle after jumping in
            time.sleep(5)
            target_priority_list = self.check_room_type()
            enemy_count = self.count_enemies()

            while (enemy_count > 0) or (loot_collected == False):
                self.get_targets(target_priority_list)
                self.ensure_drones_deployed()
                self.ensure_drones_attacking(target_priority_list)
                self.ensure_missile_launchers_active()
                self.ensure_active_modules_on()
                
                # Destroy loot cache and / or loot it
                if enemy_count < 4:
                    if not loot_collected:
                        print("Collecting loot")
                        loot_collected = self.loot_cache(loot_collected)
                    else:
                        print("Loot already collected")

                enemy_count = self.count_enemies()

            self.approach_and_take_gate()

            # Recall drones and take gate

            room_number += 1
            print(f"Entering room #{room_number}")
            self.say(f"Entering room #{room_number}")





