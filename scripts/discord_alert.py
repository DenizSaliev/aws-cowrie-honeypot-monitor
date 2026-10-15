import os
import re
import time
import requests

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "TU_WEBHOOK_AQUI")
LOG_FILE = os.getenv("COWRIE_LOG_PATH", "/home/ubuntu/cowrie-data/logs/cowrie.log")

geo_cache = {}

def get_geoip_info(ip):
    if ip.startswith(("10.", "192.168.", "172.")) or ip == "127.0.0.1":
        return "Internal / RFC1918 Network"
    if ip in geo_cache:
        return geo_cache[ip]
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org"
        res = requests.get(url, timeout=3).json()
        if res.get("status") == "success":
            country = res.get("country", "Unknown")
            city = res.get("city", "Unknown")
            isp = res.get("org") or res.get("isp", "Unknown")
            info = f"{city}, {country} ({isp})"
            geo_cache[ip] = info
            return info
    except Exception:
        pass
    return "Location unavailable"

def send_discord_alert(title, description, color=0xff0000):
    payload = {
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color
            }
        ]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] Error sending notification: {e}")

def monitor():
    print("[*] Starting Cowrie honeypot log monitor...")
    send_discord_alert("🛡️ Cowrie Honeypot Monitor", "Service successfully initialized on AWS EC2.", 0x00ff00)
    last_ip = "Unknown"

    with open(LOG_FILE, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            if "New connection:" in line:
                ip_match = re.search(r"New connection: ([\d\.]+):", line)
                if ip_match:
                    last_ip = ip_match.group(1)
                    geo = get_geoip_info(last_ip)
                    send_discord_alert(
                        "🚨 Inbound Connection Detected",
                        f"**Source IP:** `{last_ip}`\n**Geolocation:** {geo}\n**Timestamp:** `{line[:19]}`",
                        0xffa500
                    )

            elif "login attempt" in line:
                cred_match = re.search(r"login attempt \[(.*?)\] (succeeded|failed)", line)
                if cred_match:
                    creds = cred_match.group(1)
                    status = cred_match.group(2)
                    color = 0x2ecc71 if status == "succeeded" else 0xe74c3c
                    icon = "🔓" if status == "succeeded" else "❌"
                    geo = get_geoip_info(last_ip)
                    send_discord_alert(
                        f"{icon} Authentication Attempt ({status.upper()})",
                        f"**Credentials:** `{creds}`\n**Source IP:** `{last_ip}`\n**Location:** {geo}",
                        color
                    )

            elif "CMD:" in line:
                cmd_match = re.search(r"CMD:\s*(.*)", line)
                if cmd_match:
                    command = cmd_match.group(1).strip()
                    geo = get_geoip_info(last_ip)
                    send_discord_alert(
                        "💻 Emulated Shell Command Executed",
                        f"**Command:**\n```{command}```\n**Source IP:** `{last_ip}` ({geo})",
                        0x9b59b6
                    )

if __name__ == "__main__":
    monitor()
