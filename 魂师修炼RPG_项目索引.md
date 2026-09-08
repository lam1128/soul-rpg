# 魂师修炼RPG｜项目索引

> 状态：ACTIVE
>
> **唯一治理入口：** `governance/project.md` + `runtime/registry.json`。
>
> **精确项目身份：** Git `main` HEAD 的 commit SHA。
>
> **不负责：** 不定义战斗、世界、剧情、人物、经济、UI、状态 schema 或某次冒险的当前具体值。

## 1. 治理顺序与读取边界

每次开始、恢复、继续游戏或处理新游戏行动时：

`governance/project.md → runtime/registry.json → current.startup_router_fast_entry → current.control_intent_pre_router → 当前 dispatcher`

每条新的用户主动消息都重新经过 control pre-router；不得靠聊天记忆或上轮 route 永久绑定当前事务。控制事务未命中时，才进入普通游戏启动与 `interaction_route_activation`。

读取项目内容必须遵守 registry 当前登记的 access policy 与 sources：只读取当前事务所需 owner、章节、对象和动态字段；来源不足时才按登记 fallback 扩读。大型 DM ONLY 内容不得为了方便一次性全文加载。

## 2. 单一职责与主源

- 一个职责只有一个 owner。
- `runtime/registry.json` 只登记稳定 owner 路径、route、access、state access、control intent、外部 Skill 和外部 source；不复制业务常量。
- 非 owner 文件只能保留逻辑指针、调用顺序、占位符、输入/输出槽位与最小消费说明。
- 禁止消费者复制 owner 的固定数字、公式、门槛、完整表格、固定时长、价格、篇章算法或判定文本。
- UI 只拥有展示结构；README 只负责导航；QA 只定义/实现 PASS 检查；Runtime Kernel 只负责编排；交互文件不维护第二套路由表。
- `12_状态存档.md` 只拥有状态 schema、恢复、迁移、运行提交与外部 checkpoint 协议，不保存当前冒险实例值，也不复制领域业务常量。

## 3. Git-only 与状态模型

项目源码、路由、治理与当前冒险状态全部由 Git `main` HEAD 持久化：

- `state/current/SOUL_STATE_V1.yaml`：当前稳定冒险状态 owner；
- `runtime_working_state`：从当前稳定状态形成的单轮事务候选，不是第二持久化主源；
- 普通游戏 route 在领域计算与 `12` 校验通过后，通过 registry 登记的 `STATE_COMMIT` 一次写回稳定 state owner；
- Git commit SHA 是每次稳定状态变更的持久历史身份；
- 普通“存档 / 保存进度”命中 `SAVE_CURRENT`，只确认 Git current state 已保存；
- 外部 checkpoint 只用于用户明确要求的导入、恢复、便携导出或迁移，不是普通启动源，也不是项目版本；
- Git 项目整理、帮助、查看、保存确认或游戏外讨论不得自动推进游戏世界。

## 4. 项目没有 MAJOR.MINOR 版本号

本项目不维护 `v3.11`、`MAJOR.MINOR`、SemVer 或其它人工 release 序列。

- 当前源码身份只认 Git commit SHA；
- 历史只认 Git commit history；
- 比较和回滚只认 Git diff / commit；
- Git tag 若未来存在，只能作为可选导航标签，不构成第二套项目版本体系；
- 数据 schema 标识与外部 checkpoint revision 只是数据协议字段，不等于项目版本。

因此，项目维护、结构清理、内容修改和正式交付检查都不再执行“升版本号”动作。

## 5. 路由纪律

- control intent 的清单、优先级、recognition owner 与 dispatcher 映射只存在于 registry。
- 普通游戏 route 的匹配顺序和 activation 条件只存在于 registry。
- Skill 接管的复杂控制事务不得保留同职责空壳 route。
- `SAVE_CURRENT` 与外部 checkpoint `SAVE_EXPORT` 是不同控制意图：前者是只读 Git 保存确认，后者只处理用户明确要求的便携外部 checkpoint；不得因都含“存档”一词而重新合并职责。
- 一个普通 route 应有一个主 owner；跨领域子事务使用 `delegates_to` 或条件 source，不建立万能 route。
- 没有 control intent、启动入口、ordinary activation、delegates 或其他真实消费者的 route 视为孤儿，应删除或接入真实入口。

## 6. 仓库卫生

Git `main` 不保留 `_old / _backup / final_final`、已消费 patch/handoff、临时测试输出、构建产物、无消费者旧接口、重复业务主源或其它施工痕迹。历史由 Git commit 保存，不需要把旧文件复制留在当前 tree。

兼容 runtime ZIP 架构已经废止。当前 tree 不应存在：

- `compatibility/` runtime member list；
- runtime ZIP exporter；
- runtime package manifest；
- package audit / derived export QA；
- package release / `MAJOR.MINOR` 字段；
- 任何为了无 Git checkout fallback 而维护的第二运行入口。

这些内容若重新出现，仓库卫生 QA 应直接失败。

## 7. 文件维护与 QA

项目维护事务由 `soul-rpg-project-maintainer` 边界处理；外部 checkpoint 加载/导出/迁移由 `soul-rpg-save-manager` 边界处理。普通 `SAVE_CURRENT` 不调用 Save Manager。业务 owner 与 PASS 条件仍属于项目文件，外部 Skill 只拥有工作流。

- targeted 修改：运行受影响范围的增量 QA；
- registry / route / schema / state lifecycle / external Skill interface 结构修改：扩展到依赖闭包；
- 明确全局检查、整理/清理项目或正式 Git 交付检查：运行完整 Global QA；
- 不存在 compatibility runtime export gate，也不生成 package 作为 QA 产物。

## 8. 当前结构约束

- Git 源码机器主源：`runtime/registry.json`。
- startup fast entry 与 control pre-router 是运行入口；复杂项目维护和外部 checkpoint 事务按 registry 直接 dispatch 到对应 Skill，普通保存确认走只读 route。
- 当前稳定状态只认 registry 登记的 `state_model.current_state_owner`；外部 checkpoint 只从 `external_sources.checkpoint_import` 进入显式导入/恢复流程。
- README 与专用项目入口协议不复制业务实现。
- freeze 集合、route、control intent、external source、state model 只认 registry。
