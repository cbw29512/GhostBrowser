# Ghost Browser Hub
**Secure. Isolated. Ephemeral.**

A Zero-Trust dashboard built with Reflex and Docker. It provisions isolated Linux environments in RAM for single-site browsing sessions.

## 🛡️ Security Architecture
* **Admin Verification:** Salted and hashed PBKDF2-SHA256 credentials.
* **Ephemeral Containers:** Sessions run in Docker containers that are forcefully purged from RAM and disk upon exit.
* **Isolated Networking:** Containers are routed through a secure IPv4 loopback (127.0.0.1).
* **Encrypted Vault:** Personal Identifiable Information (PII) is AES-128 encrypted at rest.

## 🚀 Getting Started (Dev Mode)
1. **Activate Environment:** .\venv\Scripts\Activate.ps1
2. **Launch Hub:** eflex run
3. **First Time Setup:** Create your Master Admin account on the initialization screen.

## 🔐 Troubleshooting SSL Blocks
If the iframe shows a "Connection not private" error:
1. Click **Pop Out Window**.
2. Click the background of the warning page.
3. Type 	hisisunsafe on your keyboard.
4. Close the tab and relaunch from the Hub.
