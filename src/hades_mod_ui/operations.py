from __future__ import annotations

import ast
import copy
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any, Callable

from .patches import (
    apply_initial_stats_hero_data_profile,
    apply_initial_stats_run_logic_profile,
    apply_keepsake_editor_profile,
    apply_refresh_event_logic_profile,
    apply_refresh_hammer_profile,
    apply_refresh_market_logic_profile,
    apply_reward_editor_profile,
    WEAPON_DAMAGE_FAMILY_MAP,
    apply_epic_preset,
    apply_weapon_damage_profile,
    find_matching_brace,
    parse_roll_order,
    replace_field_in_named_section,
    replace_table_in_section,
    replace_unique_inline_array,
    replace_unique_multiline_table,
    validate_number_string,
    validate_probability_string,
    validate_positive_number_string,
    validate_signed_number_string,
    validate_whole_number_string,
)
from .paths import AppPaths
from .state import (
    BOON_MULTIPLIER_GOD_FILE_MAP,
    BOON_MULTIPLIER_GOD_SOURCES,
    DEFAULT_BOON_MULTIPLIER_STATE,
    DEFAULT_INITIAL_STATS_STATE,
    DEFAULT_KEEPSAKE_EDITOR_STATE,
    DEFAULT_RARITY_EDITOR_STATE,
    DEFAULT_REFRESH_STATE,
    DEFAULT_REWARD_EDITOR_STATE,
    DEFAULT_WEAPON_DAMAGE_STATE,
    KEEPSAKE_EDITOR_CONFIG,
    KEEPSAKE_EDITOR_ORDER,
    REFRESH_FEATURE_ORDER,
    REWARD_EDITOR_ENTRIES,
    REWARD_EDITOR_ORDER,
    StateStore,
)


class OperationError(RuntimeError):
    pass


