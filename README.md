# YAML URL Checker

This tool scans YAML configuration files (primarily for Kometa) for URLs (Trakt, IMDb, Letterboxd) and checks their accessibility. It logs results, and sends a summary of dead links to your Discord webhook, so you can keep track of broken links in your Kometa config and replace them.

## Features

- **Dockerized:** easy deployment with Docker Compose.
- **Scheduled:** built-in scheduler (no system cron needed).
- **Scans:** `.yml` and `.yaml` files recursively.
- **Checks:** Trakt, IMDb, and Letterboxd URLs using HEAD requests.
- **Notifies:** Sends dead link summaries to Discord.
- **Logs:** detailed rotating logs.

## 🚀 Quick Start (Docker)

This is the recommended way to run the checker alongside Kometa.

### 1. Configure

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit the `.env` file:

- `HOST_CONFIG_DIR`: The path to your Kometa directory where your YAML files are stored on your host machine.
- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL.
- `TZ`: Your timezone (e.g., `Europe/Stockholm`).
- `CRON_SCHEDULE`: Schedule (default is `0 3 * * *` - 3 AM daily).

### 2. Run

Start the container:

```bash
docker compose up -d
```

That's it! The container will run in the background and check your URLs on the configured schedule.

### 3. Check Logs

To see what the checker is doing open the /logs folder or run:

```bash
docker compose logs -f
```

## 🛠️ Manual Installation (Python Script)

If you prefer to run the script directly on your host without Docker, follow these steps.

### Prerequisites

- Python 3.10+
- `pip`
- `git`

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/jhn322/yaml-url-checker.git
    cd yaml-url-checker
    ```

2.  **Set up Virtual Environment:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv/Scripts/activate   # Windows
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure:**
    Copy `.env.example` to `.env` and fill in your details.

5.  **Run:**
    ```bash
    python yaml_url_checker.py
    ```

### Scheduled Execution (Cron)

To run on a schedule without Docker, add a cron job:

```bash
0 3 * * * root cd /path/to/yaml-url-checker && /path/to/yaml-url-checker/.venv/bin/python3 scheduler.py
```

_(Or use the original `yaml_url_checker.py` if you have your own cron logic)._
