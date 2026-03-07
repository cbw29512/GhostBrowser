# NLnet Grant Application — Ghost Browser
**Application Code:** 2026-04-0eb  
**Fund:** NGI Zero Commons Fund  
**Submitted:** March 2026  
**Status:** Submitted — Pending Review  

---

## Contact Information

| Field | Value |
|-------|-------|
| Name | Christopher Brian Wilson |
| Email | GhostBrowserProject@proton.me |
| Organisation | Independent / Open Source |
| Country | United States |
| Website | https://cbw29512.github.io/GhostBrowser/ |
| Repository | https://github.com/cbw29512/GhostBrowser |

---

## Project Information

**Project Name:** Ghost Browser: Ephemeral Secure Browsing Environment  
**Requested Amount:** €40,000  
**Fund:** NGI Zero Commons Fund  

---

## Abstract

Ghost Browser is an open-source ephemeral browsing environment that runs each session inside a disposable Docker/Kasm container. When the session ends, the container is destroyed, the encrypted credential vault is wiped, and no persistent artifacts remain on the host system. Every session starts clean and leaves nothing behind.

The core architecture stacks three isolation layers: (1) a Python-orchestrated Docker/Kasm container runtime that is spawned fresh per session and destroyed on exit; (2) an encrypted per-session credential vault with per-domain pinning via Chrome's --host-rules flag; and (3) per-tile ad-blocking controls that scope outbound traffic at the container level. The result is a browsing environment where persistence is not a default — it is an explicit, opt-in decision.

Ghost Browser is not designed as a daily-use consumer browser. It is a research and experimentation platform for the security community — a transparent, open-source foundation that security architects, privacy researchers, and developers can study, extend, and build upon.

---

## Expected Outcomes

- A fully functional open-source ephemeral browser prototype with documented session lifecycle
- Published architecture documentation covering the isolation model, threat model, and teardown mechanisms
- An encrypted credential vault implementation with per-domain pinning and session-scoped storage
- Per-tile ad-blocking and traffic scoping controls integrated into the container runtime
- A RAM-first storage prototype that keeps session data in volatile memory rather than disk
- Developer documentation, setup guides, and a published security model for community review
- A transparent research platform the community can fork, audit, and extend

---

## Applicant Experience

Chris Wilson is a security-focused systems engineer with 5+ years of professional IT experience and 30+ years of hands-on independent work in systems, networking, and security infrastructure. He is currently studying for CISSP certification and operates a home SOC using Wazuh and Suricata IDS for network security monitoring and has built and deployed multiple open-source security tools including NetGuard SOC — a modular Python-based network threat intelligence platform with Suricata IDS, InfluxDB, and an Ollama AI pipeline. He brings deep practical experience in containerization, Python systems development, network security architecture, and open-source project management to Ghost Browser.

---

## Budget Breakdown

| Task | Hours | Rate | Total |
|------|-------|------|-------|
| Container runtime & session lifecycle implementation | 160 hrs | €45/hr | €7,200 |
| Encrypted credential vault with per-domain pinning | 120 hrs | €45/hr | €5,400 |
| RAM-first storage architecture & artifact cleanup | 100 hrs | €45/hr | €4,500 |
| Per-tile ad-blocking & traffic scoping layer | 80 hrs | €45/hr | €3,600 |
| Security model documentation & threat modelling | 80 hrs | €45/hr | €3,600 |
| Testing, security review & hardening | 120 hrs | €45/hr | €5,400 |
| Developer documentation, setup guides & tutorials | 80 hrs | €45/hr | €3,600 |
| Community engagement, code review & maintenance | 60 hrs | €45/hr | €2,700 |
| Infrastructure, tooling & project overhead | — | — | €4,000 |
| **TOTAL** | **800 hrs** | | **€40,000** |

No other funding sources, past or present.

---

## Comparison with Existing Projects

Several existing projects address adjacent problems, but none combine Ghost Browser's specific combination of simplicity, container-native ephemeral sessions, and transparent open-source architecture:

- **Tor Browser:** Addresses network-level anonymity but does not provide container-level host isolation or ephemeral session teardown.
- **Tails OS:** Provides a full ephemeral OS environment but requires dedicated hardware or a bootable USB and is not suitable for quick, ad hoc isolated sessions on an existing workstation.
- **Whonix:** Uses a dual-VM architecture for strong isolation but requires significant system resources and virtualization overhead inaccessible to most users.
- **Browser extensions:** Firefox Multi-Account Containers and uMatrix provide cookie and tracker isolation within a persistent browser but do not eliminate host-level persistence or provide session teardown guarantees.

---

## Technical Challenges