class ModService:
    def __init__(self, paths: AppPaths, state_store: StateStore) -> None:
        self.paths = paths
        self.state_store = state_store

    def default_rarity_editor_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_RARITY_EDITOR_STATE)

    def default_weapon_damage_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_WEAPON_DAMAGE_STATE)

    def default_reward_editor_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_REWARD_EDITOR_STATE)

    def default_keepsake_editor_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_KEEPSAKE_EDITOR_STATE)

    def default_boon_multiplier_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_BOON_MULTIPLIER_STATE)

    def default_initial_stats_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_INITIAL_STATS_STATE)

    def default_refresh_state(self) -> dict[str, Any]:
        return copy.deepcopy(DEFAULT_REFRESH_STATE)

    def load_state(self) -> dict[str, Any]:
        return self.state_store.load()

    def save_state(self, state: dict[str, Any]) -> None:
        self.state_store.save(state)

    def migrate_legacy_workspace(self) -> bool:
        legacy_dir = self.paths.legacy_workspace_dir
        target_dir = self.paths.workspace_dir
        if target_dir.exists() or not legacy_dir.exists():
            return False
        shutil.move(str(legacy_dir), str(target_dir))
        return True

    def validate_scripts_dir(self) -> tuple[bool, str]:
        return self.paths.scripts_status()

    def discover_boon_multiplier_metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {"gods": {}}
        scripts_dir = self.paths.scripts_dir

        for god_key, god_title, file_name in BOON_MULTIPLIER_GOD_SOURCES:
            god_info: dict[str, Any] = {
                "title": god_title,
                "file": file_name,
                "boons": {},
            }
            source_path = scripts_dir / file_name
            if not source_path.exists():
                metadata["gods"][god_key] = god_info
                continue

            content = source_path.read_text(encoding="utf-8")
            boon_sections = self._find_boon_sections(content)
            for boon_name, boon_start, boon_end in boon_sections:
                boon_text = content[boon_start:boon_end]
                scalar_paths = self._extract_scalar_paths(boon_text)
                fields: dict[str, dict[str, Any]] = {}
                source_is_multiplier_paths: list[str] = []
                for path, value in scalar_paths:
                    normalized_path = path
                    prefix = f"{boon_name}."
                    if normalized_path.startswith(prefix):
                        normalized_path = normalized_path[len(prefix) :]

                    if self._is_boon_multiplier_field(normalized_path):
                        normalized_default = self._normalize_multiplier_default(value)
                        fields[normalized_path] = {
                            "default": normalized_default,
                            "advanced": ".AbsoluteStackValues." in normalized_path,
                        }
                        continue

                    if self._is_source_is_multiplier_flag(normalized_path):
                        source_is_multiplier_paths.append(normalized_path)

                god_info["boons"][boon_name] = {
                    "fields": fields,
                    "source_is_multiplier_paths": source_is_multiplier_paths,
                }

            metadata["gods"][god_key] = god_info

        return metadata

    def normalize_boon_multiplier_state(
        self,
        state: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        profiles = state.setdefault("profiles", {})
        raw_profile = profiles.get("boon_multiplier", {})
        raw_gods = raw_profile.get("gods", {}) if isinstance(raw_profile, dict) else {}

        normalized_gods: dict[str, Any] = {}
        for god_key, god_meta in metadata.get("gods", {}).items():
            existing_god = raw_gods.get(god_key, {}) if isinstance(raw_gods, dict) else {}
            existing_boons = existing_god.get("boons", {}) if isinstance(existing_god, dict) else {}

            normalized_boons: dict[str, Any] = {}
            for boon_name, boon_meta in god_meta.get("boons", {}).items():
                existing_boon = existing_boons.get(boon_name, {}) if isinstance(existing_boons, dict) else {}
                existing_fields = existing_boon.get("fields", {}) if isinstance(existing_boon, dict) else {}

                normalized_fields: dict[str, Any] = {}
                for field_path, field_meta in boon_meta.get("fields", {}).items():
                    existing_field = (
                        existing_fields.get(field_path, {}) if isinstance(existing_fields, dict) else {}
                    )
                    normalized_fields[field_path] = {
                        "value": str(existing_field.get("value", field_meta.get("default", "1"))),
                    }

                normalized_boons[boon_name] = {
                    "enabled": bool(existing_boon.get("enabled", False)),
                    "show_advanced": bool(existing_boon.get("show_advanced", False)),
                    "fields": normalized_fields,
                }

            normalized_gods[god_key] = {
                "enabled": bool(existing_god.get("enabled", False)),
                "boons": normalized_boons,
            }

        profiles["boon_multiplier"] = {"gods": normalized_gods}
        return state

    def get_target_files(self, profile: str, profile_state: dict[str, Any]) -> list[str]:
        if profile == "epic_preset":
            return ["TraitLogic.lua"]
        if profile == "initial_stats":
            if bool(profile_state.get("enabled")):
                return ["HeroData.lua", "RunLogic.lua"]
            return []
        if profile == "boon_multiplier":
            targets: list[str] = []
            gods = profile_state.get("gods", {})
            for god_key, god_state in gods.items():
                if not bool(god_state.get("enabled")):
                    continue
                boons = god_state.get("boons", {})
                if any(bool(boon_state.get("enabled")) for boon_state in boons.values()):
                    file_name = BOON_MULTIPLIER_GOD_FILE_MAP.get(god_key)
                    if file_name:
                        targets.append(file_name)
            return sorted(set(targets))
        if profile == "weapon_damage":
            if any(bool(weapon_state.get("enabled")) for weapon_state in profile_state.values()):
                return ["TraitData.lua"]
            return []
        if profile == "refresh":
            targets: list[str] = []
            if bool(profile_state.get("hammer_refreshable", {}).get("enabled")):
                targets.append("MetaUpgradeData.lua")
            if bool(profile_state.get("npc_boon_refreshable", {}).get("enabled")):
                targets.append("EventLogic.lua")
            if bool(profile_state.get("unlimited_exotic_goods", {}).get("enabled")):
                targets.append("MarketLogic.lua")
            return sorted(set(targets))
        if profile == "reward_editor":
            enabled_reward_names = [
                reward_name
                for reward_name, reward_state in profile_state.items()
                if bool(reward_state.get("enabled"))
            ]
            if enabled_reward_names:
                return sorted(
                    {
                        str(REWARD_EDITOR_ENTRIES[reward_name]["target_file"])
                        for reward_name in enabled_reward_names
                    }
                )
            return []
        if profile == "keepsake_editor":
            if any(bool(keepsake_state.get("enabled")) for keepsake_state in profile_state.values()):
                return ["TraitData_Keepsake.lua"]
            return []

        targets: list[str] = []
        if profile_state["normal_gods"]["enabled"] or profile_state["hermes"]["enabled"]:
            targets.append("HeroData.lua")
        if profile_state["chaos"]["enabled"]:
            targets.append("LootData_Chaos.lua")
        if profile_state["artemis"]["enabled"]:
            targets.append("NPCData_Artemis.lua")
        if profile_state["hades"]["enabled"]:
            targets.append("NPCData_Hades.lua")
        if profile_state["icarus"]["enabled"]:
            targets.append("NPCData_Icarus.lua")
        return targets

    def generate_copies(
        self,
        profile: str,
        profile_state: dict[str, Any],
        state: dict[str, Any],
    ) -> list[str]:
        valid, message = self.validate_scripts_dir()
        if not valid:
            raise OperationError(message)

        targets = self.get_target_files(profile, profile_state)
        if not targets:
            if profile == "initial_stats":
                raise OperationError("Enable Initial Stats patch before generating copies.")
            if profile == "boon_multiplier":
                raise OperationError(
                    "Enable at least one god and one boon in Boon Multipliers before generating copies."
                )
            if profile == "weapon_damage":
                raise OperationError("Enable at least one weapon damage patch before generating copies.")
            if profile == "reward_editor":
                raise OperationError("Enable at least one reward amount patch before generating copies.")
            if profile == "keepsake_editor":
                raise OperationError("Enable at least one keepsake patch before generating copies.")
            if profile == "refresh":
                raise OperationError("Enable at least one refresh patch before generating copies.")
            raise OperationError("Select at least one rarity source before generating copies.")

        generators = self._build_generators(profile, profile_state)
        self.paths.generated_scripts_dir.mkdir(parents=True, exist_ok=True)

        generated_files: list[str] = []
        for relative_name in targets:
            source_path = self.paths.scripts_dir / relative_name
            if not source_path.exists():
                raise OperationError(f"Missing target file: {source_path}")

            content = source_path.read_text(encoding="utf-8")
            transformed = generators[relative_name](content)
            destination_path = self.paths.generated_scripts_dir / relative_name
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            with destination_path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(transformed)
            generated_files.append(relative_name)

        state["generated_files"] = sorted(generated_files)
        self.save_state(state)
        return sorted(generated_files)

    def backup_originals(self, relative_names: list[str], state: dict[str, Any]) -> list[str]:
        if not relative_names:
            raise OperationError("There are no target files to back up for the current selection.")

        self.paths.originals_scripts_dir.mkdir(parents=True, exist_ok=True)
        missing_sources = [
            str(self.paths.scripts_dir / relative_name)
            for relative_name in relative_names
            if not (self.paths.scripts_dir / relative_name).exists()
        ]
        if missing_sources:
            raise OperationError("Missing files to back up:\n" + "\n".join(missing_sources))

        newly_backed_up: list[str] = []
        for relative_name in relative_names:
            source_path = self.paths.scripts_dir / relative_name
            backup_path = self.paths.originals_scripts_dir / relative_name
            if not backup_path.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, backup_path)
                newly_backed_up.append(relative_name)

        known = set(state.get("known_backups", []))
        known.update(relative_names)
        state["known_backups"] = sorted(known)
        self.save_state(state)
        return sorted(newly_backed_up)

    def apply_generated_files(self, relative_names: list[str], state: dict[str, Any], profile: str) -> list[str]:
        if not relative_names:
            raise OperationError("There are no generated files to apply.")

        self.backup_originals(relative_names, state)
        pairs = []
        for relative_name in relative_names:
            generated_path = self.paths.generated_scripts_dir / relative_name
            destination_path = self.paths.scripts_dir / relative_name
            if not generated_path.exists():
                raise OperationError(f"Generated file is missing: {generated_path}")
            pairs.append((generated_path, destination_path))

        self._replace_files(pairs)
        state["last_apply"] = {
            "profile": profile,
            "files": sorted(relative_names),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        self.save_state(state)
        return sorted(relative_names)

    def restore_all_backups(self, state: dict[str, Any]) -> list[str]:
        relative_names = sorted(state.get("known_backups", []))
        if not relative_names:
            raise OperationError("No backups are available to restore.")

        pairs = []
        missing_backups = []
        for relative_name in relative_names:
            backup_path = self.paths.originals_scripts_dir / relative_name
            destination_path = self.paths.scripts_dir / relative_name
            if not backup_path.exists():
                missing_backups.append(str(backup_path))
            else:
                pairs.append((backup_path, destination_path))

        if missing_backups:
            raise OperationError("Missing backup files:\n" + "\n".join(missing_backups))

        self._replace_files(pairs)
        state["last_restore"] = {
            "files": relative_names,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        self.save_state(state)
        return relative_names

    def _build_generators(
        self,
        profile: str,
        profile_state: dict[str, Any],
    ) -> dict[str, Callable[[str], str]]:
        if profile == "epic_preset":
            return {"TraitLogic.lua": apply_epic_preset}
        if profile == "boon_multiplier":
            metadata = self.discover_boon_multiplier_metadata()
            normalized_state = self.normalize_boon_multiplier_state(
                {"profiles": {"boon_multiplier": profile_state}},
                metadata,
            )["profiles"]["boon_multiplier"]
            validated_state = self._validate_boon_multiplier_state(normalized_state, metadata)
            return self._build_boon_multiplier_generators(validated_state, metadata)
        if profile == "weapon_damage":
            validated_state = self._validate_weapon_damage_state(profile_state)
            return {
                "TraitData.lua": lambda text: apply_weapon_damage_profile(text, validated_state),
            }
        if profile == "reward_editor":
            validated_state = self._validate_reward_editor_state(profile_state)
            target_files = sorted(
                {
                    str(REWARD_EDITOR_ENTRIES[reward_name]["target_file"])
                    for reward_name in REWARD_EDITOR_ORDER
                    if bool(validated_state[reward_name]["enabled"])
                }
            )
            return {
                target_file: (
                    lambda text, _target_file=target_file: apply_reward_editor_profile(
                        text,
                        validated_state,
                        _target_file,
                    )
                )
                for target_file in target_files
            }
        if profile == "keepsake_editor":
            validated_state = self._validate_keepsake_editor_state(profile_state)
            return {
                "TraitData_Keepsake.lua": lambda text: apply_keepsake_editor_profile(text, validated_state),
            }
        if profile == "initial_stats":
            validated_state = self._validate_initial_stats_state(profile_state)
            return {
                "HeroData.lua": lambda text: apply_initial_stats_hero_data_profile(text, validated_state),
                "RunLogic.lua": lambda text: apply_initial_stats_run_logic_profile(text, validated_state),
            }
        if profile == "refresh":
            validated_state = self._validate_refresh_state(profile_state)
            generators: dict[str, Callable[[str], str]] = {}
            if validated_state["hammer_refreshable"]["enabled"]:
                generators["MetaUpgradeData.lua"] = apply_refresh_hammer_profile
            if validated_state["npc_boon_refreshable"]["enabled"]:
                generators["EventLogic.lua"] = apply_refresh_event_logic_profile
            if validated_state["unlimited_exotic_goods"]["enabled"]:
                generators["MarketLogic.lua"] = apply_refresh_market_logic_profile
            return generators

        validated_state = self._validate_rarity_editor_state(profile_state)
        generators: dict[str, Callable[[str], str]] = {}

        if validated_state["normal_gods"]["enabled"] or validated_state["hermes"]["enabled"]:
            def hero_data_generator(text: str) -> str:
                updated = text
                if validated_state["normal_gods"]["enabled"]:
                    updated = replace_table_in_section(
                        updated,
                        "BoonData",
                        "RarityChances",
                        validated_state["normal_gods"]["values"],
                    )
                if validated_state["hermes"]["enabled"]:
                    updated = replace_table_in_section(
                        updated,
                        "HermesData",
                        "RarityChances",
                        validated_state["hermes"]["values"],
                    )
                return updated

            generators["HeroData.lua"] = hero_data_generator

        if validated_state["chaos"]["enabled"]:
            generators["LootData_Chaos.lua"] = lambda text: replace_unique_multiline_table(
                text,
                "BoonRaritiesOverride",
                validated_state["chaos"]["values"],
            )

        if validated_state["artemis"]["enabled"]:
            generators["NPCData_Artemis.lua"] = lambda text: self._apply_rarity_and_roll_order(
                text,
                "RarityChances",
                validated_state["artemis"]["values"],
                validated_state["artemis"]["roll_order_list"],
            )

        if validated_state["hades"]["enabled"]:
            generators["NPCData_Hades.lua"] = lambda text: self._apply_rarity_and_roll_order(
                text,
                "RarityChances",
                validated_state["hades"]["values"],
                validated_state["hades"]["roll_order_list"],
            )

        if validated_state["icarus"]["enabled"]:
            generators["NPCData_Icarus.lua"] = lambda text: self._apply_rarity_and_roll_order(
                text,
                "RarityChances",
                validated_state["icarus"]["values"],
                validated_state["icarus"]["roll_order_list"],
            )

        return generators

    def _apply_rarity_and_roll_order(
        self,
        text: str,
        table_name: str,
        values: dict[str, str],
        roll_order: list[str],
    ) -> str:
        updated = replace_unique_multiline_table(text, table_name, values)
        updated = replace_unique_inline_array(updated, "RarityRollOrder", roll_order)
        return updated

    def _validate_rarity_editor_state(self, rarity_editor_state: dict[str, Any]) -> dict[str, Any]:
        validated = copy.deepcopy(rarity_editor_state)
        for source_name, source_state in validated.items():
            values = source_state.get("values", {})
            for key, value in values.items():
                values[key] = validate_number_string(value, f"{source_name}.{key}")
            if "roll_order" in source_state:
                source_state["roll_order"] = source_state["roll_order"].strip()
                source_state["roll_order_list"] = parse_roll_order(
                    source_state["roll_order"],
                    f"{source_name}.roll_order",
                )
        return validated

    def _validate_weapon_damage_state(self, weapon_damage_state: dict[str, Any]) -> dict[str, Any]:
        validated = copy.deepcopy(weapon_damage_state)
        for weapon_name in WEAPON_DAMAGE_FAMILY_MAP:
            if weapon_name not in validated:
                raise OperationError(f"Missing weapon damage configuration for {weapon_name}.")
            source_state = validated[weapon_name]
            source_state["enabled"] = bool(source_state.get("enabled"))
            source_state["value"] = validate_signed_number_string(
                str(source_state.get("value", "")).strip(),
                f"{weapon_name}.value",
            )
        return validated

    def _validate_reward_editor_state(self, reward_editor_state: dict[str, Any]) -> dict[str, Any]:
        validated = copy.deepcopy(reward_editor_state)
        for reward_name in REWARD_EDITOR_ORDER:
            if reward_name not in validated:
                raise OperationError(f"Missing reward editor configuration for {reward_name}.")

            reward_meta = REWARD_EDITOR_ENTRIES[reward_name]
            reward_state = validated[reward_name]
            reward_state["enabled"] = bool(reward_state.get("enabled"))
            reward_state["show_advanced"] = bool(reward_state.get("show_advanced"))
            reward_state["value"] = validate_whole_number_string(
                str(reward_state.get("value", "")).strip(),
                f"{reward_name}.value",
            )

            if "resource_cost_money" in reward_meta:
                reward_state["resource_cost_money"] = validate_whole_number_string(
                    str(reward_state.get("resource_cost_money", "")).strip(),
                    f"{reward_name}.resource_cost_money",
                )
        return validated

    def _validate_keepsake_editor_state(self, keepsake_editor_state: dict[str, Any]) -> dict[str, Any]:
        validated = copy.deepcopy(keepsake_editor_state)
        for keepsake_name in KEEPSAKE_EDITOR_ORDER:
            if keepsake_name not in validated:
                raise OperationError(f"Missing keepsake editor configuration for {keepsake_name}.")

            keepsake_meta = KEEPSAKE_EDITOR_CONFIG[keepsake_name]
            keepsake_state = validated[keepsake_name]
            keepsake_state["enabled"] = bool(keepsake_state.get("enabled"))
            keepsake_state["show_advanced"] = bool(keepsake_state.get("show_advanced"))
            fields = keepsake_state.get("fields", {})

            for field_id, field_meta in keepsake_meta["fields"].items():
                raw_value = str(fields.get(field_id, "")).strip()
                label = f"{keepsake_name}.{field_id}"
                input_type = field_meta["input_type"]
                if input_type == "int":
                    fields[field_id] = validate_whole_number_string(raw_value, label)
                elif input_type == "float":
                    fields[field_id] = validate_number_string(raw_value, label)
                elif input_type == "chance_0_1":
                    fields[field_id] = validate_probability_string(raw_value, label)
                elif input_type == "positive_multiplier":
                    fields[field_id] = validate_positive_number_string(raw_value, label)
                else:
                    raise OperationError(f"Unsupported keepsake input type '{input_type}' for {label}.")
            keepsake_state["fields"] = fields
        return validated

    def _validate_initial_stats_state(self, initial_stats_state: dict[str, Any]) -> dict[str, Any]:
        validated = copy.deepcopy(initial_stats_state)
        validated["enabled"] = bool(validated.get("enabled"))
        validated["max_health"] = validate_whole_number_string(
            str(validated.get("max_health", "")).strip(),
            "initial_stats.max_health",
        )
        validated["max_mana"] = validate_whole_number_string(
            str(validated.get("max_mana", "")).strip(),
            "initial_stats.max_mana",
        )
        validated["starting_money"] = validate_whole_number_string(
            str(validated.get("starting_money", "")).strip(),
            "initial_stats.starting_money",
        )
        return validated

    def _validate_refresh_state(self, refresh_state: dict[str, Any]) -> dict[str, Any]:
        validated = copy.deepcopy(refresh_state)
        for feature_key, _title in REFRESH_FEATURE_ORDER:
            if feature_key not in validated:
                raise OperationError(f"Missing refresh configuration for {feature_key}.")
            feature_state = validated[feature_key]
            feature_state["enabled"] = bool(feature_state.get("enabled"))
        return validated

    def _build_boon_multiplier_generators(
        self,
        validated_state: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Callable[[str], str]]:
        generators: dict[str, Callable[[str], str]] = {}

        for god_key, god_state in validated_state.get("gods", {}).items():
            if not bool(god_state.get("enabled")):
                continue

            god_meta = metadata["gods"].get(god_key, {})
            file_name = god_meta.get("file")
            if not file_name:
                continue

            boon_updates: list[tuple[str, dict[str, str]]] = []
            for boon_name, boon_state in god_state.get("boons", {}).items():
                if not bool(boon_state.get("enabled")):
                    continue
                fields = {
                    field_path: str(field_state.get("value", ""))
                    for field_path, field_state in boon_state.get("fields", {}).items()
                }
                if fields:
                    boon_updates.append((boon_name, fields))

            if not boon_updates:
                continue

            def file_generator(text: str, updates: list[tuple[str, dict[str, str]]] = boon_updates) -> str:
                updated = text
                for boon_name, fields in updates:
                    for field_path, field_value in fields.items():
                        updated = replace_field_in_named_section(updated, boon_name, field_path, field_value)
                return updated

            generators[file_name] = file_generator

        return generators

    def _validate_boon_multiplier_state(
        self,
        boon_multiplier_state: dict[str, Any],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        validated = copy.deepcopy(boon_multiplier_state)
        gods = validated.get("gods", {})

        for god_key, god_meta in metadata.get("gods", {}).items():
            if god_key not in gods:
                raise OperationError(f"Missing boon multiplier configuration for god '{god_key}'.")

            god_state = gods[god_key]
            god_state["enabled"] = bool(god_state.get("enabled"))
            boons = god_state.get("boons", {})
            expected_boons = god_meta.get("boons", {})

            for boon_name, boon_meta in expected_boons.items():
                if boon_name not in boons:
                    raise OperationError(f"Missing boon multiplier configuration for boon '{boon_name}'.")

                boon_state = boons[boon_name]
                boon_state["enabled"] = bool(boon_state.get("enabled"))
                boon_state["show_advanced"] = bool(boon_state.get("show_advanced"))
                fields = boon_state.get("fields", {})

                for field_path in boon_meta.get("fields", {}).keys():
                    if field_path not in fields:
                        raise OperationError(f"Missing multiplier field '{boon_name}.{field_path}'.")
                    field_state = fields[field_path]
                    label = f"{boon_name}.{field_path}"
                    validated_value = validate_positive_number_string(
                        str(field_state.get("value", "")).strip(),
                        label,
                    )
                    field_state["value"] = validated_value

        return validated

    def _find_boon_sections(self, text: str) -> list[tuple[str, int, int]]:
        pattern = re.compile(r"(?m)^([ \t]*)([A-Za-z0-9_]+Boon)\s*=\s*(?:--.*)?$")
        matches = list(pattern.finditer(text))
        if not matches:
            return []

        sections: list[tuple[str, int, int, int]] = []
        for match in matches:
            open_brace_index = text.find("{", match.end())
            if open_brace_index == -1:
                continue
            try:
                close_brace_index = find_matching_brace(text, open_brace_index)
            except ValueError:
                continue
            depth = self._calculate_lua_brace_depth_before_index(text, match.start())
            sections.append((match.group(2), match.start(), close_brace_index + 1, depth))

        if not sections:
            return []

        shallowest_depth = min(depth for _name, _start, _end, depth in sections)
        top_level_sections = [
            (name, start, end)
            for name, start, end, depth in sections
            if depth == shallowest_depth
        ]
        return top_level_sections

    def _extract_scalar_paths(self, table_text: str) -> list[tuple[str, str]]:
        scalar_matches = list(
            re.finditer(
                r"(?m)^([ \t]*)([A-Za-z_][A-Za-z0-9_]*|\[\d+\])\s*=\s*([^,\r\n]+),\s*(?:--.*)?$",
                table_text,
            )
        )
        table_sections = self._discover_multiline_table_sections(table_text)
        scalar_paths: list[tuple[str, str]] = []

        for match in scalar_matches:
            raw_value = match.group(3).strip()
            if raw_value.startswith("{"):
                continue

            key_name = match.group(2)
            parent_path = self._find_parent_path(table_sections, match.start())
            full_path = ".".join([*parent_path, key_name]) if parent_path else key_name
            scalar_paths.append((full_path, self._trim_lua_comment(raw_value)))

        inline_table_matches = list(
            re.finditer(
                r"(?m)^([ \t]*)([A-Za-z_][A-Za-z0-9_]*|\[\d+\])\s*=\s*\{([^{}]*)\},\s*(?:--.*)?$",
                table_text,
            )
        )
        member_pattern = re.compile(r"([A-Za-z_][A-Za-z0-9_]*|\[\d+\])\s*=\s*([^,}]+)")
        for match in inline_table_matches:
            table_key = match.group(2)
            body = match.group(3)
            parent_path = self._find_parent_path(table_sections, match.start())
            base_path = [*parent_path, table_key] if parent_path else [table_key]
            for member_match in member_pattern.finditer(body):
                member_key = member_match.group(1)
                member_value = self._trim_lua_comment(member_match.group(2))
                full_path = ".".join([*base_path, member_key])
                scalar_paths.append((full_path, member_value))

        return scalar_paths

    def _discover_multiline_table_sections(self, text: str) -> list[dict[str, Any]]:
        header_pattern = re.compile(
            r"(?m)^([ \t]*)([A-Za-z_][A-Za-z0-9_]*|\[\d+\])\s*=\s*(?:\{\s*)?(?:--.*)?$"
        )
        matches = list(header_pattern.finditer(text))
        sections: list[dict[str, Any]] = []

        for match in matches:
            line_end = text.find("\n", match.start())
            if line_end == -1:
                line_end = len(text)
            open_brace_index = text.find("{", match.start(), line_end)
            if open_brace_index == -1:
                open_brace_index = text.find("{", line_end)
            if open_brace_index == -1:
                continue

            try:
                close_brace_index = find_matching_brace(text, open_brace_index)
            except ValueError:
                continue

            sections.append(
                {
                    "key": match.group(2),
                    "start": match.start(),
                    "end": close_brace_index + 1,
                    "path": [],
                }
            )

        sections.sort(key=lambda item: (item["start"], -(item["end"] - item["start"])))
        for section in sections:
            parent = self._find_parent_section(sections, section)
            if parent is None:
                section["path"] = [section["key"]]
            else:
                section["path"] = [*parent["path"], section["key"]]
        return sections

    def _find_parent_section(
        self,
        sections: list[dict[str, Any]],
        current: dict[str, Any],
    ) -> dict[str, Any] | None:
        candidates = [
            section
            for section in sections
            if section is not current
            and section["start"] < current["start"]
            and section["end"] >= current["end"]
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda section: section["end"] - section["start"])

    def _find_parent_path(self, sections: list[dict[str, Any]], index: int) -> list[str]:
        candidates = [
            section
            for section in sections
            if section["start"] < index < section["end"]
        ]
        if not candidates:
            return []
        deepest = min(candidates, key=lambda section: section["end"] - section["start"])
        return deepest["path"]

    def _calculate_lua_brace_depth_before_index(self, text: str, stop_index: int) -> int:
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

    def _trim_lua_comment(self, value: str) -> str:
        comment_index = value.find("--")
        if comment_index == -1:
            return value.strip()
        return value[:comment_index].strip()

    def _is_boon_multiplier_field(self, path: str) -> bool:
        segments = path.split(".")
        if len(segments) >= 3 and segments[0] == "RarityLevels" and segments[-1] == "Multiplier":
            return True
        if len(segments) >= 2 and segments[-1] == "BaseValue" and segments[-2].endswith("Multiplier"):
            return True
        if (
            len(segments) >= 3
            and segments[-2] == "AbsoluteStackValues"
            and re.fullmatch(r"\[\d+\]", segments[-1]) is not None
            and segments[-3].endswith("Multiplier")
        ):
            return True
        return False

    def _is_source_is_multiplier_flag(self, path: str) -> bool:
        segments = path.split(".")
        return (
            len(segments) >= 2
            and segments[-1] == "SourceIsMultiplier"
            and segments[-2].endswith("Multiplier")
        )

    def _normalize_multiplier_default(self, value: str) -> str:
        trimmed = value.strip()
        fraction_match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*([0-9]+(?:\.[0-9]+)?)", trimmed)
        if fraction_match:
            numerator = float(fraction_match.group(1))
            denominator = float(fraction_match.group(2))
            if denominator == 0:
                return trimmed
            computed = numerator / denominator
            return f"{computed:.10g}"
        try:
            float(trimmed)
            return trimmed
        except ValueError:
            pass
        if re.fullmatch(r"[0-9\.\+\-\*\/\(\)\s]+", trimmed):
            evaluated = self._safe_eval_numeric_expression(trimmed)
            if evaluated is not None:
                return f"{evaluated:.10g}"
        return trimmed

    def _safe_eval_numeric_expression(self, expression: str) -> float | None:
        try:
            parsed = ast.parse(expression, mode="eval")
        except SyntaxError:
            return None

        def evaluate(node: ast.AST) -> float:
            if isinstance(node, ast.Expression):
                return evaluate(node.body)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return float(node.value)
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                value = evaluate(node.operand)
                return value if isinstance(node.op, ast.UAdd) else -value
            if isinstance(node, ast.BinOp):
                left = evaluate(node.left)
                right = evaluate(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                if isinstance(node.op, ast.Div):
                    return left / right
            raise ValueError("Unsupported expression")

        try:
            return evaluate(parsed)
        except (ValueError, ZeroDivisionError):
            return None

    def _replace_files(self, pairs: list[tuple[Path, Path]]) -> None:
        if not pairs:
            raise OperationError("There are no files to copy.")

        workspace_temp_dir = self.paths.workspace_dir / "rollback"
        workspace_temp_dir.mkdir(parents=True, exist_ok=True)
        rollback_dir = Path(tempfile.mkdtemp(prefix="replace_", dir=workspace_temp_dir))
        copied_destinations: list[tuple[Path, Path]] = []

        try:
            for source_path, destination_path in pairs:
                if not source_path.exists():
                    raise OperationError(f"Missing source file for copy: {source_path}")
                if not destination_path.exists():
                    raise OperationError(f"Missing destination file for copy: {destination_path}")

            for _, destination_path in pairs:
                rollback_path = rollback_dir / destination_path.name
                shutil.copy2(destination_path, rollback_path)
                copied_destinations.append((destination_path, rollback_path))

            for source_path, destination_path in pairs:
                shutil.copy2(source_path, destination_path)
        except Exception as exc:
            for destination_path, rollback_path in copied_destinations:
                if rollback_path.exists():
                    shutil.copy2(rollback_path, destination_path)
            if isinstance(exc, OperationError):
                raise
            raise OperationError(str(exc)) from exc
        finally:
            shutil.rmtree(rollback_dir, ignore_errors=True)
