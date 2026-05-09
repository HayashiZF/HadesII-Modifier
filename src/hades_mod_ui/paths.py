from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class AppPaths:
    root_dir: Path
    scripts_dir: Path
    workspace_dir: Path
    legacy_workspace_dir: Path
    generated_scripts_dir: Path
    originals_scripts_dir: Path
    state_file: Path
    dist_dir: Path
    build_dir: Path

    def scripts_status(self) -> tuple[bool, str]:
        if self.scripts_dir.is_dir():
            return True, f"Using scripts directory: {self.scripts_dir}"
        return False, (
            "Expected Content/Scripts at the Hades parent folder, but it was not found: "
            f"{self.scripts_dir}"
        )


def _resolve_root_dir() -> Path:
    if getattr(sys, "frozen", False):
        executable_dir = Path(sys.executable).resolve().parent
        if executable_dir.name.lower() == "dist":
            return executable_dir.parent
        return executable_dir
    return Path(__file__).resolve().parents[2]


def build_app_paths() -> AppPaths:
    root_dir = _resolve_root_dir()
    scripts_dir = root_dir / "Content" / "Scripts"
    workspace_dir = root_dir / ".hades2_mod"
    legacy_workspace_dir = root_dir / ".hades2_mod_ui"
    generated_scripts_dir = workspace_dir / "generated" / "Content" / "Scripts"
    originals_scripts_dir = workspace_dir / "originals" / "Content" / "Scripts"
    state_file = workspace_dir / "state.json"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    return AppPaths(
        root_dir=root_dir,
        scripts_dir=scripts_dir,
        workspace_dir=workspace_dir,
        legacy_workspace_dir=legacy_workspace_dir,
        generated_scripts_dir=generated_scripts_dir,
        originals_scripts_dir=originals_scripts_dir,
        state_file=state_file,
        dist_dir=dist_dir,
        build_dir=build_dir,
    )
