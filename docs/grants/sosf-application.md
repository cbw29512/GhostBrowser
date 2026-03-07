\# GitHub Secure Open Source Fund — Session 4 Application Record



\*\*Application Code:\*\* GH-SOSF-2026-S4  

\*\*Status:\*\* Submitted March 2026  

\*\*Fund:\*\* GitHub Secure Open Source Fund (Session 4)  

\*\*Application URL:\*\* https://docs.google.com/forms/d/e/1FAIpQLScDBalom0XhmJrvyI3kwD7dZ-dD4\_uhmLNysVXtA8fH\_WUKoA/viewform  

\*\*Application Type:\*\* General  

\*\*Deadline:\*\* Rolling — no need to reapply for future sessions  

\*\*Funding:\*\* $10,000 cash + $10,000 Azure credits (up to $150,000 Azure via Microsoft for Startups)  

\*\*AI Disclosure:\*\* Drafted with assistance from Claude Sonnet 4 (Anthropic), March 7, 2026



---



\## Applicant



| Field | Value |

|---|---|

| Name | Chris Wilson |

| GitHub | @cbw29512 |

| Email | GhostBrowserProject@proton.me |

| City | Florence, SC, USA |

| Referred By | N/A |

| Full-time OSS | No |

| Funding Received | None ($0) |



---



\## Application Fields



\### What is your project?



GhostBrowser is an open-source ephemeral secure browsing environment — a privacy and security tool, not a browser itself. Built on Docker and Kasm container runtime, it delivers isolated browser sessions that leave zero traces on the host system after close.



Core capabilities:

\- Encrypted credential vault — secrets never touch disk in plaintext

\- Per-domain URL pinning via Chrome's --host-rules flag — prevents session leakage to unintended domains

\- Per-tile ad-blocking toggles — user-controlled, per-session

\- RAM-first storage — session artifacts exist only in memory and are destroyed on container exit

\- Clean-slate container provisioning — each session starts from a verified base image



GhostBrowser is designed for journalists, researchers, privacy-conscious users, and anyone operating in environments where browser artifact forensics pose a real threat. MIT licensed, 100% Python.



\### Repository URL

https://github.com/cbw29512/GhostBrowser



\### License

MIT



\### Core team size

1



\### Role

Sole maintainer, architect, and lead developer.



\### Other maintainers

None.



\### Security Training



Yes. Actively studying for CISSP certification. Operates a home SOC (NetGuard) using Wazuh SIEM and Suricata IDS with custom Python threat intelligence pipelines ingesting 35,000+ known malicious IPs, DNS/TLS/SNI monitoring, and AI alert triage. 30+ years hands-on systems, networking, and security infrastructure experience.



\### Security Understanding Level

High



\### External Impact if Security Issue



Container isolation failure could expose user identities, leak credentials from the encrypted vault, persist session artifacts to disk defeating the core privacy guarantee, or in worst case allow full host system compromise via container escape. Users of ephemeral browser tools often operate in high-risk contexts — a false sense of security is worse than no tool.



\### CVEs / Reported Vulnerabilities



None. No formal CVE disclosure process established yet — an explicit gap the program would help address.



\### Positive Impact of Security Improvements on Ecosystem



\- Documented container escape mitigations applicable to any Docker/Kasm-based isolation project

\- Formal threat model for ephemeral browser environments

\- Published CVE disclosure process establishing norms for this tool category

\- Verified RAM-only storage implementation others can audit

\- Security CI/CD automation demonstrating reproducible security validation



\### Funding Strategy



Two active grant applications:

\- NLnet NGI Zero Commons Fund — €40,000, submitted March 2026 (Code: 2026-04-0eb)

\- OTF Internet Freedom Fund — $55,000, submitted March 2026 (Code: IFF-2026-03)



No funding received to date.



\### How Funding Helps Security Outcomes



1\. Formal security audit of container isolation layer and credential vault

2\. Signed release verification (GPG-signed releases, reproducible builds)

3\. Formal CVE disclosure process and security policy documentation

4\. Security CI/CD automation — automated container security scanning per commit

5\. Threat model documentation covering container escape, vault encryption, RAM-storage verification



Azure credits fund CI/CD security regression testing infrastructure.



\### Underrepresented in Tech



Yes. 50+ year old independent developer from rural Florence, South Carolina — geographically and demographically underrepresented in open-source security tooling, which skews toward urban tech hubs and academic institutions. Career built entirely outside startup and academic pathways.



\### Project URLs



\- Website: https://cbw29512.github.io/GhostBrowser/

\- Repository: https://github.com/cbw29512/GhostBrowser

\- Email: GhostBrowserProject@proton.me



---



\## Grant Pipeline Status



| # | Grant | Amount | Deadline | Status |

|---|-------|--------|----------|--------|

| 1 | NLnet NGI Zero Commons Fund | €40,000 | April 1, 2026 | ✅ Submitted (2026-04-0eb) |

| 2 | OTF Internet Freedom Fund | $55,000 | Rolling | ✅ Submitted (IFF-2026-03) |

| 3 | GitHub Secure Open Source Fund | $10K + $10K Azure | Rolling | ✅ Submitted (GH-SOSF-2026-S4) |

| 4 | OTF FOSS Sustainability Fund | $150K–$400K | Rolling | ⏳ Apply 2028 (not yet eligible) |

| 5 | Mozilla Fellowship | TBD | Jan 2027 cycle | 🔲 Future |

| 6 | NSF Safe-OSE | TBD | Requires university affiliation | 🔲 Future/partnership |



