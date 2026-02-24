# 👻 Project Ghost Browser (Windows Native -> Portable)

## 1. Executive Summary
A high-speed, disposable, and anonymous browsing environment. Users interact with a "Ghost Hub" to launch domain-pinned browser sessions running inside isolated Docker containers.

## 2. Core Constraints (Senior Architect Rules)
* **Modular Enforcement:** No single file shall exceed 150 lines.
* **State-First:** Define Data Schema and State logic before any functional code.
* **Error-First:** Every module must include try/except blocks and meaningful logging.
* **Zero-Persistence:** Use tmpfs (RAM-only) mounts for browser profiles.
* **Anti-Hallucination:** Syntax must be verified against official docs.

## 3. Definition of Done (DoD)
- [ ] **The Hub:** A Reflex-based UI showing "Ghost Cards" and a secure Vault.
- [ ] **Vault Security:** AES-256 encryption with Argon2. Default 'admin' creds.
- [ ] **Disposable Sessions:** Containers created with --rm and destroyed on close.
- [ ] **Domain Pinning:** Network traffic restricted to defined target domain.
- [ ] **Performance:** Launch time < 5 seconds.

## 4. Technical Architecture
### A. The Stack
- **Frontend:** Reflex
- **Backend:** FastAPI
- **Container Engine:** Docker Desktop (Windows)
- **Database:** SQLModel (SQLite)

### B. Directory Structure
- /models.py: SQLModel schemas.
- /state.py: Global application state.
- /ui/: Modular UI components.
- /engine/: Docker/Container management.
- /security/: Encryption and hashing.
