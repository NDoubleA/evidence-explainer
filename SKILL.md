---
name: evidence
description: Log-line evidence reader. Takes any pasted log line (Windows Security/Sysmon, Linux auth.log, Entra ID sign-in, firewall/Zeek, AWS CloudTrail) and turns it into an interactive HTML page showing every field, what the line proves, what it does NOT prove, the sensor's blind spot, and where to pivot next. Use when Nigel types /evidence <log line>, or asks "what does this log prove?" or "read this event for me".
---

# Evidence: read a log line like an analyst

Goal: fix Nigel's #1 gap, **reading a log line as evidence**. Every page teaches one line the way a SOC analyst reasons about it. Anchor every page in the tutor arc's four truths:
1. Every action = a **process** under an **identity** crossing a **boundary** that can record it.
2. A record is a **sensor's claim**, not the truth.
3. **Sensor position sets the blind spot.**
4. **Proving identity is not being permitted** (and not proving the human).

## Steps
1. **Identify the source.** Work out the product and event type from the line's shape and field names:
   - Windows Security (`EventID`, `TargetUserName`, `LogonType`…) or Sysmon (`Microsoft-Windows-Sysmon`, `RuleName`, `Image`, `ProcessGuid`…)
   - Linux `auth.log`/`secure` (`sshd[pid]: Accepted publickey for…`, `sudo:`, `pam_unix`)
   - Entra ID sign-in (`ResultType`, `AppDisplayName`, `ConditionalAccessStatus`, `AuthenticationRequirement`…)
   - Firewall / Zeek (`conn.log` `uid id.orig_h id.resp_p`, `ntlm.log`, `dns.log`; vendor firewall `action=allow src= dst=`)
   - AWS CloudTrail (`eventName`, `userIdentity.type`, `sourceIPAddress`, `errorCode`…)
   If it's ambiguous, pick the most likely one and say so in the TL;DR.
