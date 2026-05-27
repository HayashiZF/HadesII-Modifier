from __future__ import annotations

import math
import re

from .state import (
    KEEPSAKE_EDITOR_CONFIG,
    KEEPSAKE_EDITOR_ORDER,
    REWARD_EDITOR_ENTRIES,
    REWARD_EDITOR_ORDER,
)


class PatchError(ValueError):
    pass


EPIC_MARKER_START = "\t\t-- HadesIIModUI Epic Preset Start"
EPIC_MARKER_END = "\t\t-- HadesIIModUI Epic Preset End"
EPIC_ANCHOR = "\t\tlootData.RarityChances = GetRarityChances( lootData )"

WEAPON_DAMAGE_MARKER_START = "-- HadesIIModUI Weapon Damage Start"
WEAPON_DAMAGE_MARKER_END = "-- HadesIIModUI Weapon Damage End"

WEAPON_DAMAGE_TRAIT_NAMES: dict[str, str] = {
    "WeaponStaffSwing": "DummyWeaponStaff",
    "WeaponDagger": "DummyWeaponDagger",
    "WeaponAxe": "DummyWeaponAxe",
    "WeaponTorch": "DummyWeaponTorch",
    "WeaponLob": "DummyWeaponLob",
    "WeaponSuit": "DummyWeaponSuit",
}

WEAPON_DAMAGE_FAMILY_MAP: dict[str, list[str]] = {
    "WeaponStaffSwing": [
        "WeaponStaffSwing",
        "WeaponStaffSwing2",
        "WeaponStaffSwing3",
        "WeaponStaffSwing5",
        "WeaponStaffDash",
        "WeaponStaffBall",
    ],
    "WeaponDagger": [
        "WeaponDagger",
        "WeaponDagger2",
        "WeaponDagger5",
        "WeaponDaggerDash",
        "WeaponDaggerThrow",
        "WeaponDaggerBlink",
        "WeaponDaggerDouble",
        "WeaponDaggerMultiStab",
    ],
    "WeaponAxe": [
        "WeaponAxe",
        "WeaponAxe2",
        "WeaponAxe3",
        "WeaponAxe4",
        "WeaponAxe5",
        "WeaponAxeDash",
        "WeaponAxeSpin",
        "WeaponAxeSpecial",
        "WeaponAxeSpecialSwing",
    ],
    "WeaponTorch": [
        "WeaponTorch",
        "WeaponTorchSpecial",
    ],
    "WeaponLob": [
        "WeaponLob",
        "WeaponLobSpecial",
        "WeaponLobPulse",
        "WeaponLobChargedPulse",
        "WeaponSkullImpulse",
    ],
    "WeaponSuit": [
        "WeaponSuit",
        "WeaponSuit2",
        "WeaponSuitDouble",
        "WeaponSuitDash",
        "WeaponSuitCharged",
        "WeaponSuitRanged",
    ],
}

REFRESH_NPC_CHOICE_FUNCTIONS: tuple[str, ...] = (
    "EchoChoice",
    "ArachneCostumeChoice",
    "NarcissusBenefitChoice",
    "MedeaCurseChoice",
    "CirceBlessingChoice",
    "IcarusBenefitChoice",
    "EchoLastRunBoon",
)


def detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def validate_number_string(raw_value: str, label: str) -> str:
    value = raw_value.strip()
    if not value:
        raise PatchError(f"{label} cannot be empty.")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise PatchError(f"{label} must be a valid number, got '{raw_value}'.") from exc
    if parsed < 0:
        raise PatchError(f"{label} must be zero or greater.")
    return value


def validate_signed_number_string(raw_value: str, label: str) -> str:
    value = raw_value.strip()
    if not value:
        raise PatchError(f"{label} cannot be empty.")
    try:
        float(value)
    except ValueError as exc:
        raise PatchError(f"{label} must be a valid number, got '{raw_value}'.") from exc
    return value


def validate_positive_number_string(raw_value: str, label: str) -> str:
    value = raw_value.strip()
    if not value:
        raise PatchError(f"{label} cannot be empty.")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise PatchError(f"{label} must be a valid number, got '{raw_value}'.") from exc
    if parsed <= 0:
        raise PatchError(f"{label} must be greater than zero.")
    return value


def validate_probability_string(raw_value: str, label: str) -> str:
    value = raw_value.strip()
    if not value:
        raise PatchError(f"{label} cannot be empty.")
    try:
        parsed = float(value)
    except ValueError as exc:
        raise PatchError(f"{label} must be a valid number, got '{raw_value}'.") from exc
    if parsed < 0 or parsed > 1:
        raise PatchError(f"{label} must be between 0 and 1.")
    return value


def validate_whole_number_string(raw_value: str, label: str) -> str:
    value = raw_value.strip()
    if not value:
        raise PatchError(f"{label} cannot be empty.")
    if not re.fullmatch(r"\d+", value):
        raise PatchError(f"{label} must be a whole number >= 0.")
    return value


def parse_roll_order(raw_value: str, label: str) -> list[str]:
    items = [item.strip() for item in raw_value.split(",")]
    cleaned = [item for item in items if item]
    if not cleaned:
        raise PatchError(f"{label} must contain at least one rarity name.")
    for item in cleaned:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", item):
            raise PatchError(f"{label} contains an invalid rarity token: '{item}'.")
    return cleaned


