<div align="center">

# DomoAppBot
*A powerful, multi-functional Telegram bot for price lookups and more, containerized with Docker for easy deployment.*

</div>

<p align="center">
  <a href="#-english">English</a> •
  <a href="#-简体中文">简体中文</a>
</p>

<p align="center">
  <img src="https://github.com/SzeMeng76/domoappbot/actions/workflows/docker-publish.yml/badge.svg" alt="GitHub Actions Workflow Status" />
</p>

---
## 🇬🇧 English

A powerful, multi-functional Telegram bot for price lookups and more, containerized with Docker for easy deployment. Forked from [domoxiaojun/domoappbot](https://github.com/domoxiaojun/domoappbot) with added features and fixes.

### ✨ Features

-   **💱 Currency Conversion:** Real-time exchange rate lookups.
-   **🎮 Steam Prices:** Query prices for Steam games and bundles across different regions.
-   **📱 App Stores:** Search for iOS, macOS, and iPadOS applications by keyword or directly by App ID.
-   **📺 Streaming Prices:** Check subscription costs for services like Netflix, Disney+, and Spotify.
-   **🔐 Admin System:** A comprehensive admin panel to manage user and group whitelists.
-   **🧹 Auto-Cleanup:** Automatically deletes commands and bot replies to keep group chats tidy.
-   **⚙️ Containerized:** The entire application stack (bot, database, cache) is managed with Docker and Docker Compose for a simple, one-command startup.

### 🛠️ Tech Stack

-   **Backend:** Python
-   **Telegram Framework:** `python-telegram-bot`
-   **Database:** MySQL
-   **Cache:** Redis
-   **Deployment:** Docker & Docker Compose
-   **CI/CD:** GitHub Actions

### 🚀 Getting Started

Getting the bot up and running is simple.

#### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)
-   A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

#### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/SzeMeng76/domoappbot.git](https://github.com/SzeMeng76/domoappbot.git)
    cd domoappbot
    ```

2.  **Create your configuration file:**
    Copy the example file to create your own configuration.
    ```bash
    cp .env.example .env
    ```

3.  **Edit the `.env` file:**
    Open the `.env` file with a text editor and fill in the required values. At a minimum, you must set:
    -   `BOT_TOKEN`: Your token from @BotFather.
    -   `SUPER_ADMIN_ID`: Your numeric Telegram User ID. You can get this by messaging `@userinfobot`.
    -   `DB_PASSWORD`: A secure password of your choice for the MySQL database.

4.  **Run the bot:**
    Start the entire application stack with a single command:
    ```bash
    docker-compose up -d
    ```
    The application code will automatically create the necessary tables in the MySQL database on the first run.

### ⚙️ Configuration

All bot configurations are managed through the `.env` file. Here are some of the key variables:

| Variable                    | Description                                                                 | Default/Example         |
| --------------------------- | --------------------------------------------------------------------------- | ----------------------- |
| `BOT_TOKEN`                 | **(Required)** Your Telegram Bot Token.                                     |                         |
| `SUPER_ADMIN_ID`            | **(Required)** The User ID of the main bot owner.                             |                         |
| `DB_HOST`                   | The hostname for the database. **Should be `mysql`** to connect to the Docker service. | `mysql`                 |
| `DB_PASSWORD`               | **(Required)** The password for the database user.                          | `your_mysql_password`   |
| `REDIS_HOST`                | The hostname for the cache. **Should be `redis`**.                          | `redis`                 |
| `DELETE_USER_COMMANDS`      | Set to `true` to enable auto-deletion of user commands.                       | `true`                  |
| `USER_COMMAND_DELETE_DELAY` | Delay in seconds before deleting a user's command. **Must be > 0**.     | `5`                     |

### 🤖 Usage Examples

-   `/help` - Get the full list of commands.
-   `/rate usd cny 100` - Convert 100 US Dollars to Chinese Yuan.
-   `/steam Elden Ring` - Search for the game "Elden Ring" on Steam.
-   `/app id1643375332 us` - Look up the price of the app with ID `1643375332` in the US store.
-   `/admin` - Open the interactive admin panel.

### 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/SzeMeng76/domoappbot/issues).

---
## 🇨🇳 简体中文

一款强大的、多功能的 Telegram 机器人，用于价格查询等功能，并使用 Docker 容器化以便轻松部署。派生自 [domoxiaojun/domoappbot](https://github.com/domoxiaojun/domoappbot)，并增加了新功能和错误修复。

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

启动和运行机器人非常简单。

#### 环境要求

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)
-   一个从 [@BotFather](https://t.me/BotFather) 获取的 Telegram Bot Token。

#### 安装与设置

1.  **克隆仓库:**
    ```bash
    git clone [https://github.com/SzeMeng76/domoappbot.git](https://github.com/SzeMeng76/domoappbot.git)
    cd domoappbot
    ```

2.  **创建你的配置文件:**
    从示例文件复制一份你自己的配置。
    ```bash
    cp .env.example .env
    ```

3.  **编辑 `.env` 文件:**
    用你喜欢的文本编辑器打开 `.env` 文件并填入必要的值。至少需要设置：
    -   `BOT_TOKEN`: 从 @BotFather 获取的机器人 Token。
    -   `SUPER_ADMIN_ID`: 你自己的数字版 Telegram User ID。可以给 `@userinfobot` 发消息获取。
    -   `DB_PASSWORD`: 为你的 MySQL 数据库设置一个安全的密码。

4.  **运行机器人:**
    使用一条命令启动整个应用：
    ```bash
    docker-compose up -d
    ```
    机器人将会启动，并且在首次运行时，程序代码会自动在 MySQL 数据库中创建所需的表。

### ⚙️ 配置

所有的机器人配置都通过 `.env` 文件管理。以下是一些关键变量：

| 变量                        | 描述                                                                    | 默认值/示例             |
| --------------------------- | ----------------------------------------------------------------------- | ----------------------- |
| `BOT_TOKEN`                 | **(必需)** 你的 Telegram Bot Token。                                    |                         |
| `SUPER_ADMIN_ID`            | **(必需)** 主要机器人所有者的用户ID。                                   |                         |
| `DB_HOST`                   | 数据库的主机名。**应为 `mysql`** 以连接到 Docker 服务。                   | `mysql`                 |
| `DB_PASSWORD`               | **(必需)** 数据库用户的密码。                                           | `your_mysql_password`   |
| `REDIS_HOST`                | 缓存的主机名。**应为 `redis`**。                                        | `redis`                 |
| `DELETE_USER_COMMANDS`      | 设置为 `true` 以启用用户命令的自动删除。                                  | `true`                  |
| `USER_COMMAND_DELETE_DELAY` | 删除用户命令前的延迟（秒）。**必须大于 0**。                        | `5`                     |

### 🤖 使用示例

-   `/help` - 获取完整的命令列表。
-   `/rate usd cny 100` - 转换100美元为人民币。
-   `/steam Elden Ring` - 在 Steam 上搜索游戏 "Elden Ring"。
-   `/app id1643375332 us` - 在美区查询 App ID 为 `1643375332` 的应用价格。
-   `/admin` - 打开交互式管理面板。

### 🤝 贡献

欢迎提交贡献、问题和功能请求。请随时查看 [Issues 页面](https://github.com/SzeMeng76/domoappbot/issues)。
