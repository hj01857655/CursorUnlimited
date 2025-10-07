# CursorUnlimited 日志系统文档

## 📝 日志系统概述

### 当前实现
**文件**: `src/utils/logger.py`

采用Python标准库 `logging` 模块实现的日志系统：

```python
def setup_logger(name="CursorUnlimited", log_dir="logs"):
    """设置并返回日志记录器"""
    # 文件处理器 - DEBUG级别
    # 控制台处理器 - INFO级别
    # 日志格式: '时间 - 名称 - 级别 - 消息'
```

### 特性
- ✅ 按日期自动分割日志文件（YYYYMMDD.log）
- ✅ 双输出：文件 + 控制台
- ✅ UTF-8编码支持中文
- ✅ 防止重复添加处理器
- ✅ 自动创建logs目录

---

## 📊 当前集成状态

### ✅ 已集成模块
1. **main.py** - 应用入口
   ```python
   logger = setup_logger()
   logger.info("Starting CursorUnlimited application...")
   ```

### ❌ 未集成模块（需要添加）
1. **src/models/database.py** - 数据库操作
2. **src/models/account.py** - 账号模型
3. **src/automation/cursor_manager.py** - Cursor进程管理
4. **src/automation/config_manager.py** - 配置管理
5. **src/services/account_switcher.py** - 账号切换服务 ⚠️ 关键模块

---

## 🎯 日志级别使用规范

### DEBUG (调试)
用于详细的调试信息
```python
logger.debug(f"读取配置文件: {config_path}")
logger.debug(f"SQL查询: {sql}")
```

### INFO (信息)
用于正常操作的确认信息
```python
logger.info("应用启动成功")
logger.info(f"切换到账号: {email}")
logger.info(f"添加账号: {email}")
```

### WARNING (警告)
用于警告信息，但不影响程序运行
```python
logger.warning("Cursor进程未找到")
logger.warning(f"账号token即将过期: {email}")
```

### ERROR (错误)
用于错误信息，功能无法完成
```python
logger.error(f"切换账号失败: {error}")
logger.error(f"数据库连接失败: {e}")
```

### CRITICAL (严重错误)
用于严重错误，可能导致程序崩溃
```python
logger.critical("数据库文件损坏")
logger.critical(f"无法创建必要目录: {e}")
```

---

## 🔧 模块集成模板

### 标准导入
```python
from ..utils.logger import setup_logger

class YourClass:
    def __init__(self):
        self.logger = setup_logger()  # 使用默认名称
        # 或
        self.logger = setup_logger("ModuleName")  # 自定义名称
```

### 使用示例
```python
class AccountSwitcher:
    def __init__(self, db: Database):
        self.logger = setup_logger("AccountSwitcher")
        self.logger.info("AccountSwitcher initialized")
    
    def switch_account(self, account_id: int):
        self.logger.info(f"开始切换账号: {account_id}")
        try:
            # ... 切换逻辑
            self.logger.info(f"账号切换成功: {account['email']}")
            return True, "切换成功"
        except Exception as e:
            self.logger.error(f"账号切换失败: {str(e)}", exc_info=True)
            return False, str(e)
```

---

## 📋 待集成清单

### 1. Database 类
**位置**: `src/models/database.py`

**需要添加的日志点**:
```python
- 数据库初始化
- 表创建
- 连接建立/关闭
- 事务提交/回滚
- 错误异常
```

### 2. Account 类
**位置**: `src/models/account.py`

**需要添加的日志点**:
```python
- 添加账号
- 更新账号
- 删除账号
- 查询操作
- Token更新
- 错误处理
```

### 3. CursorManager 类
**位置**: `src/automation/cursor_manager.py`

**需要添加的日志点**:
```python
- 进程检测
- 进程关闭（每个进程）
- 进程启动
- 路径查找
- 错误处理
```

### 4. CursorConfigManager 类
**位置**: `src/automation/config_manager.py`

**需要添加的日志点**:
```python
- 读取配置文件
- 写入配置文件
- 备份操作
- 恢复操作
- account.json操作
- 错误处理
```

### 5. AccountSwitcher 类 ⚠️
**位置**: `src/services/account_switcher.py`

**需要添加的日志点**:
```python
- 切换流程各步骤
- 备份操作
- 进程操作
- 配置更新
- 成功/失败状态
- 同步操作
- 登出操作
```

---

## 🚀 增强建议

### 1. 结构化日志
添加上下文信息：
```python
logger.info(f"切换账号", extra={
    'account_id': account_id,
    'email': email,
    'action': 'switch',
    'duration': elapsed_time
})
```

### 2. 异常日志
完整记录异常信息：
```python
try:
    # ... code
except Exception as e:
    logger.error(f"操作失败: {str(e)}", exc_info=True)
    # exc_info=True 会记录完整的堆栈跟踪
```

### 3. 性能日志
记录耗时操作：
```python
import time

start_time = time.time()
# ... 执行操作
duration = time.time() - start_time
logger.info(f"操作完成，耗时: {duration:.2f}秒")
```

### 4. 日志装饰器
为函数自动添加日志：
```python
def log_function_call(func):
    """记录函数调用的装饰器"""
    def wrapper(*args, **kwargs):
        logger = setup_logger()
        logger.debug(f"调用函数: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"函数返回: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"函数异常: {func.__name__} - {str(e)}")
            raise
    return wrapper

@log_function_call
def switch_account(account_id):
    # ... 实现
```

