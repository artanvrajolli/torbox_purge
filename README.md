# Torbox Purge

## Overview

Torbox Purge is a Python utility designed to automatically manage and clean up stalled or slow torrents from your Torbox account using the Torbox API. It periodically checks your active torrents and deletes those that are either stalled for too long or have an excessive estimated time of arrival (ETA), helping you keep your Torbox account organized and efficient.

## Features

- Connects to the Torbox API using your personal API token.
- Identifies torrents that are stalled (e.g., no seeds, missing files, or not progressing) or have an ETA above a configurable threshold.
- Automatically deletes such torrents at regular intervals.
- Logs all actions and errors to both the console and a log file (`torbox_purge.log`).

## Why was this made?

Managing torrents on Torbox can become cumbersome, especially when torrents get stuck or take too long to complete. This tool was created to automate the cleanup process, saving time and ensuring your account remains clutter-free without manual intervention.

## Configuration

Copy `.env.example` to `.env` and fill in your Torbox API token and desired thresholds:

```
API_TOKEN_TORBOX=your_torbox_api_token
ETA_THRESHOLD_TORBOX=604800  # 7 days in seconds
STALL_THRESHOLD_TORBOX=1800  # 30 minutes in seconds
CHECK_INTERVAL_TORBOX=600    # 10 minutes in seconds
```

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your `.env` file as described above.

## Usage

Run the script:
```
python app.py
```
The script will immediately perform a cleanup and then continue to run at the interval you specify.

## Logging

All actions and errors are logged to `torbox_purge.log` and printed to the console.

## Requirements

- Python 3.7+
- Torbox API access

# torbox_purge