def apply_epic_preset(text: str) -> str:
    newline = detect_newline(text)
    desired_block = newline.join(
        [
            EPIC_MARKER_START,
            "\t\tif lootData.GodLoot or lootData.TreatAsGodLootByShops then",
            "\t\t\tlootData.RarityChances.Common = 0",
            "\t\t\tlootData.RarityChances.Rare = 0",
            "\t\t\tlootData.RarityChances.Epic = 1",
            "\t\t\tlootData.RarityChances.Duo = 0",
            "\t\t\tlootData.RarityChances.Legendary = 0",
            "\t\tend",
            EPIC_MARKER_END,
        ]
    )

    marker_pattern = re.compile(
        rf"{re.escape(EPIC_MARKER_START)}.*?{re.escape(EPIC_MARKER_END)}(?:\r?\n)?",
        re.DOTALL,
    )
    if marker_pattern.search(text):
        replaced = marker_pattern.sub(desired_block + newline, text, count=1)
        return replaced

    if EPIC_ANCHOR not in text:
        raise PatchError("TraitLogic.lua no longer contains the Epic preset anchor line.")
    return text.replace(EPIC_ANCHOR, EPIC_ANCHOR + newline + desired_block, 1)


def apply_weapon_damage_profile(text: str, weapon_damage_state: dict[str, dict[str, str | bool]]) -> str:
    section_start, section_end = find_section_bounds(text, "TraitSetData.DummyWeapons")
    section_text = text[section_start:section_end]

    for weapon_name, trait_name in WEAPON_DAMAGE_TRAIT_NAMES.items():
        family = WEAPON_DAMAGE_FAMILY_MAP[weapon_name]
        weapon_state = weapon_damage_state[weapon_name]
        has_any_enabled = (
            bool(weapon_state.get("flat_enabled"))
            or bool(weapon_state.get("multiplier_enabled"))
            or bool(weapon_state.get("range_enabled"))
            or bool(weapon_state.get("interval_enabled"))
        )
        section_text = patch_dummy_weapon_trait(
            section_text,
            trait_name,
            family,
            has_any_enabled,
            {
                "flat_enabled": bool(weapon_state.get("flat_enabled")),
                "flat_value": str(weapon_state.get("flat_value", "0")),
                "multiplier_enabled": bool(weapon_state.get("multiplier_enabled")),
                "multiplier_value": str(weapon_state.get("multiplier_value", "1")),
                "range_enabled": bool(weapon_state.get("range_enabled")),
                "range_multiplier": str(weapon_state.get("range_multiplier", "1")),
                "interval_enabled": bool(weapon_state.get("interval_enabled")),
                "interval_multiplier": str(weapon_state.get("interval_multiplier", "1")),
            },
        )

    return text[:section_start] + section_text + text[section_end:]


