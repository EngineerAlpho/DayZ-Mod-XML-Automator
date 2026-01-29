# Multi-Mission Support Guide

## Overview

The script now supports managing XMLs for multiple mission folders! This is essential if you run:
- Multiple maps (Chernarus, Livonia, Sakhal, Takistan, etc.)
- Multiple game modes (Survival, PvP, Deathmatch, etc.)
- Test and production servers

## Quick Start

### First Time Setup

1. Run the script - it creates default missions:
   ```bash
   python dayz_mod_xml_automator.py
   ```

2. The default config includes:
   - `dayzOffline.chernarusplus` (Chernarus)
   - `dayzOffline.enoch` (Livonia)
   - `dayzOffline.sakhal` (Sakhal)

3. Edit `mod_config.json` to match your actual mission folders

## Configuration Structure

```json
{
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
        "MyCustomPvPServer": {
            "types": "./mpmissions/MyCustomPvPServer/db/types.xml",
            "events": "./mpmissions/MyCustomPvPServer/cfgeventspawns.xml",
            "spawnabletypes": "./mpmissions/MyCustomPvPServer/db/spawnabletypes.xml"
        }
    }
}
```

## Usage Scenarios

### Scenario 1: Add Items to One Mission

```bash
python dayz_mod_xml_automator.py
# Select: 1 (Interactive)
# Change mission if needed: y
# Select your mission
# Add items as normal
```

### Scenario 2: Add Items to All Missions

Perfect for server-wide mods that should be on all maps:

```bash
python dayz_mod_xml_automator.py
# Select: 3 (Manage missions)
# Select: 5 (Apply to all missions)
# Enter your JSON file
```

This automatically:
1. Loops through ALL configured missions
2. Updates types.xml for each
3. Updates events.xml for each
4. Creates backups for each

### Scenario 3: Different Items per Mission

Maybe you want military weapons on Chernarus but not on your PvE Livonia server:

```bash
# First, add items to Chernarus
python dayz_mod_xml_automator.py
# Select: 1 (Interactive)
# Switch to: dayzOffline.chernarusplus
# Add military items

# Then, add different items to Livonia
python dayz_mod_xml_automator.py
# Select: 1 (Interactive)
# Switch to: dayzOffline.enoch
# Add civilian items only
```

## Mission Management Menu

Access via **Option 3** in main menu:

### 1. Switch Active Mission
Changes which mission XMLs will be modified:
```
Active Mission: dayzOffline.chernarusplus
→ Switch to: dayzOffline.enoch
✓ Active mission set to: dayzOffline.enoch
```

### 2. Add New Mission
Add a custom mission folder:
```
Enter mission name: MyDeathmatchServer
Enter types.xml path: ./mpmissions/MyDeathmatchServer/db/types.xml
Enter events.xml path: ./mpmissions/MyDeathmatchServer/cfgeventspawns.xml
Enter spawnabletypes.xml path: ./mpmissions/MyDeathmatchServer/db/spawnabletypes.xml
✓ Added mission: MyDeathmatchServer
```

