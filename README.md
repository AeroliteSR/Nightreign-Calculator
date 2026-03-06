# A simple GUI application for getting basic statistics on Nightreign enemies under a variety of conditions.
## This repository also contains all of the data that was mined and used during the creation of this project. 

### Requirements:
pip install PyQt5 pyperclip

# Usage:
Select an enemy and the conditions you want and the calculated data will populate the lower tabs in the GUI.  
The `Stats` tab contains statistics for the selected enemy, such as affinities, health, and runes.  
The `Drops` tab contains possible loot from killing the enemy, displayed in a data tree. Itemlots and Tables retain their IDs from the game's params in case you wish to search it up yourself. After selecting an item, you can press `Open Wiki` to attempt to find its wiki page and display it in-app. There are a few issues with the WebEngineView that occassionally causes crashes, which I have yet to fix. Pressing `Load Selected Item` will take you to the `Item` tab.
The `Item` tab shows information regarding a loaded item. This includes: rarity, attributes, damage types, possible ashes of war, possible effects, and possible spells that could be on the weapon. Selecting a spell/effect/ash of war and pressing `Load Selected Item` again will show additional information for what you select.  
The `Wiki` tab is a built in web engine view that by default opens on the Fextralife wiki page for Nightreign. You will see a "404 Access Denied" error if the item you selected doesn't have a wiki page.  
  
### Pressing `Load Data` will open a window that allows you to manually load any data available in the calculator, regardless of the currently selected enemy.

## Notes:
 - You can input NpcParamIds to view statistics for basic enemies that aren't listed by using the Entity ID field.

## How to get NpcParamIds:
1. Download [UXM](https://www.nexusmods.com/eldenring/mods/1651?tab=files) and [Smithbox](https://github.com/vawser/Smithbox/releases)
2. Unpack the game with UXM by inputting the executable path
3. Open Smithbox and make a new project
4. Go to Map Editor, right click the map that the enemy you want is in, and click load
5. Find the enemy and click on it (you move by holding right click over the viewport)
6. On the right, click properties and scroll down to find NPC Param ID, copy this and paste it into the field within the calculator
