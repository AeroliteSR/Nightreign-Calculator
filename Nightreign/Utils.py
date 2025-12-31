try:
    from Nightreign import Effects, Enemy, Items, Player, Reference, Scaling, Names, Utils, Weapons, Magic
except ModuleNotFoundError:
    import Effects, Enemy, Items, Player, Reference, Scaling, Names, Utils, Weapons, Magic
import copy
from math import floor, ceil

class CalcFunctions():
    @staticmethod
    def mult(multiplier, val):
        return [[x * multiplier for x in item] if isinstance(item, list) else item * multiplier for item in val]

    @staticmethod
    def div(val, multiplier):
        return [[ceil(x / multiplier) for x in item] if isinstance(item, list) else ceil(item / multiplier) for item in val]

    @staticmethod
    def multiplyRecursive(data, multiplier):
        if isinstance(data, list):  # If it's a list, apply the function to each element
            return [CalcFunctions.multiplyRecursive(item, multiplier) for item in data]
        else:  # If it's not a list, just multiply the value
            return data * multiplier

    @staticmethod
    def floatConv(nested_list):
        result = []
        for item in nested_list:
            if isinstance(item, list):
                result.append(CalcFunctions.floatConv(item))
            elif isinstance(item, float):
                result.append(int(item))
            else:
                result.append(item)
        return result
    
