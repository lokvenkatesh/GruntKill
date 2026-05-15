# ⚡ GruntKill — Kill Your Repetitive Dev Work

> An agentic AI system that watches how you work, detects repetitive patterns,
> and autonomously generates + deploys automation scripts — with one-click approval.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Claude API](https://img.shields.io/badge/Claude-API-orange)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![License](https://img.shields.io/badge/license-MIT-purple)

---

## 🎯 The Problem

Developers waste **30–40% of their time** on repetitive grunt work — but never automate it because writing the script feels like extra work. GruntKill writes it for you.

---

## 🤖 How It Works

    You work normally
           ↓
    GruntKill logs every terminal command silently
           ↓
    Claude API detects repetitive patterns
           ↓
    Claude writes a Python automation script
           ↓
    Risk scorer rates the script 🟢🟡🔴
           ↓
    Slack notification → Approve or Reject
           ↓
    AWS Lambda deploys and runs it forever

---

## ✨ Features

- **Zero-prompt observation** — no configuration, just works in background
- **LLM pattern detection** — Claude finds what you repeat most
- **Auto script generation** — Claude writes production-ready Python scripts
- **Risk scoring** — every script rated 🟢 Safe / 🟡 Medium / 🔴 Risky before deploy
- **Slack notifications** — approve or reject automations from Slack
- **GruntKill CLI** — `gk status`, `gk scan`, `gk approve`, `gk logs`
- **AWS Lambda deployment** — approved scripts run on your own AWS account forever

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Activity Observer | Python — shell hooks, file watchers |
| Pattern Detection | Claude API + embeddings |
| Vector Memory | pgvector on AWS RDS |
| Script Generator | Claude API |
| Backend API | FastAPI on AWS EC2 |
| Job Queue | AWS SQS |
| Deployment Engine | AWS Lambda + CloudWatch |
| Frontend Dashboard | React + TailwindCSS |
| Notifications | Slack Webhooks |
| CLI | Typer + Rich |

---

## 📁 Project Structure

    gruntkill/
    ├── observer/
    │   ├── shell_hook.py          # captures terminal commands
    │   ├── file_watcher.py        # watches file operations
    │   ├── activity_logger.py     # logs to SQLite
    │   └── log_command.py         # PowerShell profile hook helper
    ├── engine/
    │   ├── pattern_detector.py    # Claude finds patterns
    │   ├── script_generator.py    # Claude writes scripts
    │   ├── scheduler.py           # smart scheduling
    │   └── memory.py              # pgvector memory store
    ├── risk/
    │   └── scorer.py              # Claude rates script safety
    ├── notifications/
    │   └── slack.py               # Slack approve/reject alerts
    ├── cli/
    │   └── main.py                # gk CLI commands
    ├── backend/
    │   ├── main.py                # FastAPI server
    │   ├── deployer.py            # AWS Lambda deployment
    │   └── routes/
    │       ├── automations.py
    │       └── approvals.py
    ├── frontend/
    │   └── src/
    │       ├── Dashboard.jsx
    │       ├── Suggestions.jsx
    │       └── History.jsx
    ├── infra/
    │   ├── lambda_template.py
    │   └── aws_setup.py
    ├── setup.py
    ├── requirements.txt
    └── .env.example

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git
- AWS Account (free tier works)
- Anthropic API key → https://console.anthropic.com
- Slack workspace + webhook URL

### 1 — Clone & Install

```bash
git clone https://github.com/yourusername/gruntkill.git
cd gruntkill
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install --editable .
```

### 2 — Add Your API Keys

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
```

### 3 — Set Up Auto-logging (Windows PowerShell)

Run `code $PROFILE` and add:

```powershell
function prompt {
    $lastCmd = (Get-History -Count 1).CommandLine
    if ($lastCmd -and $lastCmd -notmatch "^gk") {
        python C:\path\to\gruntkill\observer\log_command.py "$lastCmd" 2>$null
    }
    "PS $($executionContext.SessionState.Path.CurrentLocation)> "
}
```

Restart PowerShell.

### 4 — Work Normally For 3-7 Days

```bash
npm run build
git add .
git commit -m "fix"
git push origin main
```

GruntKill logs everything silently.

### 5 — Run a Scan

```bash
gk scan
```

### 6 — Check Slack and Approve

You will get a Slack message with Approve / Reject buttons.
Click Approve → Lambda deployed → runs forever.

---

## 💻 CLI Commands

```bash
gk status         # show GruntKill status
gk suggestions    # show pending automation suggestions
gk logs           # show recent logged activity
gk approve 1      # approve suggestion #1
gk reject 1       # reject suggestion #1
gk scan           # run full scan → detect → score → notify Slack
```

---

## 🔒 Security Notes

- Activity logs stay local until you explicitly run `gk scan`
- Scripts deploy to your own AWS account — nothing touches GruntKill servers
- All HIGH RISK scripts require manual confirmation before deploy
- Never auto-approve scripts that push to production branches

---

## 📝 Resume Bullet

Built GruntKill, an agentic AI system using Python, Claude API, and AWS Lambda that observes developer workflows, detects repetitive patterns via LLM analysis, and autonomously generates and deploys automation scripts — eliminating repetitive dev tasks with one-click approval.

---

## 👤 Author

**Lok Venkatesh**

---

## 📄 License

MIT License