### 3. Remove Mission
Delete a mission from configuration (doesn't delete actual files):
```
Select mission to remove:
  1. dayzOffline.chernarusplus
  2. TestServer
Remove 'TestServer'? (y/n): y
✓ Removed mission: TestServer
```

### 4. Edit Mission Paths
Update paths for existing missions:
```
Editing: dayzOffline.chernarusplus
types.xml [./mpmissions/dayzOffline.chernarusplus/db/types.xml]: 
events.xml [./mpmissions/dayzOffline.chernarusplus/cfgeventspawns.xml]: ./newpath/events.xml
✓ Mission updated
```

### 5. Apply to All Missions
Batch add items to every configured mission

### 6. Back to Main Menu

## Common Workflows

### Workflow 1: New Mod, All Maps
You installed a vehicle pack that should be on all maps:

1. Create JSON file:
   ```json
   {
       "vehicles": ["ExpansionUAZ", "ExpansionBus", "ExpansionTractor"]
   }
   ```

2. Run script:
   ```bash
   python dayz_mod_xml_automator.py
   ```

3. Select: **3** (Manage missions)
4. Select: **5** (Apply to all missions)
5. Enter: `vehicle_pack.json`

Done! All missions updated.

### Workflow 2: Map-Specific Content
You want snowy vehicles only on Sakhal:

1. Switch to Sakhal:
   ```bash
   python dayz_mod_xml_automator.py
   # Select: 3 (Manage missions)
   # Select: 1 (Switch active mission)
   # Choose: dayzOffline.sakhal
   ```

2. Add items (Interactive or JSON)

3. Other missions remain unchanged

### Workflow 3: Testing New Mods
You have a test server and production server:

**Test first:**
```bash
python dayz_mod_xml_automator.py
# Switch to: TestServer
# Add new mod items
# Test in-game
```

**Then deploy to production:**
```bash
python dayz_mod_xml_automator.py
# Switch to: ProductionServer
# Add same items (reuse JSON file!)
```

## Command Line Quick Reference

| Action | Steps |
|--------|-------|
| See active mission | Run script, shown at top |
| Switch mission | Main menu → 3 → 1 |
| Add new mission | Main menu → 3 → 2 |
| Remove mission | Main menu → 3 → 3 |
| Edit mission paths | Main menu → 3 → 4 |
| Apply to all missions | Main menu → 3 → 5 |

## Tips & Best Practices

✅ **Use descriptive mission names**: Instead of "mission1", use "ChernarusPvE" or "LivioniaDeathmatch"

✅ **Keep backups organized**: Each mission's backups are stored together with timestamps

✅ **Test on one mission first**: Before applying to all, test on your dev/test mission

✅ **Use JSON files for consistency**: Create one JSON file and reuse it across missions

✅ **Document your setup**: Add comments in your JSON about which missions use which mods

✅ **Verify paths**: Double-check paths when adding new missions - typos will cause errors

## Troubleshooting

**"No XML paths configured for active mission"**
- Check `active_mission` in config matches a mission key
- Verify the mission has types/events paths defined

**Changes not appearing in-game**
- Make sure you switched to the correct mission
- Restart the server after XML changes
- Check you're on the right map/mission in-game

**Applied to wrong mission**
- Use backups in `./backups/` folder
- Each backup has timestamp and mission in filename
- Copy backup over current XML file

**Multiple servers, same mod_config.json**
- Keep separate `mod_config.json` per server
- Or use different config filenames and specify with: `DayZXMLAutomator("server1_config.json")`

## Example: Complete Multi-Server Setup

```json
{
    "active_mission": "ChernarusPvE",
    "missions": {
        "ChernarusPvE": {
            "types": "./servers/pve/mpmissions/dayzOffline.chernarusplus/db/types.xml",
            "events": "./servers/pve/mpmissions/dayzOffline.chernarusplus/cfgeventspawns.xml",
            "spawnabletypes": "./servers/pve/mpmissions/dayzOffline.chernarusplus/db/spawnabletypes.xml"
        },
        "ChernarusPvP": {
            "types": "./servers/pvp/mpmissions/dayzOffline.chernarusplus/db/types.xml",
            "events": "./servers/pvp/mpmissions/dayzOffline.chernarusplus/cfgeventspawns.xml",
            "spawnabletypes": "./servers/pvp/mpmissions/dayzOffline.chernarusplus/db/spawnabletypes.xml"
        },
        "LivoniaSurvival": {
            "types": "./servers/livonia/mpmissions/dayzOffline.enoch/db/types.xml",
            "events": "./servers/livonia/mpmissions/dayzOffline.enoch/cfgeventspawns.xml",
            "spawnabletypes": "./servers/livonia/mpmissions/dayzOffline.enoch/db/spawnabletypes.xml"
        },
        "TestServer": {
            "types": "./testserver/mpmissions/test/db/types.xml",
            "events": "./testserver/mpmissions/test/cfgeventspawns.xml",
            "spawnabletypes": "./testserver/mpmissions/test/db/spawnabletypes.xml"
        }
    },
    "default_values": {
        // Your spawn rate configs...
    }
}
```

## Advanced: Scripted Mission Switching

For automation in batch scripts:

```python
from dayz_mod_xml_automator import DayZXMLAutomator
import json

automator = DayZXMLAutomator()
items = json.load(open("expansion_vehicles.json"))

# Add to all missions
for mission in automator.list_missions():
    automator.set_active_mission(mission)
    automator.add_items_from_list(items)
```

---

**The multi-mission feature gives you complete flexibility to manage complex DayZ server setups with ease!** 🚀