def apply_refresh_hammer_profile(text: str) -> str:
    pattern = re.compile(r"(?m)^([ \t]*)Hammer\s*=\s*-?1,\s*(?:--.*)?$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(f"Expected exactly one hammer reroll entry, found {len(matches)}.")

    indent = matches[0].group(1)
    replacement = f"{indent}Hammer = 1, -- Enabled"
    return text[: matches[0].start()] + replacement + text[matches[0].end() :]


def apply_refresh_event_logic_profile(text: str) -> str:
    pattern = re.compile(r"(?m)^([ \t]*)source\.BlockReroll\s*=\s*(?:true|false)\s*$")
    matches = list(pattern.finditer(text))
    if len(matches) != len(REFRESH_NPC_CHOICE_FUNCTIONS):
        raise PatchError(
            f"Expected {len(REFRESH_NPC_CHOICE_FUNCTIONS)} BlockReroll lines, found {len(matches)}."
        )
    return pattern.sub(r"\1source.BlockReroll = false", text)


def apply_refresh_market_logic_profile(text: str) -> str:
    newline = detect_newline(text)
    updated = text

    condition_old = (
        "if args.RefreshOncePerRun == category.RefreshOncePerRun and "
        "(args.CategoryIndex or categoryIndex) == categoryIndex then"
    )
    condition_new = (
        "if ( category.RefreshOncePerRun and args.RefreshOncePerRun ) or "
        "( not category.RefreshOncePerRun and not args.RefreshOncePerRun ) then"
    )
    if condition_old in updated:
        updated = updated.replace(condition_old, condition_new, 1)
    elif condition_new not in updated:
        raise PatchError("Could not find market refresh category anchor.")

    category_refresh_call = f"\tGenerateMarketItems( screen, {{ CategoryIndex = categoryIndex }} ){newline}"
    if category_refresh_call in updated:
        updated = updated.replace(category_refresh_call, "", 1)
    elif "GenerateMarketItems( screen, { CategoryIndex = categoryIndex } )" in updated:
        raise PatchError("Market category refresh call was found with unexpected formatting.")

    refresh_marker = "\t-- HadesIIModUI Refresh Start"
    if refresh_marker not in updated:
        open_anchor = f"\tscreen.ActiveCategoryIndex = args.DefaultCategoryIndex or 1{newline}"
        refresh_block = (
            f"{refresh_marker}{newline}"
            f"\tGenerateMarketItems(){newline}"
            f"\t-- HadesIIModUI Refresh End{newline}"
        )
        if open_anchor not in updated:
            raise PatchError("Could not find market screen open anchor.")
        updated = updated.replace(open_anchor, open_anchor + newline + refresh_block, 1)

    purchase_fail_old = (
        f"\tif not HasResources( item.Cost ) then{newline}"
        f"\t\tMarketPurchaseFailPresentation( screen, button ){newline}"
        f"\t\treturn{newline}"
        f"\tend{newline}"
    )
    purchase_fail_new = (
        f"\tif not HasResources( item.Cost ) then{newline}"
        f"\t\tMarketPurchaseFailPresentation( screen, button ){newline}"
        f"\tend{newline}"
    )
    if purchase_fail_old in updated:
        updated = updated.replace(purchase_fail_old, purchase_fail_new, 1)
    elif purchase_fail_new not in updated:
        raise PatchError("Could not find market purchase affordability anchor.")

    sold_out_old = (
        f"\t\titem.SoldOut = true{newline}"
        f"\t\tUseableOff({{ Ids = buttonIds }}){newline}"
        f"\t\tSetAlpha({{ Ids = buttonIds, Fraction = 0, Duration = 0.2 }}){newline}"
        f"\t\tModifyTextBox({{ Ids = buttonIds, FadeTarget = 0 }}){newline}"
        f"\t\tUpdateMarketScreenInteractionText( screen ){newline}"
    )
    sold_out_new = (
        f"\t\titem.SoldOut = false{newline}"
        f"\t\tMarketPurchaseSuccessRepeatablePresentation( button ){newline}"
    )
    if sold_out_old in updated:
        updated = updated.replace(sold_out_old, sold_out_new, 1)
    elif sold_out_new not in updated:
        raise PatchError("Could not find market sold-out anchor.")

    hide_unaffordable_old = (
        f"\tif category.HideUnaffordable and not HasResources( item.Cost ) then{newline}"
        f"\t\titem.SoldOut = true{newline}"
        f"\t\tUseableOff({{ Ids = buttonIds }}){newline}"
        f"\t\tSetAlpha({{ Ids = buttonIds, Fraction = 0, Duration = 0.2 }}){newline}"
        f"\t\tModifyTextBox({{ Ids = buttonIds, FadeTarget = 0 }}){newline}"
        f"\t\tUpdateMarketScreenInteractionText( screen ){newline}"
        f"\tend{newline}"
    )
    hide_unaffordable_new = (
        f"\tif category.HideUnaffordable and not HasResources( item.Cost ) then{newline}"
        f"\t\titem.SoldOut = false{newline}"
        f"\tend{newline}"
    )
    if hide_unaffordable_old in updated:
        updated = updated.replace(hide_unaffordable_old, hide_unaffordable_new, 1)
    elif hide_unaffordable_new not in updated:
        raise PatchError("Could not find market hide-unaffordable anchor.")

    return updated


def apply_reward_editor_profile(
    text: str,
    reward_editor_state: dict[str, dict[str, str | bool]],
    target_file: str,
) -> str:
    updated = text
    for reward_name in REWARD_EDITOR_ORDER:
        reward_state = reward_editor_state[reward_name]
        if not reward_state["enabled"]:
            continue

        reward_meta = REWARD_EDITOR_ENTRIES[reward_name]
        if reward_meta["target_file"] != target_file:
            continue

        patch_kind = reward_meta["patch_kind"]
        if patch_kind == "section_field":
            updated = replace_field_in_named_section(
                updated,
                str(reward_meta["section_name"]),
                str(reward_meta["field_path"]),
                str(reward_state["value"]),
            )
        elif patch_kind == "pickaxe_max_health_by_resource":
            updated = replace_pickaxe_max_health_by_resource(
                updated,
                str(reward_meta["resource_name"]),
                str(reward_state["value"]),
            )
        else:
            raise PatchError(f"Unsupported reward patch kind '{patch_kind}' for '{reward_name}'.")

        if reward_state.get("show_advanced") and "resource_cost_money" in reward_meta:
            updated = replace_resource_cost_money_in_named_section(
                updated,
                str(reward_meta["section_name"]),
                str(reward_state["resource_cost_money"]),
            )
    return updated


def apply_keepsake_editor_profile(text: str, keepsake_editor_state: dict[str, dict[str, str | bool]]) -> str:
    updated = text
    for keepsake_name in KEEPSAKE_EDITOR_ORDER:
        keepsake_state = keepsake_editor_state[keepsake_name]
        if not keepsake_state["enabled"]:
            continue

        keepsake_meta = KEEPSAKE_EDITOR_CONFIG[keepsake_name]
        show_advanced = bool(keepsake_state.get("show_advanced"))
        fields = keepsake_state["fields"]
        for field_id, field_meta in keepsake_meta["fields"].items():
            if field_meta.get("advanced") and not show_advanced:
                continue
            field_value = str(fields[field_id])
            field_path = str(field_meta["path"])
            updated = replace_field_in_named_profile_section(
                updated,
                "TraitSetData.Keepsakes",
                keepsake_name,
                field_path,
                field_value,
            )
    return updated


def apply_initial_stats_hero_data_profile(text: str, initial_stats_state: dict[str, str | bool]) -> str:
    updated = replace_unique_scalar_field(text, "MaxHealth", str(initial_stats_state["max_health"]))
    updated = replace_unique_scalar_field(updated, "MaxMana", str(initial_stats_state["max_mana"]))
    return updated


def apply_initial_stats_run_logic_profile(text: str, initial_stats_state: dict[str, str | bool]) -> str:
    return replace_function_return_value(
        text,
        "CalculateStartingMoney",
        str(initial_stats_state["starting_money"]),
    )


def apply_arcana_meta_upgrade_data_profile(
    text: str,
    arcana_editor_state: dict[str, Any],
    card_trait_map: dict[str, str],
) -> str:
    del card_trait_map  # Mapping is used by the trait patch path only.

    grasp_growth_multiplier = _parse_lua_numeric_expression(
        str(arcana_editor_state["grasp_growth_multiplier"])
    )
    unlock_upgrade_cost_multiplier = _parse_lua_numeric_expression(
        str(arcana_editor_state["unlock_upgrade_cost_multiplier"])
    )
    starting_grasp_limit = str(arcana_editor_state["starting_grasp_limit"])

    updated = text
    meta_cost_start, meta_cost_end = find_section_bounds(updated, "MetaUpgradeCostData")
    meta_cost_text = updated[meta_cost_start:meta_cost_end]
    starting_grasp_pattern = re.compile(
        r"(?m)^([ \t]*StartingMetaUpgradeLimit\s*=\s*)([^,\r\n]+)(,\s*(?:--[^\r\n]*)?)$"
    )
    starting_grasp_matches = list(starting_grasp_pattern.finditer(meta_cost_text))
    if len(starting_grasp_matches) != 1:
        raise PatchError(
            "Expected exactly one 'StartingMetaUpgradeLimit' field in MetaUpgradeCostData."
        )
    starting_grasp_match = starting_grasp_matches[0]
    meta_cost_text = (
        meta_cost_text[: starting_grasp_match.start()]
        + starting_grasp_match.group(1)
        + starting_grasp_limit
        + starting_grasp_match.group(3)
        + meta_cost_text[starting_grasp_match.end() :]
    )

    level_start, level_end = find_section_bounds(meta_cost_text, "MetaUpgradeLevelData")
    level_text = meta_cost_text[level_start:level_end]
    level_text = scale_named_assignments_in_text(
        level_text,
        "CostIncrease",
        grasp_growth_multiplier,
        integer_output=True,
        min_non_zero=True,
    )
    meta_cost_text = meta_cost_text[:level_start] + level_text + meta_cost_text[level_end:]
    updated = updated[:meta_cost_start] + meta_cost_text + updated[meta_cost_end:]

    card_data_start, card_data_end = find_section_bounds(updated, "MetaUpgradeCardData")
    card_data_text = updated[card_data_start:card_data_end]
    for card_name in arcana_editor_state["effect_multipliers"].keys():
        card_start, card_end = find_section_bounds(card_data_text, card_name)
        card_text = card_data_text[card_start:card_end]
        for table_name in ("ResourceCost", "UpgradeResourceCost"):
            if count_multiline_section_headers(card_text, table_name) == 0:
                continue
            table_start, table_end = find_section_bounds(card_text, table_name)
            table_text = card_text[table_start:table_end]
            table_text = scale_all_assignment_values_in_text(
                table_text,
                unlock_upgrade_cost_multiplier,
                integer_output=True,
                min_non_zero=True,
            )
            card_text = card_text[:table_start] + table_text + card_text[table_end:]
        card_data_text = card_data_text[:card_start] + card_text + card_data_text[card_end:]

    updated = updated[:card_data_start] + card_data_text + updated[card_data_end:]

    return updated


def apply_arcana_trait_data_profile(
    text: str,
    arcana_editor_state: dict[str, Any],
    card_trait_map: dict[str, str],
) -> str:
    updated = text
    effect_multipliers = arcana_editor_state["effect_multipliers"]
    for card_name, trait_name in card_trait_map.items():
        if card_name not in effect_multipliers:
            continue
        effect_multiplier = _parse_lua_numeric_expression(str(effect_multipliers[card_name]))
        trait_start, trait_end = find_section_bounds(updated, trait_name)
        trait_text = updated[trait_start:trait_end]
        if count_multiline_section_headers(trait_text, "RarityLevels") == 0:
            continue
        rarity_levels_start, rarity_levels_end = find_section_bounds(trait_text, "RarityLevels")
        rarity_levels_text = trait_text[rarity_levels_start:rarity_levels_end]
        for rarity_key in ("Common", "Rare", "Epic", "Heroic"):
            if count_multiline_section_headers(rarity_levels_text, rarity_key) == 0:
                continue
            rarity_start, rarity_end = find_section_bounds(rarity_levels_text, rarity_key)
            rarity_text = rarity_levels_text[rarity_start:rarity_end]
            rarity_text = scale_all_scalar_assignments_in_block(
                rarity_text,
                "Multiplier",
                effect_multiplier,
                integer_output=False,
                min_non_zero=False,
            )
            rarity_levels_text = (
                rarity_levels_text[:rarity_start] + rarity_text + rarity_levels_text[rarity_end:]
            )
        trait_text = trait_text[:rarity_levels_start] + rarity_levels_text + trait_text[rarity_levels_end:]
        updated = updated[:trait_start] + trait_text + updated[trait_end:]
    return updated


def _parse_lua_numeric_expression(raw_value: str) -> float:
    value = raw_value.strip()
    if not value:
        raise PatchError("Numeric expression cannot be empty.")
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?(?:\s*/\s*[+-]?\d+(?:\.\d+)?)*", value):
        raise PatchError(f"Unsupported expression '{raw_value}'.")
    parts = re.split(r"\s*/\s*", value)
    result = float(parts[0])
    for part in parts[1:]:
        divisor = float(part)
        if divisor == 0:
            raise PatchError(f"Invalid division by zero in expression '{raw_value}'.")
        result /= divisor
    return result


def _round_half_up(value: float) -> int:
    if value >= 0:
        return int(math.floor(value + 0.5))
    return int(math.ceil(value - 0.5))


def _format_float(value: float) -> str:
    if abs(value) < 1e-12:
        return "0"
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text if text else "0"


def scale_all_assignment_values_in_text(
    text: str,
    multiplier: float,
    *,
    integer_output: bool,
    min_non_zero: bool,
) -> str:
    pattern = re.compile(r"(=\s*)([+-]?\d+(?:\.\d+)?(?:\s*/\s*[+-]?\d+(?:\.\d+)?)*)")

    def repl(match: re.Match[str]) -> str:
        original_value = _parse_lua_numeric_expression(match.group(2))
        scaled = original_value * multiplier
        if integer_output:
            rounded = _round_half_up(scaled)
            if min_non_zero and original_value > 0 and rounded < 1:
                rounded = 1
            return f"{match.group(1)}{rounded}"
        return f"{match.group(1)}{_format_float(scaled)}"

    return pattern.sub(repl, text)


def scale_all_scalar_assignments_in_block(
    text: str,
    field_name: str,
    multiplier: float,
    *,
    integer_output: bool,
    min_non_zero: bool,
) -> str:
    pattern = re.compile(rf"(?m)^([ \t]*{re.escape(field_name)}\s*=\s*)([^,\r\n]+)(,?\s*)$")

    def repl(match: re.Match[str]) -> str:
        original_value = _parse_lua_numeric_expression(match.group(2))
        scaled = original_value * multiplier
        if integer_output:
            rounded = _round_half_up(scaled)
            if min_non_zero and original_value > 0 and rounded < 1:
                rounded = 1
            rendered = str(rounded)
        else:
            rendered = _format_float(scaled)
        return f"{match.group(1)}{rendered}{match.group(3)}"

    matches = list(pattern.finditer(text))
    if not matches:
        raise PatchError(f"Expected at least one '{field_name}' assignment to patch.")
    return pattern.sub(repl, text)


def scale_named_assignments_in_text(
    text: str,
    field_name: str,
    multiplier: float,
    *,
    integer_output: bool,
    min_non_zero: bool,
) -> str:
    pattern = re.compile(
        rf"(\b{re.escape(field_name)}\s*=\s*)([+-]?\d+(?:\.\d+)?(?:\s*/\s*[+-]?\d+(?:\.\d+)?)*)"
    )

    def repl(match: re.Match[str]) -> str:
        original_value = _parse_lua_numeric_expression(match.group(2))
        scaled = original_value * multiplier
        if integer_output:
            rounded = _round_half_up(scaled)
            if min_non_zero and original_value > 0 and rounded < 1:
                rounded = 1
            rendered = str(rounded)
        else:
            rendered = _format_float(scaled)
        return f"{match.group(1)}{rendered}"

    matches = list(pattern.finditer(text))
    if not matches:
        raise PatchError(f"Expected at least one '{field_name}' assignment to patch.")
    return pattern.sub(repl, text)


def replace_table_in_section(
    text: str,
    section_name: str,
    field_name: str,
    values: dict[str, str],
) -> str:
    section_start, section_end = find_section_bounds(text, section_name)
    section_text = text[section_start:section_end]
    updated_section = replace_unique_multiline_table(section_text, field_name, values)
    return text[:section_start] + updated_section + text[section_end:]


def replace_unique_multiline_table(
    text: str,
    field_name: str,
    values: dict[str, str],
) -> str:
    pattern = re.compile(
        rf"(?ms)^([ \t]*){re.escape(field_name)}\s*=\s*\r?\n\1\{{\r?\n.*?^\1\}},"
    )
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(f"Expected exactly one '{field_name}' table to patch, found {len(matches)}.")

    match = matches[0]
    indent = match.group(1)
    newline = detect_newline(text)
    replacement_lines = [f"{indent}{field_name} = ", f"{indent}{{"]
    for key, value in values.items():
        replacement_lines.append(f"{indent}\t{key} = {value},")
    replacement_lines.append(f"{indent}}},")
    replacement = newline.join(replacement_lines)
    return text[: match.start()] + replacement + text[match.end() :]


def replace_unique_inline_array(
    text: str,
    field_name: str,
    items: list[str],
) -> str:
    pattern = re.compile(rf"(?m)^([ \t]*){re.escape(field_name)}\s*=\s*\{{.*?\}},\s*$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(f"Expected exactly one '{field_name}' array to patch, found {len(matches)}.")

    indent = matches[0].group(1)
    rendered_items = ", ".join(f'"{item}"' for item in items)
    replacement = f"{indent}{field_name} = {{ {rendered_items} }},"
    match = matches[0]
    return text[: match.start()] + replacement + text[match.end() :]


def replace_scalar_field_in_named_section(
    text: str,
    section_name: str,
    field_name: str,
    value: str,
) -> str:
    section_start, section_end = find_section_bounds(text, section_name)
    section_text = text[section_start:section_end]
    updated_section = replace_unique_scalar_field(section_text, field_name, value)
    return text[:section_start] + updated_section + text[section_end:]


def replace_field_in_named_profile_section(
    text: str,
    parent_section_name: str,
    profile_name: str,
    field_path: str,
    value: str,
) -> str:
    parent_start, parent_end = find_section_bounds(text, parent_section_name)
    parent_text = text[parent_start:parent_end]
    profile_start, profile_end = find_section_bounds(parent_text, profile_name)
    profile_text = parent_text[profile_start:profile_end]
    updated_profile = replace_field_by_path(profile_text, field_path.split("."), value)
    updated_parent = parent_text[:profile_start] + updated_profile + parent_text[profile_end:]
    return text[:parent_start] + updated_parent + text[parent_end:]


def replace_field_in_named_section(
    text: str,
    section_name: str,
    field_path: str,
    value: str,
) -> str:
    section_start, section_end = find_section_bounds(text, section_name)
    section_text = text[section_start:section_end]
    updated_section = replace_field_by_path(section_text, field_path.split("."), value)
    return text[:section_start] + updated_section + text[section_end:]


def replace_field_by_path(text: str, path_segments: list[str], value: str) -> str:
    if not path_segments:
        raise PatchError("Empty keepsake path.")
    if len(path_segments) == 1:
        return replace_unique_scalar_field(text, path_segments[0], value)

    table_name = path_segments[0]
    remaining = path_segments[1:]
    multiline_match_count = count_multiline_section_headers(text, table_name)
    if multiline_match_count == 1:
        section_start, section_end = find_section_bounds(text, table_name)
        section_text = text[section_start:section_end]
        updated_section = replace_field_by_path(section_text, remaining, value)
        return text[:section_start] + updated_section + text[section_end:]
    if multiline_match_count > 1:
        raise PatchError(f"Expected one '{table_name}' section, found {multiline_match_count}.")
    if len(remaining) != 1:
        raise PatchError(
            f"Path segment '{table_name}' must be a multiline table when nested depth exceeds one."
        )
    return replace_inline_table_member(text, table_name, remaining[0], value)


def count_multiline_section_headers(text: str, section_name: str) -> int:
    pattern = re.compile(rf"(?m)^([ \t]*){re.escape(section_name)}\s*=\s*(?:\{{\s*)?$")
    return len(list(pattern.finditer(text)))


def replace_inline_table_member(
    text: str,
    table_name: str,
    member_name: str,
    value: str,
) -> str:
    table_pattern = re.compile(
        rf"(?m)^([ \t]*){re.escape(table_name)}\s*=\s*\{{([^\r\n]*?)\}},\s*$"
    )
    table_matches = list(table_pattern.finditer(text))
    if len(table_matches) != 1:
        raise PatchError(
            f"Expected exactly one inline table '{table_name}' to patch, found {len(table_matches)}."
        )

    table_match = table_matches[0]
    body = table_match.group(2)
    member_pattern = re.compile(rf"(\b{re.escape(member_name)}\s*=\s*)([^,}}]+)")
    member_matches = list(member_pattern.finditer(body))
    if len(member_matches) != 1:
        raise PatchError(
            f"Expected exactly one member '{member_name}' in inline table '{table_name}', "
            f"found {len(member_matches)}."
        )

    member_match = member_matches[0]
    updated_body = (
        body[: member_match.start()]
        + member_match.group(1)
        + value
        + body[member_match.end() :]
    )
    line_text = table_match.group(0)
    replacement_line = line_text.replace(body, updated_body, 1)
    return text[: table_match.start()] + replacement_line + text[table_match.end() :]


def replace_unique_scalar_field(
    text: str,
    field_name: str,
    value: str,
) -> str:
    pattern = re.compile(rf"(?m)^([ \t]*){re.escape(field_name)}\s*=\s*[^,\r\n]+,\s*$")
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        if len(matches) > 1:
            depth_pairs = [
                (calculate_lua_brace_depth_before_index(text, match.start()), match)
                for match in matches
            ]
            shallowest_depth = min(depth for depth, _ in depth_pairs)
            shallow_matches = [match for depth, match in depth_pairs if depth == shallowest_depth]
            if len(shallow_matches) == 1:
                matches = shallow_matches
            else:
                raise PatchError(
                    f"Expected exactly one '{field_name}' field to patch, found {len(matches)}."
                )
        else:
            raise PatchError(f"Expected exactly one '{field_name}' field to patch, found {len(matches)}.")

    match = matches[0]
    indent = match.group(1)
    replacement = f"{indent}{field_name} = {value},"
    return text[: match.start()] + replacement + text[match.end() :]

def calculate_lua_brace_depth_before_index(text: str, stop_index: int) -> int:
    depth = 0
    in_double_quote = False
    in_single_quote = False
    in_line_comment = False
    escape_next = False
    for index in range(0, stop_index):
        character = text[index]
        next_character = text[index + 1] if index + 1 < stop_index else ""

        if in_line_comment:
            if character == "\n":
                in_line_comment = False
            continue

        if in_double_quote:
            if escape_next:
                escape_next = False
                continue
            if character == "\\":
                escape_next = True
                continue
            if character == '"':
                in_double_quote = False
            continue

        if in_single_quote:
            if escape_next:
                escape_next = False
                continue
            if character == "\\":
                escape_next = True
                continue
            if character == "'":
                in_single_quote = False
            continue

        if character == "-" and next_character == "-":
            in_line_comment = True
            continue
        if character == '"':
            in_double_quote = True
            continue
        if character == "'":
            in_single_quote = True
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth = max(0, depth - 1)
    return depth


def replace_resource_cost_money_in_named_section(
    text: str,
    section_name: str,
    value: str,
) -> str:
    section_start, section_end = find_section_bounds(text, section_name)
    section_text = text[section_start:section_end]
    resource_start, resource_end = find_section_bounds(section_text, "ResourceCosts")
    resource_text = section_text[resource_start:resource_end]
    updated_resource_text = replace_unique_scalar_field(resource_text, "Money", value)
    updated_section = section_text[:resource_start] + updated_resource_text + section_text[resource_end:]
    return text[:section_start] + updated_section + text[section_end:]


def replace_pickaxe_max_health_by_resource(
    text: str,
    resource_name: str,
    value: str,
) -> str:
    resource_pattern = re.compile(
        rf'(?m)^([ \t]*)ResourceName\s*=\s*"{re.escape(resource_name)}",\s*$'
    )
    matches = list(resource_pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(
            f"Expected exactly one PickaxePointData entry for ResourceName '{resource_name}', found {len(matches)}."
        )

    resource_match = matches[0]
    block_start_pattern = re.compile(r"(?m)^([ \t]*)\{\s*$")
    chosen_start = None
    chosen_end = None
    chosen_size = None

    for block_match in block_start_pattern.finditer(text, 0, resource_match.start()):
        open_brace_index = text.find("{", block_match.start(), block_match.end())
        close_brace_index = find_matching_brace(text, open_brace_index)
        if not (open_brace_index < resource_match.start() < close_brace_index):
            continue
        block_text = text[block_match.start() : close_brace_index + 1]
        if f'ResourceName = "{resource_name}"' not in block_text:
            continue
        if "MaxHealth" not in block_text:
            continue
        block_size = close_brace_index - block_match.start()
        if chosen_size is None or block_size < chosen_size:
            chosen_size = block_size
            chosen_start = block_match.start()
            chosen_end = close_brace_index

    if chosen_start is None or chosen_end is None:
        raise PatchError(f"Could not locate PickaxePointData option block for ResourceName '{resource_name}'.")

    option_text = text[chosen_start : chosen_end + 1]
    updated_option_text = replace_unique_scalar_field(option_text, "MaxHealth", value)
    return text[:chosen_start] + updated_option_text + text[chosen_end + 1 :]


def patch_dummy_weapon_trait(
    section_text: str,
    trait_name: str,
    valid_weapons: list[str],
    enabled: bool,
    weapon_values: dict[str, str | bool],
) -> str:
    trait_start, trait_end = find_section_bounds(section_text, trait_name)
    trait_text = section_text[trait_start:trait_end]
    trait_text = remove_weapon_damage_marker_block(trait_text)
    if enabled:
        trait_text = insert_weapon_damage_block(trait_text, trait_name, valid_weapons, weapon_values)
    return section_text[:trait_start] + trait_text + section_text[trait_end:]


def remove_weapon_damage_marker_block(text: str) -> str:
    marker_pattern = re.compile(
        rf"(?ms)^[ \t]*{re.escape(WEAPON_DAMAGE_MARKER_START)}.*?^[ \t]*{re.escape(WEAPON_DAMAGE_MARKER_END)}\r?\n?"
    )
    return marker_pattern.sub("", text)


def insert_weapon_damage_block(
    trait_text: str,
    trait_name: str,
    valid_weapons: list[str],
    weapon_values: dict[str, str | bool],
) -> str:
    header_match = re.search(rf"(?m)^([ \t]*){re.escape(trait_name)}\s*=\s*$", trait_text)
    if not header_match:
        raise PatchError(f"Could not find trait header for '{trait_name}'.")

    trait_indent = header_match.group(1)
    inner_indent = trait_indent + "\t"
    close_pattern = re.compile(rf"(?m)^{re.escape(trait_indent)}\}}$")
    close_match = close_pattern.search(trait_text)
    if not close_match:
        raise PatchError(f"Could not find closing brace for trait '{trait_name}'.")

    newline = detect_newline(trait_text)
    rendered_weapons = ", ".join(f'"{weapon_name}"' for weapon_name in valid_weapons)
    block_lines = [f"{inner_indent}{WEAPON_DAMAGE_MARKER_START}"]

    modifier_lines: list[str] = []
    if bool(weapon_values.get("flat_enabled")):
        modifier_lines.append(
            f"{inner_indent}\tValidBaseDamageAddition = {{ BaseValue = {weapon_values['flat_value']} }},"
        )
    if bool(weapon_values.get("multiplier_enabled")):
        modifier_lines.extend(
            [
                f"{inner_indent}\tValidWeaponMultiplier = ",
                f"{inner_indent}\t{{",
                f"{inner_indent}\t\tBaseValue = {weapon_values['multiplier_value']},",
                f"{inner_indent}\t\tSourceIsMultiplier = true,",
                f"{inner_indent}\t}},",
            ]
        )
    if modifier_lines:
        block_lines.extend(
            [
                f"{inner_indent}AddOutgoingDamageModifiers = ",
                f"{inner_indent}{{",
                f"{inner_indent}\tValidWeapons = {{ {rendered_weapons} }},",
                *modifier_lines,
                f"{inner_indent}}},",
            ]
        )

    property_lines: list[str] = []
    if bool(weapon_values.get("range_enabled")):
        property_lines.extend(
            [
                f"{inner_indent}\t{{",
                f"{inner_indent}\t\tWeaponNames = {{ {rendered_weapons} }},",
                f'{inner_indent}\t\tProjectileProperty = "Range",',
                f"{inner_indent}\t\tChangeValue = {weapon_values['range_multiplier']},",
                f'{inner_indent}\t\tChangeType = "Multiply",',
                f"{inner_indent}\t}},",
                f"{inner_indent}\t{{",
                f"{inner_indent}\t\tWeaponNames = {{ {rendered_weapons} }},",
                f'{inner_indent}\t\tWeaponProperty = "AutoLockRange",',
                f"{inner_indent}\t\tChangeValue = {weapon_values['range_multiplier']},",
                f'{inner_indent}\t\tChangeType = "Multiply",',
                f"{inner_indent}\t}},",
            ]
        )
    if bool(weapon_values.get("interval_enabled")):
        property_lines.extend(
            [
                f"{inner_indent}\t{{",
                f"{inner_indent}\t\tWeaponNames = {{ {rendered_weapons} }},",
                f'{inner_indent}\t\tWeaponProperty = "Cooldown",',
                f"{inner_indent}\t\tChangeValue = {weapon_values['interval_multiplier']},",
                f'{inner_indent}\t\tChangeType = "Multiply",',
                f"{inner_indent}\t}},",
            ]
        )
    if property_lines:
        block_lines.extend(
            [
                f"{inner_indent}PropertyChanges = ",
                f"{inner_indent}{{",
                *property_lines,
                f"{inner_indent}}},",
            ]
        )

    block_lines.append(f"{inner_indent}{WEAPON_DAMAGE_MARKER_END}")
    block = newline.join(block_lines) + newline
    return trait_text[: close_match.start()] + block + trait_text[close_match.start() :]


def find_section_bounds(text: str, section_name: str) -> tuple[int, int]:
    pattern = re.compile(
        rf"(?m)^([ \t]*){re.escape(section_name)}\s*=\s*(?:\{{\s*)?(?:--[^\r\n]*)?$"
    )
    match = pattern.search(text)
    if not match:
        raise PatchError(f"Could not find section '{section_name}'.")

    open_brace_index = text.find("{", match.start(), match.end())
    if open_brace_index == -1:
        open_brace_index = text.find("{", match.end())
    if open_brace_index == -1:
        raise PatchError(f"Could not find opening brace for section '{section_name}'.")
    close_brace_index = find_matching_brace(text, open_brace_index)
    return match.start(), close_brace_index + 1


def find_matching_brace(text: str, open_brace_index: int) -> int:
    depth = 0
    in_double_quote = False
    in_single_quote = False
    in_line_comment = False
    escape_next = False
    for index in range(open_brace_index, len(text)):
        character = text[index]
        next_character = text[index + 1] if index + 1 < len(text) else ""

        if in_line_comment:
            if character == "\n":
                in_line_comment = False
            continue

        if in_double_quote:
            if escape_next:
                escape_next = False
                continue
            if character == "\\":
                escape_next = True
                continue
            if character == '"':
                in_double_quote = False
            continue

        if in_single_quote:
            if escape_next:
                escape_next = False
                continue
            if character == "\\":
                escape_next = True
                continue
            if character == "'":
                in_single_quote = False
            continue

        if character == "-" and next_character == "-":
            in_line_comment = True
            continue

        if character == '"':
            in_double_quote = True
            continue
        if character == "'":
            in_single_quote = True
            continue

        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return index
    raise PatchError("Could not find the matching closing brace for a Lua section.")


def replace_function_return_value(text: str, function_name: str, value: str) -> str:
    function_pattern = re.compile(rf"(?ms)(^function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\n)(.*?)(\nend\b)")
    matches = list(function_pattern.finditer(text))
    if len(matches) != 1:
        raise PatchError(f"Expected exactly one function '{function_name}', found {len(matches)}.")

    match = matches[0]
    body = match.group(2)
    return_pattern = re.compile(r"(?m)^([ \t]*)return\s+.*$")
    return_matches = list(return_pattern.finditer(body))
    if len(return_matches) != 1:
        raise PatchError(
            f"Expected exactly one return statement in function '{function_name}', found {len(return_matches)}."
        )

    return_match = return_matches[0]
    indent = return_match.group(1)
    replacement_body = body[: return_match.start()] + f"{indent}return {value}" + body[return_match.end() :]
    return text[: match.start()] + match.group(1) + replacement_body + match.group(3) + text[match.end() :]
