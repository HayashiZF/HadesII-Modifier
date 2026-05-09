# Boon Rarity Modding Guide

This guide explains how to change boon rarity chances in this script dump without touching any files for you automatically.

Important: this game does **not** store one standalone rarity percentage on every single boon. Rarity is decided in layers:

1. A base rarity chance table is built.
2. Room or loot-source overrides can replace that table.
3. Trait, keepsake, shop, and meta-upgrade bonuses can add or multiply the chances.
4. The final boon only uses rarities that exist in its own `RarityLevels`.

Because of that, you need to decide first what you actually want to change:

- all normal Olympian boons
- Hermes only
- one special source like Chaos, Artemis, Hades, or Icarus
- one room/shop reward
- one specific boon's allowed rarities

## 1. Understand the main files

Use these files as your map:

- `HeroData.lua:181` contains the default rarity chances for normal god boons.
- `HeroData.lua:193` contains the default rarity chances for Hermes.
- `RoomLogic.lua:2125` builds the final `rarityChances` table in `GetRarityChances`.
- `TraitLogic.lua:1750` starts assigning boon rarities in `SetTraitsOnLoot`.
- `TraitLogic.lua:1819` applies the standard boon roll order.
- `TraitData.lua:713` defines the normal boon roll order: `Common`, `Rare`, `Epic`, `Duo`, `Legendary`.

Important consequence:

- `Heroic` is **not** part of the normal boon offer roll order.
- If you want Heroic boons, those usually come from special sources or later upgrades, not from standard Olympian boon rolls.

## 2. Change the default rarity chance for most god boons

If you want to change the rarity chances for regular god boons in general:

1. Open `HeroData.lua`.
2. Find the `BoonData` block around line `181`.
3. Edit `RarityChances`.

Current defaults there are:

```lua
RarityChances =
{
    Rare = 0.10,
    Epic = 0.05,
    Duo = 0.12,
    Legendary = 0.10,
},
```

What this changes:

- all normal god boon offers that use `HeroData.BoonData`
- not Hermes
- not special loot that overrides rarity locally

## 3. Change Hermes separately

Hermes uses a separate table.

1. Open `HeroData.lua`.
2. Find the `HermesData` block around line `193`.
3. Edit its `RarityChances`.

Current Hermes defaults are:

```lua
RarityChances =
{
    Rare = 0.06,
    Epic = 0.03,
    Legendary = 0.01,
},
```

## 4. Change special loot sources that already override rarity

Some sources do not use the plain defaults. `RoomLogic.lua:2144-2152` shows that `GetRarityChances` first checks:

- `CurrentRun.CurrentRoom.BoonRaritiesOverride`
- `loot.BoonRaritiesOverride`

That means special sources can replace the normal table.

Existing examples:

- `LootData_Chaos.lua:91` has `BoonRaritiesOverride`
- `NPCData_Artemis.lua:1922` has `RarityChances`
- `NPCData_Artemis.lua:1928` has `RarityRollOrder`
- `NPCData_Hades.lua:58` has `RarityChances`
- `NPCData_Hades.lua:63` has `RarityRollOrder`
- `NPCData_Icarus.lua:5140` has `RarityChances`
- `NPCData_Icarus.lua:5145` has `RarityRollOrder`
- many `RoomData*.lua` files and `StoreLogic.lua` entries set `BoonRaritiesOverride`

If you want to tune one of those sources:

1. Open that source file.
2. Find its `RarityChances`, `RarityRollOrder`, or `BoonRaritiesOverride`.
3. Change the numbers there instead of changing `HeroData.lua`.

Use this search to find all existing overrides:

```powershell
rg -n "BoonRaritiesOverride =|RarityChances =|RarityRollOrder =" .
```

## 5. Change one specific boon's allowed rarities

This is the part most people miss.

Changing the global chance table does **not** guarantee a boon can appear at that rarity. The boon must also support that rarity in its own trait definition.

The normal roll logic in `TraitLogic.lua:1819-1923` checks whether a boon has that rarity in `traitData.RarityLevels` before it can be assigned.

To change one boon:

