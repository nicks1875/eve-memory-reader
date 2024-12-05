from lib2to3.pgen2.token import OP
from libeve import KEYMAP
from libeve.bots import Bot
from libeve.interface import UITreeNode
import pyautogui as gui

import inspect
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
        self.say("in use_filament")
        start_time = time.perf_counter()
        #self.wait_for({"_name": "aaaaaaaaaa"}, type="MenuEntryView")
    
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

            clear_inventory_search_button = self.tree.find_node({"_hint": "Clear filters"}, type="ButtonIcon")
            if clear_inventory_search_button:
                self.click_node(clear_inventory_search_button)

            self.click_node(activateFilamentButton)

        else:
            self.say(f"no {filament_type} found in inventory. Need to return to station to get more")

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def ensure_active_modules_on(self):
        self.say("in ensure_active_modules_on")
        start_time = time.perf_counter()
        # Check if multispectrum shield hardener II is active and use if it isnt
        check_shield_hardener_active = self.tree.find_node({"_name": "ModuleButton_2281", "ramp_active": True}, type="ModuleButton")
        if not check_shield_hardener_active:
            click_shield_hardener = self.tree.find_node({"_name": "ModuleButton_2281"}, type="ModuleButton")
            self.click_node(click_shield_hardener)
        
        time.sleep(0.5)

        # Check if 10MN Afterburner II is active and use if it isnt
        check_afterburner_active = self.tree.find_node({"_name": "ModuleButton_12058", "ramp_active": True}, type="ModuleButton")
        if not check_afterburner_active:
            click_afterburner = self.tree.find_node({"_name": "ModuleButton_12058"}, type="ModuleButton")
            self.click_node(click_afterburner)

        time.sleep(0.5)   

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")     

    def start_room(self):
        self.say("in start_room")
        start_time = time.perf_counter()
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

        # Deploy drones initially without checking hp
        gui.keyDown('shift')
        time.sleep(0.05)
        gui.press('f')
        time.sleep(0.05)
        gui.keyUp('shift')

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def count_enemies(self):
        self.say("in count_enemies")
        start_time = time.perf_counter()
        overview_enemies = self.tree.find_node({"_name": "scrollentry"}, type="OverviewScrollEntry", select_many=True, contains=True)

        enemy_count = 0
        for enemy in overview_enemies:
            enemy_name_field = enemy.attrs.get("_name", None)
            # Filter out Triglavian Extraction Node / Triglavian Bioadaptive Cache to count number of enemies in room. Also exclude Vila Swarmer
            if enemy_name_field != "scrollentry_49662" and enemy_name_field != "scrollentry_47951" and enemy_name_field != "scrollentry_49661" and enemy_name_field != "scrollentry_48253" and enemy_name_field != None:
                enemy_count = enemy_count + 1

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")
        self.say(f"number of enemies: {enemy_count}")
        return enemy_count

    def check_room_type(self):
        self.say("in check_room_type")
        start_time = time.perf_counter()
        target_priority_list = ["Any"] # Default target priority list if room type cannot be determined

        trig_frigate = self.tree.find_node({"_text": "Damavik"}, type="OverviewLabel", contains=True)
        trig_destroyer = self.tree.find_node({"_text": "Kikimora"}, type="OverviewLabel", contains=True)
        trig_cruiser1 = self.tree.find_node({"_text": "Vedmak"}, type="OverviewLabel", contains=True)
        trig_cruiser2 = self.tree.find_node({"_text": "Rodiva"}, type="OverviewLabel", contains=True)
        trig_battlecruiser = self.tree.find_node({"_text": "Drekavac"}, type="OverviewLabel", contains=True)
        trig_battleship = self.tree.find_node({"_text": "Leshak"}, type="OverviewLabel", contains=True)

        if trig_frigate or trig_destroyer or trig_cruiser1 or trig_cruiser2 or trig_battlecruiser or trig_battleship:
            room_type = "Triglavian"
            self.say(f"Room type is {room_type}")
            target_priority_list = ["Starving Damavik", "Starving Vedmak", "Starving Leshak", "Renewing", "Striking", "Ghosting", "Any"]
            drone_recall_percent = 0.75

        edencom_ship = self.tree.find_node({"_text": "Disparu Troop"}, type="OverviewLabel", contains=True)

        if edencom_ship:
            room_type = "Edencom"
            self.say(f"Room type is {room_type}")
            target_priority_list = ["Drainer Marshal Disparu Troop", "Drainer Enforcer Disparu Troop", "Drainer Pacifier Disparu Troop", "Marshal Disparu Troop", "Any"]
            drone_recall_percent = 0.5
        
        angel_ship = self.tree.find_node({"_text": "Lucifer"}, type="OverviewLabel", contains=True)

        if angel_ship:
            room_type = "Angel"
            self.say(f"Room type is {room_type}")
            target_priority_list = ["Lucifer Fury", "Lucifer Cynabal", "Elite Lucifer Cynabal", "Lucifer Echo", "Any"]
            drone_recall_percent = 0.75
        
        drifter_ship1 = self.tree.find_node({"_text": "Lucid"}, type="OverviewLabel", contains=True)
        drifter_ship2 = self.tree.find_node({"_text": "Ephialtes"}, type="OverviewLabel", contains=True)
        drifter_ship3 = self.tree.find_node({"_text": "Scylla"}, type="OverviewLabel", contains=True)
        drifter_ship4 = self.tree.find_node({"_text": "Karybdis Tyrannos"}, type="OverviewLabel", contains=True)

        if drifter_ship1 or drifter_ship2 or drifter_ship3 or drifter_ship4:
            room_type = "Sleeper"
            self.say(f"Room type is {room_type}")
            target_priority_list = ["Lucid Firewatcher", "Ephialtes Dissipator", "Scylla Tyrannos", "Lucid Sentinel", "Karybdis Tyrannos", "Lucid Deepwatcher", "Any"]
            drone_recall_percent = 0.75

        sansha_ship = self.tree.find_node({"_text": "Devoted"}, type="OverviewLabel", contains=True)
        if sansha_ship:
            room_type = "Sansha"
            self.say(f"Room type is {room_type}")
            target_priority_list = ["Devoted Smith", "Devoted Knight", "Any"]
            drone_recall_percent = 0.5
        
        rogue_drone_ship1 = self.tree.find_node({"_text": "Tessella"}, type="OverviewLabel", contains=True)
        rogue_drone_ship2 = self.tree.find_node({"_text": "Tessera"}, type="OverviewLabel", contains=True)
        rogue_drone_ship3 = self.tree.find_node({"_text": "Overmind"}, type="OverviewLabel", contains=True)

        if rogue_drone_ship1 or rogue_drone_ship2 or rogue_drone_ship3:
            room_type = "Rogue Drone"
            self.say(f"Room type is {room_type}")
            target_priority_list = ["Plateforger Tessella", "Fieldweaver Tessella", "Overmind", "Fogcaster Tessella", "Any"]
            drone_recall_percent = 0.75
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

        return target_priority_list, drone_recall_percent

    def get_targets(self, target_priority_list):
        self.say("in get_targets")
        start_time = time.perf_counter()
        max_targets = 7
        # there exists at least 1 enemy on overview so room is not done
        #target_priority_list = ["Starving Damavik", "Starving Vedmak", "Starving Leshak", "Renewing", "Striking", "Ghosting", "Any"]

        targets_clicked = 0

        num__targets_locked = self.tree.find_node(type="ActiveTargetOnBracket", select_many=True)
        if len(num__targets_locked) < 3:
            
            for target in target_priority_list:

                    if targets_clicked >= max_targets:
                        break
                    if target == "Any": # Lock any enemy present. Have to find a different UI element to search for them instead
                        overview_enemies = self.tree.find_node({"_name": "scrollentry"}, type="OverviewScrollEntry", select_many=True, contains=True)
                        for enemy in overview_enemies:
                            
                            enemy_name = enemy.attrs.get("_name", None)
                            if enemy_name != "scrollentry_49662" and enemy_name != "scrollentry_47951" and enemy_name != "scrollentry_49661"  and enemy_name != "scrollentry_49661" and enemy_name != "scrollentry_48253" and enemy_name != None:
                                self.say(f"Clicking target {enemy_name}")
                                gui.keyDown('ctrl')
                                time.sleep(0.005)
                                self.click_node(enemy)
                                targets_clicked = targets_clicked + 1
                                time.sleep(0.005)
                                gui.keyUp('ctrl')
                    else:
                        overview_enemies = self.tree.find_node({"_text": target, "_hint": target}, type="OverviewLabel", select_many=True, contains=True)
                        for enemy in overview_enemies:
                            self.say(f"Clicking target {target}")
                            gui.keyDown('ctrl')
                            time.sleep(0.005)
                            self.click_node(enemy)
                            targets_clicked = targets_clicked + 1
                            time.sleep(0.005)
                            gui.keyUp('ctrl')

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def ensure_drones_deployed(self, drone_recall_percent):
        self.say("in ensure_drones_deployed")
        start_time = time.perf_counter()

        drone_in_bay = self.tree.find_node({"_name": "entry_"}, type="DroneInBayEntry", contains=True)

        shield_node = self.tree.find_child_node(address=drone_in_bay.address, stop_at_key="_name", stop_at_value="shieldGauge")
        if shield_node:
            drone_shield_node = self.tree.nodes[shield_node.children[-1]]
            drone_bay_current_shield_hp_percent = drone_shield_node.attrs['_displayX'] / (drone_shield_node.attrs['_displayX'] + drone_shield_node.attrs['_displayWidth'])
            
            if drone_bay_current_shield_hp_percent >= drone_recall_percent:
                
                self.click_node(shield_node, right_click=True)
                time.sleep(0.5)
                launch_drone_text = self.wait_for({"_setText": "Launch Drone"}, type="TextBody", until=1.5)
                if launch_drone_text:
                    self.click_node(launch_drone_text)
                
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def ensure_drones_attacking(self, target_priority_list):
        start_time = time.perf_counter()
        self.say("in ensure_drones_attacking")
        self.say(f"target priority list: {target_priority_list}")
        valid_enemies = []
        drones_attacking = self.tree.find_node({"_hint": "Drones Republic Fleet Valkyrie: 2"}, type="Sprite")
        if not drones_attacking: # find suitable target for drones to attack

            for target in target_priority_list:

                if target == "Any": # Lock any enemy present. Have to find a different UI element to search for them instead
                    overview_enemies = self.tree.find_node({"_name": "scrollentry"}, type="OverviewScrollEntry", select_many=True, contains=True)
                    
                    # Filter out all objects in overview that arent npc ships
                    for overview_enemy in overview_enemies:
                        overview_enemy_name = overview_enemy.attrs.get("_name", None)
                        if overview_enemy_name != "scrollentry_49662" and overview_enemy_name != "scrollentry_47951" and overview_enemy_name != "scrollentry_49661" and overview_enemy_name != None:
                            valid_enemies.append(overview_enemy)

                    random_enemy = random.choice(valid_enemies)
                    self.say(f"Clicking target {random_enemy}")
                    self.click_node(random_enemy)
                    time.sleep(0.050)
                    gui.press('f')
                    break
                else:
                    enemy_present = self.tree.find_node({"_text": target, "_hint": target}, type="OverviewLabel", contains=True)
                    self.say(f"enemy present in ensure_drones_attacking: {enemy_present}")
                    if enemy_present:
                        self.say(f"Clicking target {target}")
                        self.click_node(enemy_present)
                        time.sleep(0.050)
                        gui.press('f')
                        break

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def find_target_of_drones(self):
        self.say("in find_target_of_drones")
        drone_attacking_target = self.tree.find_node({"_hint": "Drones Republic Fleet Valkyrie:"}, type="Sprite", contains=True)
        if drone_attacking_target:
            self.click_node(drone_attacking_target, y_offset=-150) # Click target above drone attacking target icon. Should be around target lock portrait
            return True
        else:
            return False

    def ensure_missile_launchers_active(self):
        self.say("in ensure_missile_launchers_active")
        start_time = time.perf_counter()
        missile_launcher_active = self.tree.find_node({"_name": "ModuleButton_1877", "ramp_active": True}, type="ModuleButton")
        if not missile_launcher_active:
            drones_have_target = self.find_target_of_drones()
            self.say(f"drones have target: {drones_have_target}")
            if drones_have_target:
                time.sleep(0.05)
                gui.press('f1')

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def check_drone_hp(self, drone_recall_percent):
        #drone_in_space_nodes = self.tree.find_root_nodes({"_name": "shieldGauge"}, type="HealthGauge", select_many=True, contains=False, stop_at_value="DroneInSpaceEntry")
        self.say("in check_drone_hp")
        start_time = time.perf_counter()

        drones_in_space = self.tree.find_node({"_name": "entry_"}, type="DroneInSpaceEntry", contains=True, select_many=True)
        
        for drone in drones_in_space:
            shield_node = self.tree.find_child_node(address=drone.address, stop_at_key="_name", stop_at_value="shieldGauge")
            if shield_node:
                drone_shield_node = self.tree.nodes[shield_node.children[-1]]
                current_drone_shield_hp_percent = drone_shield_node.attrs['_displayX'] / (drone_shield_node.attrs['_displayX'] + drone_shield_node.attrs['_displayWidth'])
                self.say(f"current drone shield: {current_drone_shield_hp_percent}")
                if current_drone_shield_hp_percent <= drone_recall_percent:
                    self.say("recalling drone")
                    self.click_node(shield_node, right_click=True)
                    time.sleep(0.5)
                    return_drone_text = self.wait_for({"_setText": "Return to Drone Bay"}, type="TextBody", until=1.5)
                    if return_drone_text:
                        self.click_node(return_drone_text)
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"check_drone_hp execution time: {execution_time:.6f} seconds")

    def shoot_wreck(self):
        self.say("in shoot_wreck")
        start_time = time.perf_counter()

        loot_cache_overview = self.tree.find_node({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel")
        if loot_cache_overview:
            self.say("Clicking loot cache target")
            gui.keyDown('ctrl')
            time.sleep(0.050)
            self.click_node(loot_cache_overview)
            time.sleep(0.050)
            gui.keyUp('ctrl')
            time.sleep(0.050)
            gui.press('f1')
        
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        self.say(f"{inspect.currentframe().f_code.co_name} execution time: {execution_time:.6f} seconds")

    def loot_cache(self):
        self.say("in loot cache")

        loot_all_button = self.tree.find_node({"_name": "invLootAllBtn"}, type="Button")
        if loot_all_button:
            self.say("Clicked loot all button on wreck")
            self.click_node(loot_all_button)
            return
        
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

        open_cargo = self.tree.find_node({"_name": "selectedItemOpenCargo"}, type="SelectedItemButton")
        if open_cargo:
            self.say("Clicked loot cargo")
            self.click_node(open_cargo)

    def take_gate(self):
        self.say("in take gate")

        # recall drones
        gui.keyDown('shift')
        time.sleep(0.05)
        gui.press('r')
        time.sleep(0.05)
        gui.keyUp('shift')

        # Wait for drones to be recalled
        drones_in_bay = self.tree.find_node({"_setText": "Drones in Space (0/5)"}, type="EveLabelMedium")
        
        while not drones_in_bay:

            time.sleep(0.25)

            drones_in_bay = self.tree.find_node({"_setText": "Drones in Space (0/5)"}, type="EveLabelMedium")

        transfer_gate = self.tree.find_node({"_setText": "Transfer Conduit (Triglavian)", "_hint": "Transfer Conduit (Triglavian)"}, type="OverviewLabel")
        if transfer_gate:
            self.click_node(transfer_gate)

        in_new_room = self.tree.find_node({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel")

        while not in_new_room:
            
            approach_transfer_gate = self.tree.find_node({"_name": "selectedItemActivateGate"}, type="SelectedItemButton")
            if approach_transfer_gate:
                self.click_node(approach_transfer_gate)
            
            time.sleep(1)

            in_new_room = self.tree.find_node({"_text": "Triglavian Bioadaptive Cache"}, type="OverviewLabel")

    def orbit_gate(self):
        self.say("in orbit_gate")

        gate = self.tree.find_node({"_text": "Conduit (Triglavian)"}, type="OverviewLabel", contains=True)
        if gate:
            self.click_node(gate)
            orbit_gate =  self.tree.find_node({"_name": "selectedItemOrbit"}, type="SelectedItemButton")
            if orbit_gate:
                self.click_node(orbit_gate)

    def main(self):
        
        #self.wait_for({"_name": "aaaaaaaaaa"}, type="MenuEntryView")

        # while True:

        #     max_drones_deployed_in_space = self.tree.find_node({"_setText": "Drones in Space (2/5)"}, type="EveLabelMedium")
        #     while not max_drones_deployed_in_space:
        #         self.ensure_drones_deployed(0.75)
        #         max_drones_deployed_in_space = self.tree.find_node({"_setText": "Drones in Space (2/5)"}, type="EveLabelMedium")

        self.use_filament()

        room_number = 1
        self.say(f"in room #{room_number}")

        while room_number < 4: # all filaments have 3 rooms except the special T5 / T6 single room
            loot_collected = False
            self.start_room()
            # Wait a few seconds while overview targets settle after jumping in
            time.sleep(3)
            target_priority_list, drone_recall_percent = self.check_room_type()
            enemy_count = self.count_enemies()
            
            # Record isk amount in cargo prior to determine when loot has been collected
            isk_in_cargo_node = self.tree.find_node({"_name": "totalPriceLabel"}, type="EveLabelMedium")
            room_start_isk_amount_in_cargo = int(isk_in_cargo_node.attrs['_setText'].split(' ')[0].replace(",", ""))
            self.say(f"isk in cargo at start of room {room_number}: {room_start_isk_amount_in_cargo}")

            while (enemy_count > 0):
                self.say(f"loot collected is: {loot_collected}")
                
                self.get_targets(target_priority_list)
                
                max_drones_deployed_in_space = self.tree.find_node({"_setText": "Drones in Space (2/5)"}, type="EveLabelMedium")
                while not max_drones_deployed_in_space:
                    self.ensure_drones_deployed(drone_recall_percent)
                    max_drones_deployed_in_space = self.tree.find_node({"_setText": "Drones in Space (2/5)"}, type="EveLabelMedium")

                self.ensure_drones_attacking(target_priority_list)
                self.ensure_missile_launchers_active()
                self.ensure_active_modules_on()
                self.check_drone_hp(drone_recall_percent)
                
                enemy_count = self.count_enemies()

                if loot_collected == False:
                    self.loot_cache()
                else:
                    self.orbit_gate()

                # Destroy loot cache
                if enemy_count < 5:
                    self.shoot_wreck()

                isk_in_cargo_node = self.tree.find_node({"_name": "totalPriceLabel"}, type="EveLabelMedium")
                if isk_in_cargo_node:
                    if 'ISK' in isk_in_cargo_node.attrs['_setText']:
                        current_isk_amount_in_cargo = int(isk_in_cargo_node.attrs['_setText'].split(' ')[0].replace(",", ""))
                        if current_isk_amount_in_cargo > room_start_isk_amount_in_cargo:
                            loot_collected = True
                            self.say(f"setting loot collected to {loot_collected}")

            self.take_gate()

            # Recall drones and take gate

            room_number += 1
            self.say(f"Entering room #{room_number}")