class NightreignFunctions():
    @staticmethod
    def getStats(enemy: int = 20402100, players: int = 1, time: int = 0, depth: int = 0, mutation: bool = False):
        baseStats = Enemy.Stats[enemy]
        hp = baseStats['Health']
        dmg, stamDmg = 1, 1
        NpcScales = Enemy.Scalings[enemy]

        for key, val in NpcScales.items():
            if key == 'Threat Scale' and val:
                hp *= Scaling.ThreatScalingStats[val]['HP']
                dmg *= Scaling.ThreatScalingStats[val]['Damage']
            
            if key == 'Day 2 Scale' and val and time == 2:
                hp *= Scaling.Day2ScalingStats[val]['HP']
                dmg *= Scaling.Day2ScalingStats[val]['Damage']
                stamDmg *= Scaling.Day2ScalingStats[val]['Stamina Damage']

            if key == 'Mutated Scale' and val and mutation:
                Scale = Scaling.MutatedScaling[val]['SpEffect']
                hp *= Scaling.MutatedScalingStats[Scale]['HP']
                dmg *= Scaling.MutatedScalingStats[Scale]['Damage']
            
            if key == 'Multiplayer Scale' and val and players > 1:
                Scale = Scaling.Multiplayer[val][players-2]
                hp *= Scaling.ThreatScalingStats[Scale]['HP']
                dmg *= Scaling.ThreatScalingStats[Scale]['Damage']

            if key == 'Depth Scale' and val and depth > 0:
                Scale = Scaling.DepthScaling[val][depth-1]
                hp *= Scaling.DepthScalingStats[Scale]['HP']
                dmg *= Scaling.DepthScalingStats[Scale]['Damage']

        output = {'Health': ceil(hp),
                 'Damage Multiplier': f"{dmg}x",
                 'Stamina Damage Multiplier': f"{stamDmg}x"}
        
        for k,v in baseStats.items():
            if k not in output and k != 'Type':
                if 'Taken' in k:
                    v = f'{v}x'
                output[k] = v

        return output
    
    @staticmethod
    def getWeaponInfo(weapon_id: int, effectTables: None | list = None, magicTables: None | list = None, ash_table_override: None | int = None):
        output = {}
        data = Weapons.Weapons.get(weapon_id, None)
        if data:
            output['Weapon Type'] = data['Type']
            output['Rarity'] = data['Rarity']
            output['Attribute'] = data['Attribute']
            ash_dflt = Names.AshOfWar[data['Default Ash']]
            output["Default Ash of War"] = ash_dflt
            attach_effect = data['Attach Effect']
            if attach_effect != -1:
                output['Attached Effect'] = Names.AttachEffects[attach_effect]
            output['Physical Damage'] = data['Physical Damage']
            output['Magic Damage'] = data['Magic Damage']
            output['Fire Damage'] = data['Fire Damage']
            output['Lightning Damage'] = data['Lightning Damage']
            output['Stamina Damage'] = data['Stamina Damage']
            output['Poise Damage'] = data['Poise Damage']
            output['Revive Damage'] = data['Revive Damage']
            output["Crit Damage Multiplier"] = f'{data['Crit Multiplier']}x'

            ash_table = ash_table_override or data["Ash Table"]
            output['Possible Ashes of War'] = NightreignFunctions.parseAshesChance(ash_table, ash_dflt)

            if effectTables:
                PossibleEffects = {}
                for etableID in effectTables:
                    if etableID:
                        PossibleEffects[f'Attach Effect Table {etableID}'] = NightreignFunctions.parseEffectChance(etableID)
                output['Possible Effects'] = PossibleEffects

            if magicTables:
                PossibleSpells = {}
                for mtableID in magicTables:
                    if mtableID:
                        PossibleSpells[f'Magic Table {mtableID}'] = NightreignFunctions.parseSpellChance(mtableID)
                output['Possible Spells'] = PossibleSpells

            return output
        
    @staticmethod
    def parseSpellChance(spell_table: int):
        table = copy.deepcopy(Magic.MagicTables[spell_table])
        max_weight = sum([entry['Weight'] for entry in table])
        
        for entry in table:
            entry['ID'] = Names.Magic[entry['ID']]
            entry['Weight'] = f"{(entry['Weight']/max_weight*100):.2f}%"

        return table
        
    @staticmethod
    def parseEffectChance(effect_table: int):
        table = copy.deepcopy(Effects.AttachEffectTable[effect_table])
        table = [entry for entry in table if entry['ID'] != 0 and entry['Weight'] != 0]
        max_weight = sum([entry['Weight'] for entry in table])
        
        for entry in table:
            entry['ID'] = Names.AttachEffects[Effects.AttachEffects[entry['ID']]['TextID']]
            entry['Weight'] = f"{(entry['Weight']/max_weight*100):.2f}%"

        return table
    
    @staticmethod
    def parseAshesChance(ash_table: int, default_ash: str):
        if ash_table == -1:
            return {'ID': default_ash, 'Weight': '100%'}
        
        table = copy.deepcopy(Weapons.AshOfWarTables[ash_table])
        max_weight = sum([entry['Weight'] for entry in table])
        
        for entry in table:
            entry['ID'] = Names.AshOfWar[entry['ID']]
            entry['Weight'] = f"{(entry['Weight']/max_weight*100):.2f}%"

        return table

    @staticmethod
    def parseItemTable(table, parent_weight=1, total_weight=None, depth=0):
        """Recursively parse an item table into nested structured data for tree display."""

        result = []
        if isinstance(table, dict):
            table = [table]

        if not isinstance(table, list):
            return [{"Name": str(table), "Weight": 0.0, "Children": []}]

        if not total_weight: 
            total_weight = sum(row.get("Weight", 0.0) for row in table if isinstance(row, dict)) 
            if total_weight <= 0: 
                total_weight = 1.0

        for row in table:
            if not isinstance(row, dict):
                continue

            category = row.get("Category")
            item_id = row.get("ItemID")
            count = row.get("Number", 1)
            item_class = row.get("Class", 0)
            weight = row.get("Weight", row.get('Chance', 0.0)) # WHAT THE ACTUAL FUCK IS THIS WHY IS IT WRITING CHANCE THAT SHIT ISNT ANYWHERE IN MY CODE
            normalized_weight = weight / total_weight * parent_weight

            discovery = ''
            if 'DiscoveryAffectable' in row:
                discovery = 'Yes' if row['DiscoveryAffectable'] == 1 else ''

            entry = {
                "Name": None,
                "Category": category,
                "ItemID": item_id,
                "Count": count,
                "Weight": normalized_weight,
                "Class": item_class,
                "Discovery": discovery, # TODO: make weapon types and "Is Disabled" bool get checked and added as a column in the gui
                "Children": []
            }

            # Category 7 = nested table
            if category == 7:
                nested = Items.ItemTable.get(item_id)
                if nested:
                    entry["Name"] = f"Table {item_id}"
                    temp_weight = normalized_weight if normalized_weight > 0 else 1.0
                    entry["Children"] = NightreignFunctions.parseItemTable(nested, parent_weight=temp_weight, depth=depth+1)
                else:
                    entry["Name"] = f"Unknown Table ({item_id})"

            else:
                if category == 2:
                    weapon = Weapons.Weapons.get(item_id, None)
                    rarity = weapon.get("Rarity", None)
                    entry["Name"] = Names.Weapon.get(item_id, f"Unknown Weapon ({item_id})")
                    entry["Rarity"] = Reference.Rarities.get(rarity, "Undefined")

                elif category == 6: # custom weapon
                    weapon = Weapons.CustomWeapons.get(item_id, None)
                    if weapon:
                        target = weapon.get('Weapon', None)
                        rarity = Weapons.Weapons.get(target, None).get('Rarity', None)
                        entry["Name"] = Names.Weapon.get(target, f"Unknown C-Weapon ({item_id})")
                        entry["Rarity"] = Reference.Rarities.get(rarity, "Undefined")

                elif category == 5:
                    entry["Name"] = Names.Armor.get(item_id, f"Unknown Relic ({item_id})")

                elif category == 1:
                    if item_id in Effects.PermanentBuffs:
                        entry['Name'] = Names.PermanentBuffs.get(item_id, f'Unknown Effect ({item_id})')
                        entry['Rarity'] = "PermBuff"
                    else:
                        entry['Name'] = Names.Goods.get(item_id, f'Unknown Item ({item_id})')

                elif category == 4:
                    entry["Name"] = Names.Talismans.get(item_id, f"Unknown Talisman ({item_id})")
            
            if entry['Name']: # delete "Nothings"
                result.append(entry)

        return result

    @staticmethod
    def addLotChains(itemlots, table):
        output = {}

        def expand(lots, prefix, slot_index=1):
            slot_name = f"{prefix} Slot {slot_index}"
            output[slot_name] = {}
                
            if isinstance(lots, list):
                if len(lots)==0:
                    output[slot_name] = None
                    return
                for sub_idx, item in enumerate(lots):
                    expand(item, prefix=prefix, slot_index=sub_idx+1)
            else:
                output[slot_name][lots] = []

                block_start = (lots // 10) * 10
                block_end = block_start + 10
                output.setdefault(slot_name, [])
                for i in range(block_start, block_end):
                    if i in table:
                        output[slot_name][lots].append(i) 

        if isinstance(itemlots, dict):
            for name, ids in itemlots.items():
                if not isinstance(ids, list):
                    ids = [ids]
                ids = [i for i in ids if i != None]
                expand(lots=ids, prefix=name)

        return output

    @staticmethod
    def getWeightDict(data):
        total_weights = {}
        #weight_dict = {}

        for lot in data:
            lot_items = Items.EnemyItemLots.get(lot)
            if lot_items:
                #weight_dict[lot] = [i.get("Weight", 0) for i in lot_items]
                total_weights[lot] = sum([i.get("Weight", 0) for i in lot_items])

        return total_weights
    
    @staticmethod
    def cleanItemlot(itemlot):
        return [entry for entry in itemlot if entry.get('Weight', 0.0) > 0]

    @staticmethod
    def parseDropIDs(drops, mutated):
        filtered = {k: v for k, v in drops.items() if v}

        if not mutated:
            filtered = {k: v for k, v in filtered.items() if 'Mutated' not in k}
        
        return filtered

    @staticmethod
    def getDrops(enemy: int, mutated: bool = False):
        data = {}

        cleaned = NightreignFunctions.parseDropIDs(Enemy.Drops[enemy], mutated)
        drops = NightreignFunctions.addLotChains(cleaned, Items.EnemyItemLots)

        for slot, ids in drops.items():
            slot_drops = {}
            if ids:
                for lot_id in list(ids.values())[0]:
                    itemlot = NightreignFunctions.cleanItemlot(Items.EnemyItemLots.get(lot_id, []))
                    if not itemlot:
                        continue

                    seen_items = {}
                    for lot in itemlot:
                        item_id = lot['ItemID']
                        lot_weight = lot.get('Weight', 0)

                        if item_id in seen_items:
                            seen_items[item_id]['Weight'] += lot_weight
                        else:
                            seen_items[item_id] = lot.copy()

                    fixed_itemlot = list(seen_items.values())
                    slot_drops[lot_id] = NightreignFunctions.parseItemTable(fixed_itemlot)

            data[slot] = slot_drops
        return data

if __name__ == "__main__": 
    #data = NightreignFunctions.getDrops(41109000, mutated=True) # 43550020
    #print(NightreignFunctions.getStats(75000020, 2, 0, True))
    print(NightreignFunctions.parseAshesChance(21180810))