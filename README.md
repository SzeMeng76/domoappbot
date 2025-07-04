# 🤖 多功能Telegram价格查询机器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)

一个功能强大的Telegram机器人，支持汇率查询、Steam游戏价格、流媒体订阅价格、应用商店价格查询等多种功能，具备完整的权限管理和智能消息管理系统。

## ✨ 核心功能

| 功能模块 | 描述 | 主要命令 |
|---------|------|---------|
| 💱 **汇率查询** | 实时汇率查询，支持100+种货币和数学表达式计算 | `/rate USD`, `/rate 100*1.2 EUR` |
| 🎮 **Steam游戏** | 全球游戏价格对比，支持游戏、捆绑包和综合搜索 | `/steam`, `/steamb`, `/steams` |
| 📺 **流媒体服务** | Netflix、Disney+、Spotify等服务的全球价格对比 | `/nf`, `/ds`, `/sp` |
| 📱 **应用商店** | App Store和Google Play应用价格查询 | `/app`, `/gp` |
| 🍎 **Apple服务** | iCloud、Apple One、Apple Music全球定价查询 | `/aps` |
| 🔧 **系统管理** | 三级权限管理、白名单控制、智能消息折叠 | `/admin`, `/add`, `/tasks` |
| 📋 **自动化管理** | 日志归档、缓存清理、定时任务调度 | `/logs`, `/cleancache` |

## 🚀 快速开始

> 💡 **完整部署指南**: 详细步骤请参考 [docs/deployment/QUICK_START.md](./docs/deployment/QUICK_START.md)

### 1. 克隆和安装
```bash
git clone <repository-url>
cd bot
pip install -r requirements.txt
```

### 2. 基本配置
```bash
# 创建配置文件
cp .env.example .env

# 编辑配置文件，添加必要信息
# BOT_TOKEN=your_bot_token_here
# SUPER_ADMIN_ID=your_telegram_user_id
```

### 3. 运行机器人
```bash
python main.py
```

### 4. 验证部署
发送 `/start` 命令到机器人验证是否正常运行。

## 📖 使用示例

### 基础查询
```
/rate USD        # 查询美元汇率
/steam 原神      # 查询Steam游戏价格
/nf             # Netflix全球价格对比
/app YouTube    # App Store应用价格
```

### 高级功能
```
/rate 100*1.2 EUR    # 数学表达式计算
/steams indie        # Steam综合搜索
/aps iCloud         # Apple服务价格
/admin              # 管理员面板
```

## 📚 详细文档

| 文档类型 | 描述 | 链接 |
|---------|------|------|
| 🚀 **快速部署** | 详细的安装配置步骤 | [QUICK_START.md](./docs/deployment/QUICK_START.md) |
| 👤 **用户手册** | 完整功能说明和使用示例 | [USER_MANUAL.md](./docs/user-guide/USER_MANUAL.md) |
| 🔧 **管理员指南** | 权限管理和系统配置 | [ADMIN_MANUAL.md](./docs/admin-guide/ADMIN_MANUAL.md) |
| ⚙️ **配置指南** | 详细的配置选项说明 | [CONFIG_GUIDE.md](./docs/configuration/CONFIG_GUIDE.md) |
| 💻 **开发文档** | 代码结构和扩展指南 | [DEVELOPMENT.md](./docs/development/DEVELOPMENT.md) |
| 🛠️ **维护手册** | 系统维护和故障排除 | [MAINTENANCE.md](./docs/maintenance/MAINTENANCE.md) |
| 📁 **项目结构** | 详细的目录和文件说明 | [PROJECT_STRUCTURE.md](./docs/development/PROJECT_STRUCTURE.md) |

> 📋 **完整文档索引**: [docs/README.md](./docs/README.md)

## 💬 智能消息管理

### 🔄 自动消息折叠
- **智能判断**: 超过设定行数自动折叠为spoiler格式
- **可配置阈值**: 通过 `FOLDING_THRESHOLD` 调整（默认15行）
- **保持格式**: 完整保留Markdown格式
- **一键展开**: 点击即可查看完整内容

### ⏱️ 自动删除机制
- **定时删除**: 机器人回复和用户命令可配置删除时间
- **保持整洁**: 避免群聊被机器人消息刷屏
- **灵活配置**: 支持不同类型消息设置不同延迟

```env
FOLDING_THRESHOLD=15        # 超过15行自动折叠
AUTO_DELETE_DELAY=180       # 机器人消息3分钟后删除
DELETE_USER_COMMANDS=true   # 删除用户命令
```

## 🛠️ 核心特性

### 🔒 安全性
- ✅ **三级权限控制** - 用户/管理员/超级管理员
- ✅ **白名单机制** - 用户和群组访问控制
- ✅ **安全表达式解析** - 防止代码注入攻击
- ✅ **输入验证过滤** - 全面的数据校验
- ✅ **自动消息清理** - 防止信息泄露

### ⚡ 性能优化
- ✅ **智能缓存系统** - 多层缓存策略，减少API调用
- ✅ **异步处理架构** - 支持高并发，响应速度快
- ✅ **内存优化管理** - 支持长期运行，自动会话清理
- ✅ **数据库连接池** - SQLite优化配置
- ✅ **定时任务调度** - 自动清理和维护机制

### 🎯 用户体验
- ✅ **智能消息折叠** - 基于行数的自动折叠，提升阅读体验
- ✅ **企业级稳定性** - 支持7x24小时稳定运行
- ✅ **完善监控告警** - 系统状态实时监控
- ✅ **自动日志轮转** - 归档压缩，节省存储空间

## 🏗️ 技术架构

```
├── 核心系统
│   ├── Python 3.8+ (异步架构)
│   ├── SQLite (数据存储)
│   ├── Telegram Bot API
│   └── 模块化设计
├── 功能模块
│   ├── 汇率查询服务
│   ├── Steam价格服务
│   ├── 流媒体价格服务
│   ├── 应用商店服务
│   └── Apple服务查询
└── 管理系统
    ├── 权限管理
    ├── 缓存管理
    ├── 任务调度
    └── 日志管理
```

## 🤝 贡献与支持

### 💡 参与贡献
我们欢迎任何形式的贡献！

- 🐛 **报告Bug**: 在 [Issues](../../issues) 中提交问题
- 💡 **功能建议**: 提出新功能想法和改进建议
- 🔧 **代码贡献**: 提交 Pull Request
- 📖 **文档改进**: 帮助完善和翻译文档

### 📞 获取帮助

如果遇到问题，请按以下顺序寻求帮助：

1. 📖 **查看文档** - [docs/](./docs/) 目录包含详细说明
2. 🔍 **搜索问题** - 查看 [故障排除指南](./docs/troubleshooting/TROUBLESHOOTING.md)
3. 🐛 **提交Issue** - 在 [GitHub Issues](../../issues) 报告问题
4. 💬 **讨论交流** - 参与项目讨论

### 📋 问题反馈模板

提交Issue时请包含以下信息：
- Python版本和操作系统
- 机器人版本和配置信息
- 错误日志和复现步骤
- 预期行为和实际行为描述

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

**🚀 让价格对比变得简单高效！**
