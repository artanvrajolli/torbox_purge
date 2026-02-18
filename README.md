# Torbox Purge

<div align="center">
  <img src="images/work_mods.svg" width="600"/>
</div>

## Overview

Torbox Purge is a Python utility designed to automatically manage and clean up stalled or slow torrents and web downloads from your Torbox account using the Torbox API. It periodically checks your active downloads and deletes those that are either stalled for too long or have an excessive estimated time of arrival (ETA), helping you keep your Torbox account organized and efficient.

## Features

- Connects to the Torbox API using your personal API token
- Supports both torrent and web downloads (webdl)
- Identifies downloads that are stalled (e.g., no seeds, missing files, or not progressing) or have an ETA above a configurable threshold
- Automatically deletes stalled downloads at regular intervals
- Configurable file types to monitor (torrent, webdl, or both)
- Logs all actions and errors to both the console and a log file (`torbox_purge.log`)

## Why was this made?

Managing downloads on Torbox can become cumbersome, especially when downloads get stuck or take too long to complete. This tool was created to automate the cleanup process, saving time and ensuring your account remains clutter-free without manual intervention.

## Configuration

Copy `.env.example` to `.env` and fill in your Torbox API token and desired thresholds:

```
API_TOKEN_TORBOX=your_torbox_api_token
ETA_THRESHOLD_TORBOX=86400    # 24 hours in seconds
STALL_THRESHOLD_TORBOX=7200   # 2 hours in seconds
CHECK_INTERVAL_TORBOX=600     # 10 minutes in seconds
FILES_TYPES=torrent,webdl     # Comma-separated list of file types to monitor
```

### Configuration Options

- `API_TOKEN_TORBOX`: Your Torbox API token
- `ETA_THRESHOLD_TORBOX`: Maximum allowed ETA in seconds (default: 24 hours)
- `STALL_THRESHOLD_TORBOX`: Time in seconds after which a stalled download is considered for deletion (default: 2 hours)
- `CHECK_INTERVAL_TORBOX`: How often to check for stalled downloads (default: 10 minutes)
- `FILES_TYPES`: Types of downloads to monitor (comma-separated list of 'torrent' and/or 'webdl')

## Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/torbox_purge.git
   cd torbox_purge
   ```

2. Set up your `.env` file as described above.

3. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. View logs:
   ```bash
   docker-compose logs -f
   ```

5. Stop the container:
   ```bash
   docker-compose down
   ```

### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/torbox_purge.git
   cd torbox_purge
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file as described above.

## Usage

### Using Docker

Run with Docker Compose:
```bash
docker-compose up -d
```

Or build and run manually:
```bash
docker build -t torbox-purge .
docker run -d --name torbox-purge --env-file .env -v $(pwd)/logs:/app/logs torbox-purge
```

### Manual Usage

Run the script:
```bash
python app.py
```

The script will:
1. Immediately perform a cleanup of stalled downloads
2. Continue running at the interval specified in `CHECK_INTERVAL_TORBOX`
3. Log all actions to both console and `logs/torbox_purge.log`

## Logging

All actions and errors are logged to `logs/torbox_purge.log` and printed to the console. The log includes:
- Timestamps for all operations
- Details of deleted downloads
- Any errors or issues encountered
- API response information

When using Docker, logs are persisted to the `logs/` directory on your host machine.

## Requirements

- Python 3.7+
- Docker and Docker Compose (for containerized deployment)
- Torbox API access
- Required Python packages (see `requirements.txt`):
  - requests
  - python-dotenv
  - schedule

## Contributing

Feel free to submit issues and enhancement requests!

