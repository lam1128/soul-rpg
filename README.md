# 魂师修炼RPG

Git-first source for the dedicated 魂师修炼RPG project.

## Authority model

- `main` HEAD is the current project source authority.
- `governance/project.md` owns Git-first governance.
- `runtime/registry.json` owns runtime routes, startup, access policy, external Skill dispatch, stable owner discovery, and compatibility checkpoint import registration.
- Stable domain owner files own gameplay/business truth.
- `12_状态存档.md` owns the state schema and lifecycle protocol; `state/current/SOUL_STATE_V1.yaml` is the canonical persisted adventure state in Git.
- `qa/` is the repository-owned regression suite.
- `魂师修炼RPG_manifest.json` and the compatibility runtime ZIP are generated/derived compatibility views, not source authority.

## Runtime entry

Source checkout:

`governance/project.md → runtime/registry.json → registered startup/control dispatcher`

Compatibility runtime export:

`魂师修炼RPG_文档索引与版本状态.md → 魂师修炼RPG_manifest.json`

The compatibility manifest mirrors the source registry and additionally carries export membership, bytes and SHA-256 data.

## State and checkpoint compatibility

Current gameplay state is persisted directly in `state/current/SOUL_STATE_V1.yaml` and versioned by Git `main` history. Existing `SOUL_STATE_V1` ZIPs are immutable compatibility checkpoints: `LOAD_SAVE` explicitly imports/restores one into the Git state owner, while `SAVE_EXPORT` creates a portable checkpoint from the Git state. Ordinary gameplay persistence no longer depends on exporting a ZIP.

## QA

Run:

```bash
python3 qa/validate_registry.py --project .
python3 qa/check_route_conflicts.py --project .
python3 qa/check_state_invariants.py --project .
python3 qa/check_git_first_architecture.py --project .
python3 qa/check_derived_export.py --project .
```

To build a compatibility runtime package:

```bash
python3 scripts/export_runtime_zip.py --project . --out dist/魂师修炼RPG_v3.11.zip
python3 qa/audit_runtime_package.py dist/魂师修炼RPG_v3.11.zip
```
