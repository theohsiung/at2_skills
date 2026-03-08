# AT2 Skills

[中文版](README_zh.md)

Claude Code skills for daily note-taking and weekly report generation.

## Skills

### daily-note
Quickly capture notes, meeting summaries, ideas, or any context into dated markdown files. Each day gets one file; multiple notes in the same day are appended as timestamped sections.

### weekly-report
Generate daily work summaries and weekly reports by aggregating:
- Git commits (auto-scanned across multiple repos)
- Claude conversation history (parsed from `~/.claude/projects/` JSONL files)
- Daily notes (from the `daily-note` skill)
- User-provided context (meetings, blockers, plans)

Supports a flexible workflow: run daily summaries whenever you want, and generate a weekly roll-up on demand. Missing days are auto-filled from git and conversation data.

## Installation

### Method 1: Plugin Marketplace (recommended)

In Claude Code, run:

```
/plugin marketplace add theohsiung/at2_skills
```

Then select `at2-skills` to install both skills.

### Method 2: Manual Skill Registration

```bash
# Clone the repo
git clone https://github.com/theohsiung/at2_skills.git

# In Claude Code, add each skill
/skill add /path/to/at2_skills/skills/daily-note
/skill add /path/to/at2_skills/skills/weekly-report
```

### Verify Installation

After installation, the skills will trigger automatically when you say things like:
- "record this..." / "記一下..." → triggers `daily-note`
- "daily summary" / "weekly report" / "週報" → triggers `weekly-report`

## Quick Start

### 1. Take your first note

```
You: 記一下，剛跟 Leo 開會討論 agent 架構，決定用 event-driven

Claude: 📋 Notes will be saved to ~/reports. Save this as default? (yes/no)
You: yes

Claude: Saved to ~/reports/notes/2026-03-06.md (1st note today)
```

### 2. Generate a daily summary

```
You: 今天做了什麼？

Claude: Using profile "cortex" (Agentic AI System). OK?
You: OK

Claude: Auto-collected for 2026-03-06:
  - Git: 3 commits across 2 repos
  - Conversations: 5 Claude sessions
  - Notes: 2 entries from daily notes

  Anything else to add?
  1. Meetings not captured?
  2. Non-coding work?
  3. Blockers?

You: looks good

Claude: ✅ Daily summary saved to ~/reports/week10/2026-03-06/summary.md
```

### 3. Generate a weekly report

```
You: 幫我產生這週的週報

Claude: Using profile "cortex" (Agentic AI System). OK?
You: OK

Claude: ✅ Weekly report saved to ~/reports/week10/weekly_report.md
  Please review - anything to adjust?
```

## Configuration

Both skills share a `reports-config.json` file. The config is **optional** — you can provide all settings in conversation each time. Anything you say in the conversation overrides the config file.

The config is created interactively on first use, or you can create it manually.

### Config file location

The skill looks for the config in this order:
1. `./reports-config.json` (current working directory)
2. `~/reports-config.json` (home directory)

### Single team setup

```json
{
  "report_dir": "~/reports",
  "repo_paths": ["/home/you/projects/repo1", "/home/you/projects/repo2"],
  "author_email": "you@example.com",
  "language": "zh-TW",
  "team_name": "My Team",
  "team_members": ["Alice", "Bob", "Charlie"],
  "report_author": "Your Name",
  "milestone": {
    "By Mar/E": "Release v1.0",
    "Ongoing": "Follow sprint checkpoints"
  }
}
```

### Config fields reference

| Field | Required | Description |
|---|---|---|
| `report_dir` | Yes | Where to save notes and reports (e.g., `~/reports`) |
| `repo_paths` | Yes* | Git repos to scan for commits. *Only needed for `weekly-report` |
| `author_email` | Yes* | Your git email for filtering commits. *Auto-detected from `git config user.email` if not set |
| `language` | No | Report language (default: matches your conversation language) |
| `team_name` | No | Team name shown in report header |
| `team_members` | No | Team member names shown in report header |
| `report_author` | No | Your name shown in report header |
| `milestone` | No | Milestone checkpoints shown in weekly report |

