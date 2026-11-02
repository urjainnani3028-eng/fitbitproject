"""Pull the PromQL out of monitoring/ so CI can check it with promtool.

Writes two files into the given folder:
  alert_rules.yaml      - the alert rules from monitoring/values.yaml
  dashboard_rules.yaml  - every Grafana panel query, wrapped as a recording rule
"""

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
out = Path(sys.argv[1] if len(sys.argv) > 1 else "promtool-check")
out.mkdir(parents=True, exist_ok=True)

values = yaml.safe_load((ROOT / "monitoring/values.yaml").read_text())
groups = values["additionalPrometheusRulesMap"]["fitbit-app"]["groups"]
(out / "alert_rules.yaml").write_text(yaml.safe_dump({"groups": groups}, sort_keys=False))

dashboard = json.loads((ROOT / "monitoring/fitbit-dashboard.json").read_text())
rules = []
for panel in dashboard["panels"]:
    for i, target in enumerate(panel.get("targets", [])):
        # Grafana variables aren't PromQL; swap in a real duration
        expr = target["expr"].replace("$__range", "1h")
        rules.append({"record": f"dashboard:panel_{panel['id']}_{i}", "expr": expr})
(out / "dashboard_rules.yaml").write_text(yaml.safe_dump({"groups": [{"name": "dashboard", "rules": rules}]}))

print(f"{len(groups[0]['rules'])} alert rules and {len(rules)} dashboard queries written to {out}/")
