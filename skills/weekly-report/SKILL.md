---
name: weekly-report
description: >
  Generate daily work summaries and weekly reports by aggregating git commits,
  Claude conversation history, daily notes, and user input. Trigger this skill
  whenever the user says "daily summary", "end of day report", "weekly report",
  "summarize my week", "what did I do today", "day summary", "write my work
  report", "週報", "日報", or asks to produce any kind of work status report.
  Also trigger at the end of a working session when the user wants to log what
  they accomplished. Even if the user just says something vague like "wrap up
  my day" or "what did I get done" — use this skill.
---

# Weekly Report

Produce structured daily summaries and weekly reports by pulling from four data
sources:

1. **Git commits** — auto-scanned across configured repos
2. **Claude conversation history** — parsed from `~/.claude/projects/` JSONL files
3. **Daily notes** — from the shared `notes/` folder (created by the `daily-note` skill)
4. **User-provided context** — meetings, blockers, plans (asked interactively)

## Configuration

Settings are resolved with this priority (highest first):

1. **User's current message** — anything the user says in conversation overrides
   config. E.g., "用 DeltaLLM team 的設定產生週報" switches the active profile.
2. **Config file** — look for `./reports-config.json` then `~/reports-config.json`
3. **Defaults** — `report_dir: ~/reports`, `author_email` from `git config user.email`

### First run (no config file)

Ask the user for the basics:
1. Where to save reports? (suggest `~/reports`)
2. Which git repos to scan? (suggest auto-detecting repos in `~/projects/`)
3. Git author email? (suggest output of `git config user.email`)
4. Team name and members? (optional)
5. Save as default config? (yes/no)

If yes, write `reports-config.json`. If no, just proceed with the provided values.

### Subsequent runs (config exists)

Briefly confirm which profile/settings will be used:

```
Using profile "cortex" (Agentic AI System). OK?
```

The user can say "OK", override specific fields ("用 DeltaLLM team"), or say
"different team" to provide new values on the fly.

### Config file format

```json
{
  "report_dir": "~/reports",
  "author_email": "user@example.com",
  "language": "zh-TW",
  "default_profile": "cortex",
  "profiles": {
    "cortex": {
      "repo_paths": ["/path/to/cortex"],
      "team_name": "Agentic AI System",
      "team_members": ["Leo", "Kuntai", "Joe", "Theo"],
      "report_author": "Theo",
      "milestone": {
        "By Mar/E": "Release DeltaLLM-cli v1.0",
        "Ongoing": "Follow checkpoints"
      }
    },
    "deltallm": {
      "repo_paths": ["/path/to/deltallm-cli"],
      "team_name": "DeltaLLM Team",
      "team_members": ["Theo", "Alice"],
      "report_author": "Theo"
    }
  }
}
```

Top-level fields (`report_dir`, `author_email`, `language`) are shared across
profiles. Each profile overrides team-specific settings. If there's only one
team, a flat config without `profiles` also works:

```json
{
  "report_dir": "~/reports",
  "repo_paths": ["/path/to/repo1"],
  "author_email": "user@example.com",
  "team_name": "My Team"
}
```

The skill auto-detects which format is used. Fields not set in the config are
simply omitted from the report (no team section if no team configured, etc.).

## Folder Structure

```
{report_dir}/
  reports-config.json
  notes/                         ← daily-note skill writes here
    2026-03-03.md
    2026-03-06.md
  week12/                        ← ISO week number
    2026-03-03/
      summary.md
    2026-03-06/
      summary.md
    weekly_report.md
```

Week folders use ISO week numbers (`date +%V`). Day folders use dates. This means
skipped days simply don't have folders — no gaps or confusion.

## Workflow

### Step 1 — Determine Mode

| User intent | Mode |
|---|---|
| "daily summary", "end of day", "what did I do today" | **Daily Summary** |
| "weekly report", "week summary", "週報" | **Weekly Roll-up** |
| First run / no config exists | **Initialize** → then proceed to requested mode |

### Step 2 — Daily Summary

Run these data-gathering steps in parallel where possible.

#### 2a. Git Commits

For each repo in `repo_paths`, run:

```bash
git -C {repo_path} log \
  --author="{author_email}" \
  --since="{YYYY-MM-DD} 00:00:00" \
  --until="{YYYY-MM-DD} 23:59:59" \
  --pretty=format:"%h|%s|%ai" \
  --no-merges
```

If no commits found for today, try `--since="2 days ago"` as fallback and note
the date range in output.

#### 2b. Claude Conversation History

Scan `~/.claude/projects/` for JSONL files modified today. The structure:

```
~/.claude/projects/{encoded-project-path}/
  {session-uuid}.jsonl           ← main conversation
  {session-uuid}/subagents/*.jsonl  ← subagent conversations
```

Each line is JSON with a `type` field. Focus on:
- `type: "user"` — has `message.content` (string or array of content blocks),
  `timestamp`, `cwd`, `gitBranch`
- `type: "assistant"` — has `message.content` with Claude's response

