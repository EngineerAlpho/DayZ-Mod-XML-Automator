#!/usr/bin/env python3
"""
DayZ Mod XML Automator
Automatically generates and updates types.xml, events.xml, and spawnabletypes.xml
for DayZ mods.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
from pathlib import Path
from datetime import datetime
import shutil

class DayZXMLAutomator:
    def __init__(self, config_file="mod_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load or create configuration file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "backup_enabled": True,
                "backup_folder": "./backups",
                "active_mission": "dayzOffline.chernarusplus",
                "missions": {
                    "dayzOffline.chernarusplus": {
                        "types": "./mpmissions/dayzOffline.chernarusplus/db/types.xml",
                        "events": "./mpmissions/dayzOffline.chernarusplus/cfgeventspawns.xml",
                        "spawnabletypes": "./mpmissions/dayzOffline.chernarusplus/db/spawnabletypes.xml"
                    },
                    "dayzOffline.enoch": {
                        "types": "./mpmissions/dayzOffline.enoch/db/types.xml",
                        "events": "./mpmissions/dayzOffline.enoch/cfgeventspawns.xml",
                        "spawnabletypes": "./mpmissions/dayzOffline.enoch/db/spawnabletypes.xml"
                    },
                    "dayzOffline.sakhal": {
                        "types": "./mpmissions/dayzOffline.sakhal/db/types.xml",
                        "events": "./mpmissions/dayzOffline.sakhal/cfgeventspawns.xml",
                        "spawnabletypes": "./mpmissions/dayzOffline.sakhal/db/spawnabletypes.xml"
                    }
                },
                "mod_folders": [
                    "@DayZ-Expansion-Weapons",
                    "@DayZ-Expansion-Vehicles"
                ],
                "default_values": {
                    "weapons": {
                        "nominal": 10,
                        "min": 5,
                        "quantmin": -1,
                        "quantmax": -1,
                        "cost": 100,
                        "lifetime": 3600,
                        "restock": 1800,
                        "flags": ["count_in_cargo", "count_in_hoarder", "count_in_map", "count_in_player"],
                        "category": "weapons",
                        "usage": ["Military", "Police"]
                    },
                    "vehicles": {
                        "nominal": 3,
                        "min": 1,
                        "quantmin": -1,
                        "quantmax": -1,
                        "cost": 100,
                        "lifetime": 3888000,
                        "restock": 0,
                        "flags": ["count_in_map", "count_in_player"],
                        "category": "vehicles",
                        "usage": ["Industrial", "Farm"]
                    },
                    "items": {
                        "nominal": 20,
                        "min": 10,
                        "quantmin": -1,
                        "quantmax": -1,
                        "cost": 100,
                        "lifetime": 3600,
                        "restock": 1800,
                        "flags": ["count_in_cargo", "count_in_hoarder", "count_in_map", "count_in_player"],
                        "category": "tools",
                        "usage": ["Town", "Village"]
                    }
                },
                "vehicle_events": {
                    "enabled": True,
                    "default_event": {
                        "nominal": 2,
                        "min": 1,
                        "max": 3,
                        "lifetime": 3888000,
                        "restock": 0,
                        "saferadius": 500,
                        "distanceradius": 500,
                        "cleanupradius": 200
                    }
                }
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"✓ Configuration saved to {self.config_file}")
    
    def get_xml_paths(self):
        """Get XML paths for the active mission"""
        active_mission = self.config.get("active_mission", "dayzOffline.chernarusplus")
        return self.config["missions"].get(active_mission, {})
    
    def list_missions(self):
        """List all configured missions"""
        return list(self.config["missions"].keys())
    
    def set_active_mission(self, mission_name):
        """Set the active mission"""
        if mission_name in self.config["missions"]:
            self.config["active_mission"] = mission_name
            self.save_config()
            print(f"✓ Active mission set to: {mission_name}")
            return True
        else:
            print(f"✗ Mission '{mission_name}' not found in configuration")
            return False
    
    def add_mission(self, mission_name, types_path, events_path, spawnabletypes_path):
        """Add a new mission to configuration"""
        self.config["missions"][mission_name] = {
            "types": types_path,
            "events": events_path,
            "spawnabletypes": spawnabletypes_path
        }
        self.save_config()
        print(f"✓ Added mission: {mission_name}")
    
    def backup_xml(self, xml_path):
        """Create a backup of XML file"""
        if not self.config["backup_enabled"]:
            return
        
        if not os.path.exists(xml_path):
            return
        
        backup_dir = self.config["backup_folder"]
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(xml_path)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        
        shutil.copy2(xml_path, backup_path)
        print(f"✓ Backup created: {backup_path}")
    
    def prettify_xml(self, elem):
        """Return a pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")
    
    def scan_mod_classes(self, mod_folder):
        """
        Scan mod folder for class names
        This is a simplified version - in reality, you'd parse config.cpp files
        For now, it returns a manual list that users can populate
        """
        classes = {
            "weapons": [],
            "vehicles": [],
            "items": []
        }
        
        # This is where you'd implement config.cpp parsing
        # For now, return empty - users will populate manually or we can add auto-detection
        print(f"Note: Scanning {mod_folder} - manual class list needed for now")
        
        return classes
    
    def load_existing_xml(self, xml_path):
        """Load existing XML file or create new structure"""
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                return tree.getroot()
            except ET.ParseError as e:
                print(f"⚠ Error parsing {xml_path}: {e}")
                return None
        return None
    
    def create_types_entry(self, classname, item_type="weapons"):
        """Create a types.xml entry for an item/vehicle"""
        defaults = self.config["default_values"].get(item_type, self.config["default_values"]["items"])
        
        type_elem = ET.Element("type", name=classname)
        
        # Add numerical values
        ET.SubElement(type_elem, "nominal").text = str(defaults["nominal"])
        ET.SubElement(type_elem, "lifetime").text = str(defaults["lifetime"])
        ET.SubElement(type_elem, "restock").text = str(defaults["restock"])
        ET.SubElement(type_elem, "min").text = str(defaults["min"])
        ET.SubElement(type_elem, "quantmin").text = str(defaults["quantmin"])
        ET.SubElement(type_elem, "quantmax").text = str(defaults["quantmax"])
        ET.SubElement(type_elem, "cost").text = str(defaults["cost"])
        
        # Add flags
        flags_elem = ET.SubElement(type_elem, "flags")
        flags_elem.set("count_in_cargo", "1" if "count_in_cargo" in defaults["flags"] else "0")
        flags_elem.set("count_in_hoarder", "1" if "count_in_hoarder" in defaults["flags"] else "0")
        flags_elem.set("count_in_map", "1" if "count_in_map" in defaults["flags"] else "0")
        flags_elem.set("count_in_player", "1" if "count_in_player" in defaults["flags"] else "0")
        flags_elem.set("crafted", "0")
        flags_elem.set("deloot", "0")
        
        # Add category
        ET.SubElement(type_elem, "category", name=defaults["category"])
        
        # Add usage tags
        for usage in defaults["usage"]:
            ET.SubElement(type_elem, "usage", name=usage)
        
        return type_elem
    
    def create_event_entry(self, vehicle_classname):
        """Create an events.xml entry for a vehicle"""
        if not self.config["vehicle_events"]["enabled"]:
            return None
        
        defaults = self.config["vehicle_events"]["default_event"]
        
        event_elem = ET.Element("event", name=f"{vehicle_classname}_Event")
        
        ET.SubElement(event_elem, "nominal").text = str(defaults["nominal"])
        ET.SubElement(event_elem, "min").text = str(defaults["min"])
        ET.SubElement(event_elem, "max").text = str(defaults["max"])
        ET.SubElement(event_elem, "lifetime").text = str(defaults["lifetime"])
        ET.SubElement(event_elem, "restock").text = str(defaults["restock"])
        ET.SubElement(event_elem, "saferadius").text = str(defaults["saferadius"])
        ET.SubElement(event_elem, "distanceradius").text = str(defaults["distanceradius"])
        ET.SubElement(event_elem, "cleanupradius").text = str(defaults["cleanupradius"])
        
        ET.SubElement(event_elem, "flags", deletable="1")
        ET.SubElement(event_elem, "position").text = "fixed"
        ET.SubElement(event_elem, "limit").text = "child"
        ET.SubElement(event_elem, "active").text = "1"
        
        # Add child element for the vehicle
        children_elem = ET.SubElement(event_elem, "children")
        child_elem = ET.SubElement(children_elem, "child", lootmax="0", lootmin="0", max="3", min="1", type=vehicle_classname)
        
        return event_elem
    
    def update_types_xml(self, new_items):
        """Update types.xml with new items"""
        xml_paths = self.get_xml_paths()
        xml_path = xml_paths.get("types")
        
        if not xml_path:
            print("✗ No types.xml path configured for active mission")
            return 0
        
        self.backup_xml(xml_path)
        
        root = self.load_existing_xml(xml_path)
        if root is None:
            root = ET.Element("types")
        
        # Get existing type names
        existing_types = {elem.get("name") for elem in root.findall("type")}
        
        added_count = 0
        for item_type, classnames in new_items.items():
            for classname in classnames:
                if classname not in existing_types:
                    type_entry = self.create_types_entry(classname, item_type)
                    root.append(type_entry)
                    added_count += 1
                    print(f"  + Added {classname} to types.xml")
                else:
                    print(f"  - Skipped {classname} (already exists)")
        
        # Save updated XML
        os.makedirs(os.path.dirname(xml_path), exist_ok=True)
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        
        print(f"\n✓ types.xml updated: {added_count} new entries added")
        return added_count
    
    def update_events_xml(self, vehicle_classnames):
        """Update events.xml with new vehicle events"""
        if not self.config["vehicle_events"]["enabled"]:
            print("Vehicle events disabled in config")
            return 0
        
        xml_paths = self.get_xml_paths()
        xml_path = xml_paths.get("events")
        
        if not xml_path:
            print("✗ No events.xml path configured for active mission")
            return 0
        
        self.backup_xml(xml_path)
        
        root = self.load_existing_xml(xml_path)
        if root is None:
            root = ET.Element("eventposdef")
        
        # Get existing event names
        existing_events = {elem.get("name") for elem in root.findall("event")}
        
        added_count = 0
        for classname in vehicle_classnames:
            event_name = f"{classname}_Event"
            if event_name not in existing_events:
                event_entry = self.create_event_entry(classname)
                if event_entry is not None:
                    root.append(event_entry)
                    added_count += 1
                    print(f"  + Added {event_name} to events.xml")
            else:
                print(f"  - Skipped {event_name} (already exists)")
        
        # Save updated XML
        os.makedirs(os.path.dirname(xml_path), exist_ok=True)
        tree = ET.ElementTree(root)
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        
        print(f"\n✓ events.xml updated: {added_count} new events added")
        return added_count
    
    def add_items_from_list(self, items_dict):
        """
        Add items from a dictionary
        Format: {"weapons": ["classname1", "classname2"], "vehicles": [...], "items": [...]}
        """
        print("\n" + "="*50)
        print("Adding items to XMLs...")
        print(f"Active Mission: {self.config.get('active_mission', 'Not set')}")
        print("="*50)
        
        xml_paths = self.get_xml_paths()
        if not xml_paths:
            print("✗ No XML paths configured for active mission!")
            return
        
        print(f"\nTarget XMLs:")
        print(f"  types.xml: {xml_paths.get('types', 'Not configured')}")
        print(f"  events.xml: {xml_paths.get('events', 'Not configured')}")
        
        # Update types.xml
        self.update_types_xml(items_dict)
        
        # Update events.xml for vehicles
        if "vehicles" in items_dict and items_dict["vehicles"]:
            self.update_events_xml(items_dict["vehicles"])
        
        print("\n✓ All XMLs updated successfully!")
    
    def interactive_add(self):
        """Interactive mode for adding items"""
        print("\n" + "="*50)
        print("DayZ Mod XML Automator - Interactive Mode")
        print("="*50)
        
        # Show and optionally change active mission
        print(f"\nCurrent active mission: {self.config.get('active_mission', 'Not set')}")
        print("\nAvailable missions:")
        missions = self.list_missions()
        for i, mission in enumerate(missions, 1):
            marker = "←" if mission == self.config.get('active_mission') else ""
            print(f"  {i}. {mission} {marker}")
        
        change_mission = input("\nChange active mission? (y/n): ").strip().lower()
        if change_mission == 'y':
            choice = input(f"Select mission (1-{len(missions)}) or enter custom name: ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(missions):
                    self.set_active_mission(missions[idx])
            except ValueError:
                # Custom mission name entered
                if choice:
                    print(f"\nAdding new mission: {choice}")
                    types_path = input("Enter types.xml path: ").strip()
                    events_path = input("Enter events.xml path: ").strip()
                    spawnable_path = input("Enter spawnabletypes.xml path: ").strip()
                    self.add_mission(choice, types_path, events_path, spawnable_path)
                    self.set_active_mission(choice)
        
        items_dict = {"weapons": [], "vehicles": [], "items": []}
        
        print("\nWhat type of items do you want to add?")
        print("1. Weapons")
        print("2. Vehicles")
        print("3. Other Items")
        print("4. All types")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice in ["1", "4"]:
            print("\nEnter weapon classnames (one per line, empty line to finish):")
            while True:
                classname = input("Weapon: ").strip()
                if not classname:
                    break
                items_dict["weapons"].append(classname)
        
        if choice in ["2", "4"]:
            print("\nEnter vehicle classnames (one per line, empty line to finish):")
            while True:
                classname = input("Vehicle: ").strip()
                if not classname:
                    break
                items_dict["vehicles"].append(classname)
        
        if choice in ["3", "4"]:
            print("\nEnter item classnames (one per line, empty line to finish):")
            while True:
                classname = input("Item: ").strip()
                if not classname:
                    break
                items_dict["items"].append(classname)
        
        if any(items_dict.values()):
            print("\nReview items to add:")
            for item_type, classnames in items_dict.items():
                if classnames:
                    print(f"\n{item_type.upper()}:")
                    for classname in classnames:
                        print(f"  - {classname}")
            
            confirm = input("\nProceed with adding these items? (y/n): ").strip().lower()
            if confirm == 'y':
                self.add_items_from_list(items_dict)
            else:
                print("Cancelled.")
        else:
            print("No items to add.")


def main():
    """Main function"""
    automator = DayZXMLAutomator()
    
    print("="*50)
    print("DayZ Mod XML Automator")
    print("="*50)
    print(f"\nActive Mission: {automator.config.get('active_mission', 'Not set')}")
    print("\nOptions:")
    print("1. Interactive mode (manually enter classnames)")
    print("2. Add from JSON file")
    print("3. Manage missions (add/switch/view)")
    print("4. Edit configuration")
    print("5. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        automator.interactive_add()
    
    elif choice == "2":
        json_file = input("Enter JSON file path: ").strip()
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                items_dict = json.load(f)
            automator.add_items_from_list(items_dict)
        else:
            print(f"File not found: {json_file}")
    
    elif choice == "3":
        manage_missions(automator)
    
    elif choice == "4":
        print("\nCurrent configuration saved in:", automator.config_file)
        print("Edit the file manually and restart the script.")
    
    elif choice == "5":
        print("Goodbye!")
    
    else:
        print("Invalid choice.")


def manage_missions(automator):
    """Mission management submenu"""
    while True:
        print("\n" + "="*50)
        print("Mission Management")
        print("="*50)
        print(f"\nActive Mission: {automator.config.get('active_mission', 'Not set')}")
        print("\nConfigured Missions:")
        
        missions = automator.list_missions()
        for i, mission in enumerate(missions, 1):
            marker = " ← ACTIVE" if mission == automator.config.get('active_mission') else ""
            print(f"  {i}. {mission}{marker}")
            paths = automator.config["missions"][mission]
            print(f"     types: {paths.get('types', 'N/A')}")
            print(f"     events: {paths.get('events', 'N/A')}")
        
        print("\nOptions:")
        print("1. Switch active mission")
        print("2. Add new mission")
        print("3. Remove mission")
        print("4. Edit mission paths")
        print("5. Apply to all missions")
        print("6. Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            print("\nSelect mission:")
            for i, mission in enumerate(missions, 1):
                print(f"  {i}. {mission}")
            try:
                idx = int(input("Enter number: ").strip()) - 1
                if 0 <= idx < len(missions):
                    automator.set_active_mission(missions[idx])
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "2":
            mission_name = input("\nEnter mission name (e.g., dayzOffline.enoch): ").strip()
            if mission_name:
                types_path = input("Enter types.xml path: ").strip()
                events_path = input("Enter events.xml path: ").strip()
                spawnable_path = input("Enter spawnabletypes.xml path: ").strip()
                automator.add_mission(mission_name, types_path, events_path, spawnable_path)
        
        elif choice == "3":
            print("\nSelect mission to remove:")
            for i, mission in enumerate(missions, 1):
                print(f"  {i}. {mission}")
            try:
                idx = int(input("Enter number: ").strip()) - 1
                if 0 <= idx < len(missions):
                    mission_to_remove = missions[idx]
                    confirm = input(f"Remove '{mission_to_remove}'? (y/n): ").strip().lower()
                    if confirm == 'y':
                        del automator.config["missions"][mission_to_remove]
                        if automator.config.get("active_mission") == mission_to_remove:
                            remaining = automator.list_missions()
                            if remaining:
                                automator.config["active_mission"] = remaining[0]
                        automator.save_config()
                        print(f"✓ Removed mission: {mission_to_remove}")
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "4":
            print("\nSelect mission to edit:")
            for i, mission in enumerate(missions, 1):
                print(f"  {i}. {mission}")
            try:
                idx = int(input("Enter number: ").strip()) - 1
                if 0 <= idx < len(missions):
                    mission_name = missions[idx]
                    print(f"\nEditing: {mission_name}")
                    print("Leave blank to keep current value")
                    
                    current = automator.config["missions"][mission_name]
                    types_path = input(f"types.xml [{current['types']}]: ").strip()
                    events_path = input(f"events.xml [{current['events']}]: ").strip()
                    spawnable_path = input(f"spawnabletypes.xml [{current['spawnabletypes']}]: ").strip()
                    
                    if types_path:
                        current['types'] = types_path
                    if events_path:
                        current['events'] = events_path
                    if spawnable_path:
                        current['spawnabletypes'] = spawnable_path
                    
                    automator.save_config()
                    print("✓ Mission updated")
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "5":
            print("\nApply items to ALL missions:")
            print("This will add the items to types.xml and events.xml for EVERY configured mission.")
            confirm = input("Continue? (y/n): ").strip().lower()
            
            if confirm == 'y':
                json_file = input("Enter JSON file path with items: ").strip()
                if os.path.exists(json_file):
                    with open(json_file, 'r') as f:
                        items_dict = json.load(f)
                    
                    original_mission = automator.config.get('active_mission')
                    
                    for mission in missions:
                        print(f"\n{'='*50}")
                        print(f"Processing: {mission}")
                        print(f"{'='*50}")
                        automator.set_active_mission(mission)
                        automator.add_items_from_list(items_dict)
                    
                    # Restore original active mission
                    automator.set_active_mission(original_mission)
                    print("\n✓ Items added to all missions!")
                else:
                    print(f"File not found: {json_file}")
        
        elif choice == "6":
            break
        
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