1. Find the boon in its trait file, for example `TraitData_Zeus.lua`, `TraitData_Aphrodite.lua`, `TraitData_Ares.lua`, and so on.
2. Search for the boon name.
3. Inspect its `RarityLevels` table.
4. Add, remove, or tune the rarity entries there.

Useful search:

```powershell
rg -n "YourBoonName|RarityLevels" .
```

What this changes:

- whether that boon can be `Common`, `Rare`, `Epic`, `Legendary`, etc.
- the stat scaling for that boon at each rarity

What this does **not** change by itself:

- the global probability of rolling a rarity

Important limitation:

- there is no built-in standalone "this exact boon has a 20% Epic chance" field in the trait files
- one specific boon normally inherits the same source rarity rolls as other boons from that source
- to give one exact boon a unique rarity probability, you usually need custom loot-source logic or a dedicated override path, not just a `RarityLevels` edit

## 6. Understand how the percentages are actually used

The standard roll order is in `TraitData.lua:713`:

```lua
BoonRarityRollOrder = {"Common", "Rare", "Epic", "Duo", "Legendary"}
```

The code in `TraitLogic.lua:1819-1923` rolls in that order and later successes overwrite earlier ones.

That means these values are **not** exclusive final percentages.

Example:

- if `Rare = 0.90`
- and `Epic = 0.25`
- and `Legendary = 0.10`

then a boon can roll Rare first, then get replaced by Epic, then get replaced again by Legendary.

Practical tuning rule:

- raise `Rare` if you want fewer Commons
- raise `Epic` if you want more Epics specifically
- raise `Legendary` if you want more Legendaries specifically
- if you set `Rare` very high, remember later rarities can still override it

## 7. Check extra modifiers that may be changing your results

Even if you edit the base tables correctly, other traits can still change the final numbers.

Relevant places:

- `RoomLogic.lua:2157` onward adds `RarityBonus`
- `RoomLogic.lua:2168` onward applies `MultiplicativeRarityBonus`
- `TraitData_MetaUpgrade.lua:833` contains a general rarity meta-upgrade bonus
- `TraitData_MetaUpgrade.lua:841` contains a multiplicative Legendary bonus
- `TraitData_MetaUpgrade.lua:854` contains the duo rarity meta-upgrade
- `TraitData_MetaUpgrade.lua:914` contains another rarity bonus block
- `TraitData_Store.lua:291` contains a temporary shop rarity bonus
- `TraitData_Chaos.lua:198` contains Chaos rarity bonus data
- `TraitData_Elementals.lua:56` and `:117` contain Hera's elemental rarity upgrade boon

If your edited values do not match what you see in game, check those bonuses next.

## 8. If your goal is one of these common cases

Use this rule of thumb:

- "I want every normal god boon to be rarer or more common"  
  Edit `HeroData.lua` -> `BoonData.RarityChances`.

- "I want Hermes to be different"  
  Edit `HeroData.lua` -> `HermesData.RarityChances`.

- "I want Chaos or another special source to behave differently"  
  Edit that source's local `BoonRaritiesOverride` or `RarityChances`.

- "I want one specific boon to be able to roll Legendary"  
  Edit that boon's `RarityLevels` in the matching `TraitData_<God>.lua`.

- "I want one exact boon to have a unique rarity probability, separate from other boons of the same god"  
  A plain data-only edit is usually not enough. You will need a custom override path for that boon's source logic.

## 9. Quick verification workflow

After you make your manual Lua edits:

1. Search again to confirm you changed the right table.
2. Check whether the boon has the rarity in `RarityLevels`.
3. Check whether the room, shop, or NPC source overrides the normal chance table.
4. Check whether a keepsake, Chaos blessing, shop trait, or meta-upgrade is adding bonus rarity.
5. Test from the exact source that gives the boon.

Useful searches:

```powershell
rg -n "function GetRarityChances|BoonRaritiesOverride|RarityChances =|RarityRollOrder =" .
rg -n "RarityBonus =|MultiplicativeRarityBonus =" .
rg -n "YourBoonName" .
```

## 10. Bottom line

If you only want the simplest change, start here:

- edit `HeroData.lua` for the global default rates
- edit the boon's own `RarityLevels` if you need that boon to support the rarity you want

If you tell me which exact boon or god you want to tune, I can point you to the exact file and block to edit, still without changing any `.lua` files.
