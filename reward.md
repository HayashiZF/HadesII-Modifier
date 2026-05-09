# Room Reward Amount Guide

This guide is only about changing **post-combat room-clear reward amounts** such as:

- money rewards
- max health rewards
- max mana rewards

It intentionally ignores boon reward logic.

The main file for amount tuning is:

- `Content/Scripts/ConsumableData.lua`

Use `RoomData*.lua` only when you want to change **which reward type a cleared room gives**, not how much that reward gives.

Important runtime note:

- the reward dropped after clearing enemies is spawned by `SpawnRoomReward()` in `Content/Scripts/RewardLogic.lua`
- that function creates consumable rewards from `ConsumableData.lua`
- so `RoomMoneyDrop`, `MaxHealthDrop`, and `MaxManaDrop` are part of the room-clear reward path
- however, those same consumable definitions are also reused by other systems, including store-related logic

## 1. Quick rule

If your goal is:

- "make gold rooms give more gold"
- "make centaur-heart style rooms give more max health"
- "make soul-tonic style rooms give more max mana"

then you usually want to edit `Content/Scripts/ConsumableData.lua`, not `RewardLogic.lua`.

The room-clear path is:

1. combat encounter ends
2. `Content/Scripts/EncounterLogic.lua:2173` calls `SpawnRoomReward(encounter)`
3. `Content/Scripts/RewardLogic.lua:400-406` creates the consumable reward object
4. `ApplyConsumableItemResourceMultiplier()` adjusts the reward
5. `UseConsumableItem()` grants the actual money / health / mana when picked up

## 2. Where the amount values live

The important reward definitions in this repo are:

- `RoomMoneyDrop` at `Content/Scripts/ConsumableData.lua:332`
- `RoomMoneyBigDrop` at `Content/Scripts/ConsumableData.lua:378`
- `RoomMoneyTripleDrop` at `Content/Scripts/ConsumableData.lua:390`
- `RoomMoneySmallDrop` at `Content/Scripts/ConsumableData.lua:402`
- `RoomMoneyTinyDrop` at `Content/Scripts/ConsumableData.lua:412`
- `MaxHealthDrop` at `Content/Scripts/ConsumableData.lua:457`
- `MaxHealthDropSmall` at `Content/Scripts/ConsumableData.lua:514`
- `MaxManaDrop` at `Content/Scripts/ConsumableData.lua:594`

These are consumable-style reward definitions used by the room-clear spawn path. The actual granted amount is stored directly on the reward record.

## 3. Money rewards

### Base money reward

`RoomMoneyDrop` is the standard money-room reward:

```lua
RoomMoneyDrop =
{
    ResourceCosts =
    {
        Money = 100,
    },
    DropMoney = 100,
}
```

Important fields:

- `DropMoney`: how much money the pickup gives
- `ResourceCosts.Money`: shared value/cost metadata also reused by shop-related logic

The true payout field for room-clear money rewards is `DropMoney`.

`ResourceCosts.Money` is not the money grant itself. It is a shared field reused by generic consumable/store code, so change it carefully.

### Money variants

The repo already includes several inherited money variants:

- `RoomMoneyBigDrop` -> `200`
- `RoomMoneyTripleDrop` -> `300`
- `RoomMoneySmallDrop` -> `50`
- `RoomMoneyTinyDrop` -> `20`

These inherit from `RoomMoneyDrop` and override only a few fields.

Example:

```lua
RoomMoneyTripleDrop =
{
    InheritFrom = { "RoomMoneyDrop", },
    ResourceCosts =
    {
        Money = 300,
    },
    DropMoney = 300,
}
```

## 4. Health rewards

`MaxHealthDrop` is the main max-health reward:

```lua
MaxHealthDrop =
{
    ResourceCosts =
    {
        Money = 125,
    },
    AddMaxHealth = 25,
}
```

Important fields:

- `AddMaxHealth`: how much permanent max health the reward adds
- `ResourceCosts.Money`: shared value/cost metadata for the consumable definition

There is also a smaller variant:

- `MaxHealthDropSmall` -> `AddMaxHealth = 5`

If your goal is to make heart-style room rewards stronger or weaker, `AddMaxHealth` is the main field to edit.

