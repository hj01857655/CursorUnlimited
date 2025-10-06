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
  "cursor.accessToken": "eyJhbGci...",
  "cursor.email": "user@example.com",
  "cursorAuth/accessToken": "eyJhbGci...",
  "cursorAuth/cachedEmail": "user@example.com",
  "cursorAuth/cachedSignUpType": "Auth_0",
  "cursorAuth/refreshToken": "eyJhbGci...",
  "storage.serviceMachineId": "uuid",
  "telemetry.machineId": "hash",
  // ... 其他配置
}
```

**关键字段**：
- `cursor.accessToken` - 访问令牌
- `cursor.email` - 邮箱账号
- `cursorAuth/accessToken` - 认证访问令牌
- `cursorAuth/cachedEmail` - 缓存的邮箱
- `cursorAuth/refreshToken` - 刷新令牌
- `storage.serviceMachineId` - 服务机器ID

---

### 2. **account.json**
**位置**: `User/globalStorage/account.json`

存储多个账号列表，支持快速切换：

```json
[
  {
    "email": "user1@example.com",
    "token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "workos_cursor_session_token": "WorkosCursorSessionToken=...",
    "is_current": true,
    "created_at": "2025-09-08 19:29:09"
  },
  {
    "email": "user2@example.com",
    "token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "workos_cursor_session_token": "WorkosCursorSessionToken=...",
    "is_current": false,
    "created_at": "2025-09-08 19:43:10"
  }
]
```

**关键字段**：
- `email` - 邮箱账号
- `token` - 访问令牌
- `refresh_token` - 刷新令牌
- `workos_cursor_session_token` - WorkOS会话令牌
- `is_current` - 是否为当前使用账号
- `created_at` - 创建时间

---

### 3. **state.vscdb** (SQLite数据库)
**位置**: `User/globalStorage/state.vscdb`
**大小**: ~658 MB

#### 数据库结构：
- **ItemTable** (156条记录) - 存储配置项
- **cursorDiskKV** (16987条记录) - 键值对存储

#### ItemTable 中的账号认证相关key：

```
cursor.accessToken                          # 访问令牌
cursor.email                                # 邮箱
cursor.featureStatus.dataPrivacyOnboarding  # 数据隐私入门状态

cursorAuth/accessToken                      # 认证访问令牌
cursorAuth/cachedEmail                      # 缓存的邮箱
cursorAuth/cachedSignUpType                 # 注册类型
cursorAuth/onboardingDate                   # 入职日期
cursorAuth/refreshToken                     # 刷新令牌
cursorAuth/stripeMembershipType             # Stripe会员类型

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
3. ✅ 修改 `account.json` 设置 `is_current` 标记
4. ✅ 可选：修改 `state.vscdb` 数据库中的对应字段
5. ✅ 可选：修改 `machineid`（如果需要更换设备）
6. ✅ 重启Cursor

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

| storage.json | account.json | state.vscdb (ItemTable) |
|-------------|--------------|------------------------|
| cursor.accessToken | token | cursor.accessToken |
| cursor.email | email | cursor.email |
| cursorAuth/accessToken | token | cursorAuth/accessToken |
| cursorAuth/cachedEmail | email | cursorAuth/cachedEmail |
| cursorAuth/refreshToken | refresh_token | cursorAuth/refreshToken |
| - | workos_cursor_session_token | - |

---

## ⚠️ 注意事项

1. **备份重要性**：修改前必须备份所有文件
2. **进程检查**：操作前确保Cursor完全关闭
3. **一致性**：三个存储位置的数据需要保持一致
4. **数据库锁**：操作 `state.vscdb` 时确保没有其他进程占用
5. **token有效期**：token可能会过期，需要定期更新

---

## 🛠️ 实现建议

### 切换账号的完整流程：
```python
1. 检测并关闭Cursor进程
2. 备份当前配置（storage.json, account.json, state.vscdb）
3. 从数据库读取目标账号信息
4. 更新 storage.json
5. 更新 account.json 的 is_current 标记
6. 可选：更新 state.vscdb
7. 重启Cursor
8. 记录操作日志
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
│       ├── account.json                    # 账号列表 ⭐
│       └── state.vscdb                     # 状态数据库 ⭐
└── [其他文件...]
```

⭐ = 账号切换必须处理的文件

---

**文档更新时间**: 2025-10-07
**适用版本**: Cursor 0.x
