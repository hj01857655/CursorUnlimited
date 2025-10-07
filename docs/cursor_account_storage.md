# Cursor 账号数据存储位置详解

## 📍 数据存储根目录
```
C:\Users\{USERNAME}\AppData\Roaming\Cursor
```

---

## 🔐 账号认证相关数据

### 1. **storage.json** 
**位置**: `User/globalStorage/storage.json`

存储当前登录账号的主要信息：

```json
{
  // Cursor 账号认证字段
  "cursorAuth/accessToken": "eyJhbGci...",
  "cursorAuth/cachedEmail": "user@example.com",
  "cursorAuth/cachedSignUpType": "Auth_0",
  "cursorAuth/refreshToken": "eyJhbGci...",
  
  // 机器标识字段
  "storage.serviceMachineId": "uuid",
  "telemetry.machineId": "hash",
  // ... 其他配置
}
```

**关键字段**：
- `cursorAuth/accessToken` - 访问令牌
- `cursorAuth/cachedEmail` - 缓存的邮箱
- `cursorAuth/refreshToken` - 刷新令牌
- `cursorAuth/cachedSignUpType` - 注册类型
- `storage.serviceMachineId` - 服务机器ID

---

### 2. **state.vscdb** (SQLite数据库)
**位置**: `User/globalStorage/state.vscdb`
**大小**: ~658 MB

#### 数据库结构：
- **ItemTable** (156条记录) - 存储配置项
- **cursorDiskKV** (16987条记录) - 键值对存储

#### ItemTable 中的账号认证相关key：

```
cursorAuth/accessToken                      # 访问令牌
cursorAuth/cachedEmail                      # 缓存的邮箱
cursorAuth/cachedSignUpType                 # 注册类型（如 Auth_0）
cursorAuth/onboardingDate                   # 入职日期
cursorAuth/refreshToken                     # 刷新令牌
cursorAuth/stripeMembershipType             # Stripe会员类型（free/pro）

storage.serviceMachineId                    # 服务机器ID
```

#### AI和隐私相关key：
```
aiCodeTrackingLines                         # AI代码跟踪
aiCodeTrackingScoredCommits                 # AI代码评分提交
cursor/memoriesEnabled                      # 记忆功能启用
cursor/pendingMemories                      # 待处理记忆
cursor/notepadState                         # 记事本状态

cursorai/donotchange/newPrivacyMode2        # 隐私模式
cursorai/featureConfigCache                 # 特性配置缓存
cursorai/featureStatusCache                 # 特性状态缓存
cursorai/serverConfig                       # 服务器配置
```

---

### 4. **machineid**
**位置**: `machineid`

存储设备唯一标识：
```
21a805ba-47a8-430a-a8b4-683e5e0e5a94
```

**作用**：用于设备绑定和识别

---

## 🔄 账号切换需要操作的位置

### 方案一：完整切换（推荐）
1. ✅ 关闭所有Cursor进程
2. ✅ 修改 `storage.json` 中的token和email字段
3. ✅ 修改 `state.vscdb` 数据库中的对应字段
4. ✅ 可选：修改 `machineid`（如果需要更换设备）
5. ✅ 重启Cursor

### 方案二：快速切换
1. ✅ 关闭Cursor
2. ✅ 仅修改 `storage.json` 的关键字段
3. ✅ 重启Cursor

### 方案三：数据库级切换
1. ✅ 关闭Cursor
2. ✅ 直接操作 `state.vscdb` 数据库
3. ✅ 修改 ItemTable 中的账号相关记录
4. ✅ 重启Cursor

---
## 📋 字段对应关系

|| storage.json | state.vscdb (ItemTable) |
|-------------|------------------------|
| cursorAuth/accessToken | cursorAuth/accessToken |
| cursorAuth/cachedEmail | cursorAuth/cachedEmail |
| cursorAuth/refreshToken | cursorAuth/refreshToken |
| cursorAuth/cachedSignUpType | cursorAuth/cachedSignUpType |
| storage.serviceMachineId | storage.serviceMachineId |
| telemetry.machineId | - |
| telemetry.macMachineId | - |
| telemetry.devDeviceId | - |
| telemetry.sqmId | - |

---

## ⚠️ 注意事项

1. **备份重要性**：修改前必须备份所有文件
2. **进程检查**：操作前确保Cursor完全关闭
3. **一致性**：三个存储位置的数据需要保持一致
4. **数据库锁**：操作 `state.vscdb` 时确保没有其他进程占用
5. **token有效期**：token可能会过期，需要定期更新

---

## 🛠️ 工具类实现