## 5. Mana rewards

`MaxManaDrop` is the main max-mana reward:

```lua
MaxManaDrop =
{
    ResourceCosts =
    {
        Money = 100,
    },
    AddMaxMana = 30,
}
```

Important fields:

- `AddMaxMana`: how much max mana the reward adds
- `ResourceCosts.Money`: shared value/cost metadata

If your goal is to make soul-tonic style rooms stronger or weaker, `AddMaxMana` is the main field to edit.

## 6. Which field actually changes the reward amount

Use these rules:

- gold reward amount: edit `DropMoney`
- max health reward amount: edit `AddMaxHealth`
- max mana reward amount: edit `AddMaxMana`

These are the fields that `UseConsumableItem()` actually consumes on pickup:

- `DropMoney` is granted at `Content/Scripts/InteractLogic.lua:1075-1085`
- `AddMaxHealth` is granted at `Content/Scripts/InteractLogic.lua:1055-1057`
- `AddMaxMana` is granted at `Content/Scripts/InteractLogic.lua:1066-1067`

`ResourceCosts.Money` is not the primary room-reward payout field. It is shared with generic consumable/store handling, so it should be treated as secondary metadata unless you specifically want to rebalance that side too.

## 7. Safe edit patterns

### Safest edit: change one existing reward globally

If you want **every** normal money room to give more gold, edit:

- `RoomMoneyDrop`

If you want **every** normal health room to give more max health, edit:

- `MaxHealthDrop`

If you want **every** normal mana room to give more max mana, edit:

- `MaxManaDrop`

This is safe when you intentionally want a global rebalance.

### Safer edit for limited scope: clone a reward

If you only want some rooms changed, do not directly modify a widely used base reward.

Instead:

1. create a new reward entry in `ConsumableData.lua`
2. inherit from an existing reward
3. override only the amount fields
4. point only the intended room(s) to the new reward type

Example:

```lua
RoomMoneyHugeDrop =
{
    InheritFrom = { "RoomMoneyDrop", },
    ResourceCosts =
    {
        Money = 500,
    },
    DropMoney = 500,
}
```

Then, in the target room:

```lua
ForcedReward = "RoomMoneyHugeDrop",
```

This is the best pattern when you want a special room reward without affecting all standard money rooms.

### Riskier edit: changing a shared base

Directly editing `RoomMoneyDrop`, `MaxHealthDrop`, or `MaxManaDrop` is broader than it looks because the same definitions can be reused by room rewards and store-related systems.

Do this only if you want a global change.

## 8. How to safely edit money rewards

### Global rebalance example

To raise the standard room-clear money reward from `100` to `150`:

```lua
RoomMoneyDrop =
{
    DropMoney = 150,
}
```

What this changes:

- the actual money payout on pickups using `RoomMoneyDrop`

What this does not change:

- `RoomMoneyBigDrop`
- `RoomMoneyTripleDrop`
- `RoomMoneySmallDrop`
- `RoomMoneyTinyDrop`

Those variants override their own amounts, so edit them separately if needed.

### Limited-scope example

If one room should give `500` gold, add a new variant instead of changing `RoomMoneyDrop`.

That avoids accidentally buffing every ordinary money room.

## 9. How to safely edit health rewards

To raise the standard room-clear health reward from `25` to `40`:

```lua
MaxHealthDrop =
{
    AddMaxHealth = 40,
}
```

If you also want the smaller health reward adjusted, update `MaxHealthDropSmall` too.

If only one room should give a larger health reward, clone `MaxHealthDrop` into a new entry and force that reward only in the target room.

## 10. How to safely edit mana rewards

To raise the standard room-clear mana reward from `30` to `45`:

```lua
MaxManaDrop =
{
    AddMaxMana = 45,
}
```

If only a special room should give that stronger mana reward, create a new inherited variant instead of editing `MaxManaDrop` directly.

## 11. How to point a room at a different amount reward

If you already have a reward type and only want certain rooms to use it, edit the room in `RoomData*.lua`.

Examples:

```lua
ForcedReward = "RoomMoneyTripleDrop",
```

