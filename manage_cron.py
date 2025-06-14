#!/usr/bin/env python3
"""manage_mc_backup.py

シングルファイルで完結する Minecraft ワールド Git バックアップ & cron 管理ツール。

Usage:
    python manage_mc_backup.py enable       # cron に毎時バックアップを登録
    python manage_mc_backup.py disable      # cron からバックアップジョブを除去
    python manage_mc_backup.py status       # cron の状態を確認
    python manage_mc_backup.py run-backup   # 直ちにバックアップを実行（cron 用）

* cron ジョブは 0 分（毎時）に実行。
* ジョブ行は CRON_MARKER で識別し、既存の crontab には影響しない。

環境変数や PATH 問題を回避するため、cron 行には
    <絶対パスの python> <絶対パスの本スクリプト> run-backup
を埋め込む。
"""
from __future__ import annotations

import shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
from typing import List

# ────────────────────────────────────────────────
# ▼ ユーザ設定 ----------------------------------
WORLD_BACKUP_DIR = Path("/home/tetsuro/Minecraft/mc-250608/world_data/world")
GIT_REPO_PATH = Path("/home/tetsuro/Minecraft/mc-250608")
COMMIT_MESSAGE_TEMPLATE = "Auto backup: {timestamp}"
# ▲ ユーザ設定 ----------------------------------
# ────────────────────────────────────────────────

CRON_MARKER = "# MC_WORLD_BACKUP"
BACKUP_HOUR = 0  # 毎時 0 分に実行 → "0 * * * *"
BACKUP_TMP_PREFIX = "mc_backup_"

# ────────────────────────────────────────────────
# Cron ユーティリティ
# ────────────────────────────────────────────────

def _run(cmd: List[str], **kw):
    """subprocess.run の簡易ラッパー (check=True & text=True デフォルト)"""
    return subprocess.run(cmd, check=True, text=True, **kw)

def backup_crontab() -> str:
    """現 crontab を ~/.crontab_backups/ に退避。空なら空文字を返す。"""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        content = result.stdout if result.returncode == 0 else ""
    except FileNotFoundError:
        print("Error: crontab command not found. Install cron?", file=sys.stderr)
        sys.exit(1)

    if not content.strip():
        return ""  # 空 crontab

    backup_dir = Path.home() / ".crontab_backups"
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"crontab_backup_{ts}"
    backup_file.write_text(content)
    print(f"[cron] backed‑up current crontab → {backup_file}")
    return content

def get_current_crontab() -> str:
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""

def build_cron_line() -> str:
    """毎時 BACKUP_HOUR 分に run-backup する cron 行を生成"""
    python = Path(sys.executable).resolve()
    script = Path(__file__).resolve()
    minute_field = BACKUP_HOUR
    return f"{minute_field} * * * * {python} {script} run-backup {CRON_MARKER}"

# ────────────────────────────────────────────────
# Git バックアップ処理
# ────────────────────────────────────────────────

def backup_world() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_dir = Path("/tmp") / f"{BACKUP_TMP_PREFIX}{timestamp}"
    try:
        print("[backup] copying world directory…")
        shutil.copytree(WORLD_BACKUP_DIR, tmp_dir)

        if not (GIT_REPO_PATH / ".git").exists():
            print("[backup] git repo not found → git init")
            _run(["git", "init", str(GIT_REPO_PATH)])

        # Git リポジトリ内の world_data ディレクトリにタイムスタンプ付きでバックアップ
        target_base = GIT_REPO_PATH / "world_data"
        target_dir = target_base / f"world_backup_{timestamp}"
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(tmp_dir, target_dir)

        print("[git] staging changes …")
        _run(["git", "add", "-A"], cwd=GIT_REPO_PATH)

        # 差分が無いなら何もしない
        diff_ret = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=GIT_REPO_PATH,
            text=True
        )
        if diff_ret.returncode == 0:
            print("[git] no changes; skipping backup")
            return

        # 差分あり → ブランチを切る
        branch_name = f"world_backup_{timestamp}"
        print(f"[git] creating and switching to branch '{branch_name}' …")
        _run(["git", "checkout", "-B", branch_name], cwd=GIT_REPO_PATH)

        # コミット
        msg = COMMIT_MESSAGE_TEMPLATE.format(timestamp=timestamp)
        _run(["git", "commit", "-m", msg], cwd=GIT_REPO_PATH)
        print(f"[git] committed: '{msg}'")

        # プッシュ
        print(f"[git] pushing branch '{branch_name}' to origin…")
        _run(["git", "push", "-u", "origin", branch_name], cwd=GIT_REPO_PATH)
        print("[git] push complete")

        # クリーンアップ：バックアップフォルダを削除
        print(f"[cleanup] removing backup dir {target_dir}…")
        shutil.rmtree(target_dir)
        print("[cleanup] done")
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)

# ────────────────────────────────────────────────
# CLI エントリ
# ────────────────────────────────────────────────

def print_status() -> None:
    cron = get_current_crontab()
    lines = [l for l in cron.splitlines() if CRON_MARKER in l]
    if lines:
        print("✓ Backup cron job is ENABLED:")
        for l in lines:
            print("  ", l)
    else:
        print("✗ Backup cron job is DISABLED")


def enable_cron() -> None:
    cron_content = backup_crontab()
    if CRON_MARKER in cron_content:
        print("[!] cron job already enabled; aborting")
        return

    new_cron = cron_content.strip() + "\n" + build_cron_line() + "\n"
    _apply_crontab(new_cron)
    print("[cron] backup job ENABLED (hourly)")


def disable_cron() -> None:
    cron_content = backup_crontab()
    lines = [l for l in cron_content.splitlines() if CRON_MARKER not in l]
    new_cron = "\n".join(lines) + "\n" if lines else ""
    _apply_crontab(new_cron)
    print("[cron] backup job DISABLED")


def _apply_crontab(content: str) -> None:
    temp = Path("/tmp/temp_crontab")
    temp.write_text(content)
    _run(["crontab", str(temp)])
    temp.unlink(missing_ok=True)

# ────────────────────────────────────────────────
# main
# ────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        _usage_and_exit()

    cmd = sys.argv[1]
    if cmd == "enable":
        enable_cron()
    elif cmd == "disable":
        disable_cron()
    elif cmd == "status":
        print_status()
    elif cmd == "run-backup":
        backup_world()
    else:
        _usage_and_exit()


def _usage_and_exit():
    print(__doc__)
    sys.exit(1)

if __name__ == "__main__":
    main()
