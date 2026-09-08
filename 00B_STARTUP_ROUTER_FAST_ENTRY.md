# 魂师修炼RPG｜Startup Router Fast Entry

> **文件职责：** 新窗口的极小启动入口，只决定下一步读取什么。
>
> **权威范围：** 启动顺序与“禁止无条件全文加载”的快速门。
>
> **不负责：** 不执行存档选择、状态恢复、结算、业务判断或写入。
>
> **读取策略：** `BOOT`。

## 1. 新窗口顺序

Git 源码中：

`runtime/registry.json 启动切片`
→ `current.startup_router_fast_entry`
→ `current.control_intent_pre_router`
→ `control_intents.<candidate>.recognition_owner`。

兼容 runtime ZIP 中，root `魂师修炼RPG_manifest.json` 是由同一 registry 生成的启动镜像。fast exception 是否存在、指向哪里，只读取当前机器注册表；本文件不写死当前值。

## 2. registry 启动切片

BOOT 只解析启动必需键：

- `project / status / source_authority`
- `current`
- `fast_exceptions`
- `control_intents`
- `state_model.current_state_owner` 与 `internal_services.state_commit` 的入口元数据
- `external_sources.checkpoint_import` 的兼容导入入口元数据

完整 `topic_routes / interaction_route_activation` 仍是机器权威，但只在对应事务确认后取当前需要的条目。兼容 manifest 的成员/SHA 数据属于导出完整性元数据，不应注入普通 runtime 上下文。

## 3. 状态入口

- Git 源码可用时，“继续游戏 / 继续 / 恢复游戏”默认直接读取 `state_model.current_state_owner`，不再触发外部存档选择。
- 新窗口没有会话候选态但存在合法 current state 时，直接从 Git `main` 当前 state owner 建立本轮 `runtime_working_state`。
- 只有用户明确要求“加载/恢复某个存档 ZIP、导入旧存档、切回某个外部 checkpoint”时才进入 `LOAD_SAVE`。外部候选合法性、排序与冲突规则只读取 `external_sources.checkpoint_import` 与 `12`，本文件不复制选择算法。
- 兼容 runtime ZIP 不包含 canonical Git state；仅在没有 Git checkout 的 fallback 环境中，才通过外部 checkpoint 建立会话工作态。
- Git current state 与合法 checkpoint 都不存在时，不得依赖聊天记忆重建状态；只有明确新游戏意图才进入 `NEW_GAME`。

## 4. 禁止事项

- 不得在识别意图前全文读取全部游戏文件。
- 不得启动时加载大型 DM ONLY 数据库。
- recognition 只决定“去哪里”，不代表事务已经执行成功。
- 不得把 `12_状态存档.md` 当某次冒险的数据文件。
- 不得原地修改已有 checkpoint ZIP；不得绕过 `STATE_COMMIT` 直接写稳定 Git state。
- 未确认控制事务时才进入普通游戏链。
