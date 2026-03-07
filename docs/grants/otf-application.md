\# OTF Internet Freedom Fund — Concept Note — Ghost Browser

\*\*Application Code:\*\* IFF-2026-03  

\*\*Fund:\*\* Internet Freedom Fund — Technical Development  

\*\*Submitted:\*\* March 2026  

\*\*Status:\*\* Submitted — Pending Review  

\*\*Expected Response:\*\* 6–8 weeks after submission  



---



\## Contact Information



| Field | Value |

|-------|-------|

| Name | Christopher Wilson |

| Email | GhostBrowserProject@proton.me |

| Applying as | Individual / Independent Developer |

| Location | United States |

| Repository | https://github.com/cbw29512/GhostBrowser |

| Website | https://cbw29512.github.io/GhostBrowser/ |



---



\## Project Title



GHOST BROWSER: Ephemeral Secure Browsing Environment



---



\## Project Description (1–3 Sentences)



Our project is to build Ghost Browser — an open-source ephemeral browsing environment — in order to address the challenge of persistent host-system artifacts that expose journalists, activists, and human rights defenders to surveillance and forensic compromise. Each session runs inside a disposable Docker container that is destroyed completely on exit, leaving no cookies, cache, credentials, or traces on the host machine. The primary beneficiaries are at-risk users in repressive environments who need a fast, accessible, and verifiably clean browsing session without requiring dedicated hardware or a full alternative OS.



---



\## What Problem Will This Project Address?



Journalists, human rights defenders, activists, and dissidents operating in repressive environments face a specific and underappreciated threat: the persistent data footprint left behind by standard web browsers. Even when privacy features like incognito mode are enabled, modern browsers leave significant artifacts on the host system — cookies, DNS cache entries, browsing history fragments, locally cached content, session tokens, and log files. These artifacts can be recovered by adversaries with physical or remote access to the device.



This is not a theoretical threat. Forensic analysis of devices belonging to journalists and activists has repeatedly revealed browsing artifacts that exposed sources, communications, and operational patterns. Tools like Cellebrite and commercial forensic software are widely deployed by state actors and are capable of recovering browser artifacts even after standard deletion. In authoritarian contexts — including but not limited to China, Iran, Russia, Belarus, and Myanmar — device seizure at borders, checkpoints, or during detention is a documented and routine occurrence.



The problem is compounded by the gap between the threat model and available solutions. Existing ephemeral solutions either require significant technical expertise (Tails OS, Whonix), dedicated hardware (bootable USB drives), or substantial system resources (dual-VM architectures). The result is that the users who most need clean, ephemeral browsing — frontline journalists, local activists, human rights documenters — are the least likely to have access to tools that provide it.



Ghost Browser directly addresses this gap: a lightweight, container-native ephemeral browsing session that any user with Docker installed can launch in seconds on their existing workstation, with strong guarantees that the session leaves no recoverable artifacts on the host machine.



---



\## Project Form



\*\*Technology Development\*\*



---



\## Overview of Project Activities



\*\*Objective 1: Core Container Runtime (Months 1–2)\*\*

\- Implement Docker/Kasm container orchestration layer in Python

\- Build session spawn and teardown lifecycle engine

\- Implement guaranteed artifact cleanup on session exit

\- Deliverable: Functional ephemeral session launcher with verified teardown



\*\*Objective 2: Encrypted Credential Vault (Months 3–4)\*\*

\- Build per-session encrypted credential vault with AES-256 encryption

\- Implement per-domain credential pinning via Chrome --host-rules flag

\- Ensure vault wipe on session exit, including abnormal termination

\- Deliverable: Credential vault that stores per-domain credentials in-session only, cryptographically wiped at teardown



\*\*Objective 3: Traffic Controls \& Privacy Hardening (Months 5–6)\*\*

\- Implement per-tile ad-blocking and tracker-blocking controls

\- Build RAM-first storage prototype to prevent disk writes during session

\- Cross-platform testing across Linux and Windows WSL2

\- Deliverable: Full privacy-hardened session with RAM-first storage and granular traffic controls



\*\*Objective 4: Documentation, Security Review \& Release (Months 7–8)\*\*

\- Publish full architecture and threat model documentation

\- Conduct community security review via GitHub Issues and outreach to security researchers

\- Publish developer setup guides and end-user documentation

\- Public release and outreach to at-risk user communities via Privacy Guides, Tor Project, and journalist security networks

\- Deliverable: Public release v1.0 with full documentation, security model, and community outreach completed



---



\## Similar Projects \& How Ghost Browser Is Different



Ghost Browser occupies a distinct niche that no existing tool fully addresses:



\- \*\*Tor Browser:\*\* Does not provide container-level host isolation or ephemeral session teardown. Network-level anonymity and host-level artifact elimination are separate, complementary problems.

