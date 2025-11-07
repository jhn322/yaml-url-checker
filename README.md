# YAML URL Checker

This script scans YAML configuration files in a specified directory (intended for Kometa config files but can be used for anything else) for Trakt, IMDb and Letterboxd list URLs and checks if they are accessible (returns a 2xx status code). It logs results with proper rotation, prints a summary to the console, and optionally sends a summary of dead links to a Discord webhook.

## Features

- Scans `.yml` and `.yaml` files in a configured directory.
- Recursively finds URLs matching Trakt, IMDb and Letterboxd patterns within YAML values.
- Checks URL accessibility using HEAD requests (following redirects).
- Configurable delay between requests to avoid rate-limiting.
- Configurable request timeout.
- Advanced logging system with:
  - Automatic log rotation (5MB per file, up to 3 files)
  - Timestamp and log level information
  - Both console and file output
  - Structured log format
- Sends a notification with a summary of **dead links only** to a Discord webhook if configured.
- Uses a virtual environment to manage dependencies.
- Configuration via environment variables (`.env` file).
- Proper error handling and reporting.
- URL exclusion list support.

## Prerequisites

- Python 3 (Tested with 3.10+, includes `venv`)
- `pip` (Python package installer)
- `git` (for cloning the repository)
- (Optional, for Linux/macOS) `dos2unix` if transferring files from Windows to fix line endings.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/jhn322/yaml-url-checker.git
    cd yaml-url-checker
    ```

2.  **(If needed) Fix Line Endings:** If you copied/edited the script on Windows and are running it on Linux/macOS, you might encounter errors like `/usr/bin/env: 'python3': No such file or directory`. Fix this using `dos2unix`:

    ```bash
    # Install if needed (Debian/Ubuntu): sudo apt update && sudo apt install dos2unix
    dos2unix yaml_url_checker.py
    ```

3.  **Create and Activate Virtual Environment:** It's highly recommended to use a virtual environment to isolate dependencies.

    ```bash
    # Create the virtual environment directory (.venv)
    python3 -m venv .venv

    # Activate the virtual environment (Linux/macOS)
    source .venv/bin/activate
    # Activate the virtual environment (Windows Git Bash/PowerShell)
    # .venv/Scripts/activate
    ```

    Your terminal prompt should change to indicate the active environment (e.g., '(.venv) user@host:...').

4.  **Install Dependencies:** Install the required Python packages into the active virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Configuration is managed via environment variables, typically loaded from a `.env` file in the project root.

1.  **Create `.env` file:** Copy the example file:

    ```bash
    cp .env.example .env
    ```

2.  **Edit `.env` file:** Open the `.env` file in a text editor and add your specific configuration.

    ```dotenv
    # REQUIRED: Your Discord webhook URL for notifications
    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url/here

    # --- OPTIONAL Overrides ---
    # Directory containing Kometa .yml/.yaml config files to scan
    # CONFIG_DIR=/path/to/your/kometa/config

    # Delay in seconds between checking each URL
    # REQUEST_DELAY_SECONDS=1

    # Timeout in seconds for each URL check request
    # REQUEST_TIMEOUT_SECONDS=10

    # Custom User-Agent string for HTTP requests
    # USER_AGENT=MyCustomChecker/1.0
    ```

    - **`DISCORD_WEBHOOK_URL` is required** if you want Discord notifications. Find this in your Discord channel's Integrations settings.
    - Other variables override the defaults set in `yaml_url_checker.py` if provided.

    **Important Note on Default Paths:** The script `yaml_url_checker.py` contains default paths for `CONFIG_DIR` (e.g., `/home/username/...`). If you are **not** overriding these variables in your `.env` file, you **must** edit the path in `yaml_url_checker.py` directly to match your system's configuration. Using the `.env` file to set these paths is the recommended approach.

## Usage

### Manual Execution

Ensure you are in the project directory (`yaml-url-checker`) and the virtual environment is activated (`source .venv/bin/activate`).

```bash
python yaml_url_checker.py
```

The script will:

- Print progress to the console
- Log to rotating log files in the `logs` directory
- Send a Discord notification if dead links are found and a webhook URL is configured

### Log Files

Logs are stored in the `logs` directory with the following structure:

- `yaml_url_checker.log` (current log file)
- `yaml_url_checker.log.1` (first backup)
- `yaml_url_checker.log.2` (second backup)

Log files are automatically rotated when they reach 5MB, with a maximum of 3 files maintained.

### Scheduled Execution (Cron Job - Linux/macOS)

To run the script automatically (e.g., daily), you can set up a cron job.

1.  **Edit the system crontab:**

    ```bash
    sudo nano /etc/crontab
    ```

2.  **Add the following line** at the end of the file, adjusting paths and schedule as needed:

    ```crontab
    # Run dead link checker daily at 3:00 AM
    0 3 * * * root cd /home/username/yaml-url-checker && /home/username/yaml-url-checker/.venv/bin/python3 /home/username/yaml-url-checker/yaml_url_checker.py
    ```

    **Explanation of the cron line:**

    - `0 3 * * *`: Run at 3:00 AM every day. (Minute Hour DayOfMonth Month DayOfWeek)
    - `root`: The user to run the command as.
    - `cd /home/username/yaml-url-checker`: **Crucial:** Change to the script's directory so it can find the `.env` file and relative paths. **Adjust this path** to match your installation location.
    - `&&`: Run the next command only if `cd` is successful.
    - `/home/username/yaml-url-checker/.venv/bin/python3`: **Crucial:** Execute using the Python interpreter **inside the virtual environment**. Adjust the path if your project or venv location differs.
    - `/home/username/yaml-url-checker/yaml_url_checker.py`: The full path to the script. Adjust if needed.

3.  **Save and close** the editor (e.g., `Ctrl+X`, then `Y`, then `Enter` in nano). Cron will automatically pick up the changes.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'dotenv'` (or similar):** Make sure you have activated the virtual environment (`source .venv/bin/activate`) before running `pip install` or `python yaml_url_checker.py`. If running via cron, ensure the crontab entry uses the python executable from the `.venv` directory.
- **`/usr/bin/env: 'python3': No such file or directory`:** This indicates Windows line endings (`
`) in the script file when running on Linux/macOS. Use `dos2unix yaml_url_checker.py` to convert line endings to Unix format (`
`).
- **Permission Errors (Cron):** Ensure the user running the cron job (`root` in the example) has read permissions for the script, the `.env` file, the config directory, and write permissions for the `logs` directory.
- **Discord Notification Errors:** Double-check the `DISCORD_WEBHOOK_URL` in your `.env` file. Check the logs for specific error messages from the `requests` library.
- **Log File Issues:** If you encounter problems with log files:
  - Ensure the `logs` directory exists and is writable
  - Check that the script has permissions to create and write to log files
  - Verify that there's enough disk space for log rotation
