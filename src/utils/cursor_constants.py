# -*- coding: utf-8 -*-
"""
Cursor 字段常量定义
定义 storage.json 和 state.vscdb 中使用的所有字段名
"""

# ========== storage.json 字段 ==========

# 认证字段（storage.json 中的 4 个）
STORAGE_AUTH_KEYS = [
    'cursorAuth/accessToken',
    'cursorAuth/cachedEmail',
    'cursorAuth/refreshToken',
    'cursorAuth/cachedSignUpType'
]

# 机器标识字段（storage.json 中的 5 个）
STORAGE_MACHINE_ID_KEYS = [
    'storage.serviceMachineId',
    'telemetry.machineId',
    'telemetry.macMachineId',
    'telemetry.devDeviceId',
    'telemetry.sqmId'
]

# 系统配置字段（不应在账号切换时修改）
STORAGE_SYSTEM_KEYS = [
    'backupWorkspaces',
    'profileAssociations',
    'theme',
    'themeBackground',
    'windowSplash',
    'windowSplashWorkspaceOverride',
    'windowsState',
    'windowControlHeight'
]

# ========== state.vscdb 数据库字段 (ItemTable 表) ==========

# 认证字段（ItemTable 中的 6 个）
DB_AUTH_KEYS = [
    'cursorAuth/accessToken',           # ✅ 与 storage.json 同步
    'cursorAuth/cachedEmail',           # ✅ 与 storage.json 同步
    'cursorAuth/refreshToken',          # ✅ 与 storage.json 同步
    'cursorAuth/cachedSignUpType',      # ✅ 与 storage.json 同步
    'cursorAuth/onboardingDate',        # 💾 只在数据库
    'cursorAuth/stripeMembershipType'   # 💾 只在数据库
]

# 机器标识和会话字段（ItemTable 中的 4 个）
DB_MACHINE_ID_KEYS = [
    'storage.serviceMachineId',         # ✅ 与 storage.json 同步
    'telemetry.firstSessionDate',       # 💾 只在数据库
    'telemetry.currentSessionDate',     # 💾 只在数据库
    'telemetry.lastSessionDate'         # 💾 只在数据库
]

# 数据库配置
DB_TABLE_NAME = 'ItemTable'
DB_KEY_COLUMN = 'key'
DB_VALUE_COLUMN = 'value'

# ========== 字段映射关系 ==========

# storage.json 和 state.vscdb 中同步的认证字段
SYNCED_AUTH_KEYS = [
    'cursorAuth/accessToken',
    'cursorAuth/cachedEmail',
    'cursorAuth/refreshToken',
    'cursorAuth/cachedSignUpType'
]

# 只在 state.vscdb 中的认证字段
DB_ONLY_AUTH_KEYS = [
    'cursorAuth/onboardingDate',
    'cursorAuth/stripeMembershipType'
]

# 只在 storage.json 中的机器标识字段 (📄 不在数据库)
STORAGE_ONLY_MACHINE_ID_KEYS = [
    'telemetry.machineId',
    'telemetry.macMachineId',
    'telemetry.devDeviceId',
    'telemetry.sqmId'
]

# 只在 state.vscdb 中的字段 (💾 不在 storage.json)
DB_ONLY_KEYS = [
    'cursorAuth/onboardingDate',
    'cursorAuth/stripeMembershipType',
    'telemetry.firstSessionDate',
    'telemetry.currentSessionDate',
    'telemetry.lastSessionDate'
]

# ========== 排除的字段模式 ==========

# 不应该备份/切换的系统键模式（UI状态、窗口位置等）
EXCLUDED_KEY_PATTERNS = [
    'workbench.',           # 工作台UI状态
    'terminal.',            # 终端状态
    'window.',              # 窗口位置和大小
    'editor.',              # 编辑器状态
    'files.hotExit',        # 热退出状态
    'search.history',       # 搜索历史
    'debug.'                # 调试状态
]
