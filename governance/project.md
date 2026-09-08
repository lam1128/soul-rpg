# 魂师修炼RPG｜Git-first 治理

- Git 仓库是项目规则、路由、治理、QA 与工程历史的唯一持久化权威；`main` HEAD 表示当前有效项目源码。
- `runtime/registry.json` 是唯一机器运行注册表，拥有启动入口、route、control intent、访问策略、外部 Skill 接口、稳定 owner 路径与兼容 checkpoint 导入源发现。
- 各业务规则仍由现有稳定 owner 文件独占；Git 负责版本、差异、回滚与持久化，不把业务常量复制进 registry、QA 或治理文件。
- 当前冒险状态也采用 Git-first：`state/current/SOUL_STATE_V1.yaml` 是当前稳定状态 owner，`main` HEAD 同时持有规则与状态；普通游戏候选经 schema/领域校验后通过 `STATE_COMMIT` 写入该稳定路径。外部 `SOUL_STATE_V1` ZIP 只保留为兼容导入/导出物，不再是主持久化权威。
- `魂师修炼RPG_manifest.json` 仅作为兼容运行包根目录中的**派生导出视图**存在，由 `runtime/registry.json` 与当前源码在导出时生成；Git source tree 不持久化该生成文件，它不得反向成为 Git 源码权威。
- 已明确范围的 targeted 内容修改只读取目标 owner 及直接语义/格式依赖；涉及 route、schema、state lifecycle、持久化接口或外部 Skill 接口时，只扩展到对应依赖闭包与受影响 Skill 边界。
- 只有明确的全局检查、清理/整理项目、广泛结构维护或正式 RELEASE 才运行完整 active responsibility surface 的 Global QA。
- GitHub Actions 可在 push/PR 后运行仓库回归。普通 targeted repair 不因为 CI 尚未完成而改变其业务事实；正式 RELEASE 必须以精确候选 commit 通过全部 release gate。
- 正式项目 release 以不可变 Git commit SHA 作为身份；兼容运行包保留 `MAJOR.MINOR` 仅用于导出物兼容与人工识别，不构成项目源码权威。
- 生成视图只允许作为可再生消费者存在。兼容 manifest、兼容 runtime ZIP 都必须能从 Git 源码重新生成，并通过重开验证；生成后的 manifest 只存在于导出结果/临时验证面，不作为长期 source 成员提交回 `main`。
