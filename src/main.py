from __future__ import annotations

import json
import sys

from hades_mod_ui.app import run_app
from hades_mod_ui.operations import ModService
from hades_mod_ui.paths import build_app_paths
from hades_mod_ui.state import StateStore


def main() -> int:
    if "--self-test" in sys.argv:
        paths = build_app_paths()
        service = ModService(paths, StateStore(paths.state_file))
        payload = {
            "root_dir": str(paths.root_dir),
            "scripts_dir": str(paths.scripts_dir),
            "scripts_dir_exists": paths.scripts_dir.is_dir(),
            "epic_targets": service.get_target_files("epic_preset", service.default_rarity_editor_state()),
            "rarity_targets_default": service.get_target_files(
                "rarity_editor",
                service.default_rarity_editor_state(),
            ),
            "weapon_damage_targets_default": service.get_target_files(
                "weapon_damage",
                service.default_weapon_damage_state(),
            ),
            "reward_targets_default": service.get_target_files(
                "reward_editor",
                service.default_reward_editor_state(),
            ),
            "keepsake_targets_default": service.get_target_files(
                "keepsake_editor",
                service.default_keepsake_editor_state(),
            ),
        }
        print(json.dumps(payload, indent=2))
        return 0

    run_app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
