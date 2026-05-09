from __future__ import annotations

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
        section_text = patch_dummy_weapon_trait(
            section_text,
            trait_name,
            family,
            bool(weapon_state["enabled"]),
            str(weapon_state["value"]),
        )

    return text[:section_start] + section_text + text[section_end:]


def apply_reward_editor_profile(text: str, reward_editor_state: dict[str, dict[str, str | bool]]) -> str:
    updated = text
    for reward_name in REWARD_EDITOR_ORDER:
        reward_state = reward_editor_state[reward_name]
        if not reward_state["enabled"]:
            continue

        reward_meta = REWARD_EDITOR_ENTRIES[reward_name]
        updated = replace_scalar_field_in_named_section(
            updated,
            reward_name,
            reward_meta["amount_field"],
            str(reward_state["value"]),
        )

        if reward_state.get("show_advanced") and "resource_cost_money" in reward_meta:
            updated = replace_resource_cost_money_in_named_section(
                updated,
                reward_name,
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


def patch_dummy_weapon_trait(
    section_text: str,
    trait_name: str,
    valid_weapons: list[str],
    enabled: bool,
    base_value: str,
) -> str:
    trait_start, trait_end = find_section_bounds(section_text, trait_name)
    trait_text = section_text[trait_start:trait_end]
    trait_text = remove_weapon_damage_marker_block(trait_text)
    if enabled:
        trait_text = insert_weapon_damage_block(trait_text, trait_name, valid_weapons, base_value)
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
    base_value: str,
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
    block_lines = [
        f"{inner_indent}{WEAPON_DAMAGE_MARKER_START}",
        f"{inner_indent}AddOutgoingDamageModifiers = ",
        f"{inner_indent}{{",
        f"{inner_indent}\tValidWeapons = {{ {rendered_weapons} }},",
        f"{inner_indent}\tValidBaseDamageAddition = {{ BaseValue = {base_value} }},",
        f"{inner_indent}}},",
        f"{inner_indent}{WEAPON_DAMAGE_MARKER_END}",
    ]
    block = newline.join(block_lines) + newline
    return trait_text[: close_match.start()] + block + trait_text[close_match.start() :]


def find_section_bounds(text: str, section_name: str) -> tuple[int, int]:
    pattern = re.compile(rf"(?m)^([ \t]*){re.escape(section_name)}\s*=\s*(?:\{{\s*)?$")
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
