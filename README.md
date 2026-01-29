# DayZ Mod XML Merger

**This is the script you actually need!** It automatically merges mod XML files into your server XMLs.

## What This Does

✅ **Scans your mod folders** for types.xml, events.xml, spawnabletypes.xml  
✅ **Automatically merges** them into your server's XMLs  
✅ **Removes duplicates** - won't add items that already exist  
✅ **No manual work** - no JSON files, no typing classnames  
✅ **Backs up everything** before making changes

## How It Works

```
Your Mod Folder:
  @DayZ-Expansion-Weapons/
    ├── Any folder structure         ← Script searches EVERYTHING
    │   ├── types.xml                ← Finds this
    │   └── subfolder/
    │       └── cfgeventspawns.xml   ← Finds this too
    └── Another_Random_Folder/
        └── MyTypes.xml              ← Finds this (if it contains <types>)

Your Server:
  mpmissions/dayzOffline.chernarusplus/db/
    └── types.xml          ← Script merges into this
```

The script intelligently searches **every subdirectory** in the mod folder and identifies XML files by their **content**, not their filename or location. This means it works with ANY mod structure, regardless of how the mod author organized their files.

### Intelligent XML Detection

Instead of looking for specific filenames or paths, the script:
- Recursively searches for **all .xml files** in the mod folder
- Reads the first few lines of each file
- Identifies the file type by its XML structure:
  - Contains `<types>` or `<type name=` → types.xml
  - Contains `<eventposdef>` or `<event name=` → events.xml
  - Contains `<spawnabletypes>` → spawnabletypes.xml

This works with:
- ✅ Any folder structure (xml/, XML/, Server Files/, Documentation/, etc.)
- ✅ Any filename (types.xml, Types.xml, MyModTypes.xml, etc.)
- ✅ Windows or Linux naming conventions
- ✅ Messy mod structures with files in random locations

## Quick Start

### 1. First Run - Setup

```bash
python dayz_mod_xml_merger.py
```

This creates `merge_config.json` with default settings.

### 2. Edit Config - Tell It Where Your Mods Are

Open `merge_config.json` and update:

```json
{
    "mod_search_paths": [
        "./mods",                           // If mods are in ./mods folder
        "./@*",                            // Scans all @ModName folders
        "./workshop/content/221100/*"      // Steam Workshop mods
    ],
    "missions": {
        "dayzOffline.chernarusplus": {
            "types": "./mpmissions/dayzOffline.chernarusplus/db/types.xml",
            "events": "./mpmissions/dayzOffline.chernarusplus/cfgeventspawns.xml",
            "spawnabletypes": "./mpmissions/dayzOffline.chernarusplus/db/spawnabletypes.xml"
        }
    }
}
```

### 3. Run Auto-Merge

```bash
python dayz_mod_xml_merger.py
# Select: 1 (Interactive merge)
# Select: 1 (Auto-scan and merge all mods)
# Type: y (to confirm)
```

**Done!** All your mod XMLs are now merged into your server XMLs.

## Usage Examples

### Example 1: Merge All Mods Automatically

```bash
python dayz_mod_xml_merger.py
# 1. Interactive merge
# 1. Auto-scan and merge all mods
# y (confirm)
```

Output:
```
============================================================
Processing: @DayZ-Expansion-Weapons
============================================================

  📄 Found 1 types.xml file(s)
  Merging: @DayZ-Expansion-Weapons/types.xml
  ✓ Backup: ./backups/types.xml.20240129_143022.bak
    + Added: ExpansionAK74
    + Added: ExpansionM16A4
    + Added: ExpansionAWM
    - Skipped: SVD (already exists)

  ✓ Summary: 3 added, 0 updated, 1 skipped
```

### Example 2: Merge One Specific Mod

```bash
python dayz_mod_xml_merger.py
# 1. Interactive merge
# 2. Merge specific mod folder
# Enter: @DayZ-Expansion-Vehicles
```

### Example 3: See What Mods Are Available

```bash
python dayz_mod_xml_merger.py
# 1. Interactive merge
# 3. List available mods
```

Shows:
```
Found 5 mod folder(s):
  1. @DayZ-Expansion-Weapons
     - types.xml: ✓
     - events.xml: ✓
  2. @DayZ-Expansion-Vehicles
     - types.xml: ✓
     - events.xml: ✓
  3. @CF
     - types.xml: ✓
```

## Configuration Options

### Mod Search Paths

Tell the script where to look for mods:

```json
"mod_search_paths": [
    "./mods",                    // Relative to script location
    "C:/DayZServer/mods",       // Absolute path
    "./@*",                     // All folders starting with @
    "./workshop/content/221100/*"  // Steam Workshop
]
```

### Merge Rules

