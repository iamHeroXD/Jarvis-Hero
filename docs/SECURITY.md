# PROJECT J.A.R.V.I.S. — Security & Privacy Architecture

## 1. Owner-First Authentication & Family Profiles

JARVIS implements a multi-profile permission model to support shared laptop use while strictly protecting private owner context.

### Profile Tiers
| Profile | Description | Memory Access | Computer Actions | Settings & Evolution |
|---|---|---|---|---|
| **Owner** | Primary developer & owner (Rohan) | Full personal & work memory | Level 0–3 actions | Full control |
| **Family** | Authorised family member (e.g. father's work) | Isolated family workspace only | Level 0–1 permitted tools | No access |
| **Guest** | Unauthenticated or temporary session | None | Level 0 (Read only) | No access |

---

## 2. Permission Levels

All computer operations must be validated against tiered permissions:
- **Level 0 (Read Only)**: Read public information, status queries.
- **Level 1 (Reversible Local Actions)**: Open approved applications (VS Code, Chrome), create drafts and reminders.
- **Level 2 (Confirmed Modifications)**: Modify approved files, organise folders with preview and backup.
- **Level 3 (Explicit External Actions)**: Send messages, publish content, external API writes. Mandatory user approval.
- **Level 4 (Restricted)**: Destructive system calls, arbitrary shell execution. Never exposed to AI agents.

---

## 3. Secret Management & Credential Safety
- API keys (including Gemini API Key) are stored exclusively in **Windows Credential Manager** via the `keyring` service.
- Secrets are never written to disk, database tables, or environment files.
- Passwords are encrypted using salted `bcrypt` hashes.

---

## 4. Camera & Vision Privacy
- The webcam interface for hand tracking is **disabled by default**.
- Camera streams are initiated strictly upon user consent in Mission Control.
- Video frames are processed entirely in local volatile memory. No video or images are stored on disk or transmitted over the network.
- Stream tracks are immediately terminated upon closing or navigating away.

---

## 5. Sentinel Threat Detection
- **URL Safety**: Evaluates destination URLs for known brand spoofing, typosquatting, raw IP hostnames, and suspicious TLDs.
- **Scam & Prompt Injection Scanner**: Evaluates incoming communications for coercive urgency or prompt injection bypass attempts.
