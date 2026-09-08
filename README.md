# 魂师修炼RPG

Git-first source for the dedicated 魂师修炼RPG project.

## Authority model

- `main` HEAD is the current project source authority.
- `governance/project.md` owns Git-first governance.
- `runtime/registry.json` owns runtime routes, startup, access policy, external Skill dispatch, stable owner discovery, and compatibility checkpoint import registration.
- Stable domain owner files own gameplay/business truth.
- `12_状态存档.md` owns the state schema and lifecycle protocol; `state/current/SOUL_STATE_V1.yaml` is the canonical persisted adventure state in Git.
- `qa/` is the repository-owned regression suite.
- The compatibility runtime ZIP and its package-root `魂师修炼RPG_manifest.json` are generated/derived compatibility views, not source authority. The generated manifest embeds the exact source Git commit SHA; `MAJOR.MINOR` remains only a compatibility label.

## Runtime entry

Source checkout:

`governance/project.md → runtime/registry.json → registered startup/control dispatcher`

Compatibility runtime export:

`魂师修炼RPG_文档索引与版本状态.md → generated package-root 魂师修炼RPG_manifest.json`

The compatibility manifest mirrors the source registry and additionally carries the exact source Git commit, export membership, bytes and SHA-256 data.

## State and checkpoint compatibility

Current gameplay state is persisted directly in `state/current/SOUL_STATE_V1.yaml` and versioned by Git `main` history. Ordinary gameplay changes are committed through the registered `STATE_COMMIT` service as part of normal runtime persistence.

A plain `存档 / 保存进度` is therefore only a confirmation that the current Git state is already persisted; it does not generate a ZIP and does not increment compatibility `STATE_REV`. `读档 / 继续 / 恢复游戏` reads the canonical Git current state directly.

Existing `SOUL_STATE_V1` ZIPs are immutable compatibility checkpoints. Only an explicit external request such as `导出存档 / 导出备份 / 导出 ZIP` invokes `SAVE_EXPORT`; only an explicit `导入旧存档 / 恢复某个外部 ZIP` invokes `LOAD_SAVE`. Ordinary gameplay never requires uploading or regenerating a checkpoint ZIP.

## QA

Run:

```bash
python3 qa/validate_registry.py --project .
python3 qa/check_route_conflicts.py --project .
python3 qa/check_content_contracts.py
python3 qa/check_state_invariants.py --project .
python3 qa/check_git_first_architecture.py --project .
python3 qa/check_derived_export.py --project .
```

To build a compatibility runtime package:

```bash
python3 scripts/export_runtime_zip.py --project . --out dist/魂师修炼RPG_v3.11.zip
python3 qa/audit_runtime_package.py dist/魂师修炼RPG_v3.11.zip
```
