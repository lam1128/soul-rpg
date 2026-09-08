# 魂师修炼RPG｜Git-only 治理

- Git 仓库是项目规则、路由、治理、QA、工程历史与当前正式游戏状态的唯一持久化权威；`main` HEAD 表示当前有效项目。
- `runtime/registry.json` 是唯一机器运行注册表，拥有启动入口、route、control intent、访问策略、外部 Skill 接口、稳定 owner 路径与状态生命周期指针。
- 各业务规则由现有稳定 owner 文件独占；Git 负责历史、差异、回滚与持久化，不把业务常量复制进 registry、QA 或治理文件。
- 当前冒险状态同样 Git-first：registry 登记的 `state_model.current_state_owner` 是唯一 current state；普通游戏候选经 schema/领域校验后通过 `STATE_COMMIT` 写回该稳定路径。
- 普通“存档 / 保存进度”只确认 Git current state 已持久化；普通“读档 / 继续 / 恢复游戏”直接读取 Git current state。外部 checkpoint 只在用户明确要求导入、恢复、便携导出或迁移时作为非权威输入/输出使用。
- **项目不维护 `MAJOR.MINOR`、SemVer 或 `v3.11` 一类项目 release 号。** 精确项目身份只认 Git commit SHA；Git tag 如存在也只作为可选的人类导航标签，不构成第二权威。
- **项目不再生成或维护兼容 runtime ZIP。** source tree 不保留 compatibility member list、runtime ZIP exporter、runtime package manifest、package audit 或 package release 字段；这些结构若重新出现，应由仓库卫生 QA 判失败。
- 已明确范围的 targeted 内容修改只读取目标 owner 及直接语义/格式依赖；涉及 route、schema、state lifecycle、持久化接口或外部 Skill 接口时，只扩展到对应依赖闭包与受影响 Skill 边界。
- 只有明确的全局检查、清理/整理项目、广泛结构维护或正式 Git 交付检查才运行完整 active responsibility surface 的 Global QA。
- GitHub Actions 可在 push/PR 后运行仓库回归。普通 targeted repair 不因为 CI 尚未完成而改变其业务事实；需要正式交付时，以精确候选 commit 通过全部 gate 为准，不进行版本号递增。
- 任何可从 Git current source 再生但没有独立运行职责的包级生成物、备份、补丁、旧接口和施工痕迹都属于墓碑，应从当前 tree 删除。