```json
"merge_rules": {
    "skip_vanilla_duplicates": true,    // Skip items that exist in vanilla
    "overwrite_existing": false,        // Don't replace existing entries
    "preserve_comments": true           // Keep XML comments
}
```

**overwrite_existing: false** (default)
- Skips items already in your types.xml
- Keeps your custom spawn rates
- Safest option

**overwrite_existing: true**
- Replaces existing entries with mod's values
- Use if mod updates its XML and you want the new values

## Common Scenarios

### Scenario 1: New Server, Adding All Mods

```bash
# 1. Install all mods
# 2. Update mod_search_paths in config
# 3. Run script → option 1 → option 1
# 4. Done! All mods merged
```

### Scenario 2: Adding One New Mod

```bash
# 1. Install new mod
# 2. Run script → option 1 → option 2
# 3. Enter mod folder path
# 4. Done! New mod merged
```

### Scenario 3: Multiple Missions (Chernarus + Livonia)

```bash
# Edit config - add both missions
# Change active mission
# Run auto-merge
# Switch mission
# Run auto-merge again
```

### Scenario 4: Mod Updated Its XML

If you already merged a mod, but the mod author updated their types.xml:

```bash
# Option A: Set "overwrite_existing": true in config
# Run merge again

# Option B: Manually delete the mod items from your types.xml
# Run merge with "overwrite_existing": false
```

## How the Script Finds XMLs

The script uses **intelligent content-based detection** instead of searching for specific filenames or paths. It:

1. Recursively searches **every folder** in the mod directory
2. Finds **all .xml files** regardless of name or location
3. Reads the content to identify the file type
4. Works with **any mod structure** - no matter how messy!

### Examples of Structures It Handles

**Standard structure:**
```
@ModName/
├── types.xml                    ✓ Found by content
└── cfgeventspawns.xml          ✓ Found by content
```

**Nested structure:**
```
@ModName/
├── db/
│   └── types.xml               ✓ Found by content
└── cfgeventspawns.xml          ✓ Found by content
```

**Random Windows structure:**
```
@ModName/
├── Server Files/
│   └── Types.xml               ✓ Found by content (any case)
└── Documentation/
    └── Events.xml              ✓ Found by content
```

**Deep nesting:**
```
@ModName/
└── mission/
    └── db/
        └── types.xml           ✓ Found by content
```

**Custom naming:**
```
@ModName/
├── xml_and_clasnames/          ✓ Found (searches ALL folders)
│   └── my_custom_types.xml     ✓ Found by content (any filename)
└── Installation/
    └── server_config.xml       ✓ Found by content
```

**The script doesn't care about:**
- ❌ Folder names (xml/, XML/, Server Files/, etc.)
- ❌ File names (types.xml, Types.xml, MyTypes.xml, etc.)
- ❌ Folder depth (finds files 10 levels deep)
- ❌ Windows vs Linux conventions

**The script only cares about:**
- ✅ Is it an .xml file?
- ✅ Does it contain DayZ server config XML structure?

## Troubleshooting

**"No XML files found in this mod"**
- Check `mod_search_paths` in config
- Make sure paths are correct
- Try absolute paths instead of relative

**The mod genuinely doesn't include XMLs**
- Some mods don't include server configuration files
- The script searches **every folder and subfolder** recursively
- It identifies XMLs by content, not filename
- If it says "No XML files found", the mod truly doesn't have any DayZ config XMLs
- Check the mod's Steam Workshop page - some mods are client-only or require separate server files

**Items not spawning**
- Check the merged types.xml has your items
- Restart server after merging
- Check nominal/min values aren't 0

**Accidentally merged wrong mod**
- Check `./backups/` folder
- Find the most recent backup
- Copy it back over your types.xml

## Tips

💡 **Run on a test server first** - Always test merges before production

💡 **Keep backups** - The script auto-backs up, but keep your own too

💡 **Check the output** - Look at what was added/skipped

💡 **One mod at a time** - When testing, merge one mod, test, then next

💡 **Update regularly** - When mods update, re-merge to get latest values

## Advanced: Batch Processing

Process all mods for all missions:

```python
from dayz_mod_xml_merger import DayZXMLMerger

merger = DayZXMLMerger()
mods = merger.scan_for_mods()
missions = list(merger.config["missions"].keys())

for mission in missions:
    merger.config["active_mission"] = mission
    for mod in mods:
        merger.merge_mod(mod)
```

## Comparison: Merger vs. Generator

**Use the MERGER (this script) when:**
- ✓ Mod includes types.xml files
- ✓ You want to auto-detect and merge
- ✓ You don't want to type classnames

**Use the GENERATOR (other script) when:**
- Mod doesn't include XML files
- You need to create entries from scratch
- You want custom spawn rates for everything

---

**This script does what you actually wanted - automatic XML merging!** 🎯
