# 数据库设计文档

## 账号表 (accounts)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | - | 主键ID |
| email | TEXT | UNIQUE NOT NULL | - | 邮箱账号 |
| password | TEXT | - | - | 密码（加密存储） |
| username | TEXT | - | - | 用户名/昵称 |
| access_token | TEXT | - | - | 访问令牌 |
| refresh_token | TEXT | - | - | 刷新令牌 |
| device_id | TEXT | - | - | 设备ID |
| machine_id | TEXT | - | - | 机器ID |
| account_type | TEXT | - | 'free' | 账号类型：free/trial/pro |
| status | TEXT | - | 'normal' | 账号状态：normal/banned/expired |
| pro_expire_date | DATETIME | - | - | Pro版到期时间 |
| is_active | INTEGER | - | 1 | 是否启用（1启用/0禁用） |
| last_login_time | DATETIME | - | - | 最后登录时间 |
| created_at | DATETIME | - | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | CURRENT_TIMESTAMP | 更新时间 |
| remark | TEXT | - | - | 备注信息 |

### 索引
- `idx_accounts_email` ON accounts(email)

---

## 使用记录表 (usage_logs)

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | - | 主键ID |
| account_id | INTEGER | FOREIGN KEY | - | 关联账号ID |
| action | TEXT | - | - | 操作类型：login/logout/switch/register |
| result | TEXT | - | - | 操作结果：success/failed |
| error_message | TEXT | - | - | 错误信息 |
| created_at | DATETIME | - | CURRENT_TIMESTAMP | 创建时间 |

### 索引
- `idx_logs_account_id` ON usage_logs(account_id)

---

## 字段说明

### account_type 枚举值
- `free` - 免费账号
- `trial` - 试用账号
- `pro` - 付费专业版账号

### status 枚举值
- `normal` - 正常状态
- `banned` - 已封禁
- `expired` - 已过期

### action 枚举值
- `login` - 登录操作
- `logout` - 登出操作
- `switch` - 切换账号
- `register` - 注册新账号

### result 枚举值
- `success` - 操作成功
- `failed` - 操作失败
