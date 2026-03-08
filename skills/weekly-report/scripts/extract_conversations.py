#!/usr/bin/env python3
"""Extract Claude conversation summaries from ~/.claude/projects/ JSONL files.

Usage:
    python3 extract_conversations.py --date 2026-03-06
    python3 extract_conversations.py --date 2026-03-06 --output conversations.json
    python3 extract_conversations.py --since 2026-03-03 --until 2026-03-07
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def find_jsonl_files(claude_dir: Path, since: str, until: str) -> list[Path]:
    """Find JSONL conversation files within the date range."""
    since_dt = datetime.fromisoformat(since + "T00:00:00")
    until_dt = datetime.fromisoformat(until + "T23:59:59")

    results = []
    projects_dir = claude_dir / "projects"
    if not projects_dir.exists():
        return results

    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for f in project_dir.iterdir():
            if not f.suffix == ".jsonl" or not f.is_file():
                continue
            # Skip subagent files
            if "subagents" in str(f):
                continue
            # Check modification time
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if since_dt <= mtime <= until_dt:
                results.append(f)

    return sorted(results, key=lambda f: f.stat().st_mtime)


def extract_project_name(file_path: Path) -> str:
    """Extract human-readable project name from encoded path."""
    parent = file_path.parent.name
    # Encoded format: -home-user-projects-myproject
    parts = parent.split("-")
    # Find the last meaningful segment(s)
    if "projects" in parts:
        idx = parts.index("projects")
        project_parts = parts[idx + 1 :]
        if project_parts:
            return "-".join(project_parts)
    return parent


def parse_jsonl(file_path: Path, since: str, until: str) -> dict | None:
    """Parse a JSONL file and extract conversation summary."""
    since_dt = datetime.fromisoformat(since + "T00:00:00")
    until_dt = datetime.fromisoformat(until + "T23:59:59")

    user_messages = []
    session_id = None
    cwd = None
    git_branch = None
    first_timestamp = None
    last_timestamp = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type")
            timestamp_str = entry.get("timestamp")

            if not timestamp_str:
                continue

            try:
                ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                ts_naive = ts.replace(tzinfo=None)
            except (ValueError, AttributeError):
                continue

            if ts_naive < since_dt or ts_naive > until_dt:
                continue

            if not first_timestamp:
                first_timestamp = timestamp_str
            last_timestamp = timestamp_str

            if not session_id and entry.get("sessionId"):
                session_id = entry["sessionId"]
            if not cwd and entry.get("cwd"):
                cwd = entry["cwd"]
            if not git_branch and entry.get("gitBranch"):
                git_branch = entry["gitBranch"]

            if entry_type == "user":
                msg = entry.get("message", {})
                content = msg.get("content", "")
                text = ""
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            t = block.get("text", "")
                            # Skip system/IDE metadata
                            if not t.startswith("<ide_") and not t.startswith("<system"):
                                text_parts.append(t)
                        elif isinstance(block, str):
                            text_parts.append(block)
                    text = "\n".join(text_parts)

                if text.strip():
                    # Keep first 200 chars of each message
                    user_messages.append(text.strip()[:200])

    if not user_messages:
        return None

    return {
        "session_id": session_id,
        "project": extract_project_name(file_path),
        "cwd": cwd,
        "git_branch": git_branch,
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "message_count": len(user_messages),
        "first_messages": user_messages[:5],  # First 5 user messages as preview
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract Claude conversation summaries"
    )
    parser.add_argument("--date", help="Single date (YYYY-MM-DD)")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument(
        "--claude-dir",
        default=str(Path.home() / ".claude"),
        help="Path to .claude directory",
    )

    args = parser.parse_args()

    if args.date:
        since = args.date
        until = args.date
    elif args.since and args.until:
        since = args.since
        until = args.until
    else:
        # Default to today
        since = datetime.now().strftime("%Y-%m-%d")
        until = since

    claude_dir = Path(args.claude_dir)
    files = find_jsonl_files(claude_dir, since, until)

    conversations = []
    for f in files:
        result = parse_jsonl(f, since, until)
        if result:
            conversations.append(result)

    output = json.dumps(conversations, indent=2, ensure_ascii=False)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Wrote {len(conversations)} conversations to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
