from __future__ import annotations

import copy
import re
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from ..operations import ModService, OperationError
from ..paths import build_app_paths
from ..state import (
    ARCANA_CARD_ORDER,
    KEEPSAKE_EDITOR_CONFIG,
    KEEPSAKE_EDITOR_ORDER,
    REWARD_EDITOR_ENTRIES,
    REWARD_EDITOR_SECTIONS,
    REFRESH_FEATURE_ORDER,
    StateStore,
    WEAPON_DAMAGE_WEAPONS,
)

LanguageCode = str

TEXT_TEMPLATES: dict[str, dict[LanguageCode, str]] = {
    "window_title": {"en": "Hades II Mod UI", "zh": "Hades II Mod 工具"},
    "target_root": {"en": "Target root: {root}", "zh": "目标根目录: {root}"},
    "current_profile": {"en": "Current profile: {profile}", "zh": "当前模式: {profile}"},
    "preview_empty": {"en": "No files selected for the current profile.", "zh": "当前模式未选择任何文件。"},
    "switch_to_zh": {"en": "切换到中文", "zh": "切换到中文"},
    "switch_to_en": {"en": "Switch to English", "zh": "切换到英文"},
    "workspace_updated_title": {"en": "Workspace Updated", "zh": "工作区已更新"},
    "workspace_updated_body": {
        "en": (
            "Moved the app workspace from .hades2_mod_ui to .hades2_mod so your existing "
            "backups and generated files continue to work."
        ),
        "zh": "已将应用工作区从 .hades2_mod_ui 迁移到 .hades2_mod，以确保现有备份和生成文件继续可用。",
    },
    "workspace_updated_log": {
        "en": "Migrated workspace from .hades2_mod_ui to .hades2_mod.",
        "zh": "已将工作区从 .hades2_mod_ui 迁移到 .hades2_mod。",
    },
    "generate_failed": {"en": "Generate failed: {message}", "zh": "生成失败: {message}"},
    "generate_done_log": {"en": "Generated copies for: {files}", "zh": "已生成副本: {files}"},
    "generate_done_body": {"en": "Generated copies:\n{files}", "zh": "已生成副本:\n{files}"},
    "backup_failed": {"en": "Backup failed: {message}", "zh": "备份失败: {message}"},
    "backup_done": {"en": "Backed up originals:\n{files}", "zh": "已备份原始文件:\n{files}"},
    "backup_none": {"en": "All selected originals were already backed up.", "zh": "所选原始文件均已备份。"},
    "apply_failed": {"en": "Apply failed: {message}", "zh": "替换失败: {message}"},
    "apply_done_log": {"en": "Applied generated files: {files}", "zh": "已应用生成文件: {files}"},
    "apply_done_body": {"en": "Applied files:\n{files}", "zh": "已应用文件:\n{files}"},
    "restore_failed": {"en": "Restore failed: {message}", "zh": "恢复失败: {message}"},
    "restore_done_log": {"en": "Restored backups: {files}", "zh": "已恢复备份: {files}"},
    "restore_done_body": {"en": "Restored files:\n{files}", "zh": "已恢复文件:\n{files}"},
}

STATIC_TEXT_TRANSLATIONS: dict[str, str] = {
    "Hades II Mod UI": "Hades II Mod 工具",
    "Click a tab below to switch modes.": "点击下方标签页以切换模式。",
    "Initial Stats": "初始属性",
    "Rarity": "稀有度",
    "Boon Multipliers": "祝福倍率",
    "Weapon Damage": "武器伤害",
    "Reward Amounts": "奖励数值",
    "Keepsake": "信物",
    "Refresh": "刷新",
    "Actions": "操作",
    "1. Backup Originals": "1. 备份原始文件",
    "2. Generate Copies": "2. 生成副本",
    "3. Apply Replacement": "3. 应用替换",
    "4. Restore Backups": "4. 恢复备份",
    "Target Files": "目标文件",
    "Activity": "活动日志",
    "Initial Hero Stats": "初始角色属性",
    "Enable patch": "启用补丁",
    "Normal Gods": "常规神祇",
    "Hermes": "赫尔墨斯",
    "Chaos": "混沌",
    "Artemis": "阿尔忒弥斯",
    "Hades": "哈迪斯",
    "Icarus": "伊卡洛斯",
    (
        "Enable god/boon patches and edit detected multiplier fields. "
        "Core rarity multipliers and nested *Multiplier values are discovered from live TraitData files."
    ): "启用神祇/祝福补丁并编辑检测到的倍率字段。核心稀有度倍率和嵌套的 *Multiplier 数值来自实时 TraitData 文件。",
    "No editable multiplier fields detected in this boon.": "未在该祝福中检测到可编辑的倍率字段。",
    "Show advanced stack fields": "显示高级层数字段",
    "Read-only: SourceIsMultiplier is detected and not editable.": "只读: 检测到 SourceIsMultiplier，无法编辑。",
    (
        "Generate a patched TraitData.lua that adds a flat base-damage bonus to one or more "
        "primary weapon families through the DummyWeapon* trait entries."
    ): "生成修改后的 TraitData.lua，通过 DummyWeapon* 词条为一个或多个主武器系列增加固定基础伤害。",
    "Each enabled weapon family applies a flat bonus across its linked attacks.": "每个启用的武器系列都会对其关联攻击应用固定加成。",
    "Flat damage bonus": "固定伤害加成",
    (
        "Edit the global post-combat room-clear payout values in ConsumableData.lua. "
        "Primary fields change the real pickup reward. Advanced metadata is optional and hidden by default."
    ): "编辑 ConsumableData.lua 中全局战斗结算奖励。主字段影响实际拾取奖励，高级元数据为可选且默认隐藏。",
    "Only core money, health, and mana reward definitions are included in this v1 editor.": "此 v1 编辑器仅包含金币、生命和法力奖励的核心定义。",
    "Includes money/health/mana plus configurable gameplay resources (e.g. Psyche, Bones, Ashes, Nectar, ores, and Shadow).": "包含金币/生命/法力以及可配置的玩法资源（如 Psyche、Bones、Ashes、Nectar、矿石和 Shadow）。",
    "Money": "金币",
    "Health": "生命",
    "Mana": "法力",
    "Resource": "资源",
    "Show advanced metadata": "显示高级元数据",
    (
        "Configure per-keepsake buffs for TraitData_Keepsake.lua. "
        "Primary fields are always visible. Optional rarity multipliers and "
        "secondary values are available through advanced controls."
    ): "为 TraitData_Keepsake.lua 配置每个信物的增益。主字段始终可见，可选稀有度倍率和次级数值可通过高级选项设置。",
    "Enable only the keepsakes you want to patch before generating copies.": "请仅启用你要修改的信物后再生成副本。",
    "Show advanced fields": "显示高级字段",
    "Generate Copies": "生成副本",
    "Backup Originals": "备份原始文件",
    "Apply Replacement": "应用替换",
    "Restore Backups": "恢复备份",
}

EXACT_ERROR_TRANSLATIONS: dict[str, str] = {
    "Enable Initial Stats patch before generating copies.": "请先启用初始属性补丁后再生成副本。",
    "Enable at least one god and one boon in Boon Multipliers before generating copies.": "请先在祝福倍率中至少启用一个神祇和一个祝福后再生成副本。",
    "Enable at least one weapon damage patch before generating copies.": "请先启用至少一个武器伤害补丁后再生成副本。",
    "Enable at least one reward amount patch before generating copies.": "请先启用至少一个奖励数值补丁后再生成副本。",
    "Enable at least one keepsake patch before generating copies.": "请先启用至少一个信物补丁后再生成副本。",
    "Enable at least one refresh patch before generating copies.": "请先启用至少一个刷新补丁后再生成副本。",
    "Select at least one rarity source before generating copies.": "请先选择至少一个稀有度来源后再生成副本。",
    "There are no target files to back up for the current selection.": "当前选择没有可备份的目标文件。",
    "There are no generated files to apply.": "没有可应用的生成文件。",
    "No backups are available to restore.": "没有可恢复的备份。",
    "There are no files to copy.": "没有可复制的文件。",
    "Unsupported expression": "不支持的表达式",
}

