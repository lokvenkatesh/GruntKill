import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_suggestion(pattern: dict, risk: dict):
    """Send a GruntKill suggestion to Slack with approve/reject buttons"""

    pattern_name = pattern.get("pattern_name", "unknown")
    frequency    = pattern.get("frequency", "?")
    description  = pattern.get("description", "")
    commands     = pattern.get("commands", [])
    commands_str = " → ".join(commands) if isinstance(commands, list) else commands

    risk_level   = risk.get("risk_level", "medium").lower()
    risk_score   = risk.get("risk_score", 0)
    risk_emoji   = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(risk_level, "⚪")
    recommend    = risk.get("recommendation", "")
    safe         = risk.get("safe_to_auto_deploy", False)

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "⚡ GruntKill — New Automation Suggestion"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Pattern:*\n`{pattern_name}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Detected:*\n{frequency}× this week"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*What you keep doing:*\n{description}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Commands:*\n```{commands_str}```"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Risk Level:*\n{risk_emoji} {risk_level.upper()} ({risk_score}/100)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Safe to auto-deploy:*\n{'✅ Yes' if safe else '⚠️ Needs review'}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommendation:*\n_{recommend}_"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "✅ Approve & Deploy"
                        },
                        "style": "primary",
                        "value": f"approve_{pattern_name}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "❌ Reject"
                        },
                        "style": "danger",
                        "value": f"reject_{pattern_name}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "👀 View Script"
                        },
                        "value": f"view_{pattern_name}"
                    }
                ]
            }
        ]
    }

    return send_message(message)

def send_message(payload: dict) -> bool:
    """Send any payload to Slack webhook"""
    if not WEBHOOK_URL:
        print("⚠️  SLACK_WEBHOOK_URL not set in .env")
        return False

    try:
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✓ Slack notification sent!")
                return True
    except urllib.error.URLError as e:
        print(f"⚠️  Slack error: {e}")
    return False

def send_deployed(pattern_name: str):
    """Notify Slack when a script is deployed"""
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚀 *GruntKill deployed:* `{pattern_name}`\nThis automation is now running on AWS Lambda."
                }
            }
        ]
    }
    return send_message(payload)

def send_rejected(pattern_name: str):
    """Notify Slack when a script is rejected"""
    payload = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"❌ *GruntKill rejected:* `{pattern_name}`\nSuggestion dismissed."
                }
            }
        ]
    }
    return send_message(payload)

if __name__ == "__main__":
    print("📨 Testing Slack notification...")

    # Load pattern and risk from saved files
    pattern = {}
    risk    = {}

    if os.path.exists("detected_patterns.json"):
        with open("detected_patterns.json") as f:
            patterns = json.load(f)
            if patterns:
                pattern = patterns[0]

    if os.path.exists("risk_reports.json"):
        with open("risk_reports.json") as f:
            reports = json.load(f)
            if reports:
                risk = reports[0]

    if pattern and risk:
        send_suggestion(pattern, risk)
    else:
        print("⚠️  No pattern or risk data found.")
        print("    Run pattern_detector.py and risk/scorer.py first.")