```lua
ForcedReward = "MaxHealthDrop",
```

```lua
ForcedReward = "MaxManaDrop",
```

Use this pattern when:

- the amount change should apply to only one room
- the amount change should apply to one encounter family
- you are testing a custom reward before making it global

## 12. Best practice: clone before you replace

For local edits, prefer this workflow:

1. find the nearest existing reward entry in `ConsumableData.lua`
2. copy it into a new uniquely named reward
3. keep `InheritFrom` if possible
4. change only:
   `DropMoney`, `AddMaxHealth`, or `AddMaxMana`
5. only adjust `ResourceCosts.Money` if you intentionally want the shared metadata/cost side to match
6. point only the target room to the new reward

This is the safest pattern in this repo because it avoids broad side effects.

## 13. Things that are usually safe to leave alone

If you are only changing amount balance, you usually do not need to touch:

- `SpawnSound`
- `ConsumeSound`
- `DoorIcon`
- `UseText`
- `OnSpawnVoiceLines`
- `ConsumedVoiceLines`
- `ExtractValues`

Those are usually presentation/UI behavior, not amount logic.

## 14. Things to edit carefully

### `ResourceCosts.Money`

This is the field I was too loose about before.

It exists on these reward definitions, but the actual room-clear payout comes from:

- `DropMoney`
- `AddMaxHealth`
- `AddMaxMana`

`ResourceCosts.Money` is shared with generic consumable/store logic, so do not treat it as the main reward-amount field.

A safe default is:

1. change the true payout field first
2. change `ResourceCosts.Money` only if you have confirmed you want the shared metadata/cost behavior to move too

### inherited variants

Some rewards inherit from shared parents and override only one or two fields.

Examples:

- `RoomMoneyBigDrop` inherits from `RoomMoneyDrop`
- `RoomMoneyTripleDrop` inherits from `RoomMoneyDrop`
- `RoomMoneySmallDrop` inherits from `RoomMoneyDrop`
- `RoomMoneyTinyDrop` inherits from `RoomMoneyDrop`
- `MaxHealthDropSmall` inherits from `MaxHealthDrop`

If a variant already overrides the amount field, changing the parent will not fully update that variant.

## 15. Troubleshooting

### "I changed the money reward, but some rooms still give the old amount"

Possible reason:

- those rooms use `RoomMoneyBigDrop`, `RoomMoneyTripleDrop`, `RoomMoneySmallDrop`, or `RoomMoneyTinyDrop` instead of `RoomMoneyDrop`

### "I only wanted one room changed, but many rooms changed"

Possible reason:

- you edited a shared reward entry instead of creating a new variant

Fix:

1. restore the shared reward amount
2. create a new cloned reward entry
3. point only the target room to the new reward

### "I changed a room file, but the amount did not change"

Possible reason:

- the room only selects the reward type
- the actual amount still comes from the reward definition in `ConsumableData.lua`

### "I changed `ResourceCosts.Money`, but the reward payout did not change the way I expected"

Possible reason:

- for room-clear pickups, the real payout is controlled by `DropMoney`, `AddMaxHealth`, or `AddMaxMana`
- `ResourceCosts.Money` is a shared field, not the core reward-grant field

## 16. Recommended workflow

For global balance changes:

1. edit the existing reward entry in `ConsumableData.lua`
2. verify any inherited variants that override the amount

For room-specific balance changes:

1. clone the reward in `ConsumableData.lua`
2. give it a new unique name
3. change the amount fields
4. point the intended room to it with `ForcedReward` or another room reward reference

## 17. Practical examples in this repo

Good references to copy from:

- base money reward: `Content/Scripts/ConsumableData.lua:332`
- larger money variant: `Content/Scripts/ConsumableData.lua:390`
- base health reward: `Content/Scripts/ConsumableData.lua:457`
- smaller health variant: `Content/Scripts/ConsumableData.lua:514`
- base mana reward: `Content/Scripts/ConsumableData.lua:594`

If you want, I can next turn this into a patch set that adds custom rewards like:

- `RoomMoneyHugeDrop`
- `MaxHealthDropLarge`
- `MaxManaDropLarge`

and wire them into specific rooms for you.