### SqliteUtil 工具类
**位置**: `src/utils/sqlite_util.py`

专门用于操作 Cursor 的 `state.vscdb` 数据库的工具类。

#### 核心特性：

1. **上下文管理器连接** - 自动管理数据库连接
2. **批量操作优化** - 单次连接处理多个操作
3. **内置键常量** - 预定义所有 Cursor 相关键名
4. **备份支持** - SQLite 在线备份 API

#### 预定义的键常量：

**机器标识键** (`MACHINE_ID_KEYS`):
```python
[
    'storage.serviceMachineId',
    'telemetry.machineId',
    'telemetry.macMachineId',
    'telemetry.devDeviceId',
    'telemetry.sqmId',
    'telemetry.firstSessionDate',
    'telemetry.currentSessionDate',
    'telemetry.lastSessionDate'
]
```

**账号认证键** (`AUTH_KEYS`):
```python
[
    'cursorAuth/accessToken',
    'cursorAuth/cachedEmail',
    'cursorAuth/refreshToken',
    'cursorAuth/cachedSignUpType',
    'cursorAuth/onboardingDate',
    'cursorAuth/stripeMembershipType'
]
```

**排除的系统键** (`EXCLUDED_KEYS_PATTERNS`):
```python
[
    'workbench.',      # 工作台UI状态
    'terminal.',       # 终端状态
    'window.',         # 窗口位置和大小
    'editor.',         # 编辑器状态
    'files.hotExit',   # 热退出状态
    'search.history',  # 搜索历史
    'debug.'           # 调试状态
]
```

#### 核心方法：

**连接管理**:
```python
# 上下文管理器
with SqliteUtil.get_connection(db_path) as conn:
    cursor = conn.cursor()
    # ... 数据库操作

# 数据库备份
SqliteUtil.backup_database(db_path, backup_path)
```

**Cursor 专用方法**:
```python
# 读取单个值
value = SqliteUtil.read_cursor_value(db_path, 'cursorAuth/accessToken')

# 写入单个值
SqliteUtil.write_cursor_value(db_path, 'cursorAuth/cachedEmail', 'user@example.com')

# 批量获取机器标识
machine_ids = SqliteUtil.get_machine_ids(db_path)

# 批量设置机器标识（单次连接优化）
SqliteUtil.set_machine_ids(db_path, {
    'telemetry.machineId': 'new_machine_id',
    'telemetry.devDeviceId': 'new_device_id'
})

# 批量获取认证信息
auth_info = SqliteUtil.get_auth_info(db_path)

# 批量设置认证信息（单次连接优化）
SqliteUtil.set_auth_info(db_path, {
    'cursorAuth/accessToken': 'token...',
    'cursorAuth/cachedEmail': 'user@example.com'
})

# 清空所有认证信息（登出）
SqliteUtil.clear_auth_info(db_path)

# 获取所有键名
all_keys = SqliteUtil.get_all_keys(db_path)
```

---

## 🏗️ 项目架构

### 核心模块

```
src/
├── automation/
│   ├── cursor_manager.py          # Cursor 进程管理
│   ├── config_manager.py          # 配置文件管理
│   ├── machine_id_manager.py      # 机器ID管理
│   └── auth_manager.py            # 账号认证管理
├── utils/
│   ├── sqlite_util.py             # SQLite 数据库工具类 ⭐ 新增
│   ├── file_util.py               # JSON 文件和备份工具
│   ├── registry_util.py           # Windows 注册表工具
│   ├── logger.py                  # 日志系统
│   └── config.py                  # 配置管理
├── models/
│   ├── account.py                 # 账号数据模型
│   └── database.py                # 数据库模型
└── services/
    └── account_switcher.py        # 账号切换服务
```

### 模块说明

#### 1. **CursorManager** (`cursor_manager.py`)
- 检测 Cursor 进程
- 关闭/启动 Cursor
- 获取 Cursor 安装路径
- 日志记录

#### 2. **CursorConfigManager** (`config_manager.py`)
- 读写 `storage.json`
- 读写 `state.vscdb`
- 备份/恢复配置
- 清除 token（登出）

#### 3. **MachineIdManager** (`machine_id_manager.py`)
- 生成新的机器标识
- 备份/恢复机器标识
- 重置机器标识
- 应用到配置文件

#### 4. **SqliteUtil** (`sqlite_util.py`) ⭐
- 数据库连接管理（上下文管理器）
- 批量读写优化
- Cursor 专用键定义
- 数据库备份

#### 5. **RegistryUtil** (`registry_util.py`)
- Windows 注册表读写
- 获取系统机器 GUID
- SQM ID 管理

