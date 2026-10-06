#!/usr/bin/env python3
"""
install.py — установщик хука session-log для Claude Code.

Что делает:
  1. Копирует hook/session-log.py в ~/.claude/hooks/
  2. Прописывает Stop-хук в ~/.claude/settings.json
  3. Создаёт нужные папки, если их нет

Запуск: python install.py
Удаление: python install.py --uninstall
"""
import json
import shutil
import sys
from pathlib import Path

HOME = Path.home()
HOOKS_DIR = HOME / ".claude" / "hooks"
SETTINGS = HOME / ".claude" / "settings.json"
HOOK_SRC = Path(__file__).parent / "hook" / "session-log.py"
HOOK_DST = HOOKS_DIR / "session-log.py"
HOOK_CMD = str(HOOK_DST).replace("\\", "\\\\")

HOOK_ENTRY = {
    "matcher": "",
    "hooks": [{"type": "command", "command": f"python {HOOK_DST}"}]
}


def load_settings():
    if SETTINGS.exists():
        try:
            return json.loads(SETTINGS.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_settings(data):
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def install():
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HOOK_SRC, HOOK_DST)
    print(f"✓ Скопировано: {HOOK_DST}")

    cfg = load_settings()
    hooks = cfg.setdefault("hooks", {})
    stop_hooks = hooks.setdefault("Stop", [])

    already = any(
        h.get("hooks", [{}])[0].get("command", "").endswith("session-log.py")
        for h in stop_hooks
    )
    if not already:
        stop_hooks.append(HOOK_ENTRY)
        save_settings(cfg)
        print("✓ Хук добавлен в settings.json")
    else:
        print("— Хук уже был в settings.json, пропускаю")

    log = HOME / ".claude" / "session-log.md"
    if not log.exists():
        log.write_text("# Лог сессий Claude Code\n", encoding="utf-8")
        print(f"✓ Создан лог: {log}")

    print("\n✅ Готово! Лог будет здесь:")
    print(f"   {HOME / '.claude' / 'session-log.md'}")
    print("   Записи появляются после сессий, в которых менялись файлы.")


def uninstall():
    if HOOK_DST.exists():
        HOOK_DST.unlink()
        print(f"✓ Удалено: {HOOK_DST}")

    cfg = load_settings()
    stop_hooks = cfg.get("hooks", {}).get("Stop", [])
    filtered = [
        h for h in stop_hooks
        if not h.get("hooks", [{}])[0].get("command", "").endswith("session-log.py")
    ]
    if len(filtered) < len(stop_hooks):
        cfg["hooks"]["Stop"] = filtered
        if not cfg["hooks"]["Stop"]:
            del cfg["hooks"]["Stop"]
        if not cfg["hooks"]:
            del cfg["hooks"]
        save_settings(cfg)
        print("✓ Хук убран из settings.json")

    print("✅ Удалено.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
