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
                    "./mods",
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
    
    def get_xml_paths(self):
        """Get XML paths for the active mission"""
        active_mission = self.config.get("active_mission", "dayzOffline.chernarusplus")
        return self.config["missions"].get(active_mission, {})
    
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
        """Find types.xml, events.xml, etc. in a mod folder"""
        found_files = {
            "types": [],
            "events": [],
            "spawnabletypes": []
        }
        
        # Common locations for XML files in mods
        search_patterns = [
            "types.xml",
            "*/types.xml",
            "db/types.xml",
            "mission/db/types.xml",
            "cfgeventspawns.xml",
            "*/cfgeventspawns.xml",
            "spawnabletypes.xml",
            "*/spawnabletypes.xml",
            "db/spawnabletypes.xml"
        ]
        
        mod_path_obj = Path(mod_path)
        
        # Search for types.xml
        for pattern in ["types.xml", "*/types.xml", "db/types.xml", "mission/db/types.xml", "**/types.xml"]:
            for file in mod_path_obj.glob(pattern):
                if file.is_file():
                    found_files["types"].append(str(file))
        
        # Search for events.xml
        for pattern in ["cfgeventspawns.xml", "*/cfgeventspawns.xml", "**/cfgeventspawns.xml", "events.xml", "**/events.xml"]:
            for file in mod_path_obj.glob(pattern):
                if file.is_file():
                    found_files["events"].append(str(file))
        
        # Search for spawnabletypes.xml
        for pattern in ["spawnabletypes.xml", "*/spawnabletypes.xml", "db/spawnabletypes.xml", "**/spawnabletypes.xml"]:
            for file in mod_path_obj.glob(pattern):
                if file.is_file():
                    found_files["spawnabletypes"].append(str(file))
        
        return found_files
    
    def scan_for_mods(self):
        """Scan configured paths for mod folders"""
        mods_found = []
        
        for search_path in self.config["mod_search_paths"]:
            # Handle wildcards in path
            if "*" in search_path:
                base_path = search_path.split("*")[0]
                if os.path.exists(base_path):
                    for item in Path(base_path).parent.glob(os.path.basename(search_path)):
                        if item.is_dir():
                            mods_found.append(str(item))
            else:
                if os.path.exists(search_path) and os.path.isdir(search_path):
                    # List all subdirectories
                    for item in os.listdir(search_path):
                        item_path = os.path.join(search_path, item)
                        if os.path.isdir(item_path):
                            mods_found.append(item_path)
        
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
            return 0
        
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
            return 0
        
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
            return 0
        
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
        
        print(f"\nActive mission: {self.config.get('active_mission')}")
        
        print("\nOptions:")
        print("1. Auto-scan and merge all mods")
        print("2. Merge specific mod folder")
        print("3. List available mods")
        print("4. Change active mission")
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
            missions = list(self.config["missions"].keys())
            print("\nAvailable missions:")
            for i, mission in enumerate(missions, 1):
                marker = " ← ACTIVE" if mission == self.config.get("active_mission") else ""
                print(f"  {i}. {mission}{marker}")
            
            try:
                idx = int(input("\nSelect mission: ").strip()) - 1
                if 0 <= idx < len(missions):
                    self.config["active_mission"] = missions[idx]
                    self.save_config()
                    print(f"✓ Active mission: {missions[idx]}")
            except (ValueError, IndexError):
                print("Invalid selection")
        
        elif choice == "5":
            return


def main():
    """Main function"""
    merger = DayZXMLMerger()
    
    print("="*60)
    print("DayZ Mod XML Merger")
    print("="*60)
    print(f"\nActive Mission: {merger.config.get('active_mission')}")
    print("\nOptions:")
    print("1. Interactive merge")
    print("2. Edit configuration")
    print("3. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        merger.interactive_merge()
    
    elif choice == "2":
        print(f"\nConfiguration file: {merger.config_file}")
        print("\nKey settings:")
        print(f"  - Active mission: {merger.config.get('active_mission')}")
        print(f"  - Mod search paths: {merger.config.get('mod_search_paths')}")
        print(f"  - Overwrite existing: {merger.config['merge_rules']['overwrite_existing']}")
        print("\nEdit the config file manually and restart the script.")
    
    elif choice == "3":
        print("Goodbye!")
    
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
