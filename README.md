# 魂师修炼RPG

Git-first 的《魂师修炼RPG》项目源码仓库。当前规则、路由、治理与正式游戏状态都以 Git `main` HEAD 为权威；聊天记录、旧 ZIP、旧运行包和历史副本都不是当前运行主源。

## 核心入口

| 职责 | 唯一入口 |
|---|---|
| 项目治理 | `governance/project.md` |
| 机器运行注册表 | `runtime/registry.json` |
| 当前正式游戏状态 | `state/current/SOUL_STATE_V1.yaml` |
| 状态 schema / 生命周期 | `12_状态存档.md` |
| 项目验收规则 | `QA_项目验收规则.md` |
| 自动回归 | `qa/` + `.github/workflows/qa.yml` |
| 兼容运行包成员 | `compatibility/runtime-members.json` |
| 兼容运行包导出 | `scripts/export_runtime_zip.py` |

业务规则继续由各稳定 owner 文件独占。registry 只负责发现 owner、route、control intent、访问策略、Skill 接口与状态生命周期，不复制战斗、经济、人物、篇章或 UI 的业务常量。

## 运行顺序

Git 源码模式：

```text
governance/project.md
→ runtime/registry.json
→ startup router / control pre-router
→ 当前命中的 route 或 Skill
```

普通“读档 / 继续 / 恢复游戏”直接读取 canonical Git state；不会自动寻找或上传旧 checkpoint。

## 存档模型

日常游戏进度在合法行动结算后通过 registry 登记的 `STATE_COMMIT` 写入：

```text
state/current/SOUL_STATE_V1.yaml
```

因此：

- `存档 / 保存进度`：只确认当前 Git state 已持久化，不生成 ZIP，不增加兼容 `STATE_REV`。
- `读档 / 继续 / 恢复游戏`：直接从 Git current state 恢复。
- `导出存档 / 导出备份 / 导出 ZIP`：只有明确要求外部便携文件时才进入兼容 `SAVE_EXPORT`。
- `导入旧存档 / 恢复某个外部 ZIP`：只有明确点名外部 checkpoint 时才进入 `LOAD_SAVE`。

旧 `SOUL_STATE_V1` ZIP 可以作为兼容历史备份存在于 Git 之外，但不会参与普通运行，也不需要上传到项目源。

## 兼容运行包

兼容 runtime ZIP 是从当前已提交 Git source 现场生成的派生视图，不提交回仓库。包内 `魂师修炼RPG_manifest.json` 会记录：

- 当前 registry 镜像；
- 正式 runtime 成员；
- 每个成员的 bytes / SHA-256；
- 生成该包的精确 Git commit SHA。

兼容 `MAJOR.MINOR` 只是包标签，真正源码身份始终是 Git commit SHA。

## 全局 QA

本地完整检查：

```bash
python3 qa/check_repository_hygiene.py --project .
python3 qa/validate_registry.py --project .
python3 qa/check_route_conflicts.py --project .
python3 qa/check_content_contracts.py
python3 qa/check_state_invariants.py --project .
python3 qa/check_git_first_architecture.py --project .
python3 qa/check_derived_export.py --project .
```

仓库卫生检查会阻止 ZIP、backup、patch、build/dist、临时缓存、持久化兼容 manifest，以及写死的兼容包版本文件名重新进入 source tree。

如需显式生成并审计兼容运行包：

```bash
RELEASE="$(python3 -c "import json; print(json.load(open('runtime/registry.json', encoding='utf-8'))['release'])")"
python3 scripts/export_runtime_zip.py --project . --out-dir dist
python3 qa/audit_runtime_package.py "dist/魂师修炼RPG_v${RELEASE}.zip"
```

生成目录已被 `.gitignore` 排除；兼容包只用于明确的导出、审计或无 Git checkout 的 fallback 场景。
