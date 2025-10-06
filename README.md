# CursorUnlimited - Cursor账号管理工具

## 🚀 项目简介

CursorUnlimited 是一个专为 Cursor AI 代码编辑器开发的账号管理工具，旨在帮助用户高效管理和切换多个 Cursor 账号，突破单账号使用限制，提升开发效率。

## ✨ 核心功能

### 1. 多账号管理
- **账号添加**：支持批量导入和管理多个 Cursor 账号
- **账号切换**：一键快速切换不同账号，无需重复登录
- **状态监控**：实时显示每个账号的使用状态和剩余配额

### 2. 智能调度
- **自动轮换**：根据使用频率自动切换账号，避免单账号过度使用
- **负载均衡**：智能分配请求到不同账号，优化资源利用
- **配额管理**：监控并管理每个账号的AI使用配额

### 3. 数据同步
- **配置同步**：同步编辑器设置和偏好到所有账号
- **插件同步**：自动同步安装的插件和扩展
- **工作区同步**：保持工作区配置的一致性

### 4. 安全保护
- **加密存储**：所有账号信息采用AES加密存储
- **Token管理**：安全管理和自动刷新认证令牌
- **访问控制**：支持主密码保护，防止未授权访问

## 🛠️ 技术栈

- **GUI框架**: PySide6 (Qt6 for Python)
- **编程语言**: Python 3.10+
- **自动化控制**: pywinauto / pyautogui
- **数据存储**: SQLite3 + 加密存储
- **网页自动化**: Playwright / Selenium
- **界面设计**: Qt Designer + QSS样式

## 📦 安装使用

### 系统要求
- Windows 10/11 (64位)
- macOS 10.15+
- Linux (Ubuntu 20.04+)
- 已安装 Cursor 编辑器

### 安装步骤

1. **下载安装包**
   ```bash
   # 从GitHub Release页面下载对应系统的安装包
   # Windows: CursorUnlimited-Setup.exe
   # macOS: CursorUnlimited.dmg
   # Linux: CursorUnlimited.AppImage
   ```

2. **运行安装程序**
   - Windows: 双击exe文件运行安装向导
   - macOS: 拖动应用到Applications文件夹
   - Linux: 添加执行权限并运行AppImage

3. **初始配置**
   - 首次启动时设置主密码
   - 添加第一个Cursor账号
   - 配置自动切换规则

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/hj01857655/CursorUnlimited.git
cd CursorUnlimited

# 创建虚拟环境
python -m venv venv
# Windows激活
venv\Scripts\activate
# Linux/Mac激活
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py

# 打包成exe（Windows）
pyinstaller build.spec
```

## 📖 使用指南

### 添加账号
1. 点击主界面的"添加账号"按钮
2. 输入账号邮箱和密码
3. 系统自动验证并保存账号信息

### 切换账号
1. 在账号列表中选择目标账号
2. 点击"激活"按钮
3. Cursor编辑器将自动切换到该账号

### 配置自动切换
1. 进入"设置" > "自动化"
2. 设置切换间隔时间
3. 选择轮换策略（顺序/随机/智能）
4. 启用自动切换功能

## 📁 项目结构

```
CursorUnlimited/
├── src/                       # 源代码目录
│   ├── main.py               # 主程序入口
│   ├── ui/                   # PySide6界面
│   │   ├── main_window.py    # 主窗口
│   │   ├── dialogs/          # 对话框
│   │   ├── widgets/          # 自定义组件
│   │   └── resources/        # UI资源文件
│   ├── automation/           # 自动化模块
│   │   ├── browser/          # 浏览器自动化
│   │   │   ├── base.py      # 基础接口
│   │   │   ├── playwright_driver.py  # Playwright实现
│   │   │   ├── selenium_driver.py    # Selenium实现
│   │   │   ├── drissionpage_driver.py # DrissionPage实现
│   │   │   └── puppeteer_driver.py   # Pyppeteer实现
│   │   ├── desktop/          # 桌面自动化
│   │   │   ├── cursor_control.py     # Cursor控制
│   │   │   ├── pywinauto_driver.py   # pywinauto实现
│   │   │   └── pyautogui_driver.py   # pyautogui实现
│   │   └── account/          # 账号管理
│   │       ├── register.py   # 自动注册
│   │       ├── switch.py     # 账号切换
│   │       └── manager.py    # 账号管理器
│   ├── database/             # 数据库模块
│   │   ├── models.py         # 数据模型
│   │   ├── db_manager.py     # 数据库管理
│   │   └── encryption.py     # 数据加密
│   ├── services/             # 服务层
│   │   ├── email_service.py  # 邮箱服务
│   │   ├── captcha_service.py # 验证码服务
│   │   └── proxy_service.py  # 代理服务
│   └── utils/                # 工具模块
│       ├── config.py         # 配置管理
│       ├── logger.py         # 日志系统
│       └── helpers.py        # 辅助函数
├── config/                   # 配置文件
│   ├── settings.yaml         # 应用配置
│   └── automation.json       # 自动化配置
├── resources/                # 资源文件
│   ├── icons/               # 图标
│   └── styles/              # QSS样式
├── tests/                    # 测试文件
├── docs/                     # 项目文档
├── requirements.txt          # Python依赖
├── build.spec               # PyInstaller配置
├── .gitignore               # Git忽略文件
└── README.md                # 项目说明文档
```

## 🔐 安全说明

- 所有账号密码使用AES-256-GCM加密存储
- 不会收集或上传任何用户数据
- 支持本地导出和备份账号配置
- 建议定期更新软件以获取安全补丁

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建新的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源 - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- **开发者**: hj01857655
- **GitHub**: [https://github.com/hj01857655](https://github.com/hj01857655)

## 🙏 鸣谢

- 感谢 Cursor 团队开发的优秀AI代码编辑器
- 感谢所有贡献者和使用者的支持

## 📞 联系方式

- 项目主页: [https://github.com/hj01857655/CursorUnlimited](https://github.com/hj01857655/CursorUnlimited)
- Issue反馈: [https://github.com/hj01857655/CursorUnlimited/issues](https://github.com/hj01857655/CursorUnlimited/issues)

---

⚠️ **免责声明**: 本工具仅供学习和研究使用，请遵守Cursor的服务条款。使用本工具产生的任何后果由用户自行承担。