#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import yaml


def fail(message: str) -> None:
    raise SystemExit('FAIL: ' + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', default='.')
    args = parser.parse_args()

    project = Path(args.project)
    registry = json.loads((project / 'runtime/registry.json').read_text(encoding='utf-8'))
    state_model = registry.get('state_model', {})

    if state_model.get('schema_owner') != '12_状态存档.md':
        fail('state schema owner changed')
    owner = state_model.get('current_state_owner')
    if owner != 'state/current/SOUL_STATE_V1.yaml':
        fail('current_state_owner mismatch')

    state_path = project / owner
    if not state_path.is_file():
        fail('canonical current state missing')
    try:
        document = yaml.safe_load(state_path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'current state YAML invalid: {exc}')
    if not isinstance(document, dict):
        fail('current state must be mapping')

    header = document.get('SAVE_HEADER', {})
    if header.get('CHECKPOINT_FORMAT_VERSION') != 'SOUL_STATE_V1':
        fail('checkpoint format mismatch')
    if str(header.get('SCHEMA_VERSION')) != '2.1':
        fail('schema version mismatch')
    if not header.get('ADVENTURE_ID'):
        fail('ADVENTURE_ID missing')
    if not isinstance(header.get('STATE_REV'), int) or header['STATE_REV'] < 1:
        fail('STATE_REV invalid')

    for legacy in ('RUNTIME_PACKAGE', 'RUNTIME_PACKAGE_SHA256', 'RUNTIME_RELEASE'):
        if legacy in header:
            fail(f'canonical Git state still contains legacy package binding: {legacy}')

    if state_model.get('persisted_current_source') != 'state_model.current_state_owner':
        fail('Git state not persisted authority')
    if state_model.get('project_state_persistence') != 'git_main_head':
        fail('project state persistence is not git_main_head')
    if state_model.get('checkpoint_persistence') != 'derived_import_export_only_non_authoritative':
        fail('checkpoint role mismatch')

    external = registry.get('external_sources', {}).get('checkpoint_import')
    if not external or external.get('checkpoint_format') != 'SOUL_STATE_V1':
        fail('checkpoint_import source missing')
    if external.get('role') != 'non_authoritative_compatibility_import_candidate':
        fail('checkpoint_import role must be non-authoritative')

    service = registry.get('internal_services', {}).get('state_commit', {})
    if service.get('skill') != 'soul-rpg-project-maintainer' or service.get('operation') != 'STATE_COMMIT':
        fail('STATE_COMMIT interface missing')

    controls = registry.get('control_intents', {})
    for name in ['LOAD_SAVE', 'SAVE_EXPORT', 'STATE_MIGRATION']:
        control = controls.get(name, {})
        if control.get('dispatch_type') != 'skill' or control.get('skill') != 'soul-rpg-save-manager':
            fail(f'{name} dispatcher changed')

    current = controls.get('SAVE_CURRENT', {})
    if current.get('dispatch_type') != 'route' or current.get('route') != 'readonly_query':
        fail('SAVE_CURRENT must be readonly_query route')
    if current.get('recognition_owner') != '13_交互协议.md':
        fail('SAVE_CURRENT recognition owner mismatch')
    if '§2C SAVE_CURRENT' not in current.get('recognition_sections', []):
        fail('SAVE_CURRENT recognition section missing')
    if controls['SAVE_EXPORT'].get('priority', 999) >= current.get('priority', 999):
        fail('explicit SAVE_EXPORT must be checked before SAVE_CURRENT')

    readonly = registry.get('topic_routes', {}).get('readonly_query', {})
    if readonly.get('state_access') != 'READ_CONSUMER':
        fail('readonly_query state access changed')

    interaction = (project / '13_交互协议.md').read_text(encoding='utf-8')
    ui = (project / 'UI_统一规范_日常恢复与菜单.md').read_text(encoding='utf-8')
    schema = (project / '12_状态存档.md').read_text(encoding='utf-8')
    if '## 2C. SAVE_CURRENT｜Git 当前进度确认' not in interaction:
        fail('SAVE_CURRENT interaction contract missing')
    if '只有用户明确说“导出存档' not in interaction:
        fail('interaction does not separate save from export')
    if '## 16. 存档确认｜Git current state' not in ui:
        fail('Git save confirmation UI missing')
    if '单独的“存档 / 保存进度 / 存一下档”不得命中本事务' not in schema:
        fail('SAVE_EXPORT exclusion for bare save missing')
    if '不再承担“等到导出时才清理”的职责' not in schema:
        fail('canonical state cleanup still depends on export')
    if '不是 Git current state 的源码或运行权威' not in schema:
        fail('compatibility package metadata authority boundary missing')

    ignored = (project / '.gitignore').read_text(encoding='utf-8')
    if 'state/' in {line.strip() for line in ignored.splitlines()}:
        fail('state directory is ignored by git')

    accidental = []
    for path in project.rglob('SOUL_STATE_V1.yaml'):
        rel = str(path.relative_to(project))
        if rel != owner and '.git' not in path.parts:
            accidental.append(rel)
    if accidental:
        fail('multiple canonical-like state files: ' + ','.join(accidental))

    print(json.dumps({
        'status': 'PASS',
        'checkpoint_mode': 'git_current_state',
        'state_owner': owner,
        'state_rev': header['STATE_REV'],
        'save_current_route': current.get('route'),
        'save_skill': 'soul-rpg-save-manager',
        'legacy_package_bindings': 0,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