---

## 📁 日志文件管理

### 日志目录结构
```
logs/
├── 20251007.log         # 今天的日志
├── 20251006.log         # 昨天的日志
├── 20251005.log         # 前天的日志
└── ...
```

### 日志清理策略（建议实现）
```python
import os
from datetime import datetime, timedelta

def clean_old_logs(log_dir="logs", keep_days=30):
    """清理超过指定天数的日志文件"""
    logger = setup_logger()
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            try:
                # 从文件名解析日期 (YYYYMMDD.log)
                date_str = filename.replace('.log', '')
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date < cutoff_date:
                    file_path = os.path.join(log_dir, filename)
                    os.remove(file_path)
                    logger.info(f"删除旧日志: {filename}")
            except Exception as e:
                logger.warning(f"清理日志文件失败: {filename} - {e}")
```

---

## 📊 日志分析建议

### 1. 日志查看工具
```python
# 查看今天的错误日志
grep "ERROR" logs/20251007.log

# 查看特定操作的日志
grep "switch" logs/20251007.log

# 统计错误数量
grep -c "ERROR" logs/20251007.log
```

### 2. 日志导出功能
在UI的"日志"页面提供：
- 按日期筛选
- 按级别筛选
- 按关键词搜索
- 导出为CSV/TXT

### 3. 实时日志监控
在UI显示最新日志（tail -f效果）

---

## 🔍 日志格式示例

### 当前格式
```
2025-10-07 01:50:23 - CursorUnlimited - INFO - Starting application
2025-10-07 01:50:24 - CursorUnlimited - INFO - Application started successfully
2025-10-07 01:50:30 - AccountSwitcher - INFO - 开始切换账号: 1
2025-10-07 01:50:31 - CursorManager - INFO - 检测到Cursor进程: PID 12345
2025-10-07 01:50:32 - CursorManager - INFO - 成功关闭进程: PID 12345
2025-10-07 01:50:35 - ConfigManager - INFO - 更新配置文件成功
2025-10-07 01:50:36 - AccountSwitcher - INFO - 账号切换成功: user@example.com
```

### 增强格式建议（JSON）
```json
{
  "timestamp": "2025-10-07T01:50:30Z",
  "level": "INFO",
  "module": "AccountSwitcher",
  "message": "账号切换成功",
  "context": {
    "account_id": 1,
    "email": "user@example.com",
    "duration": 5.2
  }
}
```

---

## ⚡ 性能考虑

### 日志级别控制
生产环境建议使用 INFO 级别，开发环境使用 DEBUG 级别：

```python
import os

def setup_logger(name="CursorUnlimited", log_dir="logs"):
    # ... 
    # 根据环境设置级别
    level = logging.DEBUG if os.getenv('DEBUG') else logging.INFO
    logger.setLevel(level)
```

### 异步日志（高级）
对于高频日志操作，考虑使用异步处理：
```python
from concurrent.futures import ThreadPoolExecutor
import queue

class AsyncLogger:
    def __init__(self, logger):
        self.logger = logger
        self.queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    def log(self, level, message):
        self.queue.put((level, message))
        self.executor.submit(self._process_queue)
```

---

## 📋 实施计划

### 阶段1：核心模块集成 ✅
- [x] main.py（已完成）
- [ ] account_switcher.py（最优先）
- [ ] cursor_manager.py

### 阶段2：数据层集成
- [ ] database.py
- [ ] account.py（models）

### 阶段3：配置层集成
- [ ] config_manager.py

### 阶段4：UI集成
- [ ] 日志页面显示
- [ ] 实时日志更新
- [ ] 日志导出功能

---

## 📝 示例代码

### 完整集成示例
```python
# src/services/account_switcher.py

from ..utils.logger import setup_logger

class AccountSwitcher:
    def __init__(self, db: Database):
        # 初始化日志
        self.logger = setup_logger("AccountSwitcher")
        self.logger.info("AccountSwitcher服务初始化")
        
        self.db = db
        self.account_model = Account(db)
        self.log_model = UsageLog(db)
        self.cursor_manager = CursorManager()
        self.config_manager = CursorConfigManager()
    
    def switch_account(self, account_id: int, kill_cursor: bool = True):
        self.logger.info(f"开始切换账号: ID={account_id}")
        
        # 获取账号
        account = self.account_model.get_by_id(account_id)
        if not account:
            self.logger.warning(f"账号不存在: ID={account_id}")
            return False, "账号不存在"
        
        self.logger.debug(f"账号信息: {account['email']}")
        
        try:
            # 备份配置
            self.logger.info("备份当前配置...")
            # ... 备份代码
            
            # 关闭进程
            if kill_cursor:
                self.logger.info("关闭Cursor进程...")
                killed = self.cursor_manager.kill_all()
                self.logger.info(f"已关闭 {killed} 个进程")
            
            # 更新配置
            self.logger.info("更新配置文件...")
            # ... 更新代码
            
            self.logger.info(f"账号切换成功: {account['email']}")
            return True, "切换成功"
            
        except Exception as e:
            self.logger.error(f"账号切换失败: {str(e)}", exc_info=True)
            return False, str(e)
```

---

**文档更新时间**: 2025-10-07  
**版本**: v1.0  
**状态**: 日志系统已实现，待全面集成
