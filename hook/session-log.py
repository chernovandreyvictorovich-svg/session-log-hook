#!/usr/bin/env python3
"""
session-log.py — хук Claude Code: фиксирует итог сессии в ~/.claude/session-log.md.

Пишет запись только когда в проекте были изменения (git diff).
Запускается автоматически при остановке Claude (событие Stop).
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

data = json.loads(sys.stdin.read())
cwd = data.get("cwd", os.getcwd())
log_file = Path.home() / ".claude" / "session-log.md"

diff_stat = ""
try:
    r = subprocess.run(
        ["git", "diff", "--stat", "HEAD"],
        cwd=cwd, capture_output=True, text=True, timeout=5, encoding="utf-8"
    )
    diff_stat = r.stdout.strip()
except Exception:
    pass

if not diff_stat:
    try:
        r = subprocess.run(
            ["git", "status", "--short"],
            cwd=cwd, capture_output=True, text=True, timeout=5, encoding="utf-8"
        )
        diff_stat = r.stdout.strip()
    except Exception:
        pass

if not diff_stat:
    sys.exit(0)

project = Path(cwd).name
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

entry = f"\n## {timestamp} — {project}\n\n```\n{diff_stat}\n```\n"

log_file.parent.mkdir(parents=True, exist_ok=True)
with open(log_file, "a", encoding="utf-8") as f:
    f.write(entry)
