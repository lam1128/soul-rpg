# 魂师修炼RPG

Git-only 的《魂师修炼RPG》项目源码仓库。当前规则、路由、治理与正式游戏状态都以 Git `main` HEAD 为唯一权威；聊天记录、旧 ZIP、旧运行包、历史副本和派生导出物都不是当前运行主源。

## 核心入口

| 职责 | 唯一入口 |
|---|---|
| 项目治理 | `governance/project.md` |
| 机器运行注册表 | `runtime/registry.json` |
| 项目索引 | `魂师修炼RPG_项目索引.md` |
| 当前正式游戏状态 | `state/current/SOUL_STATE_V1.yaml` |
| 状态 schema / 生命周期 | `12_状态存档.md` |
| 项目验收规则 | `QA_项目验收规则.md` |
| 自动回归 | `qa/` + `.github/workflows/qa.yml` |

业务规则继续由各稳定 owner 文件独占。registry 只负责发现 owner、route、control intent、访问策略、Skill 接口与状态生命周期，不复制战斗、经济、人物、篇章或 UI 的业务常量。

## 运行顺序

```text
governance/project.md
→ runtime/registry.json
→ startup router / control pre-router
→ 当前命中的 route 或 Skill
```

普通“读档 / 继续 / 恢复游戏”直接读取 canonical Git state；不会自动寻找或上传旧 checkpoint。

## Git 身份，不使用项目版本号

本项目**不维护 `v3.11`、`4.0`、SemVer、MAJOR.MINOR 等项目 release 号**。

- 当前项目的精确身份 = `main` 当前 Git commit SHA。
- 历史版本 = Git commit history。
- 回滚/比较 = Git diff / commit。
- 如未来使用 Git tag，它也只是可选的人类导航标签，不是新的权威或版本体系。

状态文件中的 schema 标识或外部 checkpoint revision 只用于校验数据格式/便携存档谱系，**不是项目版本号**。

## 存档模型

日常游戏进度在合法行动结算后通过 registry 登记的 `STATE_COMMIT` 写入：

```text
state/current/SOUL_STATE_V1.yaml
```

因此：

- `存档 / 保存进度`：只确认当前 Git state 已持久化。
- `读档 / 继续 / 恢复游戏`：直接从 Git current state 恢复。
- 只有明确要求外部便携 checkpoint、导入旧 checkpoint 或迁移时，才进入对应 Save Manager 控制事务；这些外部文件始终不是项目主权威。

## 不再存在兼容 runtime 包

仓库不再维护或生成兼容 runtime ZIP，也不再维护 package manifest、runtime member list、runtime exporter、package audit 或 package release 字段。

如果这些旧结构重新被提交进 source tree，仓库卫生 QA 应直接失败，而不是重新恢复一套兼容包流程。

## 全局 QA

本地完整检查：

```bash
python3 qa/check_repository_hygiene.py --project .
python3 qa/validate_registry.py --project .
python3 qa/check_route_conflicts.py --project .
python3 qa/check_content_contracts.py
python3 qa/check_state_invariants.py --project .
python3 qa/check_git_first_architecture.py --project .
```

仓库卫生检查会阻止 ZIP、backup、patch、build/dist、临时缓存、旧 package manifest、compatibility runtime 目录/导出脚本，以及写死的旧 runtime package 文件名重新进入 source tree；受管文本统一保持 UTF-8、LF 与完整文件结尾。
