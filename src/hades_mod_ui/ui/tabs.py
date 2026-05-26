from __future__ import annotations

from ..ui.main_window import HadesModUI


class TabsBuilder:
    """Compatibility stub for phase-1 split planning.

    The concrete tab construction remains in HadesModUI in this conservative pass.
    """

    def __init__(self, app: HadesModUI) -> None:
        self.app = app


__all__ = ["TabsBuilder"]
