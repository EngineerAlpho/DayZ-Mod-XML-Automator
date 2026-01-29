#!/usr/bin/env python3
"""
DayZ Mod XML Merger
Automatically merges mod types.xml, events.xml, and spawnabletypes.xml files
into your server's XMLs, removing duplicates.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
from pathlib import Path
from datetime import datetime
import shutil

class DayZXMLMerger:
    def __init__(self, config_file="merge_config.json"):
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
                    }
                },
                "mod_search_paths": [
                    "~/serverfiles/mods",
                    "./@*",
                    "./workshop/content/221100/*"
                ],
                "merge_rules": {
                    "skip_vanilla_duplicates": True,
                    "overwrite_existing": False,
                    "preserve_comments": True
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
    
    def scan_mpmissions_folders(self):
        """Scan for mission folders in mpmissions directory"""
        mpmissions_paths = [
            "./mpmissions",
            "../mpmissions",
            "../../mpmissions",
            "./DayZServer/mpmissions",
            "/home/serverfiles/mpmissions",
            "/home/serverfiles/lgsm/config-lgsm/dayzserver/mpmissions",
            os.path.expanduser("~/serverfiles/mpmissions"),
            os.path.expanduser("~/DayZServer/mpmissions"),
        ]
        
        found_missions = []
        
        for base_path in mpmissions_paths:
            if os.path.exists(base_path) and os.path.isdir(base_path):
                print(f"  Scanning: {base_path}")
                for item in os.listdir(base_path):
                    mission_path = os.path.join(base_path, item)
                    if os.path.isdir(mission_path):
                        # Check if it has db folder (typical mission structure)
                        db_path = os.path.join(mission_path, "db")
                        if os.path.exists(db_path) or os.path.exists(os.path.join(mission_path, "cfgeventspawns.xml")):
                            mission_info = {
                                "name": item,
                                "path": mission_path,
                                "types": os.path.join(mission_path, "db", "types.xml"),
                                "events": os.path.join(mission_path, "cfgeventspawns.xml"),
                                "spawnabletypes": os.path.join(mission_path, "db", "spawnabletypes.xml")
                            }
                            # Verify at least one XML exists
                            if (os.path.exists(mission_info["types"]) or 
                                os.path.exists(mission_info["events"]) or
                                os.path.exists(mission_info["spawnabletypes"])):
                                found_missions.append(mission_info)
                                print(f"    ✓ Found: {item}")
        
        return found_missions
    
    def auto_configure_missions(self):
        """Automatically detect and configure missions"""
        print("\n" + "="*60)
        print("Auto-detecting Mission Folders")
        print("="*60)
        
        found_missions = self.scan_mpmissions_folders()
        
        if not found_missions:
            print("\n✗ No mission folders found.")
            print("Searched in:")
            print("  - ./mpmissions")
            print("  - ../mpmissions") 
            print("  - /home/serverfiles/mpmissions")
            print("  - ~/serverfiles/mpmissions")
            print("\nTip: Make sure you have at least types.xml or cfgeventspawns.xml in your mission folder.")
            return False
        
        print(f"\n✓ Found {len(found_missions)} mission folder(s):")
        for i, mission in enumerate(found_missions, 1):
            exists_marker = " (already configured)" if mission["name"] in self.config["missions"] else " (new)"
            print(f"  {i}. {mission['name']}{exists_marker}")
            if os.path.exists(mission["types"]):
                print(f"     ✓ types.xml")
            if os.path.exists(mission["events"]):
                print(f"     ✓ events.xml")
            if os.path.exists(mission["spawnabletypes"]):
                print(f"     ✓ spawnabletypes.xml")
        
        print("\nOptions:")
        print("1. Add all detected missions")
        print("2. Select specific missions to add")
        print("3. Cancel")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            added_count = 0
            for mission in found_missions:
                if mission["name"] not in self.config["missions"]:
                    self.config["missions"][mission["name"]] = {
                        "types": mission["types"],
                        "events": mission["events"],
                        "spawnabletypes": mission["spawnabletypes"]
                    }
                    added_count += 1
                    print(f"  + Added: {mission['name']}")
            
            if added_count > 0:
                # Set first new mission as active if no active mission
                if not self.config.get("active_mission") or self.config["active_mission"] not in self.config["missions"]:
                    self.config["active_mission"] = found_missions[0]["name"]
                
                self.save_config()
                print(f"\n✓ Added {added_count} mission(s)")
            else:
                print("\n- All missions already configured")
            
            return True
        
        elif choice == "2":
            print("\nSelect missions to add (comma-separated numbers, e.g., 1,3,5):")
            selected = input("Enter numbers: ").strip()
            
            try:
                indices = [int(x.strip()) - 1 for x in selected.split(",")]
                added_count = 0
                
                for idx in indices:
                    if 0 <= idx < len(found_missions):
                        mission = found_missions[idx]
                        if mission["name"] not in self.config["missions"]:
                            self.config["missions"][mission["name"]] = {
                                "types": mission["types"],
                                "events": mission["events"],
                                "spawnabletypes": mission["spawnabletypes"]
                            }
                            added_count += 1
                            print(f"  + Added: {mission['name']}")
                        else:
                            print(f"  - Skipped: {mission['name']} (already configured)")
                
                if added_count > 0:
                    if not self.config.get("active_mission") or self.config["active_mission"] not in self.config["missions"]:
                        self.config["active_mission"] = found_missions[indices[0]]["name"]
                    
                    self.save_config()
                    print(f"\n✓ Added {added_count} mission(s)")
                
                return True
                
            except (ValueError, IndexError):
                print("✗ Invalid selection")
                return False
        
        return False
    
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
        print(f"  ✓ Backup: {backup_path}")
    
    def find_mod_xml_files(self, mod_path):
        """Find types.xml, events.xml, etc. in a mod folder by searching recursively"""
        found_files = {
            "types": [],
            "events": [],
            "spawnabletypes": []
        }
        
        mod_path_obj = Path(mod_path)
        
        # Recursively find ALL .xml files in the mod folder
        try:
            all_xml_files = list(mod_path_obj.rglob("*.xml"))
        except Exception as e:
            print(f"  ⚠ Warning: Could not search {mod_path}: {e}")
            return found_files
        
        # Examine each XML file to determine its type
        for xml_file in all_xml_files:
            try:
                # Skip if file is too large (probably not a config file)
                if xml_file.stat().st_size > 50 * 1024 * 1024:  # 50MB
                    continue
                
                # Read first few lines to identify the file type
                with open(xml_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content_sample = ""
                    for i, line in enumerate(f):
                        content_sample += line
                        if i > 20:  # Read first 20 lines
                            break
                    
                    content_lower = content_sample.lower()
                    
                    # Identify types.xml - contains <types> or <type name=
                    if ('<types>' in content_lower or '<types ' in content_lower or 
                        ('<type ' in content_lower and 'name=' in content_lower)):
                        if str(xml_file) not in found_files["types"]:
                            found_files["types"].append(str(xml_file))
                    
                    # Identify events.xml - contains <eventposdef> or <event name=
                    elif ('<eventposdef' in content_lower or 
                          ('<event ' in content_lower and 'name=' in content_lower)):
                        if str(xml_file) not in found_files["events"]:
                            found_files["events"].append(str(xml_file))
                    
                    # Identify spawnabletypes.xml - contains <spawnabletypes>
                    elif '<spawnabletypes' in content_lower:
                        if str(xml_file) not in found_files["spawnabletypes"]:
                            found_files["spawnabletypes"].append(str(xml_file))
            
            except Exception as e:
                # Skip files we can't read
                continue
        
        return found_files
    
    def scan_for_mods(self):
        """Scan configured paths for mod folders"""
        mods_found = []
        
        for search_path in self.config["mod_search_paths"]:
            # Expand user home directory
            search_path = os.path.expanduser(search_path)
            
            # Handle wildcards in path
            if "*" in search_path:
                base_path = search_path.split("*")[0]
                if os.path.exists(base_path):
                    try:
                        for item in Path(base_path).parent.glob(os.path.basename(search_path)):
                            if item.is_dir():
                                mods_found.append(str(item))
                    except Exception as e:
                        print(f"  Warning: Could not scan {search_path}: {e}")
            else:
                if os.path.exists(search_path) and os.path.isdir(search_path):
                    try:
                        # List all subdirectories that start with @ (typical mod naming)
                        for item in os.listdir(search_path):
                            item_path = os.path.join(search_path, item)
                            # Check if it's a directory and starts with @ or contains "mod"
                            if os.path.isdir(item_path) and (item.startswith("@") or "mod" in item.lower()):
                                mods_found.append(item_path)
                    except PermissionError:
                        print(f"  Warning: No permission to access {search_path}")
                    except Exception as e:
                        print(f"  Warning: Could not scan {search_path}: {e}")
        
        # Remove duplicates (same mod found in multiple search paths)
        mods_found = list(set(mods_found))
        mods_found.sort()
        
        return mods_found
    
    def parse_xml_safely(self, xml_path):
        """Parse XML file with error handling"""
        try:
            tree = ET.parse(xml_path)
            return tree.getroot()
        except ET.ParseError as e:
            print(f"  ⚠ Warning: Could not parse {xml_path}: {e}")
            return None
        except Exception as e:
            print(f"  ⚠ Warning: Error reading {xml_path}: {e}")
            return None
    
    def merge_types_xml(self, server_xml_path, mod_xml_path):
        """Merge mod's types.xml into server's types.xml"""
        # Load server XML
        server_root = self.parse_xml_safely(server_xml_path)
        if server_root is None:
            server_root = ET.Element("types")
        
        # Load mod XML
        mod_root = self.parse_xml_safely(mod_xml_path)
        if mod_root is None:
            print(f"  ✗ Skipping: Could not read {mod_xml_path}")
            return 0, 0, 0  # Return tuple instead of single int
        
        # Get existing type names from server
        existing_types = {elem.get("name"): elem for elem in server_root.findall("type")}
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        # Process each type in mod XML
        for mod_type in mod_root.findall("type"):
            type_name = mod_type.get("name")
            
            if not type_name:
                continue
            
            if type_name in existing_types:
                if self.config["merge_rules"]["overwrite_existing"]:
                    # Remove old entry and add new one
                    server_root.remove(existing_types[type_name])
                    server_root.append(mod_type)
                    updated_count += 1
                    print(f"    ↻ Updated: {type_name}")
                else:
                    skipped_count += 1
                    print(f"    - Skipped: {type_name} (already exists)")
            else:
                # Add new type
                server_root.append(mod_type)
                added_count += 1
                print(f"    + Added: {type_name}")
        
        # Save merged XML
        self.save_xml(server_root, server_xml_path)
        
        return added_count, updated_count, skipped_count
    
    def merge_events_xml(self, server_xml_path, mod_xml_path):
        """Merge mod's events.xml into server's events.xml"""
        # Load server XML
        server_root = self.parse_xml_safely(server_xml_path)
        if server_root is None:
            server_root = ET.Element("eventposdef")
        
        # Load mod XML
        mod_root = self.parse_xml_safely(mod_xml_path)
        if mod_root is None:
            print(f"  ✗ Skipping: Could not read {mod_xml_path}")
            return 0, 0, 0  # Return tuple instead of single int
        
        # Get existing event names from server
        existing_events = {elem.get("name"): elem for elem in server_root.findall("event")}
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        # Process each event in mod XML
        for mod_event in mod_root.findall("event"):
            event_name = mod_event.get("name")
            
            if not event_name:
                continue
            
            if event_name in existing_events:
                if self.config["merge_rules"]["overwrite_existing"]:
                    server_root.remove(existing_events[event_name])
                    server_root.append(mod_event)
                    updated_count += 1
                    print(f"    ↻ Updated: {event_name}")
                else:
                    skipped_count += 1
                    print(f"    - Skipped: {event_name} (already exists)")
            else:
                server_root.append(mod_event)
                added_count += 1
                print(f"    + Added: {event_name}")
        
        # Save merged XML
        self.save_xml(server_root, server_xml_path)
        
        return added_count, updated_count, skipped_count
    
    def merge_spawnabletypes_xml(self, server_xml_path, mod_xml_path):
        """Merge mod's spawnabletypes.xml into server's spawnabletypes.xml"""
        # Similar to types merge
        server_root = self.parse_xml_safely(server_xml_path)
        if server_root is None:
            server_root = ET.Element("spawnabletypes")
        
        mod_root = self.parse_xml_safely(mod_xml_path)
        if mod_root is None:
            print(f"  ✗ Skipping: Could not read {mod_xml_path}")
            return 0, 0, 0  # Return tuple instead of single int
        
        existing_types = {elem.get("name"): elem for elem in server_root.findall("type")}
        
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        for mod_type in mod_root.findall("type"):
            type_name = mod_type.get("name")
            
            if not type_name:
                continue
            
            if type_name in existing_types:
                if self.config["merge_rules"]["overwrite_existing"]:
                    server_root.remove(existing_types[type_name])
                    server_root.append(mod_type)
                    updated_count += 1
                    print(f"    ↻ Updated: {type_name}")
                else:
                    skipped_count += 1
                    print(f"    - Skipped: {type_name} (already exists)")
            else:
                server_root.append(mod_type)
                added_count += 1
                print(f"    + Added: {type_name}")
        
        self.save_xml(server_root, server_xml_path)
        
        return added_count, updated_count, skipped_count
    
    def save_xml(self, root, path):
        """Save XML with proper formatting"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Write XML
        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")  # Pretty print with 4 spaces
        tree.write(path, encoding="utf-8", xml_declaration=True)
    
    def merge_mod(self, mod_path):
        """Merge all XML files from a mod into server XMLs"""
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(mod_path)}")
        print(f"{'='*60}")
        
        # Find XML files in mod
        xml_files = self.find_mod_xml_files(mod_path)
        
        if not any(xml_files.values()):
            print("  ✗ No XML files found in this mod")
            return
        
        # Get server XML paths
        server_paths = self.get_xml_paths()
        
        total_added = 0
        total_updated = 0
        total_skipped = 0
        
        # Merge types.xml
        if xml_files["types"]:
            print(f"\n  📄 Found {len(xml_files['types'])} types.xml file(s)")
            for mod_types in xml_files["types"]:
                print(f"  Merging: {mod_types}")
                server_types = server_paths.get("types")
                if server_types:
                    self.backup_xml(server_types)
                    added, updated, skipped = self.merge_types_xml(server_types, mod_types)
                    total_added += added
                    total_updated += updated
                    total_skipped += skipped
                else:
                    print("    ✗ Server types.xml path not configured")
        
        # Merge events.xml
        if xml_files["events"]:
            print(f"\n  📄 Found {len(xml_files['events'])} events.xml file(s)")
            for mod_events in xml_files["events"]:
                print(f"  Merging: {mod_events}")
                server_events = server_paths.get("events")
                if server_events:
                    self.backup_xml(server_events)
                    added, updated, skipped = self.merge_events_xml(server_events, mod_events)
                    total_added += added
                    total_updated += updated
                    total_skipped += skipped
                else:
                    print("    ✗ Server events.xml path not configured")
        
        # Merge spawnabletypes.xml
        if xml_files["spawnabletypes"]:
            print(f"\n  📄 Found {len(xml_files['spawnabletypes'])} spawnabletypes.xml file(s)")
            for mod_spawnable in xml_files["spawnabletypes"]:
                print(f"  Merging: {mod_spawnable}")
                server_spawnable = server_paths.get("spawnabletypes")
                if server_spawnable:
                    self.backup_xml(server_spawnable)
                    added, updated, skipped = self.merge_spawnabletypes_xml(server_spawnable, mod_spawnable)
                    total_added += added
                    total_updated += updated
                    total_skipped += skipped
                else:
                    print("    ✗ Server spawnabletypes.xml path not configured")
        
        print(f"\n  ✓ Summary: {total_added} added, {total_updated} updated, {total_skipped} skipped")
    
    def interactive_merge(self):
        """Interactive mode for merging mods"""
        print("\n" + "="*60)
        print("DayZ Mod XML Merger - Interactive Mode")
        print("="*60)
        
        # Show and optionally change active mission
        print(f"\nCurrent active mission: {self.config.get('active_mission', 'Not set')}")
        print("\nAvailable missions:")
        missions = self.list_missions()
        for i, mission in enumerate(missions, 1):
            marker = " ← ACTIVE" if mission == self.config.get('active_mission') else ""
            print(f"  {i}. {mission}{marker}")
        
        change_mission = input("\nChange active mission? (y/n): ").strip().lower()
        if change_mission == 'y':
            print("\nOptions:")
            print(f"1-{len(missions)}. Select existing mission")
            print(f"{len(missions)+1}. Auto-detect and add new missions")
            print(f"{len(missions)+2}. Manually add new mission")
            
            choice = input(f"\nEnter choice: ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(missions):
                    self.set_active_mission(missions[idx])
                elif idx == len(missions):
                    # Auto-detect
                    if self.auto_configure_missions():
                        # Show updated mission list and let user select
                        updated_missions = self.list_missions()
                        print("\nSelect active mission from newly added:")
                        for i, mission in enumerate(updated_missions, 1):
                            print(f"  {i}. {mission}")
                        try:
                            new_idx = int(input("Select mission: ").strip()) - 1
                            if 0 <= new_idx < len(updated_missions):
                                self.set_active_mission(updated_missions[new_idx])
                        except (ValueError, IndexError):
                            print("Using first mission")
                            if updated_missions:
                                self.set_active_mission(updated_missions[0])
                elif idx == len(missions) + 1:
                    # Manual entry
                    mission_name = input("\nEnter mission name: ").strip()
                    if mission_name:
                        default_types = f"./mpmissions/{mission_name}/db/types.xml"
                        default_events = f"./mpmissions/{mission_name}/cfgeventspawns.xml"
                        default_spawnable = f"./mpmissions/{mission_name}/db/spawnabletypes.xml"
                        
                        types_path = input(f"types.xml path [{default_types}]: ").strip()
                        events_path = input(f"events.xml path [{default_events}]: ").strip()
                        spawnable_path = input(f"spawnabletypes.xml path [{default_spawnable}]: ").strip()
                        
                        types_path = types_path if types_path else default_types
                        events_path = events_path if events_path else default_events
                        spawnable_path = spawnable_path if spawnable_path else default_spawnable
                        
                        self.add_mission(mission_name, types_path, events_path, spawnable_path)
                        self.set_active_mission(mission_name)
            except ValueError:
                print("Invalid choice")
        
        print(f"\n✓ Active mission: {self.config.get('active_mission')}")
        
        print("\nOptions:")
        print("1. Auto-scan and merge all mods")
        print("2. Merge specific mod folder")
        print("3. List available mods")
        print("4. Manage missions")
        print("5. Back to main menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            print("\nScanning for mods...")
            mods = self.scan_for_mods()
            
            if not mods:
                print("No mods found. Check your mod_search_paths in config.")
                return
            
            print(f"\nFound {len(mods)} mod folder(s):")
            for i, mod in enumerate(mods, 1):
                print(f"  {i}. {os.path.basename(mod)}")
            
            confirm = input(f"\nMerge all {len(mods)} mods? (y/n): ").strip().lower()
            if confirm == 'y':
                for mod in mods:
                    self.merge_mod(mod)
                print("\n✓ All mods processed!")
        
        elif choice == "2":
            mod_path = input("\nEnter mod folder path: ").strip()
            if os.path.exists(mod_path):
                self.merge_mod(mod_path)
            else:
                print(f"✗ Path not found: {mod_path}")
        
        elif choice == "3":
            print("\nScanning for mods...")
            mods = self.scan_for_mods()
            
            if not mods:
                print("No mods found. Check your mod_search_paths in config.")
                return
            
            print(f"\nFound {len(mods)} mod folder(s):")
            for i, mod in enumerate(mods, 1):
                print(f"  {i}. {os.path.basename(mod)}")
                xml_files = self.find_mod_xml_files(mod)
                if xml_files["types"]:
                    print(f"     - types.xml: ✓")
                if xml_files["events"]:
                    print(f"     - events.xml: ✓")
                if xml_files["spawnabletypes"]:
                    print(f"     - spawnabletypes.xml: ✓")
        
        elif choice == "4":
            manage_missions(self)
        
        elif choice == "5":
            return


def manage_missions(merger):
    """Mission management submenu"""
    while True:
        print("\n" + "="*60)
        print("Mission Management")
        print("="*60)
        print(f"\nActive Mission: {merger.config.get('active_mission', 'Not set')}")
        print("\nConfigured Missions:")
        
        missions = merger.list_missions()
        for i, mission in enumerate(missions, 1):
            marker = " ← ACTIVE" if mission == merger.config.get('active_mission') else ""
            print(f"  {i}. {mission}{marker}")
            paths = merger.config["missions"][mission]
            print(f"     types: {paths.get('types', 'N/A')}")
            print(f"     events: {paths.get('events', 'N/A')}")
        
        print("\nOptions:")
        print("1. Switch active mission")
        print("2. Add new mission")
        print("3. Remove mission")
        print("4. Edit mission paths")
        print("5. Merge to all missions")
        print("6. Back to previous menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            print("\nSelect mission:")
            for i, mission in enumerate(missions, 1):
                print(f"  {i}. {mission}")
            try:
                idx = int(input("Enter number: ").strip()) - 1
                if 0 <= idx < len(missions):
                    merger.set_active_mission(missions[idx])
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "2":
            print("\n" + "="*60)
            print("Add New Mission")
            print("="*60)
            print("\nOptions:")
            print("1. Auto-detect missions from mpmissions folder")
            print("2. Manually enter mission details")
            
            sub_choice = input("\nSelect option: ").strip()
            
            if sub_choice == "1":
                merger.auto_configure_missions()
            
            elif sub_choice == "2":
                mission_name = input("\nEnter mission name (e.g., dayzOffline.sakhal): ").strip()
                if mission_name:
                    print("\nEnter paths (or press Enter to use defaults):")
                    
                    default_types = f"./mpmissions/{mission_name}/db/types.xml"
                    default_events = f"./mpmissions/{mission_name}/cfgeventspawns.xml"
                    default_spawnable = f"./mpmissions/{mission_name}/db/spawnabletypes.xml"
                    
                    types_path = input(f"types.xml path [{default_types}]: ").strip()
                    events_path = input(f"events.xml path [{default_events}]: ").strip()
                    spawnable_path = input(f"spawnabletypes.xml path [{default_spawnable}]: ").strip()
                    
                    types_path = types_path if types_path else default_types
                    events_path = events_path if events_path else default_events
                    spawnable_path = spawnable_path if spawnable_path else default_spawnable
                    
                    merger.add_mission(mission_name, types_path, events_path, spawnable_path)
        
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
                        del merger.config["missions"][mission_to_remove]
                        if merger.config.get("active_mission") == mission_to_remove:
                            remaining = merger.list_missions()
                            if remaining:
                                merger.config["active_mission"] = remaining[0]
                        merger.save_config()
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
                    
                    current = merger.config["missions"][mission_name]
                    types_path = input(f"types.xml [{current['types']}]: ").strip()
                    events_path = input(f"events.xml [{current['events']}]: ").strip()
                    spawnable_path = input(f"spawnabletypes.xml [{current['spawnabletypes']}]: ").strip()
                    
                    if types_path:
                        current['types'] = types_path
                    if events_path:
                        current['events'] = events_path
                    if spawnable_path:
                        current['spawnabletypes'] = spawnable_path
                    
                    merger.save_config()
                    print("✓ Mission updated")
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "5":
            print("\nMerge mods to ALL missions:")
            print("This will merge all found mods into EVERY configured mission.")
            
            print("\nOptions:")
            print("1. Auto-scan and merge all mods to all missions")
            print("2. Merge specific mod folder to all missions")
            
            sub_choice = input("\nSelect option: ").strip()
            
            if sub_choice == "1":
                print("\nScanning for mods...")
                mods = merger.scan_for_mods()
                
                if not mods:
                    print("No mods found.")
                    continue
                
                print(f"\nFound {len(mods)} mod folder(s)")
                print(f"Will merge into {len(missions)} mission(s)")
                confirm = input("Continue? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    original_mission = merger.config.get('active_mission')
                    
                    for mission in missions:
                        print(f"\n{'='*60}")
                        print(f"Processing Mission: {mission}")
                        print(f"{'='*60}")
                        merger.set_active_mission(mission)
                        
                        for mod in mods:
                            merger.merge_mod(mod)
                    
                    # Restore original active mission
                    merger.set_active_mission(original_mission)
                    print("\n✓ All mods merged to all missions!")
            
            elif sub_choice == "2":
                mod_path = input("\nEnter mod folder path: ").strip()
                if not os.path.exists(mod_path):
                    print(f"✗ Path not found: {mod_path}")
                    continue
                
                print(f"\nWill merge {os.path.basename(mod_path)} into {len(missions)} mission(s)")
                confirm = input("Continue? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    original_mission = merger.config.get('active_mission')
                    
                    for mission in missions:
                        print(f"\n{'='*60}")
                        print(f"Processing Mission: {mission}")
                        print(f"{'='*60}")
                        merger.set_active_mission(mission)
                        merger.merge_mod(mod_path)
                    
                    # Restore original active mission
                    merger.set_active_mission(original_mission)
                    print("\n✓ Mod merged to all missions!")
        
        elif choice == "6":
            break
        
        else:
            print("Invalid choice.")


def main():
    """Main function"""
    merger = DayZXMLMerger()
    
    print("="*60)
    print("DayZ Mod XML Merger")
    print("="*60)
    print(f"\nActive Mission: {merger.config.get('active_mission')}")
    
    # Show quick setup hint if no missions configured or paths don't exist
    configured_missions = merger.list_missions()
    if not configured_missions:
        print("\n⚠ No missions configured! Use Quick Start (Option 1) or Auto-detect (Option 4)")
    else:
        active_paths = merger.get_xml_paths()
        if active_paths and not os.path.exists(active_paths.get("types", "")):
            print(f"\n⚠ Warning: Active mission XML paths may be incorrect")
    
    print("\nOptions:")
    print("1. Quick Start (auto-detect + merge)")
    print("2. Interactive merge")
    print("3. Manage missions")
    print("4. Auto-detect missions only")
    print("5. Edit configuration")
    print("6. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        # Quick Start - Auto-detect and merge
        print("\n" + "="*60)
        print("QUICK START - Auto Setup & Merge")
        print("="*60)
        
        # Check if missions need to be configured
        if not merger.list_missions() or not merger.get_xml_paths():
            print("\nStep 1: Auto-detecting missions...")
            if not merger.auto_configure_missions():
                print("\n✗ Could not detect missions. Try manual setup.")
                return
        else:
            print("\n✓ Missions already configured")
        
        # Show current mission and allow change
        print(f"\nActive Mission: {merger.config.get('active_mission')}")
        missions = merger.list_missions()
        
        if len(missions) > 1:
            print("\nAvailable missions:")
            for i, mission in enumerate(missions, 1):
                marker = " ← ACTIVE" if mission == merger.config.get('active_mission') else ""
                print(f"  {i}. {mission}{marker}")
            
            change = input("\nChange active mission? (y/n): ").strip().lower()
            if change == 'y':
                try:
                    idx = int(input(f"Select mission (1-{len(missions)}): ").strip()) - 1
                    if 0 <= idx < len(missions):
                        merger.set_active_mission(missions[idx])
                except (ValueError, IndexError):
                    print("Invalid selection, keeping current mission")
        
        # Now scan and merge mods
        print(f"\nStep 2: Scanning for mods...")
        mods = merger.scan_for_mods()
        
        if not mods:
            print("\n✗ No mods found. Check your mod_search_paths in config.")
            print("Mod search paths:")
            for path in merger.config.get('mod_search_paths', []):
                print(f"  - {path}")
            return
        
        print(f"\n✓ Found {len(mods)} mod folder(s):")
        for i, mod in enumerate(mods, 1):
            print(f"  {i}. {os.path.basename(mod)}")
        
        confirm = input(f"\nMerge all {len(mods)} mods into {merger.config.get('active_mission')}? (y/n): ").strip().lower()
        if confirm == 'y':
            for mod in mods:
                merger.merge_mod(mod)
            print("\n" + "="*60)
            print("✓ QUICK START COMPLETE!")
            print("="*60)
            print(f"All mods have been merged into {merger.config.get('active_mission')}")
        else:
            print("\nCancelled.")
    
    elif choice == "2":
        merger.interactive_merge()
    
    elif choice == "3":
        manage_missions(merger)
    
    elif choice == "4":
        merger.auto_configure_missions()
    
    elif choice == "5":
        print(f"\nConfiguration file: {merger.config_file}")
        print("\nKey settings:")
        print(f"  - Active mission: {merger.config.get('active_mission')}")
        print(f"  - Mod search paths: {merger.config.get('mod_search_paths')}")
        print(f"  - Overwrite existing: {merger.config['merge_rules']['overwrite_existing']}")
        print("\nEdit the config file manually and restart the script.")
    
    elif choice == "6":
        print("Goodbye!")
    
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
