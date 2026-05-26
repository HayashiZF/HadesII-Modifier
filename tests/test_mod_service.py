from __future__ import annotations

from pathlib import Path

import pytest

from hades_mod_ui.operations import ModService, OperationError
from hades_mod_ui.paths import AppPaths
from hades_mod_ui.state import StateStore


def _build_paths(root: Path) -> AppPaths:
    scripts_dir = root / "Content" / "Scripts"
    workspace_dir = root / ".hades2_mod"
    return AppPaths(
        root_dir=root,
        scripts_dir=scripts_dir,
        workspace_dir=workspace_dir,
        legacy_workspace_dir=root / ".hades2_mod_ui",
        generated_scripts_dir=workspace_dir / "generated" / "Content" / "Scripts",
        originals_scripts_dir=workspace_dir / "originals" / "Content" / "Scripts",
        state_file=workspace_dir / "state.json",
        dist_dir=root / "dist",
        build_dir=root / "build",
    )


def test_get_target_files_initial_stats_enabled(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    targets = service.get_target_files("initial_stats", {"enabled": True})
    assert targets == ["HeroData.lua", "RunLogic.lua"]


def test_get_target_files_weapon_damage_disabled_returns_empty(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    targets = service.get_target_files(
        "weapon_damage",
        {
            "WeaponStaffSwing": {"enabled": False},
            "WeaponDagger": {"enabled": False},
            "WeaponAxe": {"enabled": False},
            "WeaponTorch": {"enabled": False},
            "WeaponLob": {"enabled": False},
            "WeaponSuit": {"enabled": False},
        },
    )
    assert targets == []


def test_generate_copies_requires_enabled_initial_stats(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    paths.scripts_dir.mkdir(parents=True)
    service = ModService(paths, StateStore(paths.state_file))
    with pytest.raises(OperationError):
        service.generate_copies("initial_stats", {"enabled": False}, {"profiles": {}})


def test_normalize_boon_multiplier_state_builds_defaults_from_metadata(tmp_path) -> None:
    paths = _build_paths(tmp_path)
    service = ModService(paths, StateStore(paths.state_file))
    metadata = {
        "gods": {
            "zeus": {
                "boons": {
                    "LightningBoon": {
                        "fields": {
                            "RarityLevels.Common.Multiplier": {"default": "1.0"}
                        }
                    }
                }
            }
        }
    }
    normalized = service.normalize_boon_multiplier_state({"profiles": {}}, metadata)
    field = normalized["profiles"]["boon_multiplier"]["gods"]["zeus"]["boons"]["LightningBoon"]["fields"][
        "RarityLevels.Common.Multiplier"
    ]
    assert field["value"] == "1.0"
