# Stranger Things Episode Emailer

A Python script that checks for new Stranger Things episodes and sends email notifications when new episodes air.

## Features

- Fetches episode data from the TVMaze API
- Tracks the last notified episode to avoid duplicate alerts
- Sends styled HTML emails with episode details
- Supports multiple email recipients

## Requirements

- Python 3.6+
- `requests` library

```bash
pip install requests
```

## Setup

1. Copy `config/config.sample.json` to `config/config.json`
2. Fill in your email credentials and recipient addresses
3. Run the script:

```bash
python stranger_things_ep_email.py
```

Use `-v` or `--verbose` for console output:

```bash
python stranger_things_ep_email.py -v
```

## Configuration

Edit `config/config.json` with your SMTP settings:

- `smtp_server`: Your email provider's SMTP server
- `smtp_port`: SMTP port (typically 587 for TLS)
- `username`: Your email address
- `password`: Your email password or app-specific password
- `to`: Array of recipient email addresses

## Automation

Set up a cron job or scheduled task to run the script periodically:

```bash
# Example: Check daily at 9 AM
0 9 * * * /usr/bin/python3 /path/to/stranger_things_ep_email.py
```

## Example Email

<table>
  <tr>
    <td style="background-color: #1a1a1a; padding: 20px;">
      <table style="max-width: 600px; background-color: #2d2d2d; padding: 20px; border-radius: 10px; border: 2px solid #ff0000;">
        <tr>
          <td>
            <h1 style="color: #ff0000;">⚡ Stranger Things Alert!</h1>
            <p style="color: #ffffff;"><strong>A new episode has entered the Upside Down!</strong></p>
            <hr style="border-top: 1px solid #444;" />
            <p style="color: #ffffff;"><strong>🎬 Title:</strong> Chapter One: The Vanishing of Will Byers</p>
            <p style="color: #ffffff;"><strong>🧭 Season:</strong> 1, <strong>Episode:</strong> 1</p>
            <p style="color: #ffffff;"><strong>📆 Airdate:</strong> 2016-07-15</p>
            <p style="color: #ffffff;"><strong>📜 Summary:</strong> On his way home from a friend's house, young Will sees something terrifying. Nearby, a sinister secret lurks in the depths of a government lab.</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>

## Files

- `stranger_things_ep_email.py` - Main script
- `config/config.json` - Email and API configuration
- `latest_episode.json` - Tracks the last notified episode (auto-generated)
- `app.log` - Error log file (auto-generated)