- **Guaranteed artifact elimination:** Ensuring that all session artifacts — including browser cache, cookies, DNS cache, and RAM-resident data — are reliably purged at teardown across different host operating systems and container runtimes.
- **Credential vault security:** Designing a per-session encrypted vault that is cryptographically isolated, provides per-domain access controls, and is guaranteed to be wiped on session exit even in the event of unexpected process termination.
- **RAM-first storage:** Implementing a practical RAM-first session storage model that prevents disk writes without significantly impacting browsing performance or usability.
- **Portable execution:** Designing the architecture to be portable across Linux, Windows (WSL2/Docker Desktop), and macOS without compromising the isolation guarantees.
- **Usability balance:** Maintaining a usable, responsive browsing experience within a containerized runtime while enforcing strict artifact minimization constraints.

---

## Ecosystem Engagement

- All source code, documentation, and architecture decisions will be published openly on GitHub under the MIT license from day one of the grant period.
- Architecture and security model documentation will be published as structured markdown in the repository, targeting security researchers and developers who want to audit, critique, or extend the design.
- Progress updates will be shared publicly via the project GitHub repository and the project showcase website (cbw29512.github.io/GhostBrowser/).
- The project will actively solicit community security review and bug reports through GitHub Issues, and will respond to all substantive feedback.
- Deliverables will be designed to be reusable building blocks — the credential vault, session teardown engine, and container orchestration layer are each independently useful to other privacy-focused projects.
- Ghost Browser will reach out to relevant communities including the Tor Project, Privacy Guides, and security research forums to present findings and invite collaboration.

---

## Project Timeline (10 Months)

| Period | Deliverables |
|--------|-------------|
| Months 1–2 | Architecture documentation, container runtime design, Docker/Kasm integration prototype, session lifecycle specification. |
| Months 3–4 | Prototype ephemeral session launcher, basic session teardown and artifact cleanup engine, per-tile ad-blocking layer. |
| Months 5–6 | Encrypted credential vault v1 with per-domain pinning, Chrome --host-rules integration, security model documentation. |
| Months 7–8 | RAM-first storage prototype, advanced artifact minimisation, cross-platform testing (Linux, WSL2). |
| Months 9–10 | Security hardening, full developer documentation, public release, community outreach and feedback integration. |

---

## Open Source Commitment

Ghost Browser is and will remain fully open source under the MIT license. The repository is publicly accessible at github.com/cbw29512/GhostBrowser. All code, documentation, security model documentation, architecture decisions, and development discussions are conducted in public. The project actively welcomes community review, security analysis, and contributions.

All outputs produced with NLnet grant funding will be published under the MIT license and made permanently available in the public repository. No proprietary forks or closed derivatives will be created from grant-funded work.

---

## Generative AI Disclosure

**Model used:** Claude Sonnet 4 (Anthropic), via claude.ai  
**Date:** March 7, 2026  

**Used for:**
1. Extracting project information from the GitHub repository
2. Identifying all required NLnet form fields from the application page
3. Drafting and structuring the full proposal document based on an existing draft written by the applicant, the applicant's background information provided in conversation, and the NLnet form requirements

All technical architecture descriptions, budget figures, timeline, and project details were reviewed, verified, and approved by the applicant. The applicant's original draft formed the foundation of the submission. AI was used as a drafting and structuring tool, not as the source of technical content.

---

## PGP Public Key

```
-----BEGIN PGP PUBLIC KEY BLOCK-----
xjMEaaxJnBYJKwYBBAHaRw8BAQdAysAJrmLTsF68DYsP2iFQgOpuIjpXHTfy
7LUV7ZMiSyzNPUdob3N0QnJvd3NlclByb2plY3RAcHJvdG9uLm1lIDxHaG9z
dEJyb3dzZXJQcm9qZWN0QHByb3Rvbi5tZT7CwBEEExYKAIMFgmmsSZwDCwkH
CRB10osX/DY+j0UUAAAAAAAcACBzYWx0QG5vdGF0aW9ucy5vcGVucGdwanMu
b3JnJmdYXeOmxwL/tOvsdxa7SnfD/9PmKf+idlhxd7BZ/JcDFQoIBBYAAgEC
GQECmwMCHgEWIQTKFSHOTjKjHLldD0R10osX/DY+jwAAgboA/i8vVxe/qVFR
cjFdjX2A7LKZdp5WtQObj100am3SxZQnAP9kTglgzUlCv8L6z/bRzcT3tbKJ
3zlKULyT+Qv18/xTAc44BGmsSZwSCisGAQQBl1UBBQEBB0BwdDI8TmTW+w5I
42K3FXVyCjEvyGzhRhvCN7oQAOjkYgMBCAfCvgQYFgoAcAWCaaxJnAkQddKL
F/w2Po9FFAAAAAAAHAAgc2FsdEBub3RhdGlvbnMub3BlbnBncGpzLm9yZ0ns
xnupXM3Vh12zAxRtK1z4vQjMNgYWZ04AUpufNYuuApsMFiEEyhUhzk4yoxy5
XQ9EddKLF/w2Po8AAL1TAQCb+HkKiFl6JfNchViPJioWoQdbsQSLbgyd2vVE
Y7tD3QEA9sLDpjIM6k2LeuXG7JyH4KcIDSBF/D+Pu6JUje0PVw8=
=rd2c
-----END PGP PUBLIC KEY BLOCK-----
```