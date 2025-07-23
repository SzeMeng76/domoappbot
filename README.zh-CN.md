<div align="right">

用其他语言阅读: [English](./README.md)

</div>

<div align="center">

# DomoAppBot
*一款强大的、多功能的 Telegram 机器人，用于价格查询等功能，并使用 Docker 容器化以便轻松部署。*

</div>

<p align="center">
  <img src="https://github.com/SzeMeng76/domoappbot/actions/workflows/docker-publish.yml/badge.svg" alt="GitHub Actions Workflow Status" />
</p>

### ✨ 功能特性

-   **💱 汇率转换:** 实时汇率查询。
-   **🎮 Steam 价格:** 查询 Steam 游戏和捆绑包在不同地区的价格。
-   **📱 应用商店:** 通过关键词或 App ID 直接搜索 iOS、macOS 和 iPadOS 应用。
-   **📺 流媒体价格:** 查看 Netflix、Disney+、Spotify 等服务的订阅费用。
-   **🔐 管理系统:** 功能完善的管理面板，用于管理用户和群组的白名单。
-   **🧹 自动清理:** 自动删除命令和机器人回复，以保持群聊整洁。
-   **⚙️ 容器化:** 整个应用（机器人、数据库、缓存）都由 Docker 和 Docker Compose 管理，只需一条命令即可启动。

### 🛠️ 技术栈

-   **后端:** Python
-   **Telegram 框架:** `python-telegram-bot`
-   **数据库:** MySQL
-   **缓存:** Redis
-   **部署:** Docker & Docker Compose
-   **持续集成/部署:** GitHub Actions

### 🚀 快速开始

按照以下步骤来启动和运行机器人。

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
    ```bash
    cp .env.example .env
    ```

3.  **编辑 `.env` 文件:**
    打开 `.env` 文件并填入你的信息，尤其是 `BOT_TOKEN`, `SUPER_ADMIN_ID`, 和 `DB_PASSWORD`。

4.  **运行机器人:**
    ```bash
    docker-compose up -d
    ```
    机器人将会启动，并且在首次运行时，程序会自动在 MySQL 数据库中创建所需的表。

### ⚙️ 配置

所有的机器人配置都通过 `.env` 文件管理。以下是一些关键变量：

| 变量                        | 描述                                                                    | 默认值/示例             |
| --------------------------- | ----------------------------------------------------------------------- | ----------------------- |
| `BOT_TOKEN`                 | **(必需)** 你的 Telegram Bot Token。                                    |                         |
| `SUPER_ADMIN_ID`            | **(必需)** 主要机器人所有者的用户ID。                                   |                         |
| `DB_HOST`                   | 数据库的主机名。**应为 `mysql`** 以连接到 Docker 服务。                   | `mysql`                 |
| `DB_PORT`                   | 数据库的内部端口。                                                      | `3306`                  |
| `DB_NAME`                   | 数据库名称。必须与 `docker-compose.yml` 中的设置一致。                  | `bot`                   |
| `DB_USER`                   | 数据库用户名。必须与 `docker-compose.yml` 中的设置一致。                | `bot`                   |
| `DB_PASSWORD`               | **(必需)** 数据库密码。必须与 `docker-compose.yml` 中的设置一致。       | `your_mysql_password`   |
| `REDIS_HOST`                | 缓存的主机名。**应为 `redis`**。                                        | `redis`                 |
| `DELETE_USER_COMMANDS`      | 设置为 `true` 以启用用户命令的自动删除。                                  | `true`                  |
| `USER_COMMAND_DELETE_DELAY` | 删除用户命令前的延迟（秒）。**必须大于 0**。                        | `5`                     |

### 🤖 使用示例

-   `/help` - 获取完整的命令列表。
-   `/rate usd cny 100` - 转换100美元为人民币。
-   `/steam Elden Ring` - 在 Steam 上搜索游戏 "Elden Ring"。
-   `/app id1643375332 us` - 通过 App ID 查询应用价格。
-   `/admin` - 打开交互式管理面板。

### 🤝 贡献

欢迎提交贡献、问题和功能请求。请随时查看 [Issues 页面](https://github.com/SzeMeng76/domoappbot/issues)。