---

## 📝 实现建议

### 切换账号的完整流程：
```python
from src.automation.cursor_manager import CursorManager
from src.automation.config_manager import CursorConfigManager
from src.utils.sqlite_util import SqliteUtil

# 1. 检测并关闭Cursor进程
cursor_mgr = CursorManager()
if cursor_mgr.is_cursor_running():
    cursor_mgr.close_cursor()

# 2. 备份当前配置
config_mgr = CursorConfigManager()
config_mgr.backup_config('backup_before_switch')

# 3. 更新 storage.json
storage = config_mgr.read_storage()
storage['cursorAuth/accessToken'] = new_token
storage['cursorAuth/cachedEmail'] = new_email
config_mgr.write_storage(storage)

# 4. 更新 state.vscdb（使用 SqliteUtil）
db_path = config_mgr.state_vscdb_path
SqliteUtil.set_auth_info(db_path, {
    'cursorAuth/accessToken': new_token,
    'cursorAuth/cachedEmail': new_email,
    'cursorAuth/refreshToken': new_refresh_token
})

# 5. 重启Cursor
cursor_mgr.start_cursor()
```

### 重置机器标识的完整流程：
```python
from src.automation.machine_id_manager import MachineIdManager
from src.utils.sqlite_util import SqliteUtil

# 1. 关闭 Cursor
cursor_mgr.close_cursor()

# 2. 生成新的机器标识
machine_mgr = MachineIdManager()
new_ids = machine_mgr.generate_new_machine_ids()

# 3. 应用到 storage.json
machine_mgr.apply_machine_ids(new_ids)

# 4. 同步到 state.vscdb
db_path = config_mgr.state_vscdb_path
db_machine_ids = {
    'telemetry.machineId': new_ids['machineId'],
    'telemetry.macMachineId': new_ids['macMachineId'],
    'telemetry.devDeviceId': new_ids['devDeviceId'],
    'telemetry.sqmId': new_ids['sqmId']
}
SqliteUtil.set_machine_ids(db_path, db_machine_ids)

# 5. 重启 Cursor
cursor_mgr.start_cursor()
```

---

## 📌 相关文件清单

```
Cursor数据目录/
├── machineid                               # 设备ID
├── User/
│   ├── settings.json                       # 用户设置
│   ├── keybindings.json                    # 快捷键
│   └── globalStorage/
│       ├── storage.json                    # 主配置（含token）⭐
│       └── state.vscdb                     # 状态数据库 ⭐
└── [其他文件...]
```

⭐ = 账号切换必须处理的文件

---

---

## 🔧 数据库操作最佳实践

### 1. 使用上下文管理器
```python
# ✅ 推荐：自动管理连接
with SqliteUtil.get_connection(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ItemTable")
    results = cursor.fetchall()
# 连接自动关闭

# ❌ 不推荐：手动管理连接
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
# ... 容易忘记关闭
conn.close()
```

### 2. 批量操作优化
```python
# ✅ 推荐：单次连接批量操作
SqliteUtil.set_auth_info(db_path, {
    'cursorAuth/accessToken': token,
    'cursorAuth/cachedEmail': email,
    'cursorAuth/refreshToken': refresh_token
})

# ❌ 不推荐：多次连接
SqliteUtil.write_cursor_value(db_path, 'cursorAuth/accessToken', token)
SqliteUtil.write_cursor_value(db_path, 'cursorAuth/cachedEmail', email)
SqliteUtil.write_cursor_value(db_path, 'cursorAuth/refreshToken', refresh_token)
```

### 3. 备份数据库
```python
# 使用 SQLite 在线备份 API
backup_path = 'backup/state.vscdb.backup'
SqliteUtil.backup_database(db_path, backup_path)
```

### 4. 错误处理
```python
try:
    with SqliteUtil.get_connection(db_path) as conn:
        # 数据库操作
        pass
except FileNotFoundError:
    print("数据库文件不存在")
except sqlite3.Error as e:
    print(f"数据库操作失败: {e}")
```

---

## 📊 性能优化对比

| 操作 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 批量设置认证信息 (6个字段) | 6次连接 | 1次连接 | **6x** |
| 批量设置机器标识 (8个字段) | 8次连接 | 1次连接 | **8x** |
| 数据库备份 | 文件复制 | SQLite API | **更安全** |
| 连接管理 | 手动关闭 | 自动管理 | **更可靠** |

---

**文档更新时间**: 2025-10-07  
**适用版本**: Cursor 0.x  
**工具类版本**: SqliteUtil v2.0 (优化版)