### Multiple teams (profiles)

If you work across multiple teams, use profiles:

```json
{
  "report_dir": "~/reports",
  "author_email": "you@example.com",
  "language": "zh-TW",
  "default_profile": "team-a",
  "profiles": {
    "team-a": {
      "repo_paths": ["/home/you/projects/project-a"],
      "team_name": "Team A",
      "team_members": ["Alice", "Bob"],
      "report_author": "Your Name",
      "milestone": {
        "By Q2": "Launch feature X"
      }
    },
    "team-b": {
      "repo_paths": ["/home/you/projects/project-b"],
      "team_name": "Team B",
      "team_members": ["Charlie", "Dave"],
      "report_author": "Your Name"
    }
  }
}
```

Top-level fields (`report_dir`, `author_email`, `language`) are shared across all profiles. Each profile overrides team-specific settings.

Switch profiles in conversation:

```
You: 用 team-b 的設定產生週報
You: weekly report for team-b
```

### Conversational override

You don't need a config file at all. Just tell Claude what you need:

```
You: 幫我產生週報，repos 在 ~/projects/my-app 和 ~/projects/my-lib，
     team 是 "Backend Team"，成員有 Alice 和 Bob
```

Or override specific fields when a config exists:

```
You: 產生週報，但這次多掃 ~/projects/extra-repo
```

## Output Structure

```
{report_dir}/
  reports-config.json              ← config (if saved)
  notes/                           ← daily-note writes here
    2026-03-03.md
    2026-03-04.md
    2026-03-06.md
  week10/                          ← ISO week number
    2026-03-03/
      summary.md                   ← daily summary
    2026-03-06/
      summary.md
    weekly_report.md               ← weekly roll-up
  week11/
    ...
```

### Daily note format

```markdown
# 2026-03-06 (星期五)

---

## 14:32 — Agent orchestrator 架構會議

與 Leo 開會討論 agent orchestrator 架構，決定採用 event-driven 方式。

---

## 16:05 — PR #42 review

Reviewed PR #42 for DeltaLLM. Left comments about error handling.
```

### Daily summary format

```markdown
# Daily Summary — 2026-03-06 (星期五)

## Completed
- Implemented session persistence for DeltaLLM CLI (PR #38)
- Resolved parser crash caused by missing null-check

## In Progress
- Researching workflow drawing agent

## Meetings & Collaboration
- Met with Leo about orchestrator architecture

## Notes
- Key highlight for weekly report
```

### Weekly report format

```markdown
# Weekly Report — Week 10 (2026-03-02 ~ 2026-03-06)
**Author:** Your Name
**Team:** My Team [Alice, Bob, Charlie]

## Milestone Checkpoints
- By Mar/E: Release v1.0

## Executive Summary
(2-4 sentence narrative of the week's progress)

## Completed This Week
### Project A
- Accomplishment 1
- Accomplishment 2

## In Progress
### Project A
- Active work item

## Plan for Next Week
- Concrete action item 1
- Concrete action item 2
```

## Data Sources

### Git commits
The skill scans configured repos using `git log` filtered by your author email. Raw commit messages are transformed into human-readable accomplishments (e.g., `fix: null check` → "Resolved initialization crash caused by missing null-check").

### Claude conversation history
The skill reads JSONL files from `~/.claude/projects/` to understand what you discussed with Claude throughout the day/week. This is done via a bundled Python script (`scripts/extract_conversations.py`).

### Daily notes
Notes captured via the `daily-note` skill are automatically incorporated into summaries and reports.

### User input
After auto-collecting data, the skill asks if you want to add anything (meetings, non-coding work, blockers, etc.). You can skip this step by saying "looks good".

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.10+ (for the conversation history extraction script)
- Git (for commit scanning)

## License

Apache 2.0 — see [LICENSE](LICENSE).
