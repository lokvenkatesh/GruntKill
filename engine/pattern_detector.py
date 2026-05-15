import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
from anthropic import Anthropic
from dotenv import load_dotenv
from observer.activity_logger import get_recent_activity

load_dotenv()

client = Anthropic()

def format_activity_log(rows):
    """Convert raw DB rows into readable log for Claude"""
    if not rows:
        return "No activity recorded yet."
    
    lines = []
    for row in rows:
        timestamp, event_type, data, cwd = row
        lines.append(f"[{timestamp}] {event_type}: {data}")
    
    return "\n".join(lines)

def detect_patterns(days: int = 7):
    """Send activity log to Claude and get patterns back"""
    
    print("📡 Fetching activity log...")
    rows = get_recent_activity(days)
    
    if not rows:
        print("⚠️  No activity found. Use the shell hook first to log some commands.")
        return []
    
    print(f"📋 Sending {len(rows)} events to Claude API...")
    
    activity_log = format_activity_log(rows)
    
    prompt = f"""You are a developer workflow analyst.

Here is a log of developer activity over the past {days} days:

{activity_log}

Identify any repetitive patterns that could be automated.
For each pattern return:
- pattern_name: short snake_case name
- frequency: how many times it appears
- description: what the developer is doing
- commands: the exact commands involved
- automation_feasibility: high, medium, or low
- reason: why you gave that feasibility score

Return as a JSON array only. No explanation, no markdown, just the JSON array.
If no patterns found, return an empty array [].
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.content[0].text.strip()
    
    # Clean up in case Claude adds markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()
    
    try:
        patterns = json.loads(raw)
        print(f"✓ Claude detected {len(patterns)} pattern(s)")
        return patterns
    except json.JSONDecodeError:
        print("⚠️  Could not parse Claude response:")
        print(raw)
        return []

def print_patterns(patterns):
    """Pretty print detected patterns"""
    if not patterns:
        print("\n⚠️  No patterns detected yet — log more commands first!")
        return
    
    print("\n" + "=" * 60)
    print("  GRUNTKILL — DETECTED PATTERNS")
    print("=" * 60)
    
    for i, p in enumerate(patterns, 1):
        feasibility = p.get('automation_feasibility', 'unknown').upper()
        emoji = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(feasibility, "⚪")
        
        print(f"\n[{i}] {p.get('pattern_name', 'unknown')}")
        print(f"    {emoji} Feasibility : {feasibility}")
        print(f"    🔁 Frequency   : {p.get('frequency', '?')}x")
        print(f"    📝 Description : {p.get('description', '')}")
        print(f"    💻 Commands    : {p.get('commands', '')}")
        print(f"    💡 Reason      : {p.get('reason', '')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    patterns = detect_patterns(days=7)
    print_patterns(patterns)
    
    # Save patterns to a JSON file for next step
    if patterns:
        with open("detected_patterns.json", "w") as f:
            json.dump(patterns, f, indent=2)
        print(f"\n✓ Patterns saved to detected_patterns.json")