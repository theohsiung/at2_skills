---
name: daily-note
description: >
  Quickly capture notes, meeting summaries, ideas, or any context into a dated
  markdown file. Trigger this skill whenever the user says "daily note",
  "meeting note", "jot this down", "record this", "log this", or any variation
  of wanting to save a note for later reference. Also trigger when the user
  pastes meeting content and wants it saved, or says something like "remember
  this for my weekly report". This skill appends to a single file per day so
  multiple notes accumulate naturally. Even if the user doesn't explicitly say
  "note" — if they're clearly trying to capture something for future reference,
  use this skill.
---

# Daily Note

Capture notes into dated markdown files. Each day gets one file; multiple notes
in the same day are appended as separate sections with timestamps.

## Configuration

This skill shares configuration with `weekly-report`. On each use, resolve
settings in this order:

1. **User's current message** — if they specify a directory or language in the
   conversation, use that (highest priority)
2. **Config file** — look for `./reports-config.json` then `~/reports-config.json`
3. **Defaults** — `report_dir: ~/reports`, language: match the user's language

### First run (no config file)

Ask just two things:
1. Where should notes be saved? (suggest `~/reports`)
2. Save this as default config for next time? (yes/no)

If yes, write `reports-config.json` in the chosen `report_dir`. If no, just
proceed — the skill works fine without a config file.

### Config file format

```json
{
  "report_dir": "~/reports",
  "language": "zh-TW"
}
```

The config is minimal on purpose — `weekly-report` may add more fields (like
`repo_paths`, `team`, `profiles`), and that's fine. Both skills read from the
same file.

## Taking a Note

### 1. Determine today's file path

```
{report_dir}/notes/{YYYY-MM-DD}.md
```

Create the `notes/` directory if it doesn't exist.

### 2. If the file doesn't exist yet, create it with a header

```markdown
# {YYYY-MM-DD} ({weekday})
```

Use the user's configured language for the weekday name (e.g., "星期四" or "Thursday").

### 3. Append the note

Add a section with a timestamp and the content:

```markdown

---

## {HH:MM} — {title}

{content}
```

Where:
- **title**: A short summary you generate from the content (keep it under 10 words)
- **content**: The user's input, lightly cleaned up for readability. Preserve
  the user's meaning exactly — don't rewrite or editorialize. Light formatting
  (adding bullet points, fixing obvious typos) is fine, but the substance should
  be the user's own words and intent.

### 4. Confirm to the user

After saving, respond with a brief confirmation like:

```
Saved to ~/reports/notes/2026-03-06.md (3rd note today)
```

Include how many notes are in today's file so the user has a sense of
accumulation.

## Examples

**User says:** "記一下，剛跟 Leo 開會討論了 agent orchestrator 的架構，決定用 event-driven 的方式"

**Result appended to `2026-03-06.md`:**

```markdown

---

## 14:32 — Agent orchestrator architecture meeting

與 Leo 開會討論 agent orchestrator 架構，決定採用 event-driven 方式。
```

**User says:** "log this: reviewed PR #42 for DeltaLLM, left comments about error handling in the retry logic"

**Result appended:**

```markdown

---

## 16:05 — PR #42 review

Reviewed PR #42 for DeltaLLM. Left comments about error handling in the retry logic.
```

## Edge Cases

| Situation | Behavior |
|---|---|
| User pastes a long meeting transcript | Summarize into key points, preserving decisions and action items |
| User gives no content, just says "daily note" | Ask what they'd like to record |
| Note content is in a different language than config | Write in whatever language the user provided — don't force translation |
| Config file doesn't exist and user skips setup | Default to `~/reports` and create config silently |
