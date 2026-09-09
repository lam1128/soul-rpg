#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'state/current/SOUL_STATE_V1.yaml'
TEMP_FILES = [
    ROOT / 'tools/reorganize_layout_temp.py',
    ROOT / '.github/workflows/reorganize-layout-temp.yml',
]

FILE_MOVES = {
    '魂师修炼RPG_项目索引.md': 'governance/魂师修炼RPG_项目索引.md',
    '00P_专用项目入口协议.md': 'governance/00P_专用项目入口协议.md',
    '00A_RUNTIME_KERNEL.md': 'runtime/00A_RUNTIME_KERNEL.md',
    '00B_STARTUP_ROUTER_FAST_ENTRY.md': 'runtime/00B_STARTUP_ROUTER_FAST_ENTRY.md',
    '00C_CONTROL_INTENT_PRE_ROUTER.md': 'runtime/00C_CONTROL_INTENT_PRE_ROUTER.md',
    '01_人物性格.md': 'rules/01_人物性格.md',
    '02_叙事规则.md': 'rules/02_叙事规则.md',
    '03_外形参考.md': 'rules/03_外形参考.md',
    '10A_主角武魂模板.md': 'rules/10A_主角武魂模板.md',
    '10_战斗与成长系统.md': 'rules/10_战斗与成长系统.md',
    '11_世界与NPC.md': 'rules/11_世界与NPC.md',
    '12_状态存档.md': 'rules/12_状态存档.md',
    '13_交互协议.md': 'rules/13_交互协议.md',
    'DM_ONLY_B00_魂兽数据库.md': 'data/soul-beasts/DM_ONLY_B00_魂兽数据库.md',
    'DM_ONLY_C00_伙伴篇章库.md': 'data/companions/DM_ONLY_C00_伙伴篇章库.md',
    'DM_ONLY_S00_九名核心伙伴.md': 'data/companions/DM_ONLY_S00_九名核心伙伴.md',
    'DM_ONLY_E00_经济与药品.md': 'data/economy/DM_ONLY_E00_经济与药品.md',
    'DM_ONLY_R00_猎魂区域与遭遇表.md': 'data/hunting/DM_ONLY_R00_猎魂区域与遭遇表.md',
    'QA_项目验收规则.md': 'qa/QA_项目验收规则.md',
    'UI_统一规范_日常恢复与菜单.md': 'ui/UI_统一规范_日常恢复与菜单.md',
    'UI_统一规范_魂兽遭遇.md': 'ui/UI_统一规范_魂兽遭遇.md',
}
DIR_MOVES = {
    'DM_ONLY_C10_伙伴篇章': 'data/companions/episodes',
}

TEXT_SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.py'}


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def move_tracked(old: str, new: str) -> None:
    src = ROOT / old
    dst = ROOT / new
    if not src.exists():
        raise SystemExit(f'missing move source: {old}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    run('git', 'mv', old, new)


def rewrite_text_references() -> int:
    replacements = list(FILE_MOVES.items()) + [
        ('DM_ONLY_C10_伙伴篇章/', 'data/companions/episodes/'),
    ]
    replacements.sort(key=lambda item: len(item[0]), reverse=True)
    changed = 0
    for path in ROOT.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path == STATE or path in TEMP_FILES:
            continue
        raw = path.read_text(encoding='utf-8')
        new = raw
        for old, target in replacements:
            new = new.replace(old, target)
        if new != raw:
            path.write_text(new, encoding='utf-8', newline='\n')
            changed += 1
    return changed


def update_readme_layout() -> None:
    path = ROOT / 'README.md'
    text = path.read_text(encoding='utf-8')
    section = '''## 仓库目录\n\n```text\n.\n├── governance/      # 项目治理、项目索引、专用项目入口协议\n├── runtime/         # registry、runtime kernel、startup/control router\n├── rules/           # 人物、叙事、战斗、世界、状态、交互规则 owner\n├── data/            # 魂兽、猎魂、经济、伙伴与 45 个伙伴篇章\n├── ui/              # 重复游戏界面的正式 UI owner\n├── state/current/   # canonical Git current state\n├── qa/              # 验收规则与自动回归\n└── .github/         # GitHub Actions\n```\n\n根目录只保留 `README.md` 与 `.gitignore`；其余正式内容按职责进入对应目录。目录层级不改变 runtime 的按需读取策略，实际读取仍只认 `runtime/registry.json` 当前登记的 owner / sources。\n\n'''
    if '## 仓库目录' not in text:
        marker = '## 运行顺序\n'
        if marker not in text:
            raise SystemExit('README insertion marker missing')
        text = text.replace(marker, section + marker, 1)
    path.write_text(text, encoding='utf-8', newline='\n')


def enforce_root_hygiene() -> None:
    path = ROOT / 'qa/check_repository_hygiene.py'
    text = path.read_text(encoding='utf-8')
    marker = "    if not files:\n        fail('repository has no tracked files')\n"
    addition = """    if not files:\n        fail('repository has no tracked files')\n\n    root_files = sorted(rel for rel in files if '/' not in rel)\n    allowed_root_files = ['.gitignore', 'README.md']\n    if root_files != allowed_root_files:\n        fail('root must contain only README.md and .gitignore; found: ' + ', '.join(root_files))\n"""
    if marker not in text:
        raise SystemExit('repository hygiene insertion marker missing')
    text = text.replace(marker, addition, 1)
    path.write_text(text, encoding='utf-8', newline='\n')


def remove_temp_runner() -> None:
    for path in TEMP_FILES:
        if path.exists():
            path.unlink()
    tools = ROOT / 'tools'
    if tools.exists() and not any(tools.iterdir()):
        tools.rmdir()


def run_global_qa() -> None:
    commands = [
        ['python3', 'qa/check_repository_hygiene.py', '--project', '.'],
        ['python3', 'qa/validate_registry.py', '--project', '.'],
        ['python3', 'qa/check_route_conflicts.py', '--project', '.'],
        ['python3', 'qa/check_content_contracts.py'],
        ['python3', 'qa/check_state_invariants.py', '--project', '.'],
        ['python3', 'qa/check_git_first_architecture.py', '--project', '.'],
    ]
    for command in commands:
        run(*command)


def main() -> None:
    before_state = sha256(STATE)

    for old, new in FILE_MOVES.items():
        move_tracked(old, new)
    for old, new in DIR_MOVES.items():
        move_tracked(old, new)

    rewritten = rewrite_text_references()
    update_readme_layout()
    enforce_root_hygiene()

    if sha256(STATE) != before_state:
        raise SystemExit('canonical state changed during layout migration')

    episode_dir = ROOT / 'data/companions/episodes'
    episodes = sorted(episode_dir.glob('CORE_*_C??.md'))
    if len(episodes) != 45:
        raise SystemExit(f'expected 45 episode files, got {len(episodes)}')

    remove_temp_runner()
    run('git', 'add', '-A')
    run('git', 'diff', '--cached', '--check')
    run_global_qa()

    print(json.dumps({
        'status': 'PASS',
        'moved_files': len(FILE_MOVES),
        'moved_directories': len(DIR_MOVES),
        'episodes': len(episodes),
        'rewritten_text_files': rewritten,
        'canonical_state_unchanged': True,
        'root_files': ['.gitignore', 'README.md'],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
