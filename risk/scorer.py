import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

RISK_LEVELS = {
    "low":    {"emoji": "🟢", "label": "SAFE",   "color": "green"},
    "medium": {"emoji": "🟡", "label": "MEDIUM", "color": "yellow"},
    "high":   {"emoji": "🔴", "label": "RISKY",  "color": "red"},
}

def score_script(script: str, pattern_name: str) -> dict:
    """Ask Claude to review its own generated script and give a risk score"""

    print(f"\n🔍 Risk scoring: {pattern_name}")

    prompt = f"""You are a security-focused code reviewer for an automation system.

Review this auto-generated Python script and assess its risk level:

```python
{script[:3000]}
```

Evaluate based on:
- Does it delete or overwrite files?
- Does it push code to production?
- Does it make network calls or API requests?
- Does it run shell commands with elevated privileges?
- Could it cause irreversible damage if it runs incorrectly?
- Does it have proper error handling?

Return a JSON object only with these exact fields:
{{
  "risk_level": "low" or "medium" or "high",
  "risk_score": number between 0-100,
  "reasons": ["reason 1", "reason 2"],
  "dangerous_operations": ["list any dangerous ops found"],
  "has_error_handling": true or false,
  "recommendation": "one sentence recommendation for the user",
  "safe_to_auto_deploy": true or false
}}

Return JSON only. No explanation, no markdown fences.
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
        result["pattern_name"] = pattern_name
        return result
    except json.JSONDecodeError:
        print("⚠️  Could not parse risk score response")
        return {
            "pattern_name":        pattern_name,
            "risk_level":          "medium",
            "risk_score":          50,
            "reasons":             ["Could not parse response"],
            "dangerous_operations": [],
            "has_error_handling":  False,
            "recommendation":      "Manual review recommended",
            "safe_to_auto_deploy": False
        }

def print_risk_report(result: dict):
    """Pretty print the risk report"""
    level    = result.get("risk_level", "medium").lower()
    info     = RISK_LEVELS.get(level, RISK_LEVELS["medium"])
    score    = result.get("risk_score", 0)
    name     = result.get("pattern_name", "unknown")

    print("\n" + "=" * 60)
    print(f"  RISK REPORT — {name}")
    print("=" * 60)
    print(f"  {info['emoji']}  Risk Level     : {info['label']}")
    print(f"  📊  Risk Score     : {score}/100")
    print(f"  🛡️   Error Handling : {'Yes' if result.get('has_error_handling') else 'No'}")
    print(f"  🚀  Auto-deploy    : {'Yes' if result.get('safe_to_auto_deploy') else 'No — needs approval'}")

    reasons = result.get("reasons", [])
    if reasons:
        print(f"\n  ⚠️  Reasons:")
        for r in reasons:
            print(f"     • {r}")

    dangerous = result.get("dangerous_operations", [])
    if dangerous:
        print(f"\n  🚨  Dangerous Operations:")
        for d in dangerous:
            print(f"     • {d}")

    print(f"\n  💡  Recommendation:")
    print(f"     {result.get('recommendation', '')}")
    print("=" * 60)

def score_generated_scripts(scripts_dir="."):
    """Score all generated scripts in the project"""
    scored = []

    for fname in os.listdir(scripts_dir):
        if fname.startswith("generated_") and fname.endswith(".py"):
            fpath = os.path.join(scripts_dir, fname)
            pattern_name = fname.replace("generated_", "").replace(".py", "")

            with open(fpath) as f:
                script = f.read()

            result = score_script(script, pattern_name)
            print_risk_report(result)
            scored.append(result)

    # Save all risk reports
    if scored:
        with open("risk_reports.json", "w") as f:
            json.dump(scored, f, indent=2)
        print(f"\n✓ Risk reports saved to risk_reports.json")

    return scored

if __name__ == "__main__":
    print("🛡️  GruntKill Risk Scorer")
    print("=" * 40)
    score_generated_scripts()
    