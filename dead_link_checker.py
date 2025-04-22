#!/usr/bin/env python3

import os
import yaml
import requests
import time
import glob
import re
from typing import Any, List, Tuple, Iterator
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

CONFIG_DIR = os.getenv("CONFIG_DIR", "/home/username/Docker/containers/Kometa/config/") # Adjust this path to match your installation location
LOG_FILE = os.getenv("LOG_FILE", "/home/username/dead-link-checker/dead_link_checker.log") # Adjust this path to match your installation location
REQUEST_DELAY_SECONDS = int(os.getenv("REQUEST_DELAY_SECONDS", 1))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 10))
USER_AGENT = os.getenv("USER_AGENT", "KometaLinkChecker/1.0 (+https://github.com/jhn322/dead-link-checker)")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Regex to identify potential Trakt and Letterboxd list URLs
# Adjust these patterns if your URLs have different structures
# Allows digits or slugs for Trakt lists, ignores query params, allows optional trailing slash for Letterboxd
TRAKT_LIST_PATTERN = r"https?://trakt\.tv/users/[^/]+/lists/(\d+|[a-zA-Z0-9-]+)(\?.*)?$"
LETTERBOXD_LIST_PATTERN = r"https?://letterboxd\.com/[^/]+/list/[^/]+/?$"
URL_PATTERNS = [
    re.compile(TRAKT_LIST_PATTERN),
    re.compile(LETTERBOXD_LIST_PATTERN),
]
# --- End Configuration ---

def find_urls_in_value(data: Any) -> Iterator[str]:
    """Recursively searches for strings matching URL patterns in YAML data."""
    if isinstance(data, str):
        for pattern in URL_PATTERNS:
            if pattern.fullmatch(data):
                yield data
                break # No need to check other patterns if one matches
    elif isinstance(data, list):
        for item in data:
            yield from find_urls_in_value(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            # Optionally check keys too, though less common for URLs
            # yield from find_urls_in_value(key)
            yield from find_urls_in_value(value)

def check_url(url: str) -> Tuple[bool, str]:
    """Checks if a URL is accessible via a HEAD request.

    Returns:
        Tuple[bool, str]: (is_ok, status_message)
                          is_ok is True if status is 2xx, False otherwise.
                          status_message contains details (status code or error).
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.head(
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers=headers,
            allow_redirects=True # Follow redirects to get the final status
        )
        # Consider any 2xx status code as OK
        if 200 <= response.status_code < 300:
            return True, f"OK ({response.status_code})"
        else:
            return False, f"Failed ({response.status_code} {response.reason})"
    except requests.exceptions.Timeout:
        return False, "Failed (Timeout)"
    except requests.exceptions.RequestException as e:
        # Catching other potential issues like connection errors, DNS errors
        error_type = type(e).__name__
        return False, f"Failed ({error_type})"
    except Exception as e:
        # Catch unexpected errors
        return False, f"Failed (Unexpected Error: {e})"

def send_to_discord(webhook_url: str, message: str):
    """Sends a message to the specified Discord webhook."""
    if not webhook_url:
        print("  Discord webhook URL not configured. Skipping notification.")
        return

    # Discord message limits (adjust if needed)
    max_length = 1950
    if len(message) > max_length:
        message = message[:max_length] + "... (message truncated)"

    payload = {"content": message}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        print("  Successfully sent notification to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"  Error sending Discord notification: {e}")
    except Exception as e:
        print(f"  An unexpected error occurred during Discord notification: {e}")

def main():
    """Main function to find YAML files, parse them, check URLs, and notify."""
    print(f"Starting dead link check in: {CONFIG_DIR}")
    if LOG_FILE:
        print(f"Logging results to: {LOG_FILE}")

    # Find both .yml and .yaml files
    yaml_files = glob.glob(os.path.join(CONFIG_DIR, "*.yml"))
    yaml_files.extend(glob.glob(os.path.join(CONFIG_DIR, "*.yaml")))

    if not yaml_files:
        print(f"Error: No YAML files found in {CONFIG_DIR}")
        return

    dead_links_found: List[Tuple[str, str, str]] = []
    checked_urls = set() # Keep track of checked URLs to avoid duplicates per run

    for filepath in yaml_files:
        filename = os.path.basename(filepath)
        print(f"Processing: {filename}...")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Use safe_load to avoid potential security risks with arbitrary code execution
                data = yaml.safe_load(f)
                if data is None: # Handle empty files
                    continue

            urls_to_check = set()
            for url in find_urls_in_value(data):
                if url not in checked_urls:
                    urls_to_check.add(url)
                    checked_urls.add(url) # Mark as planned to check

            for url in urls_to_check:
                print(f"  Checking: {url}...")
                is_ok, status = check_url(url)
                if not is_ok:
                    print(f"  DEAD LINK DETECTED: {url} - Status: {status}")
                    dead_links_found.append((filename, url, status))
                else:
                    # Optional: Log successful checks for debugging
                    # print(f"  OK: {url} - Status: {status}")
                    pass

                # Delay between requests
                time.sleep(REQUEST_DELAY_SECONDS)

        except yaml.YAMLError as e:
            print(f"  Error parsing YAML file {filename}: {e}")
        except FileNotFoundError:
            print(f"  Error: File not found {filename} (should not happen with glob)")
        except Exception as e:
            print(f"  An unexpected error occurred processing {filename}: {e}")

    print("-" * 30)
    print("Dead Link Check Summary:")
    if dead_links_found:
        summary_title = f"Found {len(dead_links_found)} dead link(s) during scan:"
        print(summary_title)
        output_lines = []
        discord_message_lines = [summary_title]
        for filename, url, status in dead_links_found:
            line = f"  - File: {filename}, URL: {url}, Status: {status}"
            print(line)
            discord_message_lines.append(f"- File: `{filename}`, URL: <{url}>, Status: {status}")
            if LOG_FILE:
                output_lines.append(line)

        # Send to Discord
        if DISCORD_WEBHOOK_URL:
            discord_message = "\n".join(discord_message_lines)
            send_to_discord(DISCORD_WEBHOOK_URL, discord_message)

        # Log to file
        if LOG_FILE:
            try:
                with open(LOG_FILE, 'a', encoding='utf-8') as log_f:
                    log_f.write(f"--- Check run on {time.ctime()} ---\\n")
                    log_f.write(f"Found {len(dead_links_found)} dead link(s):\\n")
                    for line in output_lines:
                        log_f.write(line + "\\n")
                    log_f.write("-" * 20 + "\\n")
            except Exception as e:
                print(f"Error writing to log file {LOG_FILE}: {e}")

    else:
        print("No dead links found.")
        if LOG_FILE:
             try:
                with open(LOG_FILE, 'a', encoding='utf-8') as log_f:
                    log_f.write(f"--- Check run on {time.ctime()} - No dead links found ---\\n")
             except Exception as e:
                print(f"Error writing to log file {LOG_FILE}: {e}")

    print("Check finished.")


if __name__ == "__main__":
    main() 