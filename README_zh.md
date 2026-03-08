# AT2 Skills

用於每日筆記與週報產生的 Claude Code Skills。

## Skills 總覽

### daily-note
快速記錄筆記、會議摘要、想法或任何上下文，存入以日期命名的 markdown 檔案。同一天的多筆記錄會自動追加為帶時間戳的段落。

### weekly-report
自動彙整以下資料來源，產生每日工作摘要與週報：
- Git commits（自動掃描多個 repo）
- Claude 對話歷史（解析 `~/.claude/projects/` 下的 JSONL 檔案）
- Daily notes（由 `daily-note` skill 建立的筆記）
- 使用者補充（會議、blockers、下週計畫等）

支援彈性工作流程：可以每天跑日報，也可以週末一次跑週報。沒有日報的天數會自動從 git 和對話歷史補齊。

## 安裝

### 方法一：Plugin Marketplace（推薦）

在 Claude Code 中執行：

```
/plugin marketplace add theohsiung/at2_skills
/plugin install at2-skills@at2-skills
```

第一行註冊 marketplace，第二行安裝兩個 skill。安裝後 skill 名稱為 `at2-skills:daily-note` 和 `at2-skills:weekly-report`。

### 方法二：手動安裝

```bash
# Clone repo
git clone https://github.com/theohsiung/at2_skills.git

# 在 Claude Code 中逐一加入
/skill add /path/to/at2_skills/skills/daily-note
/skill add /path/to/at2_skills/skills/weekly-report
```

### 驗證安裝

安裝後，以下說法會自動觸發對應 skill：
- 「記一下...」/「log this...」→ 觸發 `daily-note`
- 「日報」/「週報」/「daily summary」/「weekly report」→ 觸發 `weekly-report`

## 快速開始

### 1. 記錄第一筆筆記

```
你：記一下，剛跟 Leo 開會討論 agent 架構，決定用 event-driven

Claude：筆記將儲存到 ~/reports。要存為預設設定嗎？(yes/no)
你：yes

Claude：已儲存到 ~/reports/notes/2026-03-06.md（今天第 1 筆）
```

### 2. 產生每日摘要

```
你：今天做了什麼？

Claude：使用 "cortex" 設定 (Agentic AI System)，OK？
你：OK

Claude：自動收集 2026-03-06 的資料：
  - Git: 2 個 repo 共 3 筆 commit
  - 對話: 5 個 Claude 對話
  - 筆記: 2 筆 daily notes

  還有什麼要補充的嗎？
  1. 沒記到的會議？
  2. 非程式工作（文件、review、demo）？
  3. Blockers？

你：沒了

Claude：✅ 日報已儲存到 ~/reports/week10/2026-03-06/summary.md
```

### 3. 產生週報

```
你：幫我產生這週的週報

Claude：使用 "cortex" 設定 (Agentic AI System)，OK？
你：OK

Claude：✅ 週報已儲存到 ~/reports/week10/weekly_report.md
  請檢查看看有沒有要調整的地方。
```

## 設定

兩個 skill 共用一份 `reports-config.json`。設定檔是**可選的** — 你可以每次在對話中提供所有設定，對話中說的內容會覆蓋設定檔。

第一次使用時會透過互動問答建立設定，你也可以手動建立。

### 設定檔位置

Skill 依以下順序尋找設定檔：
1. `./reports-config.json`（目前工作目錄）
2. `~/reports-config.json`（home 目錄）

