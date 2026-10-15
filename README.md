# Cloud-Native SSH Honeypot & Threat Intelligence Detection Engine

A cloud-based detection and deception platform deployed on AWS EC2. It exposes a medium-interaction Cowrie honeypot on default port 22 while migrating administrative SSH access to an alternative port with key-pair authentication. A daemonized Python engine ingests telemetry in real time, runs IP geolocation enrichment, and dispatches structured security alerts to a Security Operations Discord channel.

##  Architecture Overview

1. **Host Hardening:** Native OpenSSH service relocated to port 2222 with strict key-pair authentication.
2. **Deception Layer:** Cowrie honeypot deployed inside an isolated Docker container binding port 22.
3. **Log Ingestion & Parsing:** Telemetry parsed in real time (`cowrie.log`) capturing session handshakes, auth attempts, and shell commands.
4. **Threat Enrichment:** Geolocation and ISP resolution via external IP intelligence API with localized memory caching.
5. **Alerting Pipeline:** Automated webhook notifications delivered via Discord embeds through a systemd daemon.

##  Tech Stack

- **Cloud Provider:** Amazon Web Services (AWS EC2 - Ubuntu 24.04 LTS)
- **Containerization:** Docker & Docker Compose
- **Honeypot Framework:** Cowrie (Medium-Interaction SSH/Telnet)
- **Monitoring & Automation:** Python 3 (Requests, Re)
- **Process Management:** Linux systemd

##  Deployment Guide

### 1. Administrative Port Migration
Update `/etc/ssh/sshd_config`:
```bash
Port 2222