PREFIX_ERROR_TRANSLATIONS: tuple[tuple[str, str], ...] = (
    ("Missing target file: ", "缺少目标文件: "),
    ("Generated file is missing: ", "缺少生成文件: "),
    ("Missing source file for copy: ", "复制缺少源文件: "),
    ("Missing destination file for copy: ", "复制缺少目标文件: "),
    ("Missing weapon damage configuration for ", "缺少武器伤害配置: "),
    ("Missing reward editor configuration for ", "缺少奖励编辑配置: "),
    ("Missing keepsake editor configuration for ", "缺少信物编辑配置: "),
    ("Missing boon multiplier configuration for god '", "缺少神祇祝福倍率配置: god '"),
    ("Missing boon multiplier configuration for boon '", "缺少祝福倍率配置: boon '"),
    ("Missing multiplier field '", "缺少倍率字段 '"),
    ("Unsupported keepsake input type '", "不支持的信物输入类型 '"),
)

STATUS_PREFIX_TRANSLATIONS: tuple[tuple[str, str], ...] = (
    ("Using scripts directory: ", "使用脚本目录: "),
    (
        "Expected Content/Scripts at the Hades parent folder, but it was not found: ",
        "在 Hades 根目录期望存在 Content/Scripts，但未找到: ",
    ),
)


class HadesModUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.paths = build_app_paths()
        self.service = ModService(self.paths, StateStore(self.paths.state_file))
        self.legacy_workspace_migrated = self.service.migrate_legacy_workspace()
        self.boon_multiplier_metadata = self.service.discover_boon_multiplier_metadata()
        self.state = self.service.load_state()
        self.state = self.service.normalize_boon_multiplier_state(
            self.state,
            self.boon_multiplier_metadata,
        )
        self.language = self._normalize_language(self.state.get("ui_language"))
        self.state["ui_language"] = self.language

        self.title(self._tr("window_title"))
        self.geometry("1024x900")
        self.minsize(1024, 900)

        self.profile_label_var = tk.StringVar()
        self.root_label_var = tk.StringVar(value=self._trf("target_root", root=self.paths.root_dir))
        self.status_label_var = tk.StringVar()
        self.language_button_var = tk.StringVar()
        self.active_scroll_canvas: tk.Canvas | None = None
        self.localized_widgets: list[tuple[tk.Misc, str]] = []
        self.localized_widgets_dyn: list[tuple[tk.Misc, Any]] = []

        self.epic_profile_key = "epic_preset"
        self.initial_stats_profile_key = "initial_stats"
        self.reward_profile_key = "reward_editor"
        self.weapon_damage_profile_key = "weapon_damage"
        self.arcana_profile_key = "arcana_editor"
        self.keepsake_profile_key = "keepsake_editor"
        self.boon_multiplier_profile_key = "boon_multiplier"
        self.refresh_profile_key = "refresh"
        self.initial_stats_vars: dict[str, Any] = {}
        self.rarity_editor_vars: dict[str, dict[str, Any]] = {}
        self.reward_editor_vars: dict[str, dict[str, Any]] = {}
        self.weapon_damage_vars: dict[str, dict[str, Any]] = {}
        self.arcana_editor_vars: dict[str, Any] = {}
        self.keepsake_editor_vars: dict[str, dict[str, Any]] = {}
        self.boon_multiplier_vars: dict[str, dict[str, Any]] = {}
        self.refresh_vars: dict[str, dict[str, Any]] = {}
        self.preview_list_var = tk.StringVar(value=[])
        self.notebook_tab_profiles = (
            self.initial_stats_profile_key,
            "rarity_editor",
            self.boon_multiplier_profile_key,
            self.weapon_damage_profile_key,
            self.arcana_profile_key,
            self.reward_profile_key,
            self.keepsake_profile_key,
            self.refresh_profile_key,
        )
        self.notebook_tab_labels = (
            "Initial Stats",
            "Rarity",
            "Boon Multipliers",
            "Weapon Damage",
            "Arcana",
            "Reward Amounts",
            "Keepsake",
            "Refresh",
        )

        self._configure_styles()
        self._build_ui()
        self._collect_localizable_widgets()
        self._load_state_into_ui()
        self._apply_language()
        self._refresh_header_state()
        self._refresh_preview()
        if self.legacy_workspace_migrated:
            self.after(50, self._show_workspace_migration_notice)

    def _normalize_language(self, value: Any) -> LanguageCode:
        return "zh" if value == "zh" else "en"

    def _tr(self, key: str) -> str:
        return TEXT_TEMPLATES.get(key, {}).get(self.language, key)

    def _trf(self, key: str, **kwargs: Any) -> str:
        return self._tr(key).format(**kwargs)

    def _translate_text(self, text: str) -> str:
        if self.language == "en":
            return text
        match = re.match(r"^Enable all (.+) boon edits$", text)
        if match:
            return f"启用 {match.group(1)} 的全部祝福编辑"
        arcana_translations = {
            "Arcana": "阿卡纳",
            "Arcana Globals": "阿卡纳全局",
            "Arcana Card Effect Multipliers": "阿卡纳卡牌效果倍率",
            "Unlock+Upgrade Cost Multiplier": "解锁+升级花费倍率",
            "Starting Grasp Limit": "起始抓握上限",
            "Grasp Growth Multiplier": "抓握成长倍率",
            (
                "Configure Arcana card effects, unlock/upgrade costs, and Grasp growth. "
                "Per-card multipliers scale Arcana trait rarity multipliers."
            ): "配置阿卡纳卡牌效果、解锁/升级花费和抓握成长。每张卡牌倍率会缩放对应阿卡纳特质的稀有度倍率。",
        }
        if text in arcana_translations:
            return arcana_translations[text]
        return STATIC_TEXT_TRANSLATIONS.get(text, text)

    def _register_text(self, widget: tk.Misc, text: str) -> None:
        self.localized_widgets.append((widget, text))

    def _register_text_dynamic(self, widget: tk.Misc, resolver: Any) -> None:
        self.localized_widgets_dyn.append((widget, resolver))

    def _translate_operation_message(self, message: str) -> str:
        if self.language == "en":
            return message
        if message == "Enable Arcana patch before generating copies.":
            return "请先启用阿卡纳补丁后再生成副本。"
        if message in EXACT_ERROR_TRANSLATIONS:
            return EXACT_ERROR_TRANSLATIONS[message]
        if message.startswith("Missing files to back up:\n"):
            tail = message.split("\n", 1)[1] if "\n" in message else ""
            return "缺少待备份文件:\n" + tail
        if message.startswith("Missing backup files:\n"):
            tail = message.split("\n", 1)[1] if "\n" in message else ""
            return "缺少备份文件:\n" + tail
        for prefix_en, prefix_zh in PREFIX_ERROR_TRANSLATIONS:
            if message.startswith(prefix_en):
                return prefix_zh + message[len(prefix_en) :]
        return message

    def _translate_status_message(self, message: str) -> str:
        if self.language == "en":
            return message
        for prefix_en, prefix_zh in STATUS_PREFIX_TRANSLATIONS:
            if message.startswith(prefix_en):
                return prefix_zh + message[len(prefix_en) :]
        return message

    def _translate_profile_name(self, profile: str) -> str:
        return self._translate_text(profile)

    def _translate_preview_item(self, item: str) -> str:
        if self.language == "en":
            return item
        if item.startswith("Content/Scripts/"):
            return "Content/Scripts/" + self._translate_text(item.removeprefix("Content/Scripts/"))
        return self._translate_text(item)

    def _set_widget_text(self, widget: tk.Misc, text: str) -> None:
        try:
            widget.configure(text=text)
        except tk.TclError:
            return

    def _collect_localizable_widgets(self) -> None:
        self.localized_widgets = []

        def walk(widget: tk.Misc) -> None:
            for child in widget.winfo_children():
                if child is getattr(self, "language_toggle_button", None):
                    walk(child)
                    continue
                try:
                    text_value = child.cget("text")
                except tk.TclError:
                    text_value = ""
                if isinstance(text_value, str) and text_value:
                    self.localized_widgets.append((child, text_value))
                walk(child)

        walk(self)

    def _update_language_button_label(self) -> None:
        if self.language == "en":
            self.language_button_var.set(self._tr("switch_to_zh"))
        else:
            self.language_button_var.set(self._tr("switch_to_en"))

    def _apply_language(self) -> None:
        self.title(self._tr("window_title"))
        self._update_language_button_label()
        for widget, text in self.localized_widgets:
            self._set_widget_text(widget, self._translate_text(text))
        for widget, resolver in self.localized_widgets_dyn:
            self._set_widget_text(widget, self._translate_text(resolver()))
        if hasattr(self, "notebook"):
            for index, tab in enumerate(self.notebook_tab_labels):
                self.notebook.tab(index, text=self._translate_text(tab))
        self._refresh_preview()
        self._refresh_header_state()

    def _toggle_language(self) -> None:
        self.language = "zh" if self.language == "en" else "en"
        self.state["ui_language"] = self.language
        self.service.save_state(self.state)
        self._apply_language()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.configure("ModeTabs.TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 11, "bold"))
        style.map(
            "ModeTabs.TNotebook.Tab",
            foreground=[("selected", "#003b73"), ("active", "#0b5cad")],
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        self.outer_canvas = tk.Canvas(outer, highlightthickness=0)
        self.outer_canvas.grid(row=0, column=0, sticky="nsew")
        outer_scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.outer_canvas.yview)
        outer_scrollbar.grid(row=0, column=1, sticky="ns")
        self.outer_canvas.configure(yscrollcommand=outer_scrollbar.set)

        container = ttk.Frame(self.outer_canvas, padding=12)
        container.bind(
            "<Configure>",
            lambda _event: self.outer_canvas.configure(scrollregion=self.outer_canvas.bbox("all")),
        )
        outer_window = self.outer_canvas.create_window((0, 0), window=container, anchor="nw")
        self.outer_canvas.bind(
            "<Configure>",
            lambda event: self.outer_canvas.itemconfigure(outer_window, width=event.width),
        )

        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self._register_scroll_target(self.outer_canvas, outer, container)

        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        self.header_title_label = ttk.Label(header, text="Hades II Mod UI", font=("Segoe UI", 16, "bold"))
        self.header_title_label.grid(
            row=0, column=0, sticky="w"
        )
        self.language_toggle_button = ttk.Button(
            header,
            textvariable=self.language_button_var,
            command=self._toggle_language,
        )
        self.language_toggle_button.grid(row=0, column=1, sticky="e")
        self.root_label = ttk.Label(header, textvariable=self.root_label_var)
        self.root_label.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.status_label = ttk.Label(header, textvariable=self.status_label_var)
        self.status_label.grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.profile_label = ttk.Label(header, textvariable=self.profile_label_var)
        self.profile_label.grid(row=3, column=0, sticky="w", pady=(4, 0))

        self.header_hint_label = ttk.Label(
            header,
            text="Click a tab below to switch modes.",
            foreground="#0b5cad",
            font=("Segoe UI", 10, "bold"),
        )
        self.header_hint_label.grid(row=4, column=0, sticky="w", pady=(6, 0))

        self.notebook_container = ttk.Frame(container)
        self.notebook_container.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        self.notebook_container.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.notebook_container, style="ModeTabs.TNotebook")
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 12))
        self.notebook.bind("<<NotebookTabChanged>>", lambda _event: self._refresh_preview())

        self.initial_stats_frame = ttk.Frame(self.notebook, padding=12)
        self.rarity_frame = ttk.Frame(self.notebook, padding=12)
        self.boon_multiplier_frame = ttk.Frame(self.notebook, padding=12)
        self.weapon_damage_frame = ttk.Frame(self.notebook, padding=12)
        self.arcana_frame = ttk.Frame(self.notebook, padding=12)
        self.reward_frame = ttk.Frame(self.notebook, padding=12)
        self.keepsake_frame = ttk.Frame(self.notebook, padding=12)
        self.refresh_frame = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.initial_stats_frame, text=self.notebook_tab_labels[0])
        self.notebook.add(self.rarity_frame, text=self.notebook_tab_labels[1])
        self.notebook.add(self.boon_multiplier_frame, text=self.notebook_tab_labels[2])
        self.notebook.add(self.weapon_damage_frame, text=self.notebook_tab_labels[3])
        self.notebook.add(self.arcana_frame, text=self.notebook_tab_labels[4])
        self.notebook.add(self.reward_frame, text=self.notebook_tab_labels[5])
        self.notebook.add(self.keepsake_frame, text=self.notebook_tab_labels[6])
        self.notebook.add(self.refresh_frame, text=self.notebook_tab_labels[7])

        self._build_initial_stats_tab()
        self._build_rarity_tab()
        self._build_boon_multiplier_tab()
        self._build_weapon_damage_tab()
        self._build_arcana_tab()
        self._build_reward_tab()
        self._build_keepsake_tab()
        self._build_refresh_tab()

        pinned_bottom = ttk.Frame(outer, padding=12)
        pinned_bottom.grid(row=1, column=0, columnspan=2, sticky="ew")
        pinned_bottom.columnconfigure(0, weight=1)

        actions = ttk.LabelFrame(pinned_bottom, text="Actions", padding=12)
        actions.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for column in range(4):
            actions.columnconfigure(column, weight=1)

        self.backup_button = ttk.Button(actions, text="1. Backup Originals", command=self._on_backup)
        self.backup_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.generate_button = ttk.Button(actions, text="2. Generate Copies", command=self._on_generate)
        self.generate_button.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.apply_button = ttk.Button(actions, text="3. Apply Replacement", command=self._on_apply)
        self.apply_button.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        self.restore_button = ttk.Button(actions, text="4. Restore Backups", command=self._on_restore)
        self.restore_button.grid(row=0, column=3, sticky="ew")

        self.bottom_split_pane = ttk.Panedwindow(pinned_bottom, orient="horizontal")
        self.bottom_split_pane.grid(row=1, column=0, sticky="ew")
        
        preview_frame = ttk.LabelFrame(self.bottom_split_pane, text="Target Files", padding=12)
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        self.preview_listbox = tk.Listbox(preview_frame, listvariable=self.preview_list_var, height=8)
        self.preview_listbox.grid(row=0, column=0, sticky="nsew")

        log_frame = ttk.LabelFrame(self.bottom_split_pane, text="Activity", padding=12)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = tk.Text(log_frame, height=8, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        self.bottom_split_pane.add(preview_frame, weight=1)
        self.bottom_split_pane.add(log_frame, weight=1)

        self.bottom_split_pane.bind("<ButtonRelease-1>", self._on_pane_sash_release)
        self.after(120, self._apply_saved_pane_positions)

    def _build_initial_stats_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.initial_stats_frame)
        scrollable.columnconfigure(1, weight=1)

        frame = ttk.LabelFrame(scrollable, text="Initial Hero Stats", padding=12)
        frame.grid(row=0, column=0, sticky="ew")
        frame.columnconfigure(1, weight=1)

        enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="Enable patch",
            variable=enabled_var,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

        max_health_var = tk.StringVar(value="30")
        ttk.Label(frame, text="MaxHealth").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=max_health_var).grid(row=1, column=1, sticky="ew", pady=2)
        max_health_var.trace_add("write", lambda *_args: self._refresh_preview())

        max_mana_var = tk.StringVar(value="50")
        ttk.Label(frame, text="MaxMana").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=max_mana_var).grid(row=2, column=1, sticky="ew", pady=2)
        max_mana_var.trace_add("write", lambda *_args: self._refresh_preview())

        starting_money_var = tk.StringVar(value="0")
        ttk.Label(frame, text="StartingMoney").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(frame, textvariable=starting_money_var).grid(row=3, column=1, sticky="ew", pady=2)
        starting_money_var.trace_add("write", lambda *_args: self._refresh_preview())

        self.initial_stats_vars = {
            "enabled": enabled_var,
            "max_health": max_health_var,
            "max_mana": max_mana_var,
            "starting_money": starting_money_var,
        }

    def _build_rarity_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.rarity_frame)
        scrollable.columnconfigure(0, weight=1)
        scrollable.columnconfigure(1, weight=1)

        sections = [
            ("normal_gods", "Normal Gods", ["Rare", "Epic", "Duo", "Legendary"], None),
            ("hermes", "Hermes", ["Rare", "Epic", "Legendary"], None),
            ("chaos", "Chaos", ["Rare", "Epic", "Duo", "Legendary"], None),
            ("artemis", "Artemis", ["Rare", "Epic"], "RarityRollOrder"),
            ("hades", "Hades", ["Common", "Legendary"], "RarityRollOrder"),
            ("icarus", "Icarus", ["Rare", "Epic"], "RarityRollOrder"),
        ]

        for index, (source_key, title, chance_keys, roll_order_label) in enumerate(sections):
            row = index // 2
            column = index % 2
            frame = ttk.LabelFrame(scrollable, text=title, padding=12)
            frame.grid(row=row, column=column, sticky="nsew", padx=(0, 8) if column == 0 else 0, pady=(0, 8))
            frame.columnconfigure(1, weight=1)

            enabled_var = tk.BooleanVar(value=False)
            enabled_check = ttk.Checkbutton(frame, text="Enable patch", variable=enabled_var)
            enabled_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
            enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

            value_vars: dict[str, tk.StringVar] = {}
            current_row = 1
            for key in chance_keys:
                ttk.Label(frame, text=key).grid(row=current_row, column=0, sticky="w", pady=2)
                value_var = tk.StringVar()
                entry = ttk.Entry(frame, textvariable=value_var)
                entry.grid(row=current_row, column=1, sticky="ew", pady=2)
                value_var.trace_add("write", lambda *_args: self._refresh_preview())
                value_vars[key] = value_var
                current_row += 1

            source_vars: dict[str, Any] = {
                "enabled": enabled_var,
                "values": value_vars,
            }

            if roll_order_label:
                ttk.Label(frame, text=roll_order_label).grid(row=current_row, column=0, sticky="w", pady=(8, 2))
                roll_order_var = tk.StringVar()
                roll_order_entry = ttk.Entry(frame, textvariable=roll_order_var)
                roll_order_entry.grid(row=current_row, column=1, sticky="ew", pady=(8, 2))
                roll_order_var.trace_add("write", lambda *_args: self._refresh_preview())
                source_vars["roll_order"] = roll_order_var

            self.rarity_editor_vars[source_key] = source_vars

    def _build_boon_multiplier_tab(self) -> None:
        self.boon_multiplier_frame.columnconfigure(0, weight=1)
        self.boon_multiplier_frame.rowconfigure(1, weight=1)

        ttk.Label(
            self.boon_multiplier_frame,
            text=(
                "Enable god/boon patches and edit detected multiplier fields. "
                "Core rarity multipliers and nested *Multiplier values are discovered from live TraitData files."
            ),
            wraplength=860,
            justify="left",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.boon_subnotebook = ttk.Notebook(self.boon_multiplier_frame)
        self.boon_subnotebook.grid(row=1, column=0, sticky="nsew")
        self.boon_subnotebook.bind("<<NotebookTabChanged>>", lambda _event: self._refresh_preview())

        for god_key, god_meta in self.boon_multiplier_metadata.get("gods", {}).items():
            god_tab = ttk.Frame(self.boon_subnotebook, padding=8)
            self.boon_subnotebook.add(god_tab, text=god_meta.get("title", god_key.title()))
            scrollable = self._create_scrollable_tab(god_tab)
            scrollable.columnconfigure(0, weight=1)

            god_enabled_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                scrollable,
                text=f"Enable all {god_meta.get('title', god_key.title())} boon edits",
                variable=god_enabled_var,
            ).grid(row=0, column=0, sticky="w", pady=(0, 8))
            god_enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

            boon_vars: dict[str, Any] = {}
            current_row = 1
            for boon_name, boon_meta in sorted(god_meta.get("boons", {}).items()):
                boon_frame = ttk.LabelFrame(scrollable, text=boon_name, padding=10)
                boon_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 8))
                boon_frame.columnconfigure(1, weight=1)
                current_row += 1

                boon_enabled_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(
                    boon_frame,
                    text="Enable patch",
                    variable=boon_enabled_var,
                ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
                boon_enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

                fields = boon_meta.get("fields", {})
                advanced_paths = {
                    field_path
                    for field_path, field_meta in fields.items()
                    if bool(field_meta.get("advanced"))
                }
                basic_paths = [
                    field_path
                    for field_path in fields.keys()
                    if field_path not in advanced_paths
                ]
                ordered_paths = basic_paths + sorted(advanced_paths)

                field_vars: dict[str, tk.StringVar] = {}
                row_cursor = 1
                for field_path in basic_paths:
                    ttk.Label(boon_frame, text=self._format_boon_multiplier_field_label(field_path)).grid(
                        row=row_cursor, column=0, sticky="w", pady=2
                    )
                    field_var = tk.StringVar()
                    ttk.Entry(boon_frame, textvariable=field_var).grid(
                        row=row_cursor, column=1, sticky="ew", pady=2
                    )
                    field_var.trace_add("write", lambda *_args: self._refresh_preview())
                    field_vars[field_path] = field_var
                    row_cursor += 1

                if not ordered_paths:
                    ttk.Label(
                        boon_frame,
                        text="No editable multiplier fields detected in this boon.",
                        foreground="#666666",
                    ).grid(row=row_cursor, column=0, columnspan=2, sticky="w", pady=(0, 2))
                    row_cursor += 1

                show_advanced_var = tk.BooleanVar(value=False)
                advanced_frame: ttk.Frame | None = None
                if advanced_paths:
                    ttk.Checkbutton(
                        boon_frame,
                        text="Show advanced stack fields",
                        variable=show_advanced_var,
                    ).grid(row=row_cursor, column=0, columnspan=2, sticky="w", pady=(6, 0))
                    row_cursor += 1

                    advanced_frame = ttk.Frame(boon_frame)
                    advanced_frame.columnconfigure(1, weight=1)
                    advanced_row = 0
                    for field_path in sorted(advanced_paths):
                        ttk.Label(
                            advanced_frame,
                            text=self._format_boon_multiplier_field_label(field_path),
                        ).grid(row=advanced_row, column=0, sticky="w", pady=(6, 2))
                        field_var = tk.StringVar()
                        ttk.Entry(advanced_frame, textvariable=field_var).grid(
                            row=advanced_row, column=1, sticky="ew", pady=(6, 2)
                        )
                        field_var.trace_add("write", lambda *_args: self._refresh_preview())
                        field_vars[field_path] = field_var
                        advanced_row += 1
                    advanced_frame.grid(row=row_cursor, column=0, columnspan=2, sticky="ew")
                    show_advanced_var.trace_add(
                        "write",
                        lambda *_args, gk=god_key, bn=boon_name: self._on_boon_multiplier_advanced_toggle(gk, bn),
                    )

                source_flags = boon_meta.get("source_is_multiplier_paths", [])
                if source_flags:
                    row_cursor += 1
                    ttk.Label(
                        boon_frame,
                        text="Read-only: SourceIsMultiplier is detected and not editable.",
                        foreground="#0b5cad",
                    ).grid(row=row_cursor, column=0, columnspan=2, sticky="w", pady=(6, 0))

                boon_vars[boon_name] = {
                    "enabled": boon_enabled_var,
                    "show_advanced": show_advanced_var,
                    "advanced_frame": advanced_frame,
                    "advanced_paths": advanced_paths,
                    "field_order": ordered_paths,
                    "fields": field_vars,
                }

            self.boon_multiplier_vars[god_key] = {
                "enabled": god_enabled_var,
                "boons": boon_vars,
            }

        for god_key, god_vars in self.boon_multiplier_vars.items():
            for boon_name, boon_vars in god_vars["boons"].items():
                if boon_vars.get("advanced_frame") is not None:
                    self._update_boon_multiplier_advanced_visibility(god_key, boon_name)

    def _format_boon_multiplier_field_label(self, field_path: str) -> str:
        if field_path.endswith(".Multiplier"):
            return field_path
        if ".AbsoluteStackValues." in field_path:
            return field_path
        return field_path

    def _build_weapon_damage_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.weapon_damage_frame)
        scrollable.columnconfigure(0, weight=1)
        scrollable.columnconfigure(1, weight=1)

        ttk.Label(
            scrollable,
            text=(
                "Generate a patched TraitData.lua that adds a flat base-damage bonus to one or more "
                "primary weapon families through the DummyWeapon* trait entries."
            ),
            wraplength=850,
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(
            scrollable,
            text="Each enabled weapon family applies a flat bonus across its linked attacks.",
            foreground="#0b5cad",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 12))

        for index, weapon_name in enumerate(WEAPON_DAMAGE_WEAPONS):
            row = index // 2 + 2
            column = index % 2
            frame = ttk.LabelFrame(scrollable, text=weapon_name, padding=12)
            frame.grid(row=row, column=column, sticky="nsew", padx=(0, 8) if column == 0 else 0, pady=(0, 8))
            frame.columnconfigure(1, weight=1)

            enabled_var = tk.BooleanVar(value=False)
            enabled_check = ttk.Checkbutton(frame, text="Enable patch", variable=enabled_var)
            enabled_check.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
            enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

            ttk.Label(frame, text="Flat damage bonus").grid(row=1, column=0, sticky="w", pady=2)
            value_var = tk.StringVar(value="0")
            entry = ttk.Entry(frame, textvariable=value_var)
            entry.grid(row=1, column=1, sticky="ew", pady=2)
            value_var.trace_add("write", lambda *_args: self._refresh_preview())

            self.weapon_damage_vars[weapon_name] = {
                "enabled": enabled_var,
                "value": value_var,
            }

    def _build_arcana_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.arcana_frame)
        scrollable.columnconfigure(0, weight=1)

        ttk.Label(
            scrollable,
            text=(
                "Configure Arcana card effects, unlock/upgrade costs, and Grasp growth. "
                "Per-card multipliers scale Arcana trait rarity multipliers."
            ),
            wraplength=850,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        global_frame = ttk.LabelFrame(scrollable, text="Arcana Globals", padding=12)
        global_frame.grid(row=1, column=0, sticky="ew", pady=(8, 8))
        global_frame.columnconfigure(1, weight=1)

        enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(global_frame, text="Enable patch", variable=enabled_var).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

        unlock_upgrade_cost_multiplier_var = tk.StringVar(value="1.0")
        ttk.Label(global_frame, text="Unlock+Upgrade Cost Multiplier").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(global_frame, textvariable=unlock_upgrade_cost_multiplier_var).grid(
            row=1, column=1, sticky="ew", pady=2
        )
        unlock_upgrade_cost_multiplier_var.trace_add("write", lambda *_args: self._refresh_preview())

        starting_grasp_limit_var = tk.StringVar(value="10")
        ttk.Label(global_frame, text="Starting Grasp Limit").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(global_frame, textvariable=starting_grasp_limit_var).grid(row=2, column=1, sticky="ew", pady=2)
        starting_grasp_limit_var.trace_add("write", lambda *_args: self._refresh_preview())

        grasp_growth_multiplier_var = tk.StringVar(value="1.0")
        ttk.Label(global_frame, text="Grasp Growth Multiplier").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(global_frame, textvariable=grasp_growth_multiplier_var).grid(row=3, column=1, sticky="ew", pady=2)
        grasp_growth_multiplier_var.trace_add("write", lambda *_args: self._refresh_preview())

        card_frame = ttk.LabelFrame(scrollable, text="Arcana Card Effect Multipliers", padding=12)
        card_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        card_frame.columnconfigure(1, weight=1)

        effect_multiplier_vars: dict[str, tk.StringVar] = {}
        for idx, card_name in enumerate(ARCANA_CARD_ORDER):
            ttk.Label(card_frame, text=f"{card_name} Effect Multiplier").grid(
                row=idx, column=0, sticky="w", pady=2
            )
            field_var = tk.StringVar(value="1.0")
            ttk.Entry(card_frame, textvariable=field_var).grid(row=idx, column=1, sticky="ew", pady=2)
            field_var.trace_add("write", lambda *_args: self._refresh_preview())
            effect_multiplier_vars[card_name] = field_var

        self.arcana_editor_vars = {
            "enabled": enabled_var,
            "unlock_upgrade_cost_multiplier": unlock_upgrade_cost_multiplier_var,
            "starting_grasp_limit": starting_grasp_limit_var,
            "grasp_growth_multiplier": grasp_growth_multiplier_var,
            "effect_multipliers": effect_multiplier_vars,
        }

    def _build_reward_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.reward_frame)
        scrollable.columnconfigure(0, weight=1)

        ttk.Label(
            scrollable,
            text=(
                "Edit the global post-combat room-clear payout values in ConsumableData.lua. "
                "Primary fields change the real pickup reward. Advanced metadata is optional and hidden by default."
            ),
            wraplength=850,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            scrollable,
            text=(
                "Includes money/health/mana plus configurable gameplay resources "
                "(e.g. Psyche, Bones, Ashes, Nectar, ores, and Shadow)."
            ),
            foreground="#0b5cad",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(8, 12))

        current_row = 2
        for section_title, reward_names in REWARD_EDITOR_SECTIONS:
            section_frame = ttk.LabelFrame(scrollable, text=section_title, padding=12)
            section_frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 8))
            section_frame.columnconfigure(0, weight=1)
            current_row += 1

            for section_row, reward_name in enumerate(reward_names):
                reward_meta = REWARD_EDITOR_ENTRIES[reward_name]
                display_name = str(reward_meta.get("display_name", reward_name))
                frame = ttk.LabelFrame(section_frame, text=display_name, padding=12)
                frame.grid(row=section_row, column=0, sticky="ew", pady=(0, 8))
                frame.columnconfigure(1, weight=1)

                enabled_var = tk.BooleanVar(value=False)
                ttk.Checkbutton(frame, text="Enable patch", variable=enabled_var).grid(
                    row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
                )
                enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

                ttk.Label(frame, text=reward_meta["amount_field"]).grid(row=1, column=0, sticky="w", pady=2)
                value_var = tk.StringVar(value=reward_meta["default_value"])
                ttk.Entry(frame, textvariable=value_var).grid(row=1, column=1, sticky="ew", pady=2)
                value_var.trace_add("write", lambda *_args: self._refresh_preview())

                reward_vars: dict[str, Any] = {
                    "enabled": enabled_var,
                    "value": value_var,
                }

                if "resource_cost_money" in reward_meta:
                    show_advanced_var = tk.BooleanVar(value=False)
                    ttk.Checkbutton(
                        frame,
                        text="Show advanced metadata",
                        variable=show_advanced_var,
                    ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

                    advanced_frame = ttk.Frame(frame)
                    advanced_frame.columnconfigure(1, weight=1)
                    ttk.Label(advanced_frame, text="ResourceCosts.Money").grid(
                        row=0, column=0, sticky="w", pady=(6, 2)
                    )
                    resource_cost_var = tk.StringVar(value=reward_meta["resource_cost_money"])
                    ttk.Entry(advanced_frame, textvariable=resource_cost_var).grid(
                        row=0, column=1, sticky="ew", pady=(6, 2)
                    )
                    resource_cost_var.trace_add("write", lambda *_args: self._refresh_preview())
                    advanced_frame.grid(row=3, column=0, columnspan=2, sticky="ew")

                    reward_vars["advanced_frame"] = advanced_frame
                    reward_vars["resource_cost_money"] = resource_cost_var
                    reward_vars["show_advanced"] = show_advanced_var
                    show_advanced_var.trace_add(
                        "write",
                        lambda *_args, key=reward_name: self._on_reward_advanced_toggle(key),
                    )
                    self.reward_editor_vars[reward_name] = reward_vars
                    self._update_reward_advanced_visibility(reward_name)
                    continue

                self.reward_editor_vars[reward_name] = reward_vars

    def _build_keepsake_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.keepsake_frame)
        scrollable.columnconfigure(0, weight=1)

        ttk.Label(
            scrollable,
            text=(
                "Configure per-keepsake buffs for TraitData_Keepsake.lua. "
                "Primary fields are always visible. Optional rarity multipliers and "
                "secondary values are available through advanced controls."
            ),
            wraplength=850,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            scrollable,
            text="Enable only the keepsakes you want to patch before generating copies.",
            foreground="#0b5cad",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(8, 12))

        current_row = 2
        for keepsake_name in KEEPSAKE_EDITOR_ORDER:
            keepsake_meta = KEEPSAKE_EDITOR_CONFIG[keepsake_name]
            frame = ttk.LabelFrame(scrollable, text=keepsake_meta.get("title", keepsake_name), padding=12)
            frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 8))
            frame.columnconfigure(1, weight=1)
            current_row += 1

            enabled_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(frame, text="Enable patch", variable=enabled_var).grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="w",
                pady=(0, 8),
            )
            enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

            field_vars: dict[str, tk.StringVar] = {}
            primary_row = 1
            for field_id, field_meta in keepsake_meta["fields"].items():
                if field_meta.get("advanced"):
                    continue
                ttk.Label(frame, text=field_meta.get("label", field_id)).grid(
                    row=primary_row,
                    column=0,
                    sticky="w",
                    pady=2,
                )
                value_var = tk.StringVar(value=str(field_meta.get("default", "")))
                ttk.Entry(frame, textvariable=value_var).grid(row=primary_row, column=1, sticky="ew", pady=2)
                value_var.trace_add("write", lambda *_args: self._refresh_preview())
                field_vars[field_id] = value_var
                primary_row += 1

            show_advanced_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                frame,
                text="Show advanced fields",
                variable=show_advanced_var,
            ).grid(row=primary_row, column=0, columnspan=2, sticky="w", pady=(8, 0))

            advanced_frame = ttk.Frame(frame)
            advanced_frame.columnconfigure(1, weight=1)
            advanced_row = 0
            for field_id, field_meta in keepsake_meta["fields"].items():
                if not field_meta.get("advanced"):
                    continue
                ttk.Label(advanced_frame, text=field_meta.get("label", field_id)).grid(
                    row=advanced_row,
                    column=0,
                    sticky="w",
                    pady=(6, 2),
                )
                value_var = tk.StringVar(value=str(field_meta.get("default", "")))
                ttk.Entry(advanced_frame, textvariable=value_var).grid(
                    row=advanced_row,
                    column=1,
                    sticky="ew",
                    pady=(6, 2),
                )
                value_var.trace_add("write", lambda *_args: self._refresh_preview())
                field_vars[field_id] = value_var
                advanced_row += 1
            advanced_frame.grid(row=primary_row + 1, column=0, columnspan=2, sticky="ew")

            show_advanced_var.trace_add(
                "write",
                lambda *_args, key=keepsake_name: self._on_keepsake_advanced_toggle(key),
            )

            self.keepsake_editor_vars[keepsake_name] = {
                "enabled": enabled_var,
                "show_advanced": show_advanced_var,
                "advanced_frame": advanced_frame,
                "fields": field_vars,
            }
            self._update_keepsake_advanced_visibility(keepsake_name)

    def _build_refresh_tab(self) -> None:
        scrollable = self._create_scrollable_tab(self.refresh_frame)
        scrollable.columnconfigure(0, weight=1)

        ttk.Label(
            scrollable,
            text="Current-version-safe community patches for rerolls and exotic market stock.",
            wraplength=850,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            scrollable,
            text="Enable only the refresh behaviors you want to generate.",
            foreground="#0b5cad",
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(8, 12))

        current_row = 2
        for feature_key, title in REFRESH_FEATURE_ORDER:
            frame = ttk.LabelFrame(scrollable, text=title, padding=12)
            frame.grid(row=current_row, column=0, sticky="ew", pady=(0, 8))
            frame.columnconfigure(0, weight=1)
            current_row += 1

            enabled_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(frame, text="Enable patch", variable=enabled_var).grid(
                row=0, column=0, sticky="w"
            )
            enabled_var.trace_add("write", lambda *_args: self._refresh_preview())

            self.refresh_vars[feature_key] = {"enabled": enabled_var}

    def _create_scrollable_tab(self, parent: ttk.Frame) -> ttk.Frame:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)

        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas, padding=2)
        scrollable.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(canvas_window, width=event.width),
        )

        self._register_scroll_target(canvas, parent, scrollable)
        return scrollable

    def _load_state_into_ui(self) -> None:
        initial_stats_state = self.state["profiles"][self.initial_stats_profile_key]
        self.initial_stats_vars["enabled"].set(bool(initial_stats_state.get("enabled")))
        self.initial_stats_vars["max_health"].set(str(initial_stats_state.get("max_health", "30")))
        self.initial_stats_vars["max_mana"].set(str(initial_stats_state.get("max_mana", "50")))
        self.initial_stats_vars["starting_money"].set(str(initial_stats_state.get("starting_money", "0")))

        rarity_state = self.state["profiles"]["rarity_editor"]
        for source_key, vars_for_source in self.rarity_editor_vars.items():
            source_state = rarity_state[source_key]
            vars_for_source["enabled"].set(bool(source_state["enabled"]))
            for key, var in vars_for_source["values"].items():
                var.set(source_state["values"][key])
            if "roll_order" in vars_for_source:
                vars_for_source["roll_order"].set(source_state.get("roll_order", ""))

        boon_multiplier_state = self.state["profiles"][self.boon_multiplier_profile_key]["gods"]
        for god_key, vars_for_god in self.boon_multiplier_vars.items():
            god_state = boon_multiplier_state.get(god_key, {})
            vars_for_god["enabled"].set(bool(god_state.get("enabled", False)))

            boon_state_map = god_state.get("boons", {})
            for boon_name, vars_for_boon in vars_for_god["boons"].items():
                boon_state = boon_state_map.get(boon_name, {})
                vars_for_boon["enabled"].set(bool(boon_state.get("enabled", False)))
                vars_for_boon["show_advanced"].set(bool(boon_state.get("show_advanced", False)))
                field_state_map = boon_state.get("fields", {})
                for field_path, field_var in vars_for_boon["fields"].items():
                    field_state = field_state_map.get(field_path, {})
                    default_value = self.boon_multiplier_metadata["gods"][god_key]["boons"][boon_name]["fields"][
                        field_path
                    ]["default"]
                    field_var.set(str(field_state.get("value", default_value)))
                self._update_boon_multiplier_advanced_visibility(god_key, boon_name)

        weapon_damage_state = self.state["profiles"]["weapon_damage"]
        for weapon_name, vars_for_weapon in self.weapon_damage_vars.items():
            source_state = weapon_damage_state[weapon_name]
            vars_for_weapon["enabled"].set(bool(source_state["enabled"]))
            vars_for_weapon["value"].set(source_state["value"])

        arcana_state = self.state["profiles"].get(
            self.arcana_profile_key,
            self.service.default_arcana_editor_state(),
        )
        self.arcana_editor_vars["enabled"].set(bool(arcana_state.get("enabled", False)))
        self.arcana_editor_vars["unlock_upgrade_cost_multiplier"].set(
            str(arcana_state.get("unlock_upgrade_cost_multiplier", "1.0"))
        )
        self.arcana_editor_vars["starting_grasp_limit"].set(
            str(arcana_state.get("starting_grasp_limit", "10"))
        )
        self.arcana_editor_vars["grasp_growth_multiplier"].set(
            str(arcana_state.get("grasp_growth_multiplier", "1.0"))
        )
        effect_multipliers = arcana_state.get("effect_multipliers", {})
        for card_name, card_var in self.arcana_editor_vars["effect_multipliers"].items():
            card_var.set(str(effect_multipliers.get(card_name, "1.0")))

        reward_editor_state = self.state["profiles"][self.reward_profile_key]
        for reward_name, vars_for_reward in self.reward_editor_vars.items():
            source_state = reward_editor_state[reward_name]
            vars_for_reward["enabled"].set(bool(source_state["enabled"]))
            vars_for_reward["value"].set(source_state["value"])
            if "show_advanced" in vars_for_reward:
                vars_for_reward["show_advanced"].set(bool(source_state.get("show_advanced")))
                vars_for_reward["resource_cost_money"].set(source_state["resource_cost_money"])
                self._update_reward_advanced_visibility(reward_name)

        keepsake_editor_state = self.state["profiles"][self.keepsake_profile_key]
        for keepsake_name, vars_for_keepsake in self.keepsake_editor_vars.items():
            source_state = keepsake_editor_state[keepsake_name]
            vars_for_keepsake["enabled"].set(bool(source_state["enabled"]))
            vars_for_keepsake["show_advanced"].set(bool(source_state.get("show_advanced")))
            for field_id, field_var in vars_for_keepsake["fields"].items():
                field_var.set(str(source_state["fields"][field_id]))
            self._update_keepsake_advanced_visibility(keepsake_name)

        refresh_state = self.state["profiles"][self.refresh_profile_key]
        for feature_key, vars_for_feature in self.refresh_vars.items():
            source_state = refresh_state.get(feature_key, {})
            vars_for_feature["enabled"].set(bool(source_state.get("enabled", False)))

    def _refresh_header_state(self) -> None:
        valid, message = self.service.validate_scripts_dir()
        self.status_label_var.set(self._translate_status_message(message))
        current_tab = self.notebook_tab_labels[self.notebook.index(self.notebook.select())]
        current_profile = self._translate_profile_name(current_tab)
        self.profile_label_var.set(self._trf("current_profile", profile=current_profile))
        self.root_label_var.set(self._trf("target_root", root=self.paths.root_dir))

        new_state = "normal" if valid else "disabled"
        for button in (self.generate_button, self.backup_button, self.apply_button, self.restore_button):
            button.configure(state=new_state)

    def _refresh_preview(self) -> None:
        self._refresh_header_state()
        profile = self._current_profile()
        profile_state = self._collect_profile_state(profile)
        targets = self.service.get_target_files(profile, profile_state)
        display_items = [self._translate_preview_item(f"Content/Scripts/{name}") for name in targets]
        if not display_items:
            display_items = [self._tr("preview_empty")]
        self.preview_list_var.set(display_items)

    def _current_profile(self) -> str:
        current_index = self.notebook.index(self.notebook.select())
        return self.notebook_tab_profiles[current_index]

    def _collect_rarity_editor_state(self) -> dict[str, Any]:
        collected: dict[str, Any] = {}
        for source_key, vars_for_source in self.rarity_editor_vars.items():
            source_state: dict[str, Any] = {
                "enabled": bool(vars_for_source["enabled"].get()),
                "values": {},
            }
            for key, var in vars_for_source["values"].items():
                source_state["values"][key] = var.get().strip()
            if "roll_order" in vars_for_source:
                source_state["roll_order"] = vars_for_source["roll_order"].get().strip()
            collected[source_key] = source_state
        return collected

    def _collect_initial_stats_state(self) -> dict[str, Any]:
        return {
            "enabled": bool(self.initial_stats_vars["enabled"].get()),
            "max_health": self.initial_stats_vars["max_health"].get().strip(),
            "max_mana": self.initial_stats_vars["max_mana"].get().strip(),
            "starting_money": self.initial_stats_vars["starting_money"].get().strip(),
        }

    def _collect_weapon_damage_state(self) -> dict[str, Any]:
        collected: dict[str, Any] = {}
        for weapon_name, vars_for_weapon in self.weapon_damage_vars.items():
            collected[weapon_name] = {
                "enabled": bool(vars_for_weapon["enabled"].get()),
                "value": vars_for_weapon["value"].get().strip(),
            }
        return collected

    def _collect_reward_editor_state(self) -> dict[str, Any]:
        collected: dict[str, Any] = {}
        for reward_name, vars_for_reward in self.reward_editor_vars.items():
            reward_state: dict[str, Any] = {
                "enabled": bool(vars_for_reward["enabled"].get()),
                "value": vars_for_reward["value"].get().strip(),
            }
            if "show_advanced" in vars_for_reward:
                reward_state["show_advanced"] = bool(vars_for_reward["show_advanced"].get())
                reward_state["resource_cost_money"] = vars_for_reward["resource_cost_money"].get().strip()
            collected[reward_name] = reward_state
        return collected

    def _collect_boon_multiplier_state(self) -> dict[str, Any]:
        collected: dict[str, Any] = {"gods": {}}
        for god_key, vars_for_god in self.boon_multiplier_vars.items():
            god_state: dict[str, Any] = {
                "enabled": bool(vars_for_god["enabled"].get()),
                "boons": {},
            }
            for boon_name, vars_for_boon in vars_for_god["boons"].items():
                boon_state: dict[str, Any] = {
                    "enabled": bool(vars_for_boon["enabled"].get()),
                    "show_advanced": bool(vars_for_boon["show_advanced"].get()),
                    "fields": {},
                }
                for field_path, field_var in vars_for_boon["fields"].items():
                    boon_state["fields"][field_path] = {"value": field_var.get().strip()}
                god_state["boons"][boon_name] = boon_state
            collected["gods"][god_key] = god_state
        return collected

    def _collect_arcana_editor_state(self) -> dict[str, Any]:
        effect_multipliers: dict[str, str] = {}
        for card_name, card_var in self.arcana_editor_vars["effect_multipliers"].items():
            effect_multipliers[card_name] = card_var.get().strip()
        return {
            "enabled": bool(self.arcana_editor_vars["enabled"].get()),
            "effect_multipliers": effect_multipliers,
            "unlock_upgrade_cost_multiplier": self.arcana_editor_vars[
                "unlock_upgrade_cost_multiplier"
            ].get().strip(),
            "starting_grasp_limit": self.arcana_editor_vars["starting_grasp_limit"].get().strip(),
            "grasp_growth_multiplier": self.arcana_editor_vars["grasp_growth_multiplier"].get().strip(),
        }

    def _collect_profile_state(self, profile: str) -> dict[str, Any]:
        if profile == self.initial_stats_profile_key:
            return self._collect_initial_stats_state()
        if profile == "rarity_editor":
            return self._collect_rarity_editor_state()
        if profile == self.boon_multiplier_profile_key:
            return self._collect_boon_multiplier_state()
        if profile == self.weapon_damage_profile_key:
            return self._collect_weapon_damage_state()
        if profile == self.arcana_profile_key:
            return self._collect_arcana_editor_state()
        if profile == self.reward_profile_key:
            return self._collect_reward_editor_state()
        if profile == self.keepsake_profile_key:
            return self._collect_keepsake_editor_state()
        if profile == self.refresh_profile_key:
            return self._collect_refresh_state()
        return copy.deepcopy(self.state["profiles"].get(profile, {}))

    def _collect_keepsake_editor_state(self) -> dict[str, Any]:
        collected: dict[str, Any] = {}
        for keepsake_name, vars_for_keepsake in self.keepsake_editor_vars.items():
            keepsake_state: dict[str, Any] = {
                "enabled": bool(vars_for_keepsake["enabled"].get()),
                "show_advanced": bool(vars_for_keepsake["show_advanced"].get()),
                "fields": {},
            }
            for field_id, field_var in vars_for_keepsake["fields"].items():
                keepsake_state["fields"][field_id] = field_var.get().strip()
            collected[keepsake_name] = keepsake_state
        return collected

    def _collect_refresh_state(self) -> dict[str, Any]:
        collected: dict[str, Any] = {}
        for feature_key, vars_for_feature in self.refresh_vars.items():
            collected[feature_key] = {
                "enabled": bool(vars_for_feature["enabled"].get()),
            }
        return collected

    def _persist_ui_state(self) -> tuple[str, dict[str, Any]]:
        self.state["profiles"][self.initial_stats_profile_key] = self._collect_initial_stats_state()
        self.state["profiles"]["rarity_editor"] = self._collect_rarity_editor_state()
        self.state["profiles"][self.boon_multiplier_profile_key] = self._collect_boon_multiplier_state()
        self.state["profiles"]["weapon_damage"] = self._collect_weapon_damage_state()
        self.state["profiles"][self.arcana_profile_key] = self._collect_arcana_editor_state()
        self.state["profiles"][self.reward_profile_key] = self._collect_reward_editor_state()
        self.state["profiles"][self.keepsake_profile_key] = self._collect_keepsake_editor_state()
        self.state["profiles"][self.refresh_profile_key] = self._collect_refresh_state()
        self._capture_pane_positions()
        self.service.save_state(self.state)
        profile = self._current_profile()
        return profile, self._collect_profile_state(profile)

    def _append_log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _register_scroll_target(self, canvas: tk.Canvas, *widgets: tk.Misc) -> None:
        for widget in widgets:
            widget.bind("<Enter>", lambda _event, target=canvas: self._set_active_scroll_canvas(target))
            widget.bind("<Leave>", lambda _event, target=canvas: self._clear_active_scroll_canvas(target))

    def _set_active_scroll_canvas(self, canvas: tk.Canvas) -> None:
        self.active_scroll_canvas = canvas

    def _clear_active_scroll_canvas(self, canvas: tk.Canvas) -> None:
        if self.active_scroll_canvas is canvas:
            self.active_scroll_canvas = None

    def _on_boon_multiplier_advanced_toggle(self, god_key: str, boon_name: str) -> None:
        self._update_boon_multiplier_advanced_visibility(god_key, boon_name)
        self._refresh_preview()

    def _update_boon_multiplier_advanced_visibility(self, god_key: str, boon_name: str) -> None:
        vars_for_boon = self.boon_multiplier_vars[god_key]["boons"][boon_name]
        advanced_frame = vars_for_boon.get("advanced_frame")
        if advanced_frame is None:
            return
        if vars_for_boon["show_advanced"].get():
            advanced_frame.grid()
        else:
            advanced_frame.grid_remove()

    def _on_reward_advanced_toggle(self, reward_name: str) -> None:
        self._update_reward_advanced_visibility(reward_name)
        self._refresh_preview()

    def _update_reward_advanced_visibility(self, reward_name: str) -> None:
        vars_for_reward = self.reward_editor_vars[reward_name]
        advanced_frame = vars_for_reward.get("advanced_frame")
        if advanced_frame is None:
            return
        if vars_for_reward["show_advanced"].get():
            advanced_frame.grid()
        else:
            advanced_frame.grid_remove()

    def _on_keepsake_advanced_toggle(self, keepsake_name: str) -> None:
        self._update_keepsake_advanced_visibility(keepsake_name)
        self._refresh_preview()

    def _update_keepsake_advanced_visibility(self, keepsake_name: str) -> None:
        vars_for_keepsake = self.keepsake_editor_vars[keepsake_name]
        advanced_frame = vars_for_keepsake["advanced_frame"]
        if vars_for_keepsake["show_advanced"].get():
            advanced_frame.grid()
        else:
            advanced_frame.grid_remove()

    def _on_pane_sash_release(self, _event: tk.Event) -> None:
        self._capture_pane_positions()
        self.service.save_state(self.state)

    def _capture_pane_positions(self) -> None:
        panes_state = self.state.setdefault("ui_layout", {}).setdefault("panes", {})
        try:
            panes_state["bottom_horizontal"] = int(self.bottom_split_pane.sashpos(0))
        except (tk.TclError, AttributeError, ValueError):
            pass

    def _apply_saved_pane_positions(self) -> None:
        panes_state = self.state.get("ui_layout", {}).get("panes", {})
        self.update_idletasks()

        container_width = self.bottom_split_pane.winfo_width()
        default_bottom_horizontal = int(container_width * 0.50) if container_width > 0 else 500

        bottom_horizontal = panes_state.get("bottom_horizontal")
        if not isinstance(bottom_horizontal, int):
            bottom_horizontal = default_bottom_horizontal
        if container_width > 0:
            bottom_horizontal = max(360, min(bottom_horizontal, container_width - 260))

        try:
            self.bottom_split_pane.sashpos(0, bottom_horizontal)
        except tk.TclError:
            pass

    def _on_mousewheel(self, event: tk.Event) -> None:
        canvas = self.active_scroll_canvas or getattr(self, "outer_canvas", None)
        if canvas is None or not canvas.winfo_exists():
            return
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _show_workspace_migration_notice(self) -> None:
        messagebox.showinfo(
            self._tr("workspace_updated_title"),
            self._tr("workspace_updated_body"),
        )
        self._append_log(self._tr("workspace_updated_log"))

    def _on_generate(self) -> None:
        profile, profile_state = self._persist_ui_state()
        try:
            generated = self.service.generate_copies(profile, profile_state, self.state)
        except (OperationError, ValueError) as exc:
            message = self._translate_operation_message(str(exc))
            messagebox.showerror(self._translate_text("Generate Copies"), message)
            self._append_log(self._trf("generate_failed", message=message))
            return

        joined = ", ".join(generated)
        self._append_log(self._trf("generate_done_log", files=joined))
        messagebox.showinfo(
            self._translate_text("Generate Copies"),
            self._trf("generate_done_body", files="\n".join(generated)),
        )

    def _on_backup(self) -> None:
        profile, profile_state = self._persist_ui_state()
        targets = self.service.get_target_files(profile, profile_state)
        try:
            backed_up = self.service.backup_originals(targets, self.state)
        except OperationError as exc:
            message = self._translate_operation_message(str(exc))
            messagebox.showerror(self._translate_text("Backup Originals"), message)
            self._append_log(self._trf("backup_failed", message=message))
            return

        if backed_up:
            message = self._trf("backup_done", files="\n".join(backed_up))
        else:
            message = self._tr("backup_none")
        self._append_log(message.replace("\n", " "))
        messagebox.showinfo(self._translate_text("Backup Originals"), message)

    def _on_apply(self) -> None:
        profile, profile_state = self._persist_ui_state()
        try:
            generated = self.service.generate_copies(profile, profile_state, self.state)
            applied = self.service.apply_generated_files(generated, self.state, profile)
        except (OperationError, ValueError) as exc:
            message = self._translate_operation_message(str(exc))
            messagebox.showerror(self._translate_text("Apply Replacement"), message)
            self._append_log(self._trf("apply_failed", message=message))
            return

        joined = ", ".join(applied)
        self._append_log(self._trf("apply_done_log", files=joined))
        messagebox.showinfo(
            self._translate_text("Apply Replacement"),
            self._trf("apply_done_body", files="\n".join(applied)),
        )

    def _on_restore(self) -> None:
        self._persist_ui_state()
        try:
            restored = self.service.restore_all_backups(self.state)
        except OperationError as exc:
            message = self._translate_operation_message(str(exc))
            messagebox.showerror(self._translate_text("Restore Backups"), message)
            self._append_log(self._trf("restore_failed", message=message))
            return

        joined = ", ".join(restored)
        self._append_log(self._trf("restore_done_log", files=joined))
        messagebox.showinfo(
            self._translate_text("Restore Backups"),
            self._trf("restore_done_body", files="\n".join(restored)),
        )


def run_app() -> None:
    app = HadesModUI()
    app.mainloop()