### 單一團隊設定

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
    "Ongoing": "依照 sprint checkpoints 執行"
  }
}
```

### 設定欄位說明

| 欄位 | 必填 | 說明 |
|---|---|---|
| `report_dir` | 是 | 筆記與報告的儲存位置（例如 `~/reports`） |
| `repo_paths` | 是* | 要掃描的 git repo 路徑。*僅 `weekly-report` 需要 |
| `author_email` | 是* | 你的 git email，用於篩選 commits。*未設定時自動從 `git config user.email` 取得 |
| `language` | 否 | 報告語言（預設：跟隨對話語言） |
| `team_name` | 否 | 顯示在報告標題的團隊名稱 |
| `team_members` | 否 | 顯示在報告標題的團隊成員 |
| `report_author` | 否 | 顯示在報告標題的作者名稱 |
| `milestone` | 否 | 顯示在週報中的里程碑 |

### 多團隊設定（profiles）

如果你同時在多個團隊工作，可以使用 profiles：

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
        "By Q2": "上線 feature X"
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

頂層欄位（`report_dir`、`author_email`、`language`）跨 profile 共用，每個 profile 覆蓋團隊專屬設定。

切換 profile：

```
你：用 team-b 的設定產生週報
```

### 對話式覆蓋

不需要設定檔也能用，直接在對話中告訴 Claude：

```
你：幫我產生週報，repos 在 ~/projects/my-app 和 ~/projects/my-lib，
    team 是 "Backend Team"，成員有 Alice 和 Bob
```

或在有設定檔的情況下覆蓋特定欄位：

```
你：產生週報，但這次多掃 ~/projects/extra-repo
```

## 輸出結構

```
{report_dir}/
  reports-config.json              ← 設定檔（如果有儲存）
  notes/                           ← daily-note 寫入這裡
    2026-03-03.md
    2026-03-04.md
    2026-03-06.md
  week10/                          ← ISO 週次
    2026-03-03/
      summary.md                   ← 每日摘要
    2026-03-06/
      summary.md
    weekly_report.md               ← 週報
  week11/
    ...
```

### Daily note 格式

```markdown
# 2026-03-06 (星期五)

---

## 14:32 — Agent orchestrator 架構會議

與 Leo 開會討論 agent orchestrator 架構，決定採用 event-driven 方式。

---

## 16:05 — PR #42 review

Review 了 DeltaLLM 的 PR #42，留了關於 retry logic 錯誤處理的 comment。
```

### Daily summary 格式

```markdown
# Daily Summary — 2026-03-06 (星期五)

## Completed
- 完成 DeltaLLM CLI 的 session persistence 功能（PR #38）
- 修正 parser 因缺少 null-check 造成的 crash

## In Progress
- 研究 workflow drawing agent 的可行方案

## Meetings & Collaboration
- 與 Leo 討論 orchestrator 架構

## Notes
- 供週報使用的重點摘要
```

### Weekly report 格式

```markdown
# Weekly Report — Week 10 (2026-03-02 ~ 2026-03-06)
**Author:** Your Name
**Team:** My Team [Alice, Bob, Charlie]

## Milestone Checkpoints
- By Mar/E: Release v1.0

## Executive Summary
（2-4 句敘述本週進展的摘要段落）

## Completed This Week
### Project A
- 完成項目 1
- 完成項目 2

## In Progress
### Project A
- 進行中的工作

## Plan for Next Week
- 具體的行動項目 1
- 具體的行動項目 2
```

## 資料來源

### Git commits
Skill 使用 `git log` 掃描設定的 repos，依你的 author email 篩選。原始 commit 訊息會被轉寫為人類可讀的成果描述（例如 `fix: null check` → 「修正 parser 因缺少 null-check 造成的初始化 crash」）。

### Claude 對話歷史
Skill 讀取 `~/.claude/projects/` 下的 JSONL 檔案，了解你這一天/這一週跟 Claude 討論了什麼。透過內建的 Python 腳本（`scripts/extract_conversations.py`）完成。

### Daily notes
透過 `daily-note` skill 記錄的筆記會自動被納入摘要和報告。

### 使用者補充
自動收集資料後，skill 會詢問你是否要補充其他內容（會議、非程式工作、blockers 等）。說「沒了」或「looks good」即可跳過。

## 系統需求

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.10+（用於對話歷史擷取腳本）
- Git（用於 commit 掃描）

## 授權

Apache 2.0 — 詳見 [LICENSE](LICENSE)。
