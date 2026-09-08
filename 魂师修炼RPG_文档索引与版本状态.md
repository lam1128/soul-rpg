# 魂师修炼RPG｜文档索引与版本状态

> 状态：ACTIVE
>
> **Git 源码治理入口：** `governance/project.md` + `runtime/registry.json`。
>
> **兼容运行包入口：** 本文件 + `魂师修炼RPG_manifest.json`。
>
> **关键约定：** 本项目旧文档中的 `manifest` 是“当前机器注册表”的语义简称。Git 源码中的唯一机器主源是 `runtime/registry.json`；兼容运行包中的 `魂师修炼RPG_manifest.json` 是由该 registry 生成的派生视图。
>
> **不负责：** 不定义战斗、世界、剧情、人物、经济、UI、状态 schema 或某次冒险的当前具体值。

## 1. 治理顺序

Git 源码维护时：

`governance/project.md → runtime/registry.json → 当前事务 owner / dispatcher`

兼容运行包启动时：

`本索引 → 兼容 manifest 启动切片 → startup router → control pre-router → 当前候选 recognition owner`

每条新的用户主动消息都重新经过 control pre-router；不得靠聊天记忆或上轮 route 永久绑定当前事务。控制事务未命中时，才进入普通游戏启动与 `interaction_route_activation`。

## 2. 单一职责与主源

- 一个职责只有一个 owner。
- `runtime/registry.json` 只登记稳定 owner 路径、route、access、state access、control intent、外部 Skill 和外部 source；不复制业务常量。
- 非 owner 文件只能保留逻辑指针、调用顺序、占位符、输入/输出槽位与最小消费说明。
- 禁止消费者复制 owner 的固定数字、公式、门槛、完整表格、固定时长、价格、篇章算法或判定文本。
- UI 只拥有展示结构；README 只负责导航；QA 只定义/实现 PASS 检查；Runtime Kernel 只负责编排；交互文件不维护第二套路由表。
- `12_状态存档.md` 只拥有状态 schema、恢复、迁移、运行提交与导出协议，不保存当前冒险实例值，也不复制领域业务常量。

## 3. Git-first 与状态模型

项目源码、路由、治理与当前冒险状态都由 Git `main` HEAD 持久化：

- `state/current/SOUL_STATE_V1.yaml`：当前稳定冒险状态 owner；
- `runtime_working_state`：从当前稳定状态形成的单轮事务候选，不是第二持久化主源；
- 普通游戏 route 在领域计算与 `12` 校验通过后，通过 registry 登记的 `STATE_COMMIT` 一次写回稳定 state owner；
- Git commit SHA 是当前状态的持久历史身份；普通游戏状态提交不自动增加 `STATE_REV`；
- `STATE_REV` 只表示兼容 checkpoint lineage revision；`SAVE_EXPORT` / 需要新 checkpoint revision 的显式迁移才更新它；
- 外部 `SOUL_STATE_V1` ZIP 只作为 immutable import/export compatibility artifact，不能覆盖 Git `main` 的状态权威；
- Git 项目整理、帮助、查看或游戏外讨论不得自动推进游戏世界。

## 4. 读取与状态访问

读取策略与状态访问等级只读取 `runtime/registry.json`。治理原则：先确认事务及 dispatcher（route 或 Skill），再读取最小必要来源；来源不足才扩读。读取静态主源不等于拥有写权限。

`DM_ONLY_C00_伙伴篇章库.md` 是篇章索引/通用规则 owner；45 章正文仍位于 `DM_ONLY_C10_伙伴篇章/`。进入或继续篇章时必须通过 `companion_episode_files[CHAPTER_ID]` 只解析一个单章文件，严禁遍历/批量加载单章目录。

## 5. 路由纪律

- control intent 的清单、优先级、recognition owner 与 dispatcher 映射只存在于 registry。
- 普通游戏 route 的匹配顺序和 activation 条件只存在于 registry。
- Skill 接管的复杂控制事务不得保留同职责空壳 route。
- 一个普通 route 应有一个主 owner；跨领域子事务使用 `delegates_to` 或条件 source，不建立万能 route。
- 没有 control intent、启动入口、ordinary activation、delegates 或其他真实消费者的 route 视为孤儿，应删除或接入真实入口。

## 6. 墓碑与仓库卫生

Git `main` 不保留 `_old / _backup / final_final`、已消费 patch/handoff、临时测试输出、构建产物、无消费者旧接口或重复业务主源。历史由 Git commit 保存，不需要把施工史继续留在当前 tree。

兼容运行包是派生视图，只包含 `compatibility/runtime-members.json` 登记的正式 runtime 成员；不得把 `.github/`、仓库 QA 脚本、导出脚本或其它 source-only 工具塞入运行包。

## 7. 文件维护与 QA

项目维护事务由 `soul-rpg-project-maintainer` 边界处理；存档加载/导出/迁移由 `soul-rpg-save-manager` 边界处理。业务 owner 与 PASS 条件仍属于项目文件，外部 Skill 只拥有工作流。

- targeted 修改：运行受影响范围的增量 QA；
- registry / route / schema / state lifecycle / external Skill interface 结构修改：扩展到依赖闭包；
- 明确全局检查、整理/清理项目或正式 RELEASE：运行完整 Global QA；
- 兼容 runtime export：必须从磁盘重开后再次校验成员、JSON、bytes/SHA 与 route 完整性。

## 8. 发布与版本

项目源码的正式 release 身份是通过全部门槛的不可变 Git commit SHA。Git tag 只可作为人类可读标签，不是权威。

兼容 runtime ZIP 继续保留两段式 `MAJOR.MINOR`，仅作为派生运行包版本：普通治理/结构清理默认只递增 MINOR；只有用户明确要求主版本时才跨 MAJOR。该 package release 与存档 `STATE_REV` 仍是独立对象。

## 9. 当前结构约束

- Git 源码机器主源：`runtime/registry.json`。
- 兼容包机器派生视图：`魂师修炼RPG_manifest.json`。
- startup fast entry 与 control pre-router 仍是运行入口；复杂项目维护和存档事务直接 dispatch 到外部 Skill。
- 当前稳定状态只认 registry 登记的 `state/current/SOUL_STATE_V1.yaml`；外部 checkpoint 只从 `external_sources.checkpoint_import` 进入显式导入/恢复流程。
- README 与专用项目入口协议不复制业务实现。
- freeze 集合、route、control intent、external source、state model 只认 registry；兼容 manifest 只能镜像，不可反向覆盖。
