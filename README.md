# AT2 Skills

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

### Claude Code (Plugin)
```bash
/plugin marketplace add <repo-url>
```

Then select `at2-skills` to install both skills.

### Manual
Clone this repo and register the skills folder in your Claude Code settings.

## Configuration

Both skills share a `reports-config.json` file (optional — skills work without it). On first use, the skill asks for basic settings and offers to save them.

Config is **not required** — you can provide all settings in conversation each time. Anything you say in conversation overrides the config file.

### Single team

```json
{
  "report_dir": "~/reports",
  "repo_paths": ["/path/to/repo1", "/path/to/repo2"],
  "author_email": "you@example.com",
  "language": "zh-TW",
  "team_name": "My Team",
  "team_members": ["Alice", "Bob"],
  "report_author": "Your Name"
}
```

### Multiple teams (profiles)

```json
{
  "report_dir": "~/reports",
  "author_email": "you@example.com",
  "language": "zh-TW",
  "default_profile": "team-a",
  "profiles": {
    "team-a": {
      "repo_paths": ["/path/to/repo1"],
      "team_name": "Team A",
      "team_members": ["Alice", "Bob"]
    },
    "team-b": {
      "repo_paths": ["/path/to/repo2"],
      "team_name": "Team B",
      "team_members": ["Charlie", "Dave"]
    }
  }
}
```

Switch profiles in conversation: `"用 team-b 的設定產生週報"`

## Usage

```
# Take a note
"record this: met with Leo about orchestrator design, decided on event-driven approach"

# Generate daily summary
"daily summary"

# Generate weekly report
"weekly report"
```

## Output Structure

```
{report_dir}/
  notes/
    2026-03-03.md
    2026-03-06.md
  week12/
    2026-03-03/
      summary.md
    2026-03-06/
      summary.md
    weekly_report.md
```

## Requirements

- Claude Code
- Python 3.10+ (for conversation history extraction script)
- Git (for commit scanning)

## License

Apache 2.0 — see [LICENSE](LICENSE).
