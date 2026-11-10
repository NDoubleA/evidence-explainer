# Evidence Explainer

An analyst-in-the-loop log explainer that turns one log event into an evidence page, separating what the log proves from what it doesn't.

screenshot coming

## Why It Exists

AI log explanations often treat alert labels as proof. This tool keeps evidence, interpretation, and next steps separate.

## The Four Evidence Labels

Every claim and extracted entity carries an explicit evidence tag:

- **CONFIRMED**: Directly stated in a field in the log line.
- **INFERRED**: Follows logically from fields, but is not directly recorded.
- **UNVERIFIED**: A possible explanation or hypothesis that needs checking outside this log.
- **UNKNOWN**: Cannot be determined from this log line or sensor position.

Inferred, unverified, and unknown claims may never appear in the field anatomy or evidence ("This line proves") sections. Action items carry no labels.

## What a Page Contains

Each generated standalone HTML report contains:

- **Raw Log Line**: Displayed at the top with dynamic token highlighting upon selecting fields.
- **Analyst Challenge**: Four questions (*What happened?*, *What evidence supports that?*, *What's unknown?*, *What would you check next?*) with answers hidden behind reveal buttons to test the analyst before scrolling.
- **Field Anatomy**: Vendor-documented meaning and investigation significance for every key field.
- **Entities & Relationships**: Users, hosts, IP addresses, processes, and session IDs tied to source fields, with explicit link relationships.
- **Process · Identity · Boundary**: Clear separation of authenticated account, executing process, and recording sensor boundary.
- **Proves vs Does NOT Prove**: Strict boundary between confirmed facts and unverified assumptions.
- **Sensor Blind Spot & Gaps**: Visualized sensor position (Mermaid diagram) and concrete log sources that fill blind spots.
- **Triage Decision Tree**: Nested collapsible yes/no questions naming concrete sources to check, ending in triage paths (*Escalate*, *Close as benign*, or *Need more data*).
- **Candidate ATT&CK Mappings**: Up to three relevant MITRE ATT&CK techniques with confirmation and rule-out criteria.
- **Draft Detection Idea**: A draft SIEM-agnostic pseudo-query with named fields, false positives, and telemetry prerequisites.
- **Next Pivots & KQL**: Concrete query logic and follow-up paths.
- **Context Toggle**: Compares benign vs suspicious interpretations of the exact same event.
- **Self-Check Quiz**: Interactive trap-detection questions with click-to-reveal answers.

## How to Run

Generate an evidence page from a JSON values file:

```bash
python3 fill.py example.json output.html
```

To overwrite an existing output file during iteration:

```bash
python3 fill.py --overwrite example.json output.html
```

A generated sample is available at `examples/windows-4624-type3.html`.

## Limits

- Works on one event at a time.
- ATT&CK mappings are candidates, never confirmed from one line.
- Detection ideas are untested drafts.
- Sample data is synthetic.
- The analyst makes every decision; the tool only displays the paths.

## Roadmap

- Multi-log input
- Timeline and correlation