2. **Pin the sensor and its position.** Which component wrote the line (LSASS on the destination host, the Sysmon driver on an endpoint, sshd on the server, Entra's token service, a perimeter firewall, Zeek on a SPAN port, CloudTrail at the AWS API)? Which **boundary** does it sit on (network → host, user → kernel, identity provider, cloud control plane, network segment)? This sets the blind spot.
3. **Field meanings come from the vendor docs.** For each field, write its meaning from Microsoft Learn, Sysmon, Zeek, AWS, Entra or the man page. If you're not 100% sure, **WebFetch the vendor page** before writing it. Never invent a field or a value meaning. If something is still uncertain, say so on the page. Put the doc links in Sources.
4. **Fill the page** from `template.html` in the skill folder. Write `values.json` with every placeholder (see `example.json` for the 4624 demo), then run:
   `python3 fill.py values.json output.html`
   `fill.py` fails if any placeholder is missing or left over, and refuses to overwrite.
   Sections (all required):
   - **Header**: eyebrow `SOURCE · EVENT_ID`, title, TL;DR in plain English (one or two sentences: "X's log says Y happened"), sensor + boundary chips, an "Example data" badge if the line is sample data (empty string if it's real), and the raw line (`RAW_JSON`, auto-highlights the selected field).
   - **Analyst challenge** (`CHALLENGE_JSON` = 4 × `{q, a}`): click-to-reveal questions placed at the top before the breakdown (what happened, what evidence supports that, what's unknown, what would you check next), challenging the analyst before they scroll.
   - **Evidence labels**: every claim on the page must be tagged with a coloured badge as `CONFIRMED` (directly in a field), `INFERRED` (follows from fields), `UNVERIFIED` (possible, needs checking), or `UNKNOWN`.
   - **Entities & Relationships** (`ENTITIES_JSON` = `{entities: [{type, value, field, label}], relationships: [{source, target, rel, fields, label}]}`): who and what is involved in the log (types: user, host, IP, process, logon session). Values must match the log exactly. Every entity and link must cite real log fields. Never invent entities not in the log (no invented names, departments or roles).
   - **Anatomy** (`FIELDS_JSON`): a list of `{k, v, meaning, why, kind, tok?}`. `kind` = `clue` (changes the reading), `pivot` (joins to other logs), or `""` (context). `tok` = the exact substring to highlight in the raw line, if it isn't `k=v`. Cover every field that matters; skip pure noise.
   - **Process / Identity / Boundary** (`WHO`, `WHAT_RAN`, `BOUNDARY`): who (the account, not the person), what process ran (on which host; say "unknown" when the sensor can't see it), which boundary recorded it.
   - **Proves vs Does NOT prove** (`PROVES`, `NOT_PROVES` as `<ul>`): be strict. Always include in "does not prove": the human behind the account, how the credential was obtained, what happened next (when true).
   - **Blind spot** (`BLIND_SPOT`, `FILLS_GAP`): what this sensor, from its position, could not have seen, plus the specific other logs (with event IDs or log names) that fill each gap.
   - **Sensor position** (`MERMAID`, `MERMAID_NOTE`): a Mermaid `flowchart LR` or `TD` with subgraphs for source / destination / other sensors. Use `<br/>` for line breaks inside labels (never `\n`). Highlight the writing sensor with `classDef sensor stroke:#e6b84f,stroke-width:2px;` and the blind parts with `classDef blind stroke:#f43f5e,stroke-dasharray:5 4;`.
   - **Triage decision tree** (`DECISION_TREE_JSON` = nested `{q, yes, no}` with outcomes `{outcome, detail}`): a small triage tree (max ~6 nodes) of yes/no questions naming specific things to check, ending in "escalate", "close as benign", or "need more data". Questions and outcomes are actions, so carry no evidence labels. The tree must never decide for the analyst.
   - **Next pivot** (`PIVOTS` as `<ol class="pivots">`, `KQL`): 2-3 follow-ups in plain language, then a KQL example (Sentinel `SecurityEvent`/`SigninLogs`/`Syslog`/`AWSCloudTrail` or Defender `Device*` tables). Use `=~` for case-insensitive string matches. Escape `<`, `>` and `&` in KQL.
   - **MITRE ATT&CK candidates** (`ATTACK_JSON` = max 3 × `{id, name, fields, label, confirm, rule_out}`): behavioral hypotheses. A single log line almost never confirms a technique; default label is INFERRED or UNVERIFIED. Only real ATT&CK IDs matching the technique name. If nothing fits, say "no technique supported by this log alone". Valid accounts (T1078) may be cited only as a candidate, never as proof of malice.
   - **Detection engineering idea** (`DETECTION_JSON` = `{behaviour, description, events_fields, query, false_positives, missing_data}`): one draft detection idea in plain English using a SIEM-agnostic pseudo-query, exact fields and event IDs, likely false positives, and missing data required. Labeled clearly as a draft idea, untested.
   - **Normal vs suspicious** (`CONTEXT_JSON` = `{n:{title,setup,facts[],verdict}, s:{…}}`): the **same line**, unchanged, read in two different surrounding contexts. Show which outside facts flip the verdict.
   - **Self-check** (`QUIZ_JSON` = 3 × `{q, a}`): click-to-reveal. At least one "does this prove…?" trap question.
   - **Sources** (`SOURCES`): real links: vendor field docs first, then MITRE ATT&CK pages, then Sigma rules if you cite them.
5. **Check it.** `grep -n '{{' <page>` must return nothing. Open the page and click a chip, the toggle and a Reveal.
6. **Report back**: page path, a one-line "what this line proves / doesn't", the first chip to click, and "Proof link for a Science turn". Do NOT tick or pin tech tree nodes.

## Rules
- Evidence labels: tag every claim on the page as CONFIRMED (directly in a field), INFERRED (follows from fields), UNVERIFIED (possible, needs checking) or UNKNOWN. An inferred, unverified or unknown claim may never appear in the field or evidence sections. Action items, follow-up checks, and decision tree questions/outcomes are actions, not claims, and do not carry labels.
- Entities and relationships: every entity and link in ENTITIES_JSON must cite a real field from the log. If no field proves it, label it UNKNOWN or leave it out. Never add entities that are not in the log (no invented names, departments or roles).
- Decision tree: triage tree nodes must be yes/no questions naming a specific check, ending in "escalate", "close as benign", or "need more data". The tree must never decide for the analyst.
- ATT&CK mappings: max 3 candidates, default INFERRED or UNVERIFIED, strictly real IDs matching the name (write UNKNOWN if unsure). T1078 Valid Accounts may only appear as a candidate, never proof of malice.
- Detection engineering: exactly one draft rule idea, clearly labeled untested, with plain-logic pseudo-query, exact event IDs/fields, explicit false positives, and missing data dependencies.
- Real field names, event IDs and value codes only (e.g. `%%1842` = Yes, `%%1843` = No). Unsure → WebFetch the vendor doc → still unsure → say so on the page.
- If Nigel pastes a real line, keep it as given, but tell him if it contains real usernames/IPs before he shares the page. Sample lines use private IPs (10.x, 192.168.x), `example.local` domains and made-up names, and get the "Example data" badge.
- Same theme as /detect and /visualize (black-gold, Inter + JetBrains Mono, 18px cards, rounded Mermaid boxes, Mermaid 11 CDN, single file).
- Never overwrite (add `-2`), never edit other files.