To extract conversation topics efficiently:

1. Find today's JSONL files:
   ```bash
   find ~/.claude/projects/ -name "*.jsonl" -newermt "{YYYY-MM-DD}" \
     -not -newermt "{YYYY-MM-DD} + 1 day" -not -path "*/subagents/*"
   ```

2. Use the bundled script to extract summaries:
   ```bash
   python3 {skill_dir}/scripts/extract_conversations.py \
     --date {YYYY-MM-DD} \
     --output {report_dir}/week{W}/{YYYY-MM-DD}/conversations.json
   ```

3. The script outputs a JSON array of conversation summaries with project path,
   branch, and first user message for each session. Use these to write a
   human-readable summary of what was discussed.

If the script is not available or fails, fall back to manually reading the JSONL
files — look at `type: "user"` entries to understand what topics were discussed.

#### 2c. Daily Notes

Check if `{report_dir}/notes/{YYYY-MM-DD}.md` exists. If so, read it and
incorporate its content. These notes contain meeting records, ideas, and other
context the user captured throughout the day.

#### 2d. Ask User for Supplement

After gathering auto-collected data, show the user what was found and ask for
anything missing:

```
Auto-collected for {YYYY-MM-DD}:
  - Git: {N} commits across {M} repos
  - Conversations: {K} Claude sessions
  - Notes: {J} entries from daily notes

Anything else to add?
  1. Meetings not captured in daily notes?
  2. Non-coding work (docs, reviews, demos)?
  3. Blockers?
  4. Key highlights for weekly report?

(Say "looks good" to skip)
```

#### 2e. Generate summary.md

Write to `{report_dir}/week{W}/{YYYY-MM-DD}/summary.md`:

```markdown
# Daily Summary — {YYYY-MM-DD} ({weekday})

## Completed
- {Accomplishment — rewritten from raw commit into human-readable form}
- {e.g., "Implemented session persistence for DeltaLLM CLI (PR #38)"}

## In Progress
- {Work discussed or started but not finished}

## Meetings & Collaboration
- {From daily notes and user input — omit section if none}

## Blockers
- {Omit section if none}

## Notes
- {Highlights to carry forward to weekly report}
```

The key quality principle: **transform raw data into accomplishments**. A commit
message like `fix: null check in parser` should become "Resolved parser crash
caused by missing null-check in config initialization". Group by project, not by
data source.

### Step 3 — Weekly Roll-up

Triggered on Friday or when user explicitly requests.

#### 3a. Gather All Data

1. Read all existing daily summaries in `{report_dir}/week{W}/*/summary.md`
2. For days without a summary, auto-generate one by pulling git + conversations +
   notes for that date (the same logic as Step 2, just for a past date)
3. Re-scan the full week's daily notes for anything not captured in summaries

#### 3b. Generate weekly_report.md

Write to `{report_dir}/week{W}/weekly_report.md`:

```markdown
# Weekly Report — Week {W} ({Mon date} ~ {Fri date})
**Author:** {report_author}
**Team:** {team_name} [{team_members}]

---

## Milestone Checkpoints
{Only if milestone is configured — display as-is from config}

---

## Executive Summary

{2-4 sentence narrative. Cover: main focus, what was delivered, project phases,
direction for next week. Dense and informative — assume the reader knows the
projects. Written in the user's configured language.}

---

## Completed This Week

### {Project Name}
- {Specific accomplishment}
- {Another accomplishment}

### {Project Name}
- ...

---

## In Progress

### {Project Name}
- {Active work items}

---

## Plan for Next Week
- {Concrete, actionable — not "continue working on X" but "implement Y" or "finalize Z"}

---

*Generated on {date} by weekly-report skill*
```

#### 3c. Review

After generating, show the user the report and ask:

```
Weekly report draft saved to {path}.

Please review:
  1. Anything missing or inaccurate?
  2. Tone of Executive Summary OK?
  3. Add/remove any projects or bullets?
```

## Edge Cases

| Situation | Behavior |
|---|---|
| No git commits for a day | Note it; still generate summary from other sources |
| No Claude conversations found | Skip that section; rely on git + notes + user input |
| No daily notes for a day | Skip; generate from git + conversations |
| All sources empty for a day | Ask user to provide input manually |
| Mid-week weekly report | Generate partial report, label as "Week {W} (Partial)" |
| User skips days | Weekly roll-up fills gaps automatically from git/conversations |
| New week starts | Auto-detect via ISO week number, create new week folder |
| Multiple git author emails | Support array in `author_email` config field |

## Output Quality Guidelines

- **Transform commits into accomplishments** — "fix: null check" becomes
  "Resolved initialization crash caused by missing null-check"
- **Group by project**, not by time or data source
- **Preserve specificity** — keep model names, feature names, team-specific terms
- **Executive Summary should be dense** — skip background, focus on progress and
  trajectory
- **Next week plan should be concrete** — "implement X component" not "continue
  work on X"
- **Respect language setting** — write reports in the user's configured language
