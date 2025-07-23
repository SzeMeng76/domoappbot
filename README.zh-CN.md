<div align="right">

Read this in other languages: [English](./README.md)

</div>

<div align="center">

# DomoAppBot
*一款强大的、多功能的 Telegram 机器人，用于价格查询等功能，并使用 Docker 容器化以便轻松部署。*

</div>

<p align="center">
  <img src="https://github.com/SzeMeng76/domoappbot/actions/workflows/docker-publish.yml/badge.svg" alt="GitHub Actions Workflow Status" />
</p>

这是一款强大的、多功能的 Telegram 机器人，用于价格查询等功能，并通过 Docker 容器化以便轻松部署。派生自 [domoxiaojun/domoappbot](https://github.com/domoxiaojun/domoappbot) 的原始版本，并增加了大量新功能、错误修复，以及使用 MySQL 和 Redis 的重构架构。

### ✨ 功能特性

-   **💱 汇率转换:** 实时汇率查询。
-   **🎮 Steam 价格:** 查询 Steam 游戏和捆绑包在不同地区的价格。
-   **📱 应用商店:** 通过关键词或 App ID 直接搜索 iOS、macOS 和 iPadOS 应用，并支持多国价格对比。
-   **📺 流媒体价格:** 查看 Netflix、Disney+、Spotify 等服务的订阅费用。
-   **🔐 管理系统:** 功能完善的、交互式的管理面板 (`/admin`)，用于管理用户/群组白名单和机器人管理员。
-   **🧹 自动清理:** 自动删除用户命令和机器人回复，以保持群聊整洁。
-   **⚙️ 完全容器化:** 整个应用（机器人、数据库、缓存）都由 Docker 和 Docker Compose 管理，只需一条命令即可启动。
-   **🚀 自动化设置:** 数据库表结构由程序在首次运行时自动创建，无需手动准备 `init.sql` 文件。

### 🛠️ 技术栈

-   **后端:** Python
-   **Telegram 框架:** `python-telegram-bot`
-   **数据库:** MySQL
-   **缓存:** Redis
-   **部署:** Docker & Docker Compose
-   **持续集成/部署:** GitHub Actions

### 🚀 快速开始

启动和运行机器人非常简单。

#### 环境要求

-   [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)
-   一个从 [@BotFather](https://t.me/BotFather) 获取的 Telegram Bot Token。

#### 安装与设置

1.  **克隆仓库:**
    ```bash
    git clone [https://github.com/SzeMeng76/domoappbot.git](https://github.com/SzeMeng76/domoappbot.git)
    cd domoappbot
    ```

2.  **创建你的配置文件:**
    从示例文件复制一份你自己的配置，这是机器人启动的必需文件。
    ```bash
    cp .env.example .env
    ```

3.  **编辑 `.env` 文件:**
    用你喜欢的文本编辑器打开 `.env` 文件并填入必要的值。详情请参考下方的配置说明。

4.  **运行机器人:**
    使用一条命令启动整个应用：
    ```bash
    docker-compose up -d
    ```
    机器人将会启动，连接到 MySQL 和 Redis 容器，并在首次运行时自动创建所需的数据库表。

### ⚙️ 配置

所有的机器人配置都通过 `.env` 文件管理。

| 变量                        | 描述                                                                    | 默认值/示例             |
| --------------------------- | ----------------------------------------------------------------------- | ----------------------- |
| `BOT_TOKEN`                 | **(必需)** 你的 Telegram Bot Token。                                    |                         |
| `SUPER_ADMIN_ID`            | **(必需)** 主要机器人所有者的用户ID，拥有所有权限。                      |                         |
| `DB_HOST`                   | 数据库的主机名。**必须为 `mysql`** 以连接到 Docker 服务。                 | `mysql`                 |
| `DB_PORT`                   | 数据库的内部端口。                                                      | `3306`                  |
| `DB_NAME`                   | 数据库名称。必须与 `docker-compose.yml` 中的设置一致。                  | `bot`                   |
| `DB_USER`                   | 数据库用户名。必须与 `docker-compose.yml` 中的设置一致。                | `bot`                   |
| `DB_PASSWORD`               | **(必需)** 数据库密码。必须与 `docker-compose.yml` 中的设置一致。       | `your_mysql_password`   |
| `REDIS_HOST`                | 缓存的主机名。**必须为 `redis`**。                                        | `redis`                 |
| `DELETE_USER_COMMANDS`      | 设置为 `true` 以启用用户命令的自动删除。                                  | `true`                  |
| `USER_COMMAND_DELETE_DELAY` | 删除用户命令前的延迟（秒）。使用 `0` 表示立即删除。                 | `5`                     |
| `DELETE_BOT_RESPONSE_MESSAGE`| 设置为 `true` 以启用机器人回复的自动删除。                               | `true`                  |
| `DELETE_BOT_RESPONSE_DELAY` | 删除机器人回复前的延迟（秒）。                                          | `900`                   |

### 🤖 使用示例

-   `/help` - 获取完整的命令列表。
-   `/rate usd cny 100` - 转换100美元为人民币。
-   `/steam Elden Ring` - 在 Steam 上搜索游戏 "Elden Ring"。
-   `/app id1643375332 us jp` - 在美区和日区查询指定 App ID 的应用价格。
-   `/admin` - 打开交互式管理面板。

### 📖 架构与高级用法

#### 系统架构
* **MySQL：** 用于存储用户权限、白名单、管理员等持久化数据。
* **Redis：** 用于缓存价格数据、汇率数据，并管理消息删除调度，提高性能。
* **自动数据库初始化：** 程序首次运行时会自动在数据库中创建必要的表结构。

#### 生产环境建议
* 在 `.env` 文件中设置 `DEBUG=false`。
* 配置多个 `EXCHANGE_RATE_API_KEYS` 以提高汇率查询的 API 限制。
* 确保 `logs` 目录具有写入权限。
* 对于大规模使用，建议使用独立的 MySQL 和 Redis 服务器。
* 定期备份 MySQL 数据库。

#### 更多文档
* **项目架构：** `CLAUDE.md`
* **Docker部署：** `docker-compose.yml`
* **数据库结构：** `database/init.sql`

### 🤝 贡献

欢迎提交贡献、问题和功能请求。请随时查看 [Issues 页面](https://github.com/SzeMeng76/domoappbot/issues)。

### 许可证
本项目采用 MIT 许可证。