\- \*\*Tails OS:\*\* Provides a full ephemeral OS but requires a dedicated bootable USB device. Not suitable for ad-hoc sessions on an existing workstation — a significant barrier for frontline users who cannot modify their devices.

\- \*\*Whonix:\*\* Provides strong dual-VM isolation but requires substantial system resources and technical setup. Not accessible to most at-risk users without significant technical support.

\- \*\*Firefox Multi-Account Containers:\*\* Provides cookie and tracker isolation within a persistent browser but makes no host-level artifact elimination guarantees.

\- \*\*Ghost Browser (commercial):\*\* A commercial product that is not open source, not auditable, and focused on multi-account management rather than ephemeral session teardown.



Ghost Browser is complementary to Tor Browser — the two can be combined, with Ghost Browser providing host-level artifact elimination and Tor providing network-level anonymity. Collaboration with the Tor Project and Privacy Guides communities is a planned outcome of the project.



---



\## Estimated Duration



\*\*6 months to 1 year\*\* (8 months planned)



---



\## Estimated Funding



\*\*$55,000 USD\*\*



Covers 8 months of full-time independent development at approximately $6,500/month plus infrastructure costs for testing environments, security tooling, and documentation hosting. No administrative overhead, no organisational costs, no marketing spend. May be revised at full proposal stage.



---



\## Who Would Benefit?



\*\*Primary Beneficiaries — At-Risk Users in Repressive Environments:\*\*



\- Journalists and investigative reporters in authoritarian contexts (China, Iran, Russia, Belarus, Myanmar) who access sensitive sources or documentation via the web and face device seizure at borders, checkpoints, or detention

\- Human rights defenders and documenters who access evidence of abuses, communicate with witnesses, or coordinate with international organisations — and whose devices may be subject to forensic analysis

\- Civil society activists and political dissidents who face targeted surveillance by state actors and need browsing sessions that leave no recoverable trace

\- Whistleblowers and sources who need to access or transmit sensitive information without leaving host-system artifacts that could be used to identify them



\*\*Secondary Beneficiaries:\*\*



\- Security researchers and developers who need isolated environments for investigating malicious URLs, phishing infrastructure, or malware delivery without contaminating the host system

\- The broader internet freedom and security community, who gain a transparent, auditable, open-source research platform for studying ephemeral browsing architecture



---



\## Geographic Focus



Primary regions selected on the OTF form:



\- Eastern Europe (Russia, Belarus, Ukraine)

\- Eastern Asia (China, Hong Kong)

\- Western Asia (Iran, Turkey, Saudi Arabia)

\- South-Eastern Asia (Myanmar, Vietnam, Cambodia)

\- Eastern Africa (Ethiopia)

\- Global (open-source tool accessible worldwide)



---



\## Why the Applicant Is the Right Person



Chris Wilson is a security-focused systems engineer with 5+ years of professional IT experience and 30+ years of hands-on independent work in systems, networking, and security infrastructure. He is currently studying for CISSP certification.



He operates a full home SOC using Wazuh and Suricata IDS for network security monitoring and threat detection. He has independently built and deployed NetGuard SOC — a production-grade, modular Python network threat intelligence platform integrating Suricata IDS, InfluxDB time-series storage, and an Ollama AI pipeline for automated threat analysis across 35,000+ threat intelligence IP feeds.



Ghost Browser's core technical stack — Python, Docker containerization, session lifecycle management, and encrypted storage — maps directly to his demonstrated skills. He has already built the foundational architecture and published the repository publicly at github.com/cbw29512/GhostBrowser, with 48 commits and documented architecture in the repository.



As an independent developer without institutional backing, he represents exactly the profile OTF prioritizes: a first-time applicant, self-funded to this point, building open-source internet freedom tooling without commercial motivation.



---



\## Supporting Documents



\- Uploaded: `ghost\_browser\_otf\_concept\_note.docx`



---



\## Code Security Audit



Agreed to undergo a code security audit facilitated by OTF via their Red Team Lab — \*\*Yes\*\*.



---



\## Notes for Full Proposal Stage



\- Activities field was submitted at 46 words — expand significantly if invited to full proposal

\- Budget of $55,000 may be revised upward at full proposal stage

\- Code security audit will be facilitated by OTF Red Team Lab at no cost

\- OTF currently in legal proceedings re: USAGM funding — monitor status at opentech.fund

\- Expected response timeline: 6–8 weeks from submission



---



\## GenAI Disclosure



Model: Claude Sonnet 4 (Anthropic), via claude.ai. Date: March 7, 2026.



Used for: Drafting and structuring the concept note based on the applicant's existing project materials, GitHub repository content, and the OTF application guidebook field requirements. All technical descriptions, project details, and background were reviewed and approved by the applicant. AI was used as a drafting tool, not as the source of technical content.

