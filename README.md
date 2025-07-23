<div align="right">

Read this in other languages: [简体中文](./README.zh-CN.md)

</div>

<div align="center">

# DomoAppBot
*A powerful, multi-functional Telegram bot for price lookups and more, containerized with Docker for easy deployment.*

</div>

<p align="center">
  <img src="https://github.com/SzeMeng76/domoappbot/actions/workflows/docker-publish.yml/badge.svg" alt="GitHub Actions Workflow Status" />
</p>

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

Follow these steps to get the bot up and running.

#### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
-   A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

#### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/SzeMeng76/domoappbot.git](https://github.com/SzeMeng76/domoappbot.git)
    cd domoappbot
    ```

2.  **Create your configuration file:**
    ```bash
    cp .env.example .env
    ```

3.  **Edit the `.env` file:**
    Open the `.env` file and fill in your details, especially `BOT_TOKEN`, `SUPER_ADMIN_ID`, and `DB_PASSWORD`.

4.  **Run the bot:**
    ```bash
    docker-compose up -d
    ```
    The bot will start, and the database schema will be created automatically on the first run.

### ⚙️ Configuration

All bot configurations are managed through the `.env` file. Here are the key variables:

| Variable                    | Description                                                                 | Default/Example         |
| --------------------------- | --------------------------------------------------------------------------- | ----------------------- |
| `BOT_TOKEN`                 | **(Required)** Your Telegram Bot Token from @BotFather.                     |                         |
| `SUPER_ADMIN_ID`            | **(Required)** The User ID of the main bot owner.                             |                         |
| `DB_HOST`                   | The hostname for the database. **Should be `mysql`** to connect to the Docker service. | `mysql`                 |
| `DB_PORT`                   | The internal port for the database.                                         | `3306`                  |
| `DB_NAME`                   | The name of the database. Must match `docker-compose.yml`.                  | `bot`                   |
| `DB_USER`                   | The username for the database. Must match `docker-compose.yml`.             | `bot`                   |
| `DB_PASSWORD`               | **(Required)** The password for the database. Must match `docker-compose.yml`. | `your_mysql_password`   |
| `REDIS_HOST`                | The hostname for the cache. **Should be `redis`**.                          | `redis`                 |
| `DELETE_USER_COMMANDS`      | Set to `true` to enable auto-deletion of user commands.                       | `true`                  |
| `USER_COMMAND_DELETE_DELAY` | Delay in seconds before deleting a user's command. **Must be > 0**.     | `5`                     |

### 🤖 Usage Examples

-   `/help` - Get the full list of commands.
-   `/rate usd cny 100` - Convert 100 US Dollars to Chinese Yuan.
-   `/steam Elden Ring` - Search for the game "Elden Ring" on Steam.
-   `/app id1643375332 us` - Look up the price of an app by its ID.
-   `/admin` - Open the interactive admin panel.

### 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/SzeMeng76/domoappbot/issues).
