#!/usr/bin/env python3
"""Fill the /evidence template. Usage: python3 fill.py [--overwrite] values.json out.html
values.json: keys = placeholder names. *_JSON keys hold real JSON (lists/objects/strings);
all other keys hold HTML strings. Refuses to overwrite unless --overwrite/-f is passed,
and fails on any leftover {{PLACEHOLDER}}."""
import json, os, re, sys

BADGE_MAP = {
    "[CONFIRMED]": '<span class="badge badge-confirmed">CONFIRMED</span>',
    "[INFERRED]": '<span class="badge badge-inferred">INFERRED</span>',
    "[UNVERIFIED]": '<span class="badge badge-unverified">UNVERIFIED</span>',
    "[UNKNOWN]": '<span class="badge badge-unknown">UNKNOWN</span>',
}

def replace_badges(obj):
    if isinstance(obj, str):
        for tag, badge in BADGE_MAP.items():
            obj = obj.replace(tag, badge)
        return obj
    elif isinstance(obj, list):
        return [replace_badges(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: replace_badges(v) for k, v in obj.items()}
    return obj

here = os.path.dirname(os.path.abspath(__file__))
allow_overwrite = "--overwrite" in sys.argv or "-f" in sys.argv or os.environ.get("OVERWRITE") == "1"
args = [a for a in sys.argv[1:] if not a.startswith("-")]
if len(args) < 2:
    sys.exit("Usage: python3 fill.py [--overwrite] values.json out.html")
vals_path, out = args[0], args[1]

tpl = open(os.path.join(here, "template.html"), encoding="utf-8").read()
vals = json.load(open(vals_path, encoding="utf-8"))

# Backwards compatibility: default optional JSON placeholders if absent
vals.setdefault("CHALLENGE_JSON", [])
vals.setdefault("ENTITIES_JSON", {"entities": [], "relationships": []})
vals.setdefault("DECISION_TREE_JSON", {})
vals.setdefault("ATTACK_JSON", [])
vals.setdefault("DETECTION_JSON", {})

vals = replace_badges(vals)

needed = set(re.findall(r"\{\{([A-Z_]+)\}\}", tpl))
missing = needed - set(vals)
if missing:
    sys.exit(f"Missing values for: {sorted(missing)}")
for k in needed:
    v = vals[k]
    if k.endswith("_JSON"):
        v = json.dumps(v, ensure_ascii=False).replace("</", "<\\/")
    tpl = tpl.replace("{{" + k + "}}", v)
left = re.findall(r"\{\{[A-Z_]+\}\}", tpl)
assert not left, f"Leftover placeholders: {left}"
if os.path.exists(out) and not allow_overwrite:
    sys.exit(f"{out} exists - pick a new name (add -2), never overwrite")
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, "w", encoding="utf-8").write(tpl)
print("wrote", out)
