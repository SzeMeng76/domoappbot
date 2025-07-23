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

This is a powerful, multi-functional Telegram bot for price lookups and more, containerized with Docker for easy deployment. Forked from the original [domoxiaojun/domoappbot](https://github.com/domoxiaojun/domoappbot) with significant feature enhancements, bug fixes, and a refactored architecture using MySQL and Redis.

### ✨ Features

-   **💱 Currency Conversion:** Real-time exchange rate lookups.
-   **🎮 Steam Prices:** Query prices for Steam games and bundles across different regions.
-   **📱 App Stores:** Search for iOS, macOS, and iPadOS applications by keyword or directly by App ID, with support for multi-country price comparison.
-   **📺 Streaming Prices:** Check subscription costs for services like Netflix, Disney+, and Spotify.
-   **🔐 Admin System:** A comprehensive, interactive admin panel (`/admin`) to manage user/group whitelists and bot administrators.
-   **🧹 Auto-Cleanup:** Automatically deletes commands and bot replies to keep group chats tidy.
-   **⚙️ Fully Containerized:** The entire application stack (bot, database, cache) is managed with Docker and Docker Compose for a simple, one-command startup.
-   **🚀 Automated Setup:** The database schema is created automatically by the application on its first run, no manual `init.sql` needed.

### 🛠️ Tech Stack

-   **Backend:** Python
-   **Telegram Framework:** `python-telegram-bot`
-   **Database:** MySQL
-   **Cache:** Redis
-   **Deployment:** Docker & Docker Compose
-   **CI/CD:** GitHub Actions for automated Docker image builds and pushes.

### 🚀 Getting Started

Getting the bot up and running is designed to be as simple as possible.

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
    Copy the example file to create your own configuration. The bot will not start without it.
    ```bash
    cp .env.example .env
    ```

3.  **Edit the `.env` file:**
    Open the `.env` file with a text editor and fill in the required values. See the configuration section below for details.

4.  **Run the bot:**
    Start the entire application stack with a single command:
    ```bash
    docker-compose up -d
    ```
    The bot will start, connect to the MySQL and Redis containers, and automatically create the necessary database tables on the first run.

### ⚙️ Configuration

All bot configurations are managed through the `.env` file.

| Variable                    | Description                                                                 | Default/Example         |
| --------------------------- | --------------------------------------------------------------------------- | ----------------------- |
| `BOT_TOKEN`                 | **(Required)** Your Telegram Bot Token from @BotFather.                     |                         |
| `SUPER_ADMIN_ID`            | **(Required)** The User ID of the main bot owner. This user has all permissions. |                         |
| `DB_HOST`                   | The hostname for the database. **Must be `mysql`** to connect to the Docker service. | `mysql`                 |
| `DB_PORT`                   | The internal port for the database.                                         | `3306`                  |
| `DB_NAME`                   | The name of the database. Must match `docker-compose.yml`.                  | `bot`                   |
| `DB_USER`                   | The username for the database. Must match `docker-compose.yml`.             | `bot`                   |
| `DB_PASSWORD`               | **(Required)** The password for the database. Must match `docker-compose.yml`. | `your_mysql_password`   |
| `REDIS_HOST`                | The hostname for the cache. **Must be `redis`**.                          | `redis`                 |
| `DELETE_USER_COMMANDS`      | Set to `true` to enable auto-deletion of user commands.                       | `true`                  |
| `USER_COMMAND_DELETE_DELAY` | Delay in seconds before deleting a user's command. Use `0` for immediate deletion. | `5`                     |
| `DELETE_BOT_RESPONSE_MESSAGE`| Set to `true` to enable auto-deletion of the bot's own replies.              | `true`                  |
| `DELETE_BOT_RESPONSE_DELAY` | Delay in seconds before deleting a bot's reply.                               | `900`                   |


### 🤖 Usage Examples

-   `/help` - Get the full list of commands.
-   `/rate usd cny 100` - Convert 100 US Dollars to Chinese Yuan.
-   `/steam Elden Ring` - Search for the game "Elden Ring" on Steam.
-   `/app id1643375332 us jp` - Look up the price of an app by its ID in the US and Japan stores.
-   `/admin` - Open the interactive admin panel.

### 📖 Architecture & Advanced Usage

#### System Architecture
* **MySQL:** Used for persistent storage of user permissions, whitelists (users and groups), and administrator data.
* **Redis:** Acts as a high-performance cache for price data, exchange rates, and managing the message deletion schedule.
* **Automatic Database Initialization:** The application will automatically create the required database tables on its first startup.

#### Production Recommendations
* Set `DEBUG=false` in your `.env` file for a production environment.
* Configure multiple `EXCHANGE_RATE_API_KEYS` to increase API rate limits.
* Ensure the `logs` directory has write permissions.
* For larger-scale use, consider using managed or separate servers for MySQL and Redis.
* Regularly back up the MySQL database.

#### Further Documentation
* **Project Architecture:** `CLAUDE.md`
* **Docker Deployment:** `docker-compose.yml`
* **Database Schema:** `database/init.sql`

### 🤝 Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](https://github.com/SzeMeng76/domoappbot/issues).

### License
This project is licensed under the MIT License.
