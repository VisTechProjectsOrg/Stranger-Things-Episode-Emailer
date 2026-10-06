import requests
from datetime import datetime, date
import smtplib
from email.utils import parseaddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import re
import os
import logging
import argparse

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_EP_FILE = os.path.join(SCRIPT_DIR, "latest_episode.json")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config", "config.json")
LOG_FILE = os.path.join(SCRIPT_DIR, "app.log")

def setup_logging(verbose=False):
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO if verbose else logging.ERROR)
    fmt = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(fmt)
    log.addHandler(file_handler)

    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(fmt)
        log.addHandler(console_handler)

    return log

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def send_email(subject, body, email_config, log):
    msg = MIMEMultipart()
    sender = email_config.get("from") or email_config["username"]
    msg["From"] = sender
    msg["To"] = ", ".join(email_config["to"])
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
            # The server's own mail system takes the message as is; a remote one (Gmail)
            # needs TLS and a login, which a password in the config switches on.
            if email_config.get("password"):
                server.starttls()
                server.login(email_config["username"], email_config["password"])
            server.sendmail(parseaddr(sender)[1], email_config["to"], msg.as_string())
    except Exception as e:
        log.error(f"Failed to send email: {e}")
        return False
    return True

def load_previous_episode():
    if os.path.exists(LATEST_EP_FILE):
        with open(LATEST_EP_FILE, "r") as f:
            return json.load(f)
    return None

def save_latest_episode(episode):
    with open(LATEST_EP_FILE, "w") as f:
        json.dump({
            "title": episode["name"],
            "season": episode["season"],
            "episode": episode["number"],
            "airdate": episode["airdate"]
        }, f, indent=2)

def fetch_episodes(log):
    url = "https://api.tvmaze.com/singlesearch/shows?q=stranger+things&embed=episodes"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        log.error(f"Failed to fetch episode data: {e}")
        return None

    today = date.today().isoformat()
    episodes = data.get("_embedded", {}).get("episodes", [])

    if not episodes:
        log.error("No episodes found in API response")
        return None

    aired = [ep for ep in episodes if ep.get("airdate") and ep["airdate"] <= today]

    if not aired:
        log.error("No aired episodes found")
        return None

    for ep in aired:
        summary = ep.get("summary") or "No summary available."
        ep["summary"] = re.sub(r'</?p>', '', summary).strip()

    return sorted(aired, key=lambda ep: (ep["airdate"], ep["season"], ep["number"]))

def get_new_episodes(episodes, previous):
    if not previous:
        # First run - just return latest episode
        return [episodes[-1]]

    new_eps = []
    for ep in episodes:
        if ep["season"] > previous["season"]:
            new_eps.append(ep)
        elif ep["season"] == previous["season"] and ep["number"] > previous["episode"]:
            new_eps.append(ep)
    return new_eps

def build_email_body(new_episodes):
    count = len(new_episodes)
    if count == 1:
        header = "A new episode has entered the Upside Down!"
    else:
        header = f"{count} new episodes have entered the Upside Down!"

    body = f'''<html>
  <body style="font-family: Arial, sans-serif; background-color: #1a1a1a; padding: 20px;">
    <div style="max-width: 600px; background-color: #2d2d2d; padding: 20px; border-radius: 10px; border: 2px solid #ff0000;">
      <h1 style="color: #ff0000;">⚡ Stranger Things Alert!</h1>
      <p style="color: #ffffff;"><strong>{header}</strong></p>
      <hr style="border-top: 1px solid #444;" />
'''

    for ep in new_episodes:
        body += f'''      <p style="color: #ffffff;"><strong>🎬 Title:</strong> {ep["name"]}</p>
      <p style="color: #ffffff;"><strong>🧭 Season:</strong> {ep["season"]}, <strong>Episode:</strong> {ep["number"]}</p>
      <p style="color: #ffffff;"><strong>📆 Airdate:</strong> {ep["airdate"]}</p>
      <p style="color: #ffffff;"><strong>📜 Summary:</strong> {ep["summary"]}</p>
      <hr style="border-top: 1px solid #444;" />
'''

    body += '''    </div>
  </body>
</html>'''
    return body

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='Print output to console')
    args = parser.parse_args()

    log = setup_logging(args.verbose)

    try:
        config = load_config()
    except Exception as e:
        log.error(f"Failed to load config: {e}")
        return

    email_config = config["email"]
    previous_episode = load_previous_episode()
    episodes = fetch_episodes(log)

    if episodes is None:
        return

    new_episodes = get_new_episodes(episodes, previous_episode)

    if not new_episodes:
        log.info("No new episode found")
        print("No new episode found")
        return

    count = len(new_episodes)
    latest = new_episodes[-1]

    if count == 1:
        log.info(f"New episode: S{latest['season']}E{latest['number']} - {latest['name']}")
        print(f"New episode: S{latest['season']}E{latest['number']} - {latest['name']}")
        subject = f"New Stranger Things Episode: S{latest['season']}E{latest['number']}"
    else:
        log.info(f"{count} new episodes, latest: S{latest['season']}E{latest['number']}")
        print(f"{count} new episodes, latest: S{latest['season']}E{latest['number']}")
        subject = f"New Stranger Things Episodes: {count} new episodes!"

    body = build_email_body(new_episodes)

    if send_email(subject, body, email_config, log):
        save_latest_episode(latest)
        log.info("Email sent successfully")
        print("Email sent successfully")

if __name__ == "__main__":
    main()
