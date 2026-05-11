# Hades II Modifier （机翻）

[English](README.md)

适合像你我一样的手残党。

## 概述

`HadesIIModUI` 使用确定性的 Lua 文本转换将补丁插入到 `Content/Scripts` 文件夹中。该应用程序始终确保在应用更改之前进行备份，并在本地的 `.hades2_mod` 工作区中维护状态。

## 快速入门

### 构建工具
如果你还没有构建，可以通过运行以下命令将 Python 工具编译为独立的 Windows 可执行文件：
```powershell
.\build_exe.ps1
```
*(等待构建完成。可执行文件将在 `dist/HadesIIModUI.exe` 生成。)*

### 运行工具
双击 `dist/HadesIIModUI.exe` 启动应用程序。

## 如何使用

用户界面分为用于配置的**选项卡（模式）**和用于执行的**操作**面板。

### 文件路径设置

将 exe 放到 `Hades II` 的主目录下。

### 配置补丁
选择顶部的选项卡以在不同的修改模式之间切换。在每种模式中，你可以切换 `Enable patch`（启用补丁）来激活特定的修改：

- **Rarity Editor（稀有度编辑器）**：调整普通神明、赫尔墨斯、混沌、阿尔忒弥斯等的出现概率。你可以更改稀有、史诗、双重和传奇祝福的概率，以及自定义掷骰顺序。
- **Boon Multipliers（祝福乘数）**：微调每个神明特定祝福提供的属性乘数（伤害、速度等）。高级字段默认隐藏，但可以展开进行更深度的自定义。
- **Weapon Damage（武器伤害）**：为整个武器家族添加基础伤害奖励。
- **Reward Amounts（奖励数量）**：编辑全球战斗后房间清除的结算值（例如：金钱、生命值、法力值）。
- **Keepsake（信物）**：配置在 `TraitData_Keepsake.lua` 中应用的每个信物的增益。

### 模组制作流程
配置好补丁后，按以下顺序使用**操作**按钮：

1. **1. Backup Originals（备份原文件）**：安全地在 `.hades2_mod/originals/` 文件夹中创建原始、未修改的 Lua 脚本备份。在应用第一个补丁之前，请务必执行此操作！

2. **2. Generate Copies（生成副本）**：首先点击此按钮。它会读取你当前的配置，并在 `.hades2_mod/generated/` 文件夹中创建打过补丁的 Lua 文件的预览副本。*这还不会影响你的实际游戏。*你可以在“目标文件”列表中验证目标文件。

3. **3. Apply Replacement（应用替换）**：应用程序会自动将生成的补丁文件复制到你的实际 `Content/Scripts/` 文件夹中。你的游戏现在已经修改完成了！

### 恢复游戏
如果你想恢复更改并返回到原版游戏：
- **4. Restore Backups（恢复备份）**：应用程序会自动用安全保存在 `.hades2_mod/originals/` 中的原始文件替换 `Content/Scripts/` 中的修改文件。

## 本地构建

- 创建虚拟环境。
```bash
python -m venv .venv
```

- 激活虚拟环境。
```bash
.venv\Scripts\activate
```

- 安装依赖。
```bash
pip install pyinstaller
```

- 构建可执行文件。
```bash
./build.ps1
```

## 开发者说明

- 该工具会将你的 UI 设置和应用程序状态保存在本地的 `.hades2_mod/state.json` 中。
- 高级 AI 代理指南和规则可以在 `AGENTS.md` 和 `CLAUDE.md` 中找到。